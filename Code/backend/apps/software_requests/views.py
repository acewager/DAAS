from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.software_requests.models import SoftwareRequest, SoftwareRequestStatus
from services.software_request_service import SoftwareRequestService

from .serializers import SoftwareRequestCreateSerializer, SoftwareRequestSerializer

User = get_user_model()


def _is_admin(user) -> bool:
    return user.is_authenticated and (user.role == UserRole.ADMIN or user.is_superuser)


class SoftwareRequestListCreateView(APIView):
    """GET/POST /api/v1/software-requests (07_REST_API.md Section 11, VS-045).

    Regular users see their own requests; admins see all (optionally filtered
    with ?status=PENDING for the approval page)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_filter = request.query_params.get("status", "").upper()
        queryset = SoftwareRequest.objects.select_related("instance", "user", "reviewed_by")
        if _is_admin(request.user):
            requests = queryset.all()
        else:
            requests = queryset.filter(user=request.user)
        if status_filter in SoftwareRequestStatus.values:
            requests = requests.filter(status=status_filter)
        return Response({"success": True, "message": "Software requests retrieved successfully.", "data": {"requests": SoftwareRequestSerializer(requests[:100], many=True).data}})

    def post(self, request):
        serializer = SoftwareRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        software_request = SoftwareRequestService.submit(user=request.user, instance_id=data["instance_id"], software_name=data["software_name"], justification=data.get("justification", ""))
        return Response({"success": True, "message": "Software request submitted.", "data": {"request": SoftwareRequestSerializer(software_request).data}}, status=201)


class SoftwareRequestDetailView(APIView):
    """GET /api/v1/software-requests/{id} — ownership-scoped; admins any."""

    permission_classes = [IsAuthenticated]

    def get(self, request, request_id):
        software_request = get_object_or_404(SoftwareRequest, pk=request_id)
        if software_request.user_id != request.user.id and not _is_admin(request.user):
            return Response({"success": False, "error": {"code": "FORBIDDEN", "message": "You do not have access to this request."}}, status=403)
        return Response({"success": True, "message": "Software request retrieved successfully.", "data": {"request": SoftwareRequestSerializer(software_request).data}})


class SoftwareRequestApproveView(APIView):
    """POST /api/v1/software-requests/{id}/approve — Admin Only (VS-046/047)."""

    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        if not _is_admin(request.user):
            return Response({"success": False, "error": {"code": "FORBIDDEN", "message": "Admin role required."}}, status=403)
        software_request = SoftwareRequestService.approve(reviewer=request.user, request_id=request_id)
        return Response({"success": True, "message": "Software request approved; installation queued.", "data": {"request": SoftwareRequestSerializer(software_request).data}})


class SoftwareRequestRejectView(APIView):
    """POST /api/v1/software-requests/{id}/reject — Admin Only (VS-046)."""

    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        if not _is_admin(request.user):
            return Response({"success": False, "error": {"code": "FORBIDDEN", "message": "Admin role required."}}, status=403)
        software_request = SoftwareRequestService.reject(reviewer=request.user, request_id=request_id)
        return Response({"success": True, "message": "Software request rejected.", "data": {"request": SoftwareRequestSerializer(software_request).data}})
