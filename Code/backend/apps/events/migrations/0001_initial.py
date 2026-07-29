# Generated manually for the Sprint 1 authentication slice.
import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EventLog",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="event_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("USER_REGISTERED", "User Registered"),
                            ("USER_LOGGED_IN", "User Logged In"),
                            ("USER_LOGGED_OUT", "User Logged Out"),
                            ("USER_LOGIN_FAILED", "User Login Failed"),
                        ],
                        max_length=64,
                    ),
                ),
                ("message", models.CharField(max_length=255)),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
