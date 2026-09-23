"""Authentication endpoint throttles."""
from django.core.exceptions import ImproperlyConfigured
from rest_framework.settings import api_settings
from rest_framework.throttling import AnonRateThrottle


class ScopedAnonRateThrottle(AnonRateThrottle):
    """Resolve a scoped rate from the current DRF settings.

    DRF normally snapshots rates when the class is imported. Looking the rate
    up at request time keeps Django's ``override_settings`` useful in tests
    while using the same configured rate in normal application requests.
    """

    def get_rate(self):
        try:
            return api_settings.DEFAULT_THROTTLE_RATES[self.scope]
        except KeyError as error:
            raise ImproperlyConfigured(
                f"No default throttle rate set for {self.scope!r} scope"
            ) from error


class RegisterRateThrottle(ScopedAnonRateThrottle):
    scope = "register"


class LoginRateThrottle(ScopedAnonRateThrottle):
    scope = "login"


class PasswordResetRateThrottle(ScopedAnonRateThrottle):
    scope = "password_reset"
