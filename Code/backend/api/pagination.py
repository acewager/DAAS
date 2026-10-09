"""Shared pagination for list endpoints (07_REST_API.md Section 15).

?page=1, ?page_size=20 (default), maximum 100.
"""
import math


def paginate(request, default_page_size: int = 20, max_page_size: int = 100):
    try:
        page = max(1, int(request.query_params.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = min(max(1, int(request.query_params.get("page_size", default_page_size))), max_page_size)
    except (TypeError, ValueError):
        page_size = default_page_size
    return page, page_size


def pagination_meta(total: int, page: int, page_size: int) -> dict:
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": max(1, math.ceil(total / page_size)) if total else 1,
    }
