"""
API v1 root router.

Per 07_REST_API.md Section 7, the API is divided into business domains.
Each domain app registers its own routes here as it is implemented.
"""
from django.urls import include, path

from api.health import HealthCheckView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("auth/", include("apps.accounts.urls")),
    path("templates/", include("apps.templates.urls")),
    path("instances/", include("apps.instances.urls")),
]
