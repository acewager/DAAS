import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.events.models import EventLog, EventType
from apps.templates.models import DesktopTemplate


def payload(**overrides):
    return {"name": "XFCE Minimal", "slug": "xfce-minimal", "description": "Small desktop", "json_configuration": {"image": "ghcr.io/example/xfce:1"}, "enabled": True, **overrides}


@pytest.mark.django_db
def test_templates_are_admin_managed_and_visible_only_when_enabled():
    client = APIClient()
    user = User.objects.create_user("user", "user@example.com", "SecurePass123!")
    admin = User.objects.create_user("admin", "admin@example.com", "SecurePass123!", role=UserRole.ADMIN)
    client.force_authenticate(user)
    assert client.post(reverse("template-list"), payload(), format="json").status_code == 403
    client.force_authenticate(admin)
    created = client.post(reverse("template-list"), payload(), format="json")
    assert created.status_code == 201
    template_id = created.data["data"]["template"]["id"]
    assert EventLog.objects.filter(event_type=EventType.TEMPLATE_CREATED, actor=admin).exists()
    client.force_authenticate(user)
    assert len(client.get(reverse("template-list")).data["data"]["templates"]) == 1
    client.force_authenticate(admin)
    assert client.delete(reverse("template-detail", kwargs={"template_id": template_id})).status_code == 204
    client.force_authenticate(user)
    assert client.get(reverse("template-list")).data["data"]["templates"] == []


@pytest.mark.django_db
def test_template_rejects_invalid_json_configuration():
    admin = User.objects.create_user("admin", "admin@example.com", "SecurePass123!", role=UserRole.ADMIN)
    client = APIClient(); client.force_authenticate(admin)
    response = client.post(reverse("template-list"), payload(json_configuration={}), format="json")
    assert response.status_code == 400
    assert not DesktopTemplate.objects.exists()
