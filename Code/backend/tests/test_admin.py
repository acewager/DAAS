import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.events.models import EventLog, EventType
from apps.instances.models import DesktopInstance, InstanceStatus
from apps.software_requests.models import SoftwareRequest
from apps.templates.models import DesktopTemplate


def auth_client(user):
    client = APIClient(); client.force_authenticate(user)
    return client


def make_admin(role=UserRole.ADMIN, username="admin"):
    return User.objects.create_user(username, f"{username}@example.com", "SecurePass123!", role=role)


def make_instance(user, status=InstanceStatus.RUNNING, name="Mine"):
    template, _ = DesktopTemplate.objects.get_or_create(
        name="Minimal", slug="minimal", defaults={"json_configuration": {"image": "desktop:minimal"}}
    )
    return DesktopInstance.objects.create(user=user, template=template, name=name, cpu_limit="2", memory_limit="2G", status=status)


@pytest.mark.django_db
def test_admin_user_list_is_admin_only_with_search_and_pagination():
    admin = make_admin()
    user = User.objects.create_user("alice", "alice@example.com", "SecurePass123!")
    other = User.objects.create_user("bob", "bob@example.com", "SecurePass123!")
    make_instance(user)

    url = reverse("admin-user-list")
    assert auth_client(user).get(url).status_code == 403

    client = auth_client(admin)
    response = client.get(url)
    assert response.status_code == 200
    data = response.data["data"]
    assert data["pagination"]["total"] == 3
    alice = next(u for u in data["users"] if u["username"] == "alice")
    assert alice["instance_count"] == 1

    found = client.get(url + "?search=alice")
    assert found.data["data"]["pagination"]["total"] == 1
    assert found.data["data"]["users"][0]["username"] == "alice"

    admins_only = client.get(url + "?role=ADMIN")
    assert admins_only.data["data"]["pagination"]["total"] == 1

    paged = client.get(url + "?page=2&page_size=1")
    assert paged.data["data"]["pagination"]["page"] == 2
    assert len(paged.data["data"]["users"]) == 1


@pytest.mark.django_db
def test_admin_user_patch_role_and_activation():
    super_admin = make_admin(role=UserRole.SUPER_ADMIN, username="super")
    admin = make_admin(username="admin")
    user = User.objects.create_user("alice", "alice@example.com", "SecurePass123!")
    url = reverse("admin-user-detail", kwargs={"user_id": str(user.id)})

    # Any admin can toggle activation
    response = auth_client(admin).patch(url, {"is_active": False}, format="json")
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.is_active is False

    # Role changes require a super admin
    response = auth_client(admin).patch(url, {"role": UserRole.ADMIN}, format="json")
    assert response.status_code == 400
    response = auth_client(super_admin).patch(url, {"role": UserRole.ADMIN}, format="json")
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.role == UserRole.ADMIN


@pytest.mark.django_db
def test_admin_cannot_change_own_role_or_activation():
    super_admin = make_admin(role=UserRole.SUPER_ADMIN, username="super")
    url = reverse("admin-user-detail", kwargs={"user_id": str(super_admin.id)})
    client = auth_client(super_admin)
    assert client.patch(url, {"role": UserRole.USER}, format="json").status_code == 400
    assert client.patch(url, {"is_active": False}, format="json").status_code == 400


@pytest.mark.django_db
def test_admin_instance_list_shows_all_users_instances():
    admin = make_admin()
    alice = User.objects.create_user("alice", "alice@example.com", "SecurePass123!")
    bob = User.objects.create_user("bob", "bob@example.com", "SecurePass123!")
    make_instance(alice, name="Alice desktop")
    make_instance(bob, status=InstanceStatus.STOPPED, name="Bob desktop")

    url = reverse("admin-instance-list")
    assert auth_client(alice).get(url).status_code == 403

    client = auth_client(admin)
    response = client.get(url)
    assert response.status_code == 200
    data = response.data["data"]
    assert data["pagination"]["total"] == 2
    usernames = {i["username"] for i in data["instances"]}
    assert usernames == {"alice", "bob"}

    stopped = client.get(url + "?status=STOPPED")
    assert stopped.data["data"]["pagination"]["total"] == 1
    assert stopped.data["data"]["instances"][0]["username"] == "bob"

    found = client.get(url + "?search=alice")
    assert found.data["data"]["pagination"]["total"] == 1


