from rest_framework import serializers

from services.software_request_service import PACKAGE_NAME_PATTERN
from .models import SoftwareRequest


class SoftwareRequestSerializer(serializers.ModelSerializer):
    instance_name = serializers.CharField(source="instance.name", read_only=True)
    reviewer_name = serializers.CharField(source="reviewed_by.username", read_only=True, default="")

    class Meta:
        model = SoftwareRequest
        fields = ("id", "instance", "instance_name", "software_name", "justification", "status", "reviewer_name", "reviewed_at", "created_at")
        read_only_fields = ("id", "status", "reviewer_name", "reviewed_at", "created_at")


class SoftwareRequestCreateSerializer(serializers.Serializer):
    instance_id = serializers.UUIDField()
    software_name = serializers.RegexField(PACKAGE_NAME_PATTERN, max_length=120)
    justification = serializers.CharField(required=False, allow_blank=True, max_length=2000, trim_whitespace=True)

    def validate(self, attrs):
        attrs["justification"] = (attrs.get("justification") or "").strip()
        return attrs
