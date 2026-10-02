import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.events.models import EventLog, EventType
from apps.instances.models import DesktopInstance, InstanceStatus
from apps.templates.models import DesktopTemplate


@pytest.mark.django_db
def test_dashboard_statistics_are_scoped_to_the_user():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    other = User.objects.create_user("other", "other@example.com", "SecurePass123!")
    template = DesktopTemplate.objects.create(name="Minimal", slug="minimal", json_configuration={"image": "desktop:minimal"})
    DesktopInstance.objects.create(user=user, template=template, name="Running", cpu_limit="2.00", memory_limit="2G", status=InstanceStatus.RUNNING)
    DesktopInstance.objects.create(user=user, template=template, name="Failed", cpu_limit="1", memory_limit="1G", status=InstanceStatus.FAILED)
    DesktopInstance.objects.create(user=other, template=template, name="Other running", cpu_limit="8.00", memory_limit="8G", status=InstanceStatus.RUNNING)
    EventLog.objects.create(actor=user, event_type=EventType.INSTANCE_REQUESTED, message="Instance provisioning requested.")

    client = APIClient()
    # Session authentication has no WWW-Authenticate header, so DRF signals
    # unauthenticated requests with 403 (code NOT_AUTHENTICATED).
    assert client.get(reverse("analytics-dashboard")).status_code == 403

    client.force_authenticate(user)
    response = client.get(reverse("analytics-dashboard"))
    assert response.status_code == 200
    data = response.data["data"]
    assert data["instances"]["total"] == 2
    assert data["instances"]["running"] == 1
    assert data["instances"]["failed"] == 1
    # Usage aggregates only the user's running instances
    assert data["usage"]["cpu_cores"] == 2.0
    assert data["usage"]["memory_gb"] == 2.0
    assert any(event["event_type"] == EventType.INSTANCE_REQUESTED for event in data["recent_activity"])


@pytest.mark.django_db
def test_event_history_returns_only_own_events():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    other = User.objects.create_user("other", "other@example.com", "SecurePass123!")
    EventLog.objects.create(actor=user, event_type=EventType.INSTANCE_REQUESTED, message="Mine.")
    EventLog.objects.create(actor=other, event_type=EventType.INSTANCE_REQUESTED, message="Theirs.")

    client = APIClient()
    # See the dashboard test: unauthenticated requests surface as 403.
    assert client.get(reverse("event-list")).status_code == 403

    client.force_authenticate(user)
    response = client.get(reverse("event-list"))
    assert response.status_code == 200
    events = response.data["data"]["events"]
    assert len(events) == 1
    assert events[0]["message"] == "Mine."
