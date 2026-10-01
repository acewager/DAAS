from decimal import Decimal

from rest_framework import serializers

from apps.templates.models import DesktopTemplate

from .models import DesktopInstance


class InstanceSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source="template.name", read_only=True)
    subdomain = serializers.CharField(read_only=True)

    class Meta:
        model = DesktopInstance
        fields = ("id", "name", "template", "template_name", "status", "subdomain", "cpu_limit", "memory_limit", "persistent", "auto_stop_minutes", "error_message", "created_at")
        read_only_fields = ("id", "status", "subdomain", "error_message", "created_at")


class InstanceOrderSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    template_id = serializers.UUIDField()
    cpu_limit = serializers.DecimalField(max_digits=4, decimal_places=2, min_value=Decimal("0.25"), max_value=Decimal("16"))
    memory_limit = serializers.RegexField(r"^\d+[MG]$", max_length=20)
    persistent = serializers.BooleanField(default=False)
    auto_stop_minutes = serializers.IntegerField(min_value=5, max_value=1440, default=60)

    def validate_template_id(self, value):
        try:
            return DesktopTemplate.objects.get(pk=value, enabled=True)
        except DesktopTemplate.DoesNotExist:
            raise serializers.ValidationError("Selected template is unavailable.")

    def create(self, validated_data):
        raise NotImplementedError
