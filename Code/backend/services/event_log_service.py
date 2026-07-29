"""Event log service used by security-sensitive workflows."""
from apps.events.models import EventLog


class EventLogService:
    @staticmethod
    def record(*, actor=None, event_type, message: str, metadata=None) -> EventLog:
        return EventLog.objects.create(
            actor=actor,
            event_type=event_type,
            message=message,
            metadata=metadata or {},
        )


def record_event(*, actor=None, event_type, message: str, metadata=None) -> EventLog:
    return EventLogService.record(
        actor=actor,
        event_type=event_type,
        message=message,
        metadata=metadata,
    )
