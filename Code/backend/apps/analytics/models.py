"""
Aggregated per-instance usage metrics (03_Database_Design.md #analytics,
VS-054/VS-055).
"""
from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Analytics(TimeStampedModel):
    instance = models.OneToOneField(
        "instances.DesktopInstance",
        on_delete=models.CASCADE,
        related_name="analytics",
    )
    cpu_average = models.FloatField(default=0.0)
    ram_average = models.FloatField(default=0.0)  # MB
    uptime_seconds = models.BigIntegerField(default=0)
    last_calculated = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"Analytics for instance {self.instance_id}"
