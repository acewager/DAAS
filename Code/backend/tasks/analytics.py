"""Usage analytics aggregation task (VS-055, Sprint 9)."""
from config.celery import app
from services.analytics_service import AnalyticsService


@app.task(name="dcp.aggregate_usage")
def aggregate_usage():
    """Sample all RUNNING instances' container usage into the Analytics model."""
    sampled = AnalyticsService.aggregate_running_instances()
    return {"sampled": sampled}
