"""Software request workflow service (VS-045, VS-048, M7)."""
from django.utils import timezone

from api.exceptions import Conflict
from apps.events.models import EventType
from apps.instances.models import DesktopInstance, InstanceStatus
from apps.software_requests.models import SoftwareRequest, SoftwareRequestStatus
from services.event_log_service import record_event

# Debian package naming: alphanumeric (plus + . -), no shell metacharacters.
# The install command is executed without a shell, but validation stays strict.
PACKAGE_NAME_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9+._-]*$"


class SoftwareRequestService:
    @staticmethod
    def submit(*, user, instance_id, software_name, justification=""):
        """Create a PENDING request for the user's own instance (VS-045)."""
        instance = (
            DesktopInstance.objects.filter(pk=instance_id, user=user)
            .exclude(status=InstanceStatus.DELETED)
            .first()
        )
        if instance is None:
            raise Conflict("Instance not available for software requests.")
        request = SoftwareRequest.objects.create(
            user=user,
            instance=instance,
            software_name=software_name,
            justification=justification,
        )
        record_event(actor=user, event_type=EventType.SOFTWARE_REQUESTED, message=f"Software requested: {software_name}.", metadata={"request_id": str(request.id), "instance_id": str(instance.id)})
        return request

    @staticmethod
    def approve(*, reviewer, request_id):
        """Approve a PENDING request and queue installation (VS-047)."""
        request = SoftwareRequestService._get(request_id)
        if request.status != SoftwareRequestStatus.PENDING:
            raise Conflict("Only pending requests can be approved.")
        request.status = SoftwareRequestStatus.APPROVED
        request.reviewed_by = reviewer
        request.reviewed_at = timezone.now()
        request.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])
        record_event(actor=reviewer, event_type=EventType.SOFTWARE_REQUEST_APPROVED, message=f"Software request approved: {request.software_name}.", metadata={"request_id": str(request.id)})
        from tasks.software_installation import install_software_task
        install_software_task.delay(str(request.id))
        return request

    @staticmethod
    def reject(*, reviewer, request_id):
        """Reject a PENDING request (VS-046)."""
        request = SoftwareRequestService._get(request_id)
        if request.status != SoftwareRequestStatus.PENDING:
            raise Conflict("Only pending requests can be rejected.")
        request.status = SoftwareRequestStatus.REJECTED
        request.reviewed_by = reviewer
        request.reviewed_at = timezone.now()
        request.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])
        record_event(actor=reviewer, event_type=EventType.SOFTWARE_REQUEST_REJECTED, message=f"Software request rejected: {request.software_name}.", metadata={"request_id": str(request.id)})
        return request

    @staticmethod
    def _get(request_id):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(SoftwareRequest, pk=request_id)
