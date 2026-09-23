"""Authentication service layer for register/login/logout flows."""
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

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

    @staticmethod
    def request_password_reset(email: str) -> None:
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if not user:
            return
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password/confirm?uid={uid}&token={token}"
        send_mail("Reset your Desktop Cloud Platform password", f"Use this link to reset your password: {reset_url}", settings.DEFAULT_FROM_EMAIL, [user.email])
        record_event(actor=user, event_type=EventType.PASSWORD_RESET_REQUESTED, message="Password reset requested.")

    @staticmethod
    def reset_password(*, uid: str, token: str, password: str) -> bool:
        try:
            user = User.objects.get(pk=force_str(urlsafe_base64_decode(uid)))
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return False
        if not default_token_generator.check_token(user, token):
            return False
        user.set_password(password)
        user.save(update_fields=["password"])
        record_event(actor=user, event_type=EventType.PASSWORD_RESET_COMPLETED, message="Password reset completed.")
        return True
