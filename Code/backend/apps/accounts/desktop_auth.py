"""Traefik ForwardAuth endpoint (M6 — Browser Desktop Access).

Per 05_Container_Architecture.md Section 13: Traefik validates the
authenticated session before routing desktop traffic. This endpoint receives
every request to a desktop subdomain (forwarded by Traefik with the original
Host header and cookies) and decides whether it may proceed:

- Authenticated owner + RUNNING instance -> 200 (Traefik forwards)
- Unauthenticated                        -> 401 friendly sign-in page
- Authenticated, not the owner           -> 403 friendly access-denied page
- Owner, instance not RUNNING            -> 409 friendly not-running page

Error responses are friendly HTML pages: they are rendered directly by the
user's browser (09_User_Experience.md — friendly messages, no technical
details).
"""
from django.http import HttpResponse

from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.instances.models import DesktopInstance, InstanceStatus

# Platform hosts that must never be authorized through this endpoint.
PLATFORM_HOST_PREFIXES = ("app", "api", "www", "traefik")

PAGE_SHELL = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — Desktop Cloud Platform</title>
  <style>
    body {{ font-family: system-ui, -apple-system, sans-serif; background: #f8fafc; color: #0f172a;
           display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }}
    .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 2.5rem;
             max-width: 26rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.06); }}
    h1 {{ font-size: 1.25rem; margin: 0 0 0.75rem; }}
    p {{ font-size: 0.95rem; color: #475569; margin: 0 0 1.5rem; line-height: 1.5; }}
    a {{ display: inline-block; background: #2563eb; color: #fff; text-decoration: none;
         padding: 0.6rem 1.25rem; border-radius: 8px; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{title}</h1>
    <p>{message}</p>
    <a href="{link}">{link_text}</a>
  </div>
</body>
</html>"""


def _error_page(title: str, message: str, link: str, link_text: str, status: int) -> HttpResponse:
    html = PAGE_SHELL.format(title=title, message=message, link=link, link_text=link_text)
    return HttpResponse(html, status=status, content_type="text/html")


def _original_host(request) -> str:
    """The desktop subdomain host the browser asked for (X-Forwarded-Host set
    by Traefik's ForwardAuth); falls back to the request Host."""
    host = request.META.get("HTTP_X_FORWARDED_HOST") or request.META.get("HTTP_HOST", "")
    host = host.split(",")[0].strip().split(":")[0].lower()
    return host


def desktop_fallback(request):
    """Friendly page for desktop subdomains without an active route (M6).

    Traefik drops routes for exited containers, so requests to a stopped
    instance's subdomain — and unknown subdomains — never reach the
    ForwardAuth middleware. This catch-all (the desktop-fallback router,
    lowest priority) serves the friendly explanation instead.
    """
    from django.conf import settings

    app_url = getattr(settings, "FRONTEND_URL", "http://app.localhost")
    host = _original_host(request)
    prefix = host.split(".")[0] if host else ""

    if prefix and prefix not in PLATFORM_HOST_PREFIXES:
        instance = (
            DesktopInstance.objects.filter(access_hash__istartswith=prefix)
            .exclude(status=InstanceStatus.DELETED)
            .first()
        )
        if instance is not None:
            return _error_page(
                "Desktop not running",
                "This desktop is not running right now. Start it from your dashboard and try again.",
                f"{app_url}/instances", "Back to instances", 409,
            )
    return _error_page(
        "Desktop not found",
        "No desktop exists at this address. Check the link or launch your desktop from the dashboard.",
        app_url, "Back to dashboard", 404,
    )


class DesktopAuthView(APIView):
    """GET /api/v1/auth/desktop-auth/ — Traefik ForwardAuth (M6)."""

    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        from django.conf import settings

        app_url = getattr(settings, "FRONTEND_URL", "http://app.localhost")
        host = _original_host(request)
        prefix = host.split(".")[0] if host else ""

        if not prefix or prefix in PLATFORM_HOST_PREFIXES:
            return _error_page(
                "Sign in required",
                "Please sign in to the Desktop Cloud Platform to access your desktop.",
                app_url, "Go to sign in", 401,
            )

        if not request.user.is_authenticated:
            return _error_page(
                "Sign in required",
                "Please sign in to the Desktop Cloud Platform to access your desktop.",
                app_url, "Go to sign in", 401,
            )

        instance = (
            DesktopInstance.objects.filter(access_hash__istartswith=prefix, user=request.user)
            .exclude(status=InstanceStatus.DELETED)
            .first()
        )
        if instance is None:
            return _error_page(
                "Access denied",
                "You do not have access to this desktop.",
                app_url, "Back to dashboard", 403,
            )
        if instance.status != InstanceStatus.RUNNING:
            return _error_page(
                "Desktop not running",
                "This desktop is not running right now. Start it from your dashboard and try again.",
                f"{app_url}/instances", "Back to instances", 409,
            )
        return Response({"success": True, "message": "Desktop access authorized."})
