"""Per-user dashboard aggregation (VS-030, Sprint 4)."""
from django.db.models import Q, Sum

from apps.events.models import EventLog
from apps.instances.models import DesktopInstance, InstanceStatus


def _memory_gb(limit: str) -> float:
    """Parse a Docker memory limit string ("2G", "512M") into GB."""
    if limit.upper().endswith("G"):
        return float(limit[:-1])
    if limit.upper().endswith("M"):
        return float(limit[:-1]) / 1024
    return 0.0


class DashboardService:
    """Aggregates instance summary, resource usage, and recent activity for
    the authenticated user's dashboard (09_User_Experience.md Section 4)."""

    @staticmethod
    def dashboard(*, user, activity_limit: int = 8) -> dict:
        instances = DesktopInstance.objects.filter(user=user)
        running = instances.filter(status=InstanceStatus.RUNNING)

        usage = running.aggregate(cpu=Sum("cpu_limit")) or {}
        cpu_cores = float(usage.get("cpu") or 0)
        memory_gb = sum(_memory_gb(i.memory_limit) for i in running)

        activity = [
            {
                "event_type": event.event_type,
                "message": event.message,
                "created_at": event.created_at.isoformat(),
            }
            for event in EventLog.objects.filter(actor=user)[:activity_limit]
        ]

        return {
            "instances": {
                "total": instances.count(),
                "running": running.count(),
                "stopped": instances.filter(status=InstanceStatus.STOPPED).count(),
                "failed": instances.filter(status=InstanceStatus.FAILED).count(),
                "provisioning": instances.filter(~Q(status=InstanceStatus.RUNNING) & ~Q(status=InstanceStatus.STOPPED) & ~Q(status=InstanceStatus.FAILED)).count(),
            },
            "usage": {
                "cpu_cores": cpu_cores,
                "memory_gb": memory_gb,
            },
            "recent_activity": activity,
        }
