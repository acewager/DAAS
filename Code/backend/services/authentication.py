"""Authentication service layer for register/login/logout flows."""
from django.contrib.auth import authenticate

from apps.accounts.models import User
from apps.events.models import EventType

from .event_log_service import record_event


class AuthenticationService:
    @staticmethod
    def register_user(*, username: str, email: str, password: str, role: str = "USER") -> User:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
        )
        record_event(
            actor=user,
            event_type=EventType.USER_REGISTERED,
            message="User account created.",
            metadata={"username": user.username},
        )
        return user

    @staticmethod
    def authenticate_user(*, username: str, password: str) -> User | None:
        return authenticate(username=username, password=password)

    @staticmethod
    def record_login(user: User) -> None:
        record_event(
            actor=user,
            event_type=EventType.USER_LOGGED_IN,
            message="User logged in.",
            metadata={"username": user.username},
        )

    @staticmethod
    def record_failed_login(username: str) -> None:
        record_event(
            actor=None,
            event_type=EventType.USER_LOGIN_FAILED,
            message="Invalid login attempt.",
            metadata={"username": username},
        )

    @staticmethod
    def record_logout(user: User | None) -> None:
        record_event(
            actor=user,
            event_type=EventType.USER_LOGGED_OUT,
            message="User logged out.",
            metadata={"username": getattr(user, "username", None)},
        )