@pytest.mark.django_db
def test_admin_can_act_on_any_users_instance():
    admin = make_admin()
    alice = User.objects.create_user("alice", "alice@example.com", "SecurePass123!")
    instance = make_instance(alice, status=InstanceStatus.STOPPED, name="Alice desktop")

    # Admin starts alice's instance (ownership relaxed for admins, VS-051)
    with patch("docker_manager.manager.docker_manager.start_container") as start_mock:
        response = auth_client(admin).post(reverse("instance-start", kwargs={"instance_id": str(instance.id)}))
        assert response.status_code == 200
        start_mock.assert_called_once()
    instance.refresh_from_db()
    assert instance.status == InstanceStatus.RUNNING

    # ...and stops it again
    with patch("docker_manager.manager.docker_manager.stop_container"):
        response = auth_client(admin).post(reverse("instance-stop", kwargs={"instance_id": str(instance.id)}))
        assert response.status_code == 200
    instance.refresh_from_db()
    assert instance.status == InstanceStatus.STOPPED


from unittest.mock import patch  # noqa: E402  (used above)


@pytest.mark.django_db
def test_admin_event_list_shows_all_events_with_filters():
    admin = make_admin()
    alice = User.objects.create_user("alice", "alice@example.com", "SecurePass123!")
    EventLog.objects.create(actor=alice, event_type=EventType.USER_LOGGED_IN, message="Alice logged in.")
    EventLog.objects.create(actor=alice, event_type=EventType.INSTANCE_REQUESTED, message="Alice requested an instance.")
    EventLog.objects.create(actor=admin, event_type=EventType.SOFTWARE_REQUESTED, message="Software requested: htop.")

    url = reverse("admin-event-list")
    assert auth_client(alice).get(url).status_code == 403

    client = auth_client(admin)
    response = client.get(url)
    assert response.status_code == 200
    assert response.data["data"]["pagination"]["total"] == 3

    by_type = client.get(url + "?event_type=INSTANCE_REQUESTED")
    assert by_type.data["data"]["pagination"]["total"] == 1

    by_search = client.get(url + "?search=htop")
    assert by_search.data["data"]["pagination"]["total"] == 1
    assert by_search.data["data"]["events"][0]["actor_name"] == "admin"


@pytest.mark.django_db
def test_admin_analytics_is_admin_only_with_platform_stats():
    admin = make_admin()
    alice = User.objects.create_user("alice", "alice@example.com", "SecurePass123!")
    make_instance(alice, status=InstanceStatus.RUNNING)
    make_instance(alice, status=InstanceStatus.FAILED, name="Broken")
    SoftwareRequest.objects.create(user=alice, instance=DesktopInstance.objects.first(), software_name="htop")
    EventLog.objects.create(actor=alice, event_type=EventType.INSTANCE_REQUESTED, message="Alice requested an instance.")

    url = reverse("admin-analytics")
    assert auth_client(alice).get(url).status_code == 403

    response = auth_client(admin).get(url)
    assert response.status_code == 200
    data = response.data["data"]
    assert data["users"]["total"] == 2
    assert data["instances"]["running"] == 1
    assert data["instances"]["failed"] == 1
    assert data["software_requests"]["pending"] == 1
    assert len(data["recent_events"]) >= 1


@pytest.mark.django_db
def test_admin_health_reports_checks():
    admin = make_admin()
    url = reverse("admin-health")
    assert auth_client(User.objects.create_user("u", "u@example.com", "SecurePass123!")).get(url).status_code == 403

    with patch("docker_manager.manager.docker_manager.ping", return_value=True):
        response = auth_client(admin).get(url)
    assert response.status_code == 200
    data = response.data["data"]
    assert data["status"] == "healthy"
    assert set(data["checks"]) == {"database", "redis", "docker"}
