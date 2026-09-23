from apps.events.models import EventType
from services.event_log_service import record_event
from apps.templates.models import DesktopTemplate


class TemplateService:
    @staticmethod
    def create(*, actor, **data):
        template = DesktopTemplate.objects.create(**data)
        record_event(actor=actor, event_type=EventType.TEMPLATE_CREATED, message="Desktop template created.", metadata={"template_id": str(template.id), "slug": template.slug})
        return template

    @staticmethod
    def update(*, actor, template, **data):
        for field, value in data.items():
            setattr(template, field, value)
        template.full_clean()
        template.save()
        record_event(actor=actor, event_type=EventType.TEMPLATE_UPDATED, message="Desktop template updated.", metadata={"template_id": str(template.id), "slug": template.slug})
        return template

    @staticmethod
    def archive(*, actor, template):
        template.enabled = False
        template.save(update_fields=["enabled", "updated_at"])
        record_event(actor=actor, event_type=EventType.TEMPLATE_ARCHIVED, message="Desktop template archived.", metadata={"template_id": str(template.id), "slug": template.slug})
