import pytest
from django.urls import reverse
from unittest.mock import MagicMock, patch
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


@pytest.mark.django_db
def test_instance_subdomain_is_hash_based(settings):
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = DesktopTemplate.objects.create(name="Minimal", slug="minimal", json_configuration={"image": "desktop:minimal"})
    instance = DesktopInstance.objects.create(user=user, template=template, name="My desktop", cpu_limit="1", memory_limit="1G")
    assert instance.subdomain == f"{instance.access_hash[:7].lower()}.{settings.TRAEFIK_DOMAIN}"
    assert instance.subdomain.endswith(".localhost")
    assert instance.subdomain == instance.subdomain.lower()


@pytest.mark.django_db
def test_container_creation_assigns_subdomain_labels():
    from docker_manager.manager import DockerManager

    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = DesktopTemplate.objects.create(name="Minimal", slug="minimal", json_configuration={"image": "desktop:minimal"})
    instance = DesktopInstance.objects.create(user=user, template=template, name="My desktop", cpu_limit="2", memory_limit="2G", persistent=True)

    manager = DockerManager()
    manager._client = MagicMock()
    manager.create_container(instance=instance, template=template)

    _, kwargs = manager._client.containers.create.call_args
    router = f"desktop-{instance.id}"
    labels = kwargs["labels"]
    assert labels["traefik.enable"] == "true"
    assert labels[f"traefik.http.routers.{router}.rule"] == f"Host(`{instance.subdomain}`)"
    assert labels[f"traefik.http.services.{router}.loadbalancer.server.port"] == "3000"
    assert kwargs["volumes"]  # persistent volume attached for persistent instances


@pytest.mark.django_db
def test_launch_returns_url_for_running_owned_instance(settings):
    settings.DEBUG = True  # match development, where the launch URL is http
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    other = User.objects.create_user("other", "other@example.com", "SecurePass123!")
    template = DesktopTemplate.objects.create(name="Minimal", slug="minimal", json_configuration={"image": "desktop:minimal"})
    running = DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.RUNNING)
    theirs = DesktopInstance.objects.create(user=other, template=template, name="Theirs", cpu_limit="1", memory_limit="1G", status=InstanceStatus.RUNNING)
    queued = DesktopInstance.objects.create(user=user, template=template, name="Queued", cpu_limit="1", memory_limit="1G")

    client = APIClient(); client.force_authenticate(user)
    response = client.get(reverse("instance-launch", kwargs={"instance_id": running.id}))
    assert response.status_code == 200
    assert response.data["data"]["url"] == f"http://{running.subdomain}"
    assert EventLog.objects.filter(actor=user, event_type=EventType.INSTANCE_LAUNCHED).exists()
    # Not running → 409; not owned → 404
    assert client.get(reverse("instance-launch", kwargs={"instance_id": queued.id})).status_code == 409
    assert client.get(reverse("instance-launch", kwargs={"instance_id": theirs.id})).status_code == 404
