import pytest
from django.urls import reverse
from unittest.mock import patch
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.events.models import EventLog, EventType
from apps.instances.models import DesktopInstance, InstanceStatus
from apps.templates.models import DesktopTemplate


@pytest.mark.django_db
@patch("tasks.provisioning.provision_instance.delay")
def test_user_can_order_enabled_template_and_only_see_own_instances(delay):
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    other = User.objects.create_user("other", "other@example.com", "SecurePass123!")
    template = DesktopTemplate.objects.create(name="Minimal", slug="minimal", json_configuration={"image": "desktop:minimal"})
    client = APIClient(); client.force_authenticate(user)
    response = client.post(reverse("instance-list"), {"name": "My desktop", "template_id": str(template.id), "cpu_limit": "2.00", "memory_limit": "2G", "persistent": True, "auto_stop_minutes": 60}, format="json")
    assert response.status_code == 202
    instance = DesktopInstance.objects.get()
    assert instance.status == InstanceStatus.QUEUED
    assert instance.container_name.startswith("dcp-")
    delay.assert_called_once_with(str(instance.id))
    assert EventLog.objects.filter(actor=user, event_type=EventType.INSTANCE_REQUESTED).exists()
    DesktopInstance.objects.create(user=other, template=template, name="Other", cpu_limit="1", memory_limit="1G")
    listed = client.get(reverse("instance-list"))
    assert len(listed.data["data"]["instances"]) == 1


@pytest.mark.django_db
def test_instance_order_rejects_disabled_or_missing_template():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = DesktopTemplate.objects.create(name="Disabled", slug="disabled", json_configuration={"image": "desktop:old"}, enabled=False)
    client = APIClient(); client.force_authenticate(user)
    response = client.post(reverse("instance-list"), {"name": "No", "template_id": str(template.id), "cpu_limit": "2", "memory_limit": "2G"}, format="json")
    assert response.status_code == 400
