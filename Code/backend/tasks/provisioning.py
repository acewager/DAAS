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
        instance.status = InstanceStatus.RUNNING
        instance.save(update_fields=["container_id", "status", "updated_at"])
        record_event(actor=instance.user, event_type=EventType.INSTANCE_PROVISIONED, message="Instance provisioned.", metadata={"instance_id": str(instance.id)})
    except DockerManagerError as exc:
        instance.status = InstanceStatus.FAILED
        instance.error_message = str(exc)
        instance.save(update_fields=["status", "error_message", "updated_at"])
        record_event(actor=instance.user, event_type=EventType.INSTANCE_PROVISION_FAILED, message="Instance provisioning failed.", metadata={"instance_id": str(instance.id)})
        raise
