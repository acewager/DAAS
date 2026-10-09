from django.urls import path

from .views import DashboardStatisticsView, InstanceUsageView

urlpatterns = [
    path("dashboard/", DashboardStatisticsView.as_view(), name="analytics-dashboard"),
    path("instances/<uuid:instance_id>/", InstanceUsageView.as_view(), name="analytics-instance-usage"),
]

# Admin analytics/health live in the /api/v1/admin/ section (api/admin_urls.py).
