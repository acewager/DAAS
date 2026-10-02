from rest_framework import serializers

from .models import EventLog


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventLog
        fields = ("id", "event_type", "message", "created_at")
