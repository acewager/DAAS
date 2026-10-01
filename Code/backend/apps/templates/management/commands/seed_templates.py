"""Create safe, repeatable development template records."""
from django.core.management.base import BaseCommand

from apps.templates.models import DesktopTemplate


TEMPLATES = (
    {
        "name": "XFCE Minimal",
        "slug": "xfce-minimal",
        "description": "A lightweight XFCE desktop for basic testing.",
        "json_configuration": {"image": "lscr.io/linuxserver/webtop:ubuntu-xfce", "memory": "2G", "cpus": 2, "internet": True, "persistent_supported": True},
    },
    {
        "name": "XFCE Developer Tools",
        "slug": "xfce-developer-tools",
        "description": "An XFCE desktop intended for development workflows.",
        "json_configuration": {"image": "lscr.io/linuxserver/webtop:ubuntu-xfce", "memory": "4G", "cpus": 4, "internet": True, "persistent_supported": True},
    },
    {
        "name": "XFCE Browser",
        "slug": "xfce-browser",
        "description": "An XFCE desktop for browser-based testing.",
        "json_configuration": {"image": "lscr.io/linuxserver/webtop:ubuntu-xfce", "memory": "2G", "cpus": 2, "internet": True, "persistent_supported": True},
    },
)


class Command(BaseCommand):
    help = "Create or update the development desktop templates."

    def handle(self, *args, **options):
        for data in TEMPLATES:
            template, created = DesktopTemplate.objects.update_or_create(
                slug=data["slug"], defaults={**data, "enabled": True}
            )
            self.stdout.write(f"{'Created' if created else 'Updated'} {template.name}")
