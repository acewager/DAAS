"""Signed tokens bridging the app session to desktop subdomains (M6).

Browsers reject Domain cookies for the single-label "localhost" dev domain,
so the platform-domain session cookie cannot carry the session to desktop
subdomains there. The launch URL instead carries a short-lived signed token
(a capability link); the ForwardAuth validates it and sets a host-only
cookie for the desktop subdomain for the desktop UI's subsequent requests.
In production (a multi-label domain) the platform-domain session cookie
works directly.
"""
from django.core import signing

DESKTOP_AUTH_SALT = "dcp.desktop-auth"
DESKTOP_AUTH_COOKIE = "dcp_desktop_auth"
DESKTOP_AUTH_TOKEN_MAX_AGE = 300  # seconds — launch URLs are capability links
DESKTOP_AUTH_COOKIE_AGE = 60 * 60 * 8


def issue_token(*, user_id, instance_hash) -> str:
    return signing.dumps({"u": str(user_id), "h": instance_hash}, salt=DESKTOP_AUTH_SALT)


def read_token(value, *, max_age=None):
    """Returns {"u": ..., "h": ...} or None for invalid or expired tokens."""
    if not value:
        return None
    try:
        return signing.loads(value, salt=DESKTOP_AUTH_SALT, max_age=max_age)
    except signing.BadSignature:
        return None
