from apps.instances.models import DesktopInstance, InstanceStatus
from apps.events.models import EventType
from services.event_log_service import record_event


class InstanceService:
    @staticmethod
    def request(*, user, template, **data):
        instance = DesktopInstance.objects.create(user=user, template=template, **data)
        instance.status = InstanceStatus.QUEUED
        instance.save(update_fields=["status", "updated_at"])
        record_event(actor=user, event_type=EventType.INSTANCE_REQUESTED, message="Instance provisioning requested.", metadata={"instance_id": str(instance.id), "template_id": str(template.id)})
        from tasks.provisioning import provision_instance
        provision_instance.delay(str(instance.id))
        return instance
