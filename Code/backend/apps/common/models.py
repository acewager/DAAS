"""
Shared abstract base models.

Per 03_Database_Design.md Section 6 (Global Standards), every table
includes id, created_at, and updated_at. Domain models (introduced from
Sprint 1 onward) should inherit from TimeStampedModel rather than
duplicating these fields.
"""
import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base providing a UUID primary key and audit timestamps."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
