"""Desktop template definitions used during instance provisioning."""
from django.core.exceptions import ValidationError
from django.db import models

from apps.common.models import TimeStampedModel


class DesktopTemplate(TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    json_configuration = models.JSONField(default=dict)
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def clean(self):
        if not isinstance(self.json_configuration, dict):
            raise ValidationError({"json_configuration": "Configuration must be a JSON object."})
        image = self.json_configuration.get("image")
        if not isinstance(image, str) or not image.strip():
            raise ValidationError({"json_configuration": "Configuration requires a non-empty 'image' value."})

    def __str__(self):
        return self.name
