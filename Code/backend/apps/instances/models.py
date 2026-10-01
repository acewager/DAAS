import secrets

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


def generate_access_hash():
    return secrets.token_urlsafe(16)


class InstanceStatus(models.TextChoices):
    REQUESTED = "REQUESTED", "Requested"
    QUEUED = "QUEUED", "Queued"
    PROVISIONING = "PROVISIONING", "Provisioning"
    RUNNING = "RUNNING", "Running"
    FAILED = "FAILED", "Failed"


class DesktopInstance(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="instances")
    template = models.ForeignKey("templates.DesktopTemplate", on_delete=models.PROTECT, related_name="instances")
    name = models.CharField(max_length=120)
    status = models.CharField(max_length=20, choices=InstanceStatus.choices, default=InstanceStatus.REQUESTED)
    container_name = models.CharField(max_length=100, unique=True, blank=True)
    container_id = models.CharField(max_length=128, blank=True)
    access_hash = models.CharField(max_length=32, unique=True, default=generate_access_hash)
    cpu_limit = models.DecimalField(max_digits=4, decimal_places=2)
    memory_limit = models.CharField(max_length=20)
    persistent = models.BooleanField(default=False)
    auto_stop_minutes = models.PositiveIntegerField(default=60)
    error_message = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.container_name:
            self.container_name = f"dcp-{str(self.id)[:8]}"
        super().save(*args, **kwargs)
