from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EventLog
from .serializers import EventSerializer


class EventHistoryView(APIView):
    """GET /api/v1/events — My Event History (07_REST_API.md Section 13)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        events = EventLog.objects.filter(actor=request.user)[:50]
        return Response({"success": True, "message": "Event history retrieved successfully.", "data": {"events": EventSerializer(events, many=True).data}})
