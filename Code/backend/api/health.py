"""
Platform health endpoint.

Used by:
- The frontend, to confirm it can reach the backend (M1 acceptance
  criteria: "Backend and frontend communicate").
- Docker / orchestration health checks.
- The future Administration Portal system-health widget
  (11_Analytics_Logging_Monitoring.md Section 9).
"""
from django.db import connections
from django.db.utils import OperationalError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Reports the health of core platform dependencies."""

    permission_classes = [AllowAny]

    def get(self, request):
        checks = {"database": self._check_database()}
        overall = "healthy" if all(v == "healthy" for v in checks.values()) else "critical"

        return Response(
            {
                "success": True,
                "data": {
                    "status": overall,
                    "checks": checks,
                },
                "message": "Platform health retrieved successfully.",
            }
        )

    @staticmethod
    def _check_database() -> str:
        try:
            connections["default"].cursor()
            return "healthy"
        except OperationalError:
            return "critical"
