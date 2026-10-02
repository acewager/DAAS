"""Instance provisioning task (VS-024)."""
import time
from urllib.request import urlopen

from config.celery import app
from docker_manager.manager import DockerManagerError, docker_manager
from apps.instances.models import DesktopInstance, InstanceStatus
from apps.events.models import EventType
from services.event_log_service import record_event


@app.task(name="dcp.provision_instance")
def provision_instance(instance_id):
    instance = DesktopInstance.objects.select_related("template").get(pk=instance_id)
    instance.status = InstanceStatus.PROVISIONING
    instance.save(update_fields=["status", "updated_at"])
    try:
        container = docker_manager.create_container(instance=instance, template=instance.template)
        instance.container_id = container.id
        instance.save(update_fields=["container_id", "updated_at"])
        from services.volume_service import VolumeService
        VolumeService.record_for_instance(instance)
        _wait_for_desktop_ui(instance, container)
        instance.status = InstanceStatus.RUNNING
        instance.save(update_fields=["status", "updated_at"])
        record_event(actor=instance.user, event_type=EventType.INSTANCE_PROVISIONED, message="Instance provisioned.", metadata={"instance_id": str(instance.id)})
    except DockerManagerError as exc:
        instance.status = InstanceStatus.FAILED
        instance.error_message = str(exc)
        instance.save(update_fields=["status", "error_message", "updated_at"])
        record_event(actor=instance.user, event_type=EventType.INSTANCE_PROVISION_FAILED, message="Instance provisioning failed.", metadata={"instance_id": str(instance.id)})
        raise


def _wait_for_desktop_ui(instance, container, attempts: int = 30) -> None:
    """Wait until the desktop web UI accepts connections (VS-034 UX): the
    Launch button only appears for RUNNING instances, so RUNNING should mean
    the desktop is actually reachable. Bounded wait — slow boots still end up
    RUNNING rather than FAILED."""
    web_port = instance.template.json_configuration.get("web_port", 3000)
    ip = container.attrs.get("NetworkSettings", {}).get("Networks", {}).get("dcp-network", {}).get("IPAddress")
    if not ip:
        return
    for _ in range(attempts):
        try:
            with urlopen(f"http://{ip}:{web_port}/", timeout=2) as response:
                if response.status == 200:
                    return
        except Exception:  # noqa: BLE001 — UI not ready yet; keep waiting
            pass
        time.sleep(2)
