"""Persistent volume lifecycle (VS-041, Sprint 6).

The Docker SDK is only touched through DockerManager; this service owns the
volume bookkeeping that pairs each persistent instance with its data volume
record (03_Database_Design.md #volumes).
"""
from docker_manager.manager import DockerManagerError, docker_manager
from apps.instances.models import Volume
from apps.events.models import EventType
from services.event_log_service import record_event


def volume_name(instance) -> str:
    """Named data volume for an instance — created implicitly when the
    container references it (DockerManager.create_container)."""
    return f"dcp-data-{instance.id}"


class VolumeService:
    @staticmethod
    def record_for_instance(instance) -> Volume | None:
        """Track a persistent instance's data volume. Called from provisioning
        after the container exists (Docker auto-creates the named volume)."""
        if not instance.persistent:
            return None
        volume, _ = Volume.objects.get_or_create(
            instance=instance,
            defaults={"host_path": volume_name(instance), "persistent": True, "retain_after_delete": True},
        )
        return volume

    @staticmethod
    def remove(instance, *, actor=None) -> None:
        """Remove an instance's data volume and its tracking record (VS-043 —
        Retain/Delete data option). Retained volumes keep their record."""
        try:
            volume = Volume.objects.get(instance=instance)
        except Volume.DoesNotExist:
            return
        try:
            docker_manager.remove_volume(name=volume.host_path)
        except DockerManagerError as exc:
            record_event(actor=actor, event_type=EventType.INSTANCE_DELETE_FAILED, message="Persistent data removal failed.", metadata={"instance_id": str(instance.id), "volume": volume.host_path})
            raise
        volume.delete()
