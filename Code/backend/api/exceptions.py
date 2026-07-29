"""
Standardized API exception handling.

Per 06_Backend_Architecture.md Section 13 (API Response Standard), every
error response follows the same shape:

    {
      "success": false,
      "error": {"code": "...", "message": "..."}
    }
"""
from rest_framework.views import exception_handler


def standard_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "success": False,
            "error": {
                "code": getattr(exc, "default_code", "ERROR").upper()
                if hasattr(exc, "default_code")
                else "ERROR",
                "message": response.data.get("detail", str(response.data))
                if isinstance(response.data, dict)
                else str(response.data),
            },
        }

    return response
