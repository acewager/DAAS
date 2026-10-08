import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.instances.models import DesktopInstance, InstanceStatus
from apps.templates.models import DesktopTemplate


def make_template():
    return DesktopTemplate.objects.create(name="Minimal", slug="minimal", json_configuration={"image": "desktop:minimal"})


def auth_request(client, host):
    """Simulate Traefik's ForwardAuth call: the original host header is
    forwarded as X-Forwarded-Host."""
    return client.get("/api/v1/auth/desktop-auth/", HTTP_X_FORWARDED_HOST=host)


@pytest.mark.django_db
def test_unauthenticated_desktop_access_gets_401_page():
    client = APIClient()
    response = auth_request(client, "abcdefg.localhost")
    assert response.status_code == 401
    assert response["Content-Type"] == "text/html"
    assert b"Sign in required" in response.content


@pytest.mark.django_db
def test_owner_running_instance_is_authorized():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    instance = DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.RUNNING)
    client = APIClient(); client.force_authenticate(user)
    response = auth_request(client, instance.subdomain)
    assert response.status_code == 200


@pytest.mark.django_db
def test_owner_stopped_instance_gets_not_running_page():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    instance = DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.STOPPED)
    client = APIClient(); client.force_authenticate(user)
    response = auth_request(client, instance.subdomain)
    assert response.status_code == 409
    assert b"Desktop not running" in response.content


@pytest.mark.django_db
def test_non_owner_is_denied():
    owner = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    other = User.objects.create_user("other", "other@example.com", "SecurePass123!")
    template = make_template()
    DesktopInstance.objects.create(user=owner, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.RUNNING)
    client = APIClient(); client.force_authenticate(other)
    response = auth_request(client, "abcdefg.localhost")
    assert response.status_code == 403
    assert b"Access denied" in response.content


@pytest.mark.django_db
def test_deleted_instances_are_not_authorized():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.DELETED)
    client = APIClient(); client.force_authenticate(user)
    assert auth_request(client, "abcdefg.localhost").status_code == 403


@pytest.mark.django_db
def test_unknown_subdomain_is_denied():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    client = APIClient(); client.force_authenticate(user)
    assert auth_request(client, "zzzzzzz.localhost").status_code == 403


@pytest.mark.django_db
def test_platform_hosts_never_authorized_via_forwardauth():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    client = APIClient(); client.force_authenticate(user)
    for host in ("app.localhost", "api.localhost", "traefik.localhost"):
        assert auth_request(client, host).status_code == 401


@pytest.mark.django_db
def test_forwarded_host_with_port_and_mixed_case_resolves():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    # access_hash is case-sensitive base64; browsers lowercase hostnames.
    instance = DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.RUNNING)
    client = APIClient(); client.force_authenticate(user)
    subdomain = instance.subdomain  # lowercase label
    assert auth_request(client, f"{subdomain}:80").status_code == 200


@pytest.mark.django_db
def test_fallback_serves_not_running_page_for_stopped_instance(settings):
    # Traefik drops routes for exited containers, so a stopped instance's
    # subdomain lands on the desktop-fallback catch-all (a plain Django view).
    from django.test import Client

    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    instance = DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.STOPPED)
    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, instance.subdomain]
    client = Client()
    response = client.get("/", HTTP_HOST=instance.subdomain)
    assert response.status_code == 409
    assert b"Desktop not running" in response.content


@pytest.mark.django_db
def test_fallback_serves_not_found_for_unknown_subdomain(settings):
    from django.test import Client

    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, "zzzzzzz.localhost"]
    client = Client()
    response = client.get("/", HTTP_HOST="zzzzzzz.localhost")
    assert response.status_code == 404
    assert b"Desktop not found" in response.content


@pytest.mark.django_db
def test_launch_token_authorizes_unauthenticated_desktop_request():
    """The dev bridge: browsers reject Domain cookies for single-label
    localhost, so the launch URL carries a short-lived signed token that the
    ForwardAuth validates — and sets the desktop cookie from."""
    from services.desktop_auth_tokens import DESKTOP_AUTH_COOKIE

    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    instance = DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.RUNNING)

    client = APIClient()  # no session — the token carries the authorization
    response = client.get("/api/v1/auth/desktop-auth/", {"auth": _launch_token(user, instance)}, HTTP_X_FORWARDED_HOST=instance.subdomain)
    assert response.status_code == 200
    assert DESKTOP_AUTH_COOKIE in response.cookies


def _launch_token(user, instance):
    from services.desktop_auth_tokens import issue_token
    return issue_token(user_id=user.id, instance_hash=instance.access_hash)


@pytest.mark.django_db
def test_expired_launch_token_gets_friendly_page():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    instance = DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.RUNNING)

    client = APIClient()
    response = client.get("/api/v1/auth/desktop-auth/", {"auth": _launch_token(user, instance) + "tampered"}, HTTP_X_FORWARDED_HOST=instance.subdomain)
    assert response.status_code == 401
    assert b"Link expired" in response.content


@pytest.mark.django_db
def test_launch_token_bound_to_another_desktop_is_denied():
    owner = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    mine = DesktopInstance.objects.create(user=owner, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.RUNNING)
    other = DesktopInstance.objects.create(user=owner, template=template, name="Other", cpu_limit="1", memory_limit="1G", status=InstanceStatus.RUNNING)

    client = APIClient()
    # A token issued for "Other" used against "Mine"'s subdomain → denied.
    response = client.get("/api/v1/auth/desktop-auth/", {"auth": _launch_token(owner, other)}, HTTP_X_FORWARDED_HOST=mine.subdomain)
    assert response.status_code == 403
    assert b"Access denied" in response.content


@pytest.mark.django_db
def test_desktop_cookie_carries_subsequent_requests():
    from services.desktop_auth_tokens import DESKTOP_AUTH_COOKIE, issue_token

    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    template = make_template()
    instance = DesktopInstance.objects.create(user=user, template=template, name="Mine", cpu_limit="1", memory_limit="1G", status=InstanceStatus.RUNNING)

    client = APIClient()
    client.cookies[DESKTOP_AUTH_COOKIE] = issue_token(user_id=user.id, instance_hash=instance.access_hash)
    response = client.get("/api/v1/auth/desktop-auth/", HTTP_X_FORWARDED_HOST=instance.subdomain)
    assert response.status_code == 200

    # A cookie for a different desktop is denied on this host.
    other = DesktopInstance.objects.create(user=user, template=template, name="Other", cpu_limit="1", memory_limit="1G", status=InstanceStatus.RUNNING)
    client.cookies[DESKTOP_AUTH_COOKIE] = issue_token(user_id=user.id, instance_hash=other.access_hash)
    response = client.get("/api/v1/auth/desktop-auth/", HTTP_X_FORWARDED_HOST=instance.subdomain)
    assert response.status_code == 403
