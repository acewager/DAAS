"""
Software request workflow (03_Database_Design.md #software_requests, M7).

Users request additional software for their desktop instances; admins
approve or reject, and installation runs through Celery.
"""
from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class SoftwareRequestStatus(models.TextChoices):
	PENDING = "PENDING", "Pending"
	APPROVED = "APPROVED", "Approved"
	REJECTED = "REJECTED", "Rejected"
	INSTALLING = "INSTALLING", "Installing"
	INSTALLED = "INSTALLED", "Installed"
	FAILED = "FAILED", "Failed"


class SoftwareRequest(TimeStampedModel):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="software_requests",
	)
	instance = models.ForeignKey(
		"instances.DesktopInstance",
		on_delete=models.CASCADE,
		related_name="software_requests",
	)
	software_name = models.CharField(max_length=120)
	justification = models.TextField(blank=True)
	status = models.CharField(
		max_length=20,
		choices=SoftwareRequestStatus.choices,
		default=SoftwareRequestStatus.PENDING,
	)
	reviewed_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="reviewed_software_requests",
	)
	reviewed_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ["-created_at"]
		indexes = [
			models.Index(fields=["instance", "created_at"]),
			models.Index(fields=["status", "created_at"]),
		]

	def __str__(self) -> str:
		return f"{self.software_name} ({self.status}) for instance {self.instance_id}"
