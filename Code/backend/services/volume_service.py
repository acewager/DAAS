"""Persistent volume lifecycle (VS-041, Sprint 6; re-attach VS-043, Sprint 10).

The Docker SDK is only touched through DockerManager; this service owns the
volume bookkeeping that pairs each persistent instance with its data volume
record (03_Database_Design.md #volumes). Retained volumes can be re-attached
to a newly created instance so user data survives instance deletion.
"""
from docker_manager.manager import DockerManagerError, docker_manager
from apps.events.models import EventType
from apps.instances.models import InstanceStatus, Volume
from services.event_log_service import record_event


def volume_name(instance) -> str:
    """Named data volume for an instance — created implicitly when the
    container references it (DockerManager.create_container)."""
    return f"dcp-data-{instance.id}"


class VolumeService:
    @staticmethod
    def record_for_instance(instance) -> Volume | None:
        """Track a persistent instance's data volume. Called from provisioning
        after the container exists (Docker auto-creates the named volume).
        Instances created with an attached retained volume already carry their
        re-pointed record and are left untouched."""
        if not instance.persistent:
            return None
        volume, _ = Volume.objects.get_or_create(
            instance=instance,
            defaults={"host_path": volume_name(instance), "persistent": True, "retain_after_delete": True},
        )
        return volume

    @staticmethod
    def volume_path_for(instance) -> str:
        """The Docker volume name to mount for an instance: an attached
        retained volume's name when the record predates provisioning, else the
        instance's own implicit volume."""
        volume = Volume.objects.filter(instance=instance).first()
        return volume.host_path if volume else volume_name(instance)

    @staticmethod
    def attach(volume_id, *, user, new_instance) -> Volume:
        """Re-point a retained volume record to a new instance (VS-043 —
        "Keep my data (can be re-attached later)"). The Docker volume keeps
        its name, so the data carries over to the new desktop."""
        from django.shortcuts import get_object_or_404

        from api.exceptions import Conflict

        volume = get_object_or_404(Volume, pk=volume_id, persistent=True, retain_after_delete=True)
        if volume.instance.user_id != user.id:
            raise Conflict("Volume not available for this account.")
        if volume.instance_id == new_instance.id:
            raise Conflict("Cannot attach a volume to its own instance.")
        volume.instance = new_instance
        volume.save(update_fields=["instance", "updated_at"])
        return volume

    @staticmethod
    def retained_volumes(user):
        """The user's retained volumes awaiting re-attachment (their owning
        instance is DELETED)."""
        return (
            Volume.objects.filter(
                instance__user=user,
                instance__status=InstanceStatus.DELETED,
                persistent=True,
            )
            .select_related("instance")
            .order_by("-updated_at")
        )

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
