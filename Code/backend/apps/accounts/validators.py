"""Password validation required by the platform security policy."""
import re

from django.core.exceptions import ValidationError


class StrongPasswordValidator:
    """Require mixed case, a number, and a special character."""

    def validate(self, password, user=None):
        requirements = (
            (r"[a-z]", "a lowercase letter"),
            (r"[A-Z]", "an uppercase letter"),
            (r"\d", "a number"),
            (r"[^\w\s]", "a special character"),
        )
        missing = [label for pattern, label in requirements if not re.search(pattern, password)]
        if missing:
            raise ValidationError(
                "Password must include " + ", ".join(missing) + ".",
                code="password_too_weak",
            )

    def get_help_text(self):
        return "Your password must include upper- and lowercase letters, a number, and a special character."
