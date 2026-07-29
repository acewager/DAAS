"""
Foundation-slice Celery tasks (VS-005: "Configure Celery — background
worker, test task").

Run manually to confirm the worker is wired up correctly:

    docker compose exec backend celery -A config call dcp.debug_task
"""
import logging

from config.celery import app

logger = logging.getLogger("celery")


@app.task(name="dcp.ping")
def ping() -> str:
    """Minimal end-to-end smoke-test task."""
    logger.info("dcp.ping task executed successfully.")
    return "pong"
