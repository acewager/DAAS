from django.urls import path

from .views import DashboardStatisticsView

urlpatterns = [path("dashboard/", DashboardStatisticsView.as_view(), name="analytics-dashboard")]

# Admin analytics/health live in the /api/v1/admin/ section (api/admin_urls.py).
