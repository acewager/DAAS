from apps.accounts.permissions import IsAdminRole
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from services.dashboard_service import DashboardService


class DashboardStatisticsView(APIView):
    """GET /api/v1/analytics/dashboard (07_REST_API.md Section 12, VS-030)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = DashboardService.dashboard(user=request.user)
        return Response({"success": True, "message": "Dashboard statistics retrieved successfully.", "data": data})


class AdminAnalyticsView(APIView):
    """GET /api/v1/admin/analytics/ — platform analytics (VS-053, Admin Only)."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        from django.contrib.auth import get_user_model

        from apps.instances.models import DesktopInstance, InstanceStatus
        from apps.software_requests.models import SoftwareRequest, SoftwareRequestStatus
        from apps.events.models import EventLog

        User = get_user_model()
        instances = DesktopInstance.objects.all()
        software = SoftwareRequest.objects.all()
        recent_events = list(EventLog.objects.select_related("actor").order_by("-created_at")[:10])
        data = {
            "users": {
                "total": User.objects.count(),
                "active": User.objects.filter(is_active=True).count(),
            },
            "instances": {
                "total": instances.count(),
                "running": instances.filter(status=InstanceStatus.RUNNING).count(),
                "stopped": instances.filter(status=InstanceStatus.STOPPED).count(),
                "failed": instances.filter(status=InstanceStatus.FAILED).count(),
                "deleted": instances.filter(status=InstanceStatus.DELETED).count(),
            },
            "software_requests": {
                "total": software.count(),
                "pending": software.filter(status=SoftwareRequestStatus.PENDING).count(),
                "approved": software.filter(status=SoftwareRequestStatus.APPROVED).count(),
                "rejected": software.filter(status=SoftwareRequestStatus.REJECTED).count(),
                "installed": software.filter(status=SoftwareRequestStatus.INSTALLED).count(),
                "failed": software.filter(status=SoftwareRequestStatus.FAILED).count(),
            },
            "recent_events": [
                {
                    "event_type": event.event_type,
                    "message": event.message,
                    "actor": event.actor.username if event.actor else None,
                    "created_at": event.created_at.isoformat(),
                }
                for event in recent_events
            ],
        }
        return Response({"success": True, "message": "Platform analytics retrieved successfully.", "data": data})


class AdminHealthView(APIView):
    """GET /api/v1/admin/health/ — system health incl. Redis and Docker."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        from django.db import connection
        from django.core.cache import cache

        from docker_manager.manager import docker_manager

        def check(fn):
            try:
                fn()
                return "healthy"
            except Exception:  # noqa: BLE001 — surfaced to the health page
                return "unhealthy"

        def database():
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")

        def redis():
            cache.set("dcp-health-probe", "1", 5)
            if cache.get("dcp-health-probe") != "1":
                raise RuntimeError("cache probe failed")

        def docker():
            if not docker_manager.ping():
                raise RuntimeError("docker daemon unreachable")

        checks = {
            "database": check(database),
            "redis": check(redis),
            "docker": check(docker),
        }
        status = "healthy" if all(value == "healthy" for value in checks.values()) else "unhealthy"
        return Response({"success": True, "message": "System health retrieved successfully.", "data": {"status": status, "checks": checks}})
