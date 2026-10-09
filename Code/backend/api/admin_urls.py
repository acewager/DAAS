"""Administration endpoints (07_REST_API.md Section 14, Sprint 8 / M9).

Admin-only management: users, instances, events, platform analytics, and
system health. Views live in their domain apps; this module wires them.
"""
from django.urls import path

from apps.accounts.views import AdminUserDetailView, AdminUserListView
from apps.events.views import AdminEventListView
from apps.instances.views import AdminInstanceListView
from apps.analytics.views import AdminAnalyticsView, AdminHealthView

urlpatterns = [
    path("users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("users/<uuid:user_id>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("instances/", AdminInstanceListView.as_view(), name="admin-instance-list"),
    path("events/", AdminEventListView.as_view(), name="admin-event-list"),
    path("analytics/", AdminAnalyticsView.as_view(), name="admin-analytics"),
    path("health/", AdminHealthView.as_view(), name="admin-health"),
]
