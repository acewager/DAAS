from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from services.dashboard_service import DashboardService


class DashboardStatisticsView(APIView):
    """GET /api/v1/analytics/dashboard (07_REST_API.md Section 12, VS-030)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = DashboardService.dashboard(user=request.user)
        return Response({"success": True, "message": "Dashboard statistics retrieved successfully.", "data": data})
