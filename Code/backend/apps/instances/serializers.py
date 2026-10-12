from decimal import Decimal

from rest_framework import serializers

from apps.templates.models import DesktopTemplate

from .models import DesktopInstance


class InstanceSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source="template.name", read_only=True)
    subdomain = serializers.CharField(read_only=True)
    # Usage analytics (VS-056): null-safe — instances without an Analytics
    # record report zeros (a source traversal on a missing OneToOne returns
    # None, so read-only defaults alone do not apply).
    cpu_average = serializers.SerializerMethodField()
    ram_average = serializers.SerializerMethodField()
    uptime_seconds = serializers.SerializerMethodField()

    class Meta:
        model = DesktopInstance
        fields = ("id", "name", "template", "template_name", "status", "subdomain", "cpu_limit", "memory_limit", "persistent", "auto_stop_minutes", "error_message", "cpu_average", "ram_average", "uptime_seconds", "created_at")
        read_only_fields = ("id", "status", "subdomain", "error_message", "created_at")

    def _analytics(self, instance):
        from apps.analytics.models import Analytics
        try:
            return Analytics.objects.get(instance=instance)
        except Analytics.DoesNotExist:
            return None

    def get_cpu_average(self, instance) -> float:
        analytics = self._analytics(instance)
        return analytics.cpu_average if analytics else 0.0

    def get_ram_average(self, instance) -> float:
        analytics = self._analytics(instance)
        return analytics.ram_average if analytics else 0.0

    def get_uptime_seconds(self, instance) -> int:
        analytics = self._analytics(instance)
        return analytics.uptime_seconds if analytics else 0


class InstanceOrderSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    template_id = serializers.UUIDField()
    # Tolerates "" (the form's "Fresh storage" default) — normalized to None.
    attach_volume_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    cpu_limit = serializers.DecimalField(max_digits=4, decimal_places=2, min_value=Decimal("0.25"), max_value=Decimal("16"))
    memory_limit = serializers.RegexField(r"^\d+[MG]$", max_length=20)
    persistent = serializers.BooleanField(default=False)
    auto_stop_minutes = serializers.IntegerField(min_value=5, max_value=1440, default=60)

    def validate_template_id(self, value):
        try:
            return DesktopTemplate.objects.get(pk=value, enabled=True)
        except DesktopTemplate.DoesNotExist:
            raise serializers.ValidationError("Selected template is unavailable.")

    def validate_attach_volume_id(self, value):
        # "" (the form's "Fresh storage" default) normalizes to None.
        if value in (None, ""):
            return None
        import uuid as uuid_module
        try:
            return str(uuid_module.UUID(str(value)))
        except (ValueError, AttributeError, TypeError):
            raise serializers.ValidationError("Attach volume must be a valid UUID.")

    def create(self, validated_data):
        raise NotImplementedError


class AdminInstanceSerializer(InstanceSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta(InstanceSerializer.Meta):
        fields = InstanceSerializer.Meta.fields + ("username", "container_name", "container_id")
        read_only_fields = fields
