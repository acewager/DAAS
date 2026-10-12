from django.conf import settings
from django.shortcuts import get_object_or_404

from api.exceptions import Conflict
from apps.instances.models import DesktopInstance, InstanceStatus
from apps.events.models import EventType
from docker_manager.manager import docker_manager
from services.event_log_service import record_event


class InstanceService:
    @staticmethod
    def request(*, user, template, **data):
        # VS-043: an optional retained volume id re-points the volume record
        # to the new instance so its data carries over.
        attach_volume_id = data.pop("attach_volume_id", None)
        if attach_volume_id:
            # Attaching retained storage implies persistence — otherwise the
            # container would be created without the volume mounted.
            data["persistent"] = True
        instance = DesktopInstance.objects.create(user=user, template=template, **data)
        instance.status = InstanceStatus.QUEUED
        instance.save(update_fields=["status", "updated_at"])
        attached = None
        if attach_volume_id:
            from services.volume_service import VolumeService
            attached = VolumeService.attach(attach_volume_id, user=user, new_instance=instance)
        record_event(actor=user, event_type=EventType.INSTANCE_REQUESTED, message="Instance provisioning requested.", metadata={"instance_id": str(instance.id), "template_id": str(template.id), "attached_volume": attached.host_path if attached else None})
        from tasks.provisioning import provision_instance
        provision_instance.delay(str(instance.id))
        return instance

    @staticmethod
    def _get_instance(*, user=None, instance_id):
        if user is None:
            return get_object_or_404(DesktopInstance, pk=instance_id)
        return get_object_or_404(DesktopInstance, pk=instance_id, user=user)

    @staticmethod
    def _actor_scope(actor):
        """Admins manage any instance; regular users only their own (VS-051)."""
        from apps.accounts.models import UserRole
        if actor is not None and (actor.role == UserRole.ADMIN or actor.role == UserRole.SUPER_ADMIN or getattr(actor, "is_superuser", False)):
            return None
        return actor

    @staticmethod
    def launch(*, user, instance_id) -> str:
        """Return the desktop launch URL for a running, user-owned instance
        (VS-034). The URL carries a short-lived signed token (capability
        link): browsers reject Domain cookies for the single-label localhost
        dev domain, so the token bridges the app session to the desktop
        subdomain — the ForwardAuth validates it and sets a host-only cookie
        for the desktop UI's subsequent requests. HTTPS hardening is M10."""
        instance = InstanceService._get_instance(user=user, instance_id=instance_id)
        if instance.status != InstanceStatus.RUNNING:
            raise Conflict("Instance is not running.")
        record_event(actor=user, event_type=EventType.INSTANCE_LAUNCHED, message="Desktop launch URL generated.", metadata={"instance_id": str(instance.id)})
        from services.desktop_auth_tokens import issue_token
        token = issue_token(user_id=user.id, instance_hash=instance.access_hash)
        scheme = "http" if settings.DEBUG else "https"
        return f"{scheme}://{instance.subdomain}/?auth={token}"

    # -- Container operations (VS-035 through VS-038, Sprint 5) -----------
    # Start/stop/restart are quick Docker calls and run synchronously; the
    # Docker rules (01D_Development_Roadmap.md Section 8) reserve Celery for
    # long-running operations such as provisioning and deletion.

    @staticmethod
    def start(*, instance_id, actor=None):
        instance = InstanceService._get_instance(user=InstanceService._actor_scope(actor), instance_id=instance_id)
        if instance.status != InstanceStatus.STOPPED:
            raise Conflict("Only stopped instances can be started.")
        try:
            docker_manager.start_container(instance=instance)
        except Exception as exc:
            instance.status = InstanceStatus.FAILED
            instance.error_message = str(exc)
            instance.save(update_fields=["status", "error_message", "updated_at"])
            record_event(actor=actor, event_type=EventType.INSTANCE_START_FAILED, message="Instance start failed.", metadata={"instance_id": str(instance.id)})
            raise Conflict("Instance could not be started.") from exc
        instance.status = InstanceStatus.RUNNING
        instance.error_message = ""
        instance.save(update_fields=["status", "error_message", "updated_at"])
        record_event(actor=actor, event_type=EventType.INSTANCE_STARTED, message="Instance started.", metadata={"instance_id": str(instance.id)})
        return instance

    @staticmethod
    def stop(*, instance_id, actor=None):
        instance = InstanceService._get_instance(user=InstanceService._actor_scope(actor), instance_id=instance_id)
        if instance.status != InstanceStatus.RUNNING:
            raise Conflict("Only running instances can be stopped.")
        try:
            docker_manager.stop_container(instance=instance)
        except Exception as exc:
            record_event(actor=actor, event_type=EventType.INSTANCE_STOP_FAILED, message="Instance stop failed.", metadata={"instance_id": str(instance.id)})
            raise Conflict("Instance could not be stopped.") from exc
        instance.status = InstanceStatus.STOPPED
        instance.save(update_fields=["status", "updated_at"])
        record_event(actor=actor, event_type=EventType.INSTANCE_STOPPED, message="Instance stopped.", metadata={"instance_id": str(instance.id)})
        return instance

    @staticmethod
    def restart(*, instance_id, actor=None):
        instance = InstanceService._get_instance(user=InstanceService._actor_scope(actor), instance_id=instance_id)
        if instance.status != InstanceStatus.RUNNING:
            raise Conflict("Only running instances can be restarted.")
        try:
            docker_manager.restart_container(instance=instance)
        except Exception as exc:
            record_event(actor=actor, event_type=EventType.INSTANCE_RESTART_FAILED, message="Instance restart failed.", metadata={"instance_id": str(instance.id)})
            raise Conflict("Instance could not be restarted.") from exc
        instance.status = InstanceStatus.RUNNING
        instance.save(update_fields=["status", "updated_at"])
        record_event(actor=actor, event_type=EventType.INSTANCE_RESTARTED, message="Instance restarted.", metadata={"instance_id": str(instance.id)})
        return instance

    @staticmethod
    def delete(*, instance_id, actor=None, delete_data=False):
        """Queue asynchronous deletion of a user-owned instance (VS-038).
        With delete_data the persistent volume is removed too (VS-043);
        by default the data is retained (Sprint 6)."""
        instance = InstanceService._get_instance(user=InstanceService._actor_scope(actor), instance_id=instance_id)
        if instance.status not in (InstanceStatus.RUNNING, InstanceStatus.STOPPED, InstanceStatus.FAILED):
            raise Conflict("Instance cannot be deleted in its current state.")
        instance.status = InstanceStatus.DELETING
        instance.save(update_fields=["status", "updated_at"])
        record_event(actor=actor, event_type=EventType.INSTANCE_DELETE_REQUESTED, message="Instance deletion requested.", metadata={"instance_id": str(instance.id), "delete_data": bool(delete_data)})
        from tasks.lifecycle import delete_instance
        delete_instance.delay(str(instance.id), delete_data=delete_data)
        return instance
