"""Software installation task (VS-047, M7)."""
from config.celery import app
from apps.software_requests.models import SoftwareRequest, SoftwareRequestStatus
from apps.events.models import EventType
from services.event_log_service import record_event


@app.task(name="dcp.install_software")
def install_software_task(request_id):
    """Install approved software into the request's instance container."""
    request = SoftwareRequest.objects.select_related("instance", "user").get(pk=request_id)
    request.status = SoftwareRequestStatus.INSTALLING
    request.save(update_fields=["status", "updated_at"])
    try:
        from docker_manager.manager import DockerManagerError, docker_manager
        docker_manager.install_software(instance=request.instance, name=request.software_name)
    except DockerManagerError as exc:
        request.status = SoftwareRequestStatus.FAILED
        request.save(update_fields=["status", "updated_at"])
        record_event(actor=request.user, event_type=EventType.SOFTWARE_INSTALL_FAILED, message=f"Software installation failed: {request.software_name}.", metadata={"request_id": str(request.id), "error": str(exc)[-500:]})
        raise
    request.status = SoftwareRequestStatus.INSTALLED
    request.save(update_fields=["status", "updated_at"])
    record_event(actor=request.user, event_type=EventType.SOFTWARE_INSTALLED, message=f"Software installed: {request.software_name}.", metadata={"request_id": str(request.id)})
    return str(request.id)
