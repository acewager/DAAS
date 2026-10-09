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
	INSTANCE_REQUESTED = "INSTANCE_REQUESTED", "Instance Requested"
	INSTANCE_PROVISIONED = "INSTANCE_PROVISIONED", "Instance Provisioned"
	INSTANCE_PROVISION_FAILED = "INSTANCE_PROVISION_FAILED", "Instance Provision Failed"
	INSTANCE_LAUNCHED = "INSTANCE_LAUNCHED", "Instance Launched"
	INSTANCE_STARTED = "INSTANCE_STARTED", "Instance Started"
	INSTANCE_START_FAILED = "INSTANCE_START_FAILED", "Instance Start Failed"
	INSTANCE_STOPPED = "INSTANCE_STOPPED", "Instance Stopped"
	INSTANCE_STOP_FAILED = "INSTANCE_STOP_FAILED", "Instance Stop Failed"
	INSTANCE_RESTARTED = "INSTANCE_RESTARTED", "Instance Restarted"
	INSTANCE_RESTART_FAILED = "INSTANCE_RESTART_FAILED", "Instance Restart Failed"
	INSTANCE_DELETE_REQUESTED = "INSTANCE_DELETE_REQUESTED", "Instance Delete Requested"
	INSTANCE_DELETE_FAILED = "INSTANCE_DELETE_FAILED", "Instance Delete Failed"
	INSTANCE_DELETED = "INSTANCE_DELETED", "Instance Deleted"
	SOFTWARE_REQUESTED = "SOFTWARE_REQUESTED", "Software Requested"
	SOFTWARE_REQUEST_APPROVED = "SOFTWARE_REQUEST_APPROVED", "Software Request Approved"
	SOFTWARE_REQUEST_REJECTED = "SOFTWARE_REQUEST_REJECTED", "Software Request Rejected"
	SOFTWARE_INSTALLED = "SOFTWARE_INSTALLED", "Software Installed"
	SOFTWARE_INSTALL_FAILED = "SOFTWARE_INSTALL_FAILED", "Software Install Failed"


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
		indexes = [
			models.Index(fields=["created_at"]),
			models.Index(fields=["event_type", "created_at"]),
			models.Index(fields=["actor", "created_at"]),
		]

	def __str__(self) -> str:
		return f"{self.event_type}: {self.message}"
