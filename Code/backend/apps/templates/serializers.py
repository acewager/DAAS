from rest_framework import serializers

from .models import DesktopTemplate


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesktopTemplate
        fields = ("id", "name", "slug", "description", "json_configuration", "enabled", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_json_configuration(self, value):
        instance = DesktopTemplate(json_configuration=value)
        instance.clean()
        return value
