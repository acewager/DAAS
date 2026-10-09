from apps.accounts.permissions import IsAdminRole
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


class AdminEventListView(APIView):
    """GET /api/v1/admin/events/ — all events (VS-052, Admin Only).
    Supports ?event_type=, ?search= (message/actor), and pagination."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        from django.db.models import Q

        from api.pagination import pagination_meta, paginate

        events = EventLog.objects.select_related("actor").order_by("-created_at")
        event_type = request.query_params.get("event_type", "").upper()
        if event_type:
            events = events.filter(event_type=event_type)
        search = request.query_params.get("search", "").strip()
        if search:
            events = events.filter(Q(message__icontains=search) | Q(actor__username__icontains=search))
        page, page_size = paginate(request)
        total = events.count()
        data = [EventSerializer(e).data for e in events[(page - 1) * page_size : page * page_size]]
        return Response({"success": True, "message": "Events retrieved successfully.", "data": {"events": data, "pagination": pagination_meta(total, page, page_size)}})
