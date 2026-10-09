from rest_framework import serializers

from .models import EventLog


class EventSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source="actor.username", read_only=True, default="")

    class Meta:
        model = EventLog
        fields = ("id", "event_type", "message", "created_at", "actor_name")
