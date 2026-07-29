"""
Root URL configuration.

The backend never renders HTML (06_Backend_Architecture.md Section 1);
every capability is exposed through /api/v1/ (07_REST_API.md).
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.urls")),
]
