"""
Celery application entrypoint.

Per 06_Backend_Architecture.md Section 8, Celery owns all long-running
work (container provisioning, deletion, software installation, analytics
aggregation, auto-stop). Workers never expose HTTP endpoints.
"""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("dcp")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# VS-039: periodic auto-stop sweep for idle running instances.
app.conf.beat_schedule = {
    "auto-stop-instances": {
        "task": "dcp.auto_stop_instances",
        "schedule": 60.0,
    },
}


@app.task(bind=True, name="dcp.debug_task")
def debug_task(self):
    """Sanity-check task used to confirm the worker is alive (VS-005)."""
    print(f"Celery worker OK — request: {self.request!r}")
    return "pong"
