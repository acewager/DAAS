"""Authentication flow tests for Sprint 1."""
import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.accounts.permissions import IsAdminRole, IsSuperAdminRole


@pytest.mark.django_db
def test_register_login_me_and_logout_flow():
    client = APIClient()

    client.get(reverse("auth-csrf"))

    register_response = client.post(
        reverse("auth-register"),
        {
            "username": "alex",
            "email": "alex@example.com",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
        },
        format="json",
    )

    assert register_response.status_code == 201
    assert register_response.data["success"] is True
    assert register_response.data["data"]["user"]["username"] == "alex"

    me_response = client.get(reverse("auth-me"))
    assert me_response.status_code == 200
    assert me_response.data["data"]["user"]["email"] == "alex@example.com"

    logout_response = client.post(reverse("auth-logout"), {}, format="json")
    assert logout_response.status_code == 200


@pytest.mark.django_db
def test_login_rejects_invalid_password():
    client = APIClient()

    client.get(reverse("auth-csrf"))
    client.post(
        reverse("auth-register"),
        {
            "username": "sam",
            "email": "sam@example.com",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
        },
        format="json",
    )
    client.post(reverse("auth-logout"), {}, format="json")

    login_response = client.post(
        reverse("auth-login"),
        {"username": "sam", "password": "wrong-password"},
        format="json",
    )

    assert login_response.status_code == 401
    assert login_response.data["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.django_db
@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.SessionAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.IsAuthenticated",
        ],
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.AnonRateThrottle",
        ],
        "DEFAULT_THROTTLE_RATES": {
            "login": "2/min",
            "register": "2/min",
        },
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 20,
        "EXCEPTION_HANDLER": "api.exceptions.standard_exception_handler",
    }
)
def test_login_rate_limit_enforced():
    cache.clear()
    client = APIClient()
    client.get(reverse("auth-csrf"))
    client.post(
        reverse("auth-register"),
        {
            "username": "ratelimited",
            "email": "ratelimited@example.com",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
        },
        format="json",
    )
    client.post(reverse("auth-logout"), {}, format="json")

    for _ in range(2):
        response = client.post(
            reverse("auth-login"),
            {"username": "ratelimited", "password": "bad-password"},
            format="json",
        )
        assert response.status_code == 401

    throttled_response = client.post(
        reverse("auth-login"),
        {"username": "ratelimited", "password": "bad-password"},
        format="json",
    )
    assert throttled_response.status_code == 429
    assert throttled_response.data["success"] is False
    assert throttled_response.data["error"]["code"] == "THROTTLED"


@pytest.mark.django_db
@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.SessionAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.IsAuthenticated",
        ],
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.AnonRateThrottle",
        ],
        "DEFAULT_THROTTLE_RATES": {
            "login": "2/min",
            "register": "2/min",
        },
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 20,
        "EXCEPTION_HANDLER": "api.exceptions.standard_exception_handler",
    }
)
def test_register_rate_limit_enforced():
    cache.clear()
    client = APIClient()
    client.get(reverse("auth-csrf"))

    for index in range(2):
        response = client.post(
            reverse("auth-register"),
            {
                "username": f"user-{index}",
                "email": f"user-{index}@example.com",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
            },
            format="json",
        )
        assert response.status_code == 201
        client.post(reverse("auth-logout"), {}, format="json")

    throttled_response = client.post(
        reverse("auth-register"),
        {
            "username": "user-over-limit",
            "email": "user-over-limit@example.com",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
        },
        format="json",
    )
    assert throttled_response.status_code == 429
    assert throttled_response.data["success"] is False
    assert throttled_response.data["error"]["code"] == "THROTTLED"


@pytest.mark.django_db
def test_role_permissions_for_admin_and_super_admin():
    factory = APIRequestFactory()
    request = factory.get("/api/v1/auth/me/")

    request.user = AnonymousUser()
    assert IsAdminRole().has_permission(request, view=None) is False
    assert IsSuperAdminRole().has_permission(request, view=None) is False

    user = User.objects.create_user(
        username="basic-user",
        email="basic-user@example.com",
        password="SecurePass123!",
        role=UserRole.USER,
    )
    request.user = user
    assert IsAdminRole().has_permission(request, view=None) is False
    assert IsSuperAdminRole().has_permission(request, view=None) is False

    user.role = UserRole.ADMIN
    assert IsAdminRole().has_permission(request, view=None) is True
    assert IsSuperAdminRole().has_permission(request, view=None) is False

    user.role = UserRole.SUPER_ADMIN
    assert IsAdminRole().has_permission(request, view=None) is True
    assert IsSuperAdminRole().has_permission(request, view=None) is True
