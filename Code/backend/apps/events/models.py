"""Audit event log records."""
from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class EventType(models.TextChoices):
	USER_REGISTERED = "USER_REGISTERED", "User Registered"
	USER_LOGGED_IN = "USER_LOGGED_IN", "User Logged In"
	USER_LOGGED_OUT = "USER_LOGGED_OUT", "User Logged Out"
	USER_LOGIN_FAILED = "USER_LOGIN_FAILED", "User Login Failed"
	PASSWORD_RESET_REQUESTED = "PASSWORD_RESET_REQUESTED", "Password Reset Requested"
	PASSWORD_RESET_COMPLETED = "PASSWORD_RESET_COMPLETED", "Password Reset Completed"
	TEMPLATE_CREATED = "TEMPLATE_CREATED", "Template Created"
	TEMPLATE_UPDATED = "TEMPLATE_UPDATED", "Template Updated"
	TEMPLATE_ARCHIVED = "TEMPLATE_ARCHIVED", "Template Archived"


class EventLog(TimeStampedModel):
	actor = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="event_logs",
	)
	event_type = models.CharField(max_length=64, choices=EventType.choices)
	message = models.CharField(max_length=255)
	metadata = models.JSONField(default=dict, blank=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:
		return f"{self.event_type}: {self.message}"
