"""Usage analytics service (VS-054, VS-055, Sprint 9)."""
from django.utils import timezone

from apps.analytics.models import Analytics
from apps.instances.models import DesktopInstance, InstanceStatus


class AnalyticsService:
    @staticmethod
    def sample_instance(instance) -> Analytics | None:
        """Sample one RUNNING instance's container usage and fold it into a
        smoothing average (the mean of the stored average and the sample —
        simple, no extra fields beyond the documented schema)."""
        from docker_manager.manager import docker_manager

        usage = docker_manager.container_usage(instance=instance)
        if usage is None:
            return None
        analytics, _ = Analytics.objects.get_or_create(instance=instance)
        if analytics.last_calculated is None:
            # First sample sets the value; later samples smooth toward it.
            analytics.cpu_average = usage["cpu_percent"]
            analytics.ram_average = usage["ram_mb"]
        else:
            analytics.cpu_average = round((analytics.cpu_average + usage["cpu_percent"]) / 2, 2)
            analytics.ram_average = round((analytics.ram_average + usage["ram_mb"]) / 2, 2)
        # Uptime: seconds since the last state change (RUNNING since then);
        # non-running instances report 0.
        if instance.status == InstanceStatus.RUNNING:
            analytics.uptime_seconds = int((timezone.now() - instance.updated_at).total_seconds())
        analytics.last_calculated = timezone.now()
        analytics.save(update_fields=["cpu_average", "ram_average", "uptime_seconds", "last_calculated", "updated_at"])
        return analytics

    @staticmethod
    def for_instance(instance) -> Analytics | None:
        return Analytics.objects.filter(instance=instance).first()

    @staticmethod
    def aggregate_running_instances() -> int:
        """Sample every RUNNING instance (VS-055, called by the beat task)."""
        sampled = 0
        for instance in DesktopInstance.objects.filter(status=InstanceStatus.RUNNING):
            if AnalyticsService.sample_instance(instance) is not None:
                sampled += 1
        return sampled
