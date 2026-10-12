from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.events.models import EventLog, EventType
from docker_manager.manager import docker_manager
from apps.instances.models import DesktopInstance, InstanceStatus
from apps.templates.models import DesktopTemplate


def make_template():
    return DesktopTemplate.objects.create(name="Minimal", slug="minimal", json_configuration={"image": "desktop:minimal"})


def make_running_instance(user, name="Mine", status=InstanceStatus.RUNNING):
    template, _ = DesktopTemplate.objects.get_or_create(
        name="Minimal", slug="minimal", defaults={"json_configuration": {"image": "desktop:minimal"}}
    )
    return DesktopInstance.objects.create(user=user, template=template, name=name, cpu_limit="2", memory_limit="2G", status=status)


@pytest.mark.django_db
def test_start_stop_restart_transitions_with_events():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    instance = DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.STOPPED)
    client = APIClient(); client.force_authenticate(user)

    with patch("docker_manager.manager.docker_manager.start_container") as start_mock:
        assert client.post(reverse("instance-start", kwargs={"instance_id": instance.id})).status_code == 200
        start_mock.assert_called_once()
    instance.refresh_from_db()
    assert instance.status == InstanceStatus.RUNNING
    assert EventLog.objects.filter(actor=user, event_type=EventType.INSTANCE_STARTED).exists()

    # Starting a running instance conflicts → 409
    assert client.post(reverse("instance-start", kwargs={"instance_id": instance.id})).status_code == 409

    with patch("docker_manager.manager.docker_manager.restart_container") as restart_mock:
        assert client.post(reverse("instance-restart", kwargs={"instance_id": instance.id})).status_code == 200
        restart_mock.assert_called_once()
    assert EventLog.objects.filter(actor=user, event_type=EventType.INSTANCE_RESTARTED).exists()

    with patch("docker_manager.manager.docker_manager.stop_container") as stop_mock:
        assert client.post(reverse("instance-stop", kwargs={"instance_id": instance.id})).status_code == 200
        stop_mock.assert_called_once()
    instance.refresh_from_db()
    assert instance.status == InstanceStatus.STOPPED
    assert EventLog.objects.filter(actor=user, event_type=EventType.INSTANCE_STOPPED).exists()

    # Stopping a stopped instance conflicts → 409
    assert client.post(reverse("instance-stop", kwargs={"instance_id": instance.id})).status_code == 409


@pytest.mark.django_db
def test_lifecycle_actions_are_ownership_scoped():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    other = User.objects.create_user("other", "other@example.com", "SecurePass123!")
    template = make_template()
    theirs = DesktopInstance.objects.create(user=other, template=template, name="Theirs", cpu_limit="1", memory_limit="1G", status=InstanceStatus.STOPPED)
    client = APIClient(); client.force_authenticate(user)
    assert client.post(reverse("instance-start", kwargs={"instance_id": theirs.id})).status_code == 404
    assert client.delete(reverse("instance-delete", kwargs={"instance_id": theirs.id})).status_code == 404


@pytest.mark.django_db
@patch("tasks.lifecycle.delete_instance.delay")
def test_delete_queues_async_deletion(delay):
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    instance = DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.RUNNING)
    client = APIClient(); client.force_authenticate(user)

    response = client.delete(reverse("instance-delete", kwargs={"instance_id": instance.id}))
    assert response.status_code == 202
    instance.refresh_from_db()
    assert instance.status == InstanceStatus.DELETING
    delay.assert_called_once_with(str(instance.id), delete_data=False)
    assert EventLog.objects.filter(actor=user, event_type=EventType.INSTANCE_DELETE_REQUESTED).exists()


@pytest.mark.django_db
def test_delete_instance_task_removes_container_and_marks_deleted():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    instance = DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.DELETING)

    with patch("docker_manager.manager.docker_manager.delete_container") as delete_mock:
        from tasks.lifecycle import delete_instance
        delete_instance(str(instance.id))
        delete_mock.assert_called_once()

    instance.refresh_from_db()
    assert instance.status == InstanceStatus.DELETED
    assert EventLog.objects.filter(event_type=EventType.INSTANCE_DELETED).exists()


@pytest.mark.django_db
def test_delete_instance_task_failure_marks_failed():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    instance = DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.DELETING)

    with patch("docker_manager.manager.docker_manager.delete_container", side_effect=Exception("boom")):
        from tasks.lifecycle import delete_instance
        with pytest.raises(Exception):
            delete_instance(str(instance.id))

    instance.refresh_from_db()
    assert instance.status == InstanceStatus.FAILED
    assert EventLog.objects.filter(event_type=EventType.INSTANCE_DELETE_FAILED).exists()


@pytest.mark.django_db
def test_auto_stop_task_stops_only_idle_running_instances():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    idle = DesktopInstance.objects.create(user=user, template=template, name="Idle", cpu_limit="1", memory_limit="1G", status=InstanceStatus.RUNNING, auto_stop_minutes=60)
    recent = DesktopInstance.objects.create(user=user, template=template, name="Recent", cpu_limit="1", memory_limit="1G", status=InstanceStatus.RUNNING, auto_stop_minutes=60)
    DesktopInstance.objects.filter(pk=idle.pk).update(updated_at=timezone.now() - timedelta(minutes=90))

    with patch("docker_manager.manager.docker_manager.stop_container") as stop_mock:
        from tasks.lifecycle import auto_stop_instances
        auto_stop_instances()
        stop_mock.assert_called_once()

    idle.refresh_from_db()
    recent.refresh_from_db()
    assert idle.status == InstanceStatus.STOPPED
    assert recent.status == InstanceStatus.RUNNING


