"""Traefik ForwardAuth endpoint (M6 — Browser Desktop Access).

Per 05_Container_Architecture.md Section 13: Traefik validates the
authenticated session before routing desktop traffic. This endpoint receives
every request to a desktop subdomain (forwarded by Traefik with the original
Host header and cookies) and decides whether it may proceed:

- Authenticated owner + RUNNING instance -> 200 (Traefik forwards)
- Unauthenticated                        -> 401 friendly sign-in page
- Authenticated, not the owner           -> 403 friendly access-denied page
- Owner, instance not RUNNING            -> 409 friendly not-running page
- Expired launch link                    -> 401 friendly link-expired page

Error responses are friendly HTML pages: they are rendered directly by the
user's browser (09_User_Experience.md — friendly messages, no technical
details).

Credentials are resolved from (in order): the ?auth= launch token, the
desktop cookie set by a previous ForwardAuth on this host, and the Django
session. Browsers reject Domain cookies for the single-label "localhost" dev
domain, so the launch token bridges the app session to the desktop subdomain
in dev; in production the platform-domain session cookie works directly.
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

        from services.desktop_auth_tokens import (
            DESKTOP_AUTH_COOKIE,
            DESKTOP_AUTH_COOKIE_AGE,
            DESKTOP_AUTH_TOKEN_MAX_AGE,
            issue_token,
            read_token,
        )

        app_url = getattr(settings, "FRONTEND_URL", "http://app.localhost")
        host = _original_host(request)
        prefix = host.split(".")[0] if host else ""

        if not prefix or prefix in PLATFORM_HOST_PREFIXES:
            return _error_page(
                "Sign in required",
                "Please sign in to the Desktop Cloud Platform to access your desktop.",
                app_url, "Go to sign in", 401,
            )

        user_id = None
        token_hash = None

        # The original request URI (path + query) arrives as X-Forwarded-Uri —
        # the auth address's query is not the original one. Parse the launch
        # token from it (falling back to this request's own query params).
        forwarded_uri = request.META.get("HTTP_X_FORWARDED_URI", "")
        token = request.query_params.get("auth")
        if not token and forwarded_uri:
            from urllib.parse import parse_qs, urlsplit
            token = parse_qs(urlsplit(forwarded_uri).query).get("auth", [None])[0]

        # 1) ?auth= token from the launch URL — the dev bridge (browsers
        #    reject Domain cookies for the single-label localhost). Expired
        #    links get their own friendly page; malformed ones fall through.
        if token:
            data = read_token(token, max_age=DESKTOP_AUTH_TOKEN_MAX_AGE)
            if data is None:
                return _error_page(
                    "Link expired",
                    "This desktop link has expired. Launch it again from your dashboard.",
                    f"{app_url}/instances", "Back to instances", 401,
                )
            user_id, token_hash = data["u"], data["h"]

        # 2) The desktop cookie set by a previous ForwardAuth on this host —
        #    carries the desktop UI's subsequent requests.
        if user_id is None:
            data = read_token(request.COOKIES.get(DESKTOP_AUTH_COOKIE))
            if data is not None:
                user_id, token_hash = data["u"], data["h"]

        # 3) The Django session — works in production, where the platform
        #    domain cookie is accepted by browsers.
        if user_id is None and request.user.is_authenticated:
            user_id = str(request.user.id)

        if user_id is None:
            return _error_page(
                "Sign in required",
                "Please sign in to the Desktop Cloud Platform to access your desktop.",
                app_url, "Go to sign in", 401,
            )

        # A token/cookie is bound to one desktop; using it against another
        # subdomain's host is denied.
        if token_hash is not None and token_hash[:7].lower() != prefix:
            return _error_page(
                "Access denied",
                "You do not have access to this desktop.",
                app_url, "Back to dashboard", 403,
            )

        instance = (
            DesktopInstance.objects.filter(access_hash__istartswith=prefix, user_id=user_id)
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

        # Success — set the host-only cookie for this desktop subdomain so the
        # desktop UI's subsequent requests skip the token dance. Traefik
        # forwards the auth response's headers (including Set-Cookie) to the
        # client, and the cookie is scoped to the requested host.
        response = Response({"success": True, "message": "Desktop access authorized."})
        response.set_cookie(
            DESKTOP_AUTH_COOKIE,
            issue_token(user_id=user_id, instance_hash=instance.access_hash),
            max_age=DESKTOP_AUTH_COOKIE_AGE,
            httponly=True,
            samesite="Strict",
        )
        return response
