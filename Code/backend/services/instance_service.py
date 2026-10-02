from django.conf import settings
from django.shortcuts import get_object_or_404

from api.exceptions import Conflict
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

    @staticmethod
    def launch(*, user, instance_id) -> str:
        """Return the desktop launch URL for a running, user-owned instance
        (VS-034). Session validation before routing arrives in M6 (Browser
        Desktop Access); HTTPS hardening is M10."""
        instance = get_object_or_404(DesktopInstance.objects.select_related("template"), pk=instance_id, user=user)
        if instance.status != InstanceStatus.RUNNING:
            raise Conflict("Instance is not running.")
        record_event(actor=user, event_type=EventType.INSTANCE_LAUNCHED, message="Desktop launch URL generated.", metadata={"instance_id": str(instance.id)})
        scheme = "http" if settings.DEBUG else "https"
        return f"{scheme}://{instance.subdomain}"