@pytest.mark.django_db
def test_provisioning_records_persistent_volume():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    instance = DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="2", memory_limit="2G", persistent=True)

    with patch("docker_manager.manager.docker_manager.create_container") as create_mock, patch("tasks.provisioning._wait_for_desktop_ui"):
        container = MagicMock()
        container.id = "container-id-123"
        create_mock.return_value = container
        from tasks.provisioning import provision_instance
        provision_instance(str(instance.id))

    instance.refresh_from_db()
    assert instance.status == InstanceStatus.RUNNING
    volume = instance.volume
    assert volume.host_path == f"dcp-data-{instance.id}"
    assert volume.persistent is True
    assert volume.retain_after_delete is True


@pytest.mark.django_db
@patch("tasks.lifecycle.delete_instance.delay")
def test_delete_retains_data_by_default(delay):
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    instance = DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.RUNNING, persistent=True)
    from apps.instances.models import Volume
    Volume.objects.create(instance=instance, host_path=f"dcp-data-{instance.id}")
    client = APIClient(); client.force_authenticate(user)

    response = client.delete(reverse("instance-delete", kwargs={"instance_id": instance.id}))
    assert response.status_code == 202
    delay.assert_called_once_with(str(instance.id), delete_data=False)


@pytest.mark.django_db
@patch("tasks.lifecycle.delete_instance.delay")
def test_delete_with_delete_data_flag_queues_volume_removal(delay):
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    instance = DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.RUNNING, persistent=True)
    client = APIClient(); client.force_authenticate(user)

    response = client.delete(reverse("instance-delete", kwargs={"instance_id": instance.id}) + "?delete_data=true")
    assert response.status_code == 202
    delay.assert_called_once_with(str(instance.id), delete_data=True)


@pytest.mark.django_db
def test_delete_instance_task_removes_volume_only_when_requested():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    instance = DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.DELETING, persistent=True)
    from apps.instances.models import Volume
    volume = Volume.objects.create(instance=instance, host_path=f"dcp-data-{instance.id}")

    # Default (retain): the volume record survives, no Docker call.
    with patch("docker_manager.manager.docker_manager.delete_container") as delete_mock, patch("docker_manager.manager.docker_manager.remove_volume") as remove_mock:
        from tasks.lifecycle import delete_instance
        delete_instance(str(instance.id), delete_data=False)
        delete_mock.assert_called_once()
        remove_mock.assert_not_called()
    assert Volume.objects.filter(pk=volume.pk).exists()
    assert EventLog.objects.filter(event_type=EventType.INSTANCE_DELETED, message__contains="retained").exists()

    # delete_data=True: the volume and its record are removed.
    with patch("docker_manager.manager.docker_manager.delete_container"), patch("docker_manager.manager.docker_manager.remove_volume") as remove_mock:
        delete_instance(str(instance.id), delete_data=True)
        remove_mock.assert_called_once_with(name=f"dcp-data-{instance.id}")
    assert not Volume.objects.filter(pk=volume.pk).exists()
    assert EventLog.objects.filter(event_type=EventType.INSTANCE_DELETED, message__contains="removed").exists()


@pytest.mark.django_db
def test_attached_volume_implies_persistence_and_mounts_data_path():
    """VS-043: attaching retained storage forces persistence and mounts the
    retained volume at the desktop's data path (VS-054 follow-up — the
    webtop's home is /config, not /home/user)."""
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    old_instance = make_running_instance(user, name="Old")

    from apps.instances.models import Volume

    volume = Volume.objects.create(instance=old_instance, host_path="dcp-data-old", persistent=True)

    client = APIClient(); client.force_authenticate(user)
    response = client.post(reverse("instance-list"), {
        "name": "New desktop", "template_id": str(old_instance.template_id),
        "cpu_limit": "2", "memory_limit": "2G",
        "persistent": False,  # the user forgot — attaching implies it
        "auto_stop_minutes": 60, "attach_volume_id": str(volume.id),
    }, format="json")
    assert response.status_code == 202
    new_instance = DesktopInstance.objects.get(name="New desktop")
    assert new_instance.persistent is True  # forced by the attach
    assert new_instance.volume.host_path == "dcp-data-old"  # the retained volume re-pointed

    client_mock = MagicMock()
    fake_container = MagicMock(); fake_container.id = "abc123"
    client_mock.containers.create.return_value = fake_container
    with patch.object(docker_manager, "_client", client_mock), patch("tasks.provisioning._wait_for_desktop_ui"):
        from tasks.provisioning import provision_instance
        provision_instance(str(new_instance.id))
        _, kwargs = client_mock.containers.create.call_args
        assert list(kwargs["volumes"].keys()) == ["dcp-data-old"]  # the retained volume mounted
        assert kwargs["volumes"]["dcp-data-old"]["bind"] == "/config"  # the webtop data path


@pytest.mark.django_db
def test_volume_attach_is_ownership_scoped():
    owner = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    other = User.objects.create_user("other", "other@example.com", "SecurePass123!")
    template, _ = DesktopTemplate.objects.get_or_create(
        name="Minimal", slug="minimal", defaults={"json_configuration": {"image": "desktop:minimal"}}
    )
    old_instance = make_running_instance(owner, name="Old")
    from apps.instances.models import Volume
    volume = Volume.objects.create(instance=old_instance, host_path="dcp-data-old", persistent=True)

    other_client = APIClient(); other_client.force_authenticate(other)
    response = other_client.post(reverse("instance-list"), {
        "name": "Steal", "template_id": str(template.id), "cpu_limit": "2",
        "memory_limit": "2G", "persistent": True, "auto_stop_minutes": 60,
        "attach_volume_id": str(volume.id),
    }, format="json")
    assert response.status_code == 409  # not this account's volume
