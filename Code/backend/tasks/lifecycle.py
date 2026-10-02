"""Instance lifecycle tasks — deletion and auto-stop (VS-038, VS-039)."""
from django.utils import timezone

from config.celery import app
from apps.instances.models import DesktopInstance, InstanceStatus
from apps.events.models import EventType
from services.event_log_service import record_event
from services.instance_service import InstanceService


@app.task(name="dcp.delete_instance")
def delete_instance(instance_id):
    """Remove the container for a DELETING instance and mark it DELETED.
    The persistent volume is retained by default (Sprint 6, VS-043)."""
    instance = DesktopInstance.objects.get(pk=instance_id)
    try:
        from docker_manager.manager import docker_manager
        docker_manager.delete_container(instance=instance)
    except Exception as exc:  # noqa: BLE001 — recorded, instance left visible
        instance.status = InstanceStatus.FAILED
        instance.error_message = str(exc)
        instance.save(update_fields=["status", "error_message", "updated_at"])
        record_event(actor=instance.user, event_type=EventType.INSTANCE_DELETE_FAILED, message="Instance deletion failed.", metadata={"instance_id": str(instance.id)})
        raise
    instance.status = InstanceStatus.DELETED
    instance.save(update_fields=["status", "updated_at"])
    record_event(actor=instance.user, event_type=EventType.INSTANCE_DELETED, message="Instance deleted.", metadata={"instance_id": str(instance.id)})
    return str(instance.id)


@app.task(name="dcp.auto_stop_instances")
def auto_stop_instances():
    """Stop running instances idle for longer than their auto-stop timeout
    (VS-039). Idle means time since the last instance state change — noVNC
    activity tracking arrives in M6 (05_Container_Architecture.md)."""
    now = timezone.now()
    stopped = []
    for instance in DesktopInstance.objects.filter(status=InstanceStatus.RUNNING):
        idle_minutes = (now - instance.updated_at).total_seconds() / 60
        if idle_minutes < instance.auto_stop_minutes:
            continue
        try:
            InstanceService.stop(instance_id=instance.id, actor=None)
            stopped.append(str(instance.id))
        except Exception:  # noqa: BLE001 — skip instances that cannot stop
            continue
    if stopped:
        record_event(event_type=EventType.INSTANCE_STOPPED, message=f"Auto-stopped {len(stopped)} idle instance(s).", metadata={"instance_ids": stopped})
    return stopped
