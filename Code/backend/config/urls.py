"""
Root URL configuration.

The backend never renders HTML (06_Backend_Architecture.md Section 1);
every capability is exposed through /api/v1/ (07_REST_API.md). The single
sanctioned exception is the M6 friendly error pages: the desktop-fallback
catch-all below serves them for desktop subdomains without an active route
(stopped instances, unknown subdomains).
"""
from django.contrib import admin
from django.urls import include, path, re_path

from apps.accounts.desktop_auth import desktop_fallback

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.urls")),
    # Catch-all LAST — real routes always match first.
    re_path(r"^", desktop_fallback),
]
