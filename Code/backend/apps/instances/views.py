from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminRole
from services.instance_service import InstanceService

from .models import DesktopInstance
from .serializers import InstanceOrderSerializer, InstanceSerializer


class InstanceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        instances = DesktopInstance.objects.filter(user=request.user).select_related("template")
        return Response({"success": True, "message": "Instances retrieved successfully.", "data": {"instances": InstanceSerializer(instances, many=True).data}})

    def post(self, request):
        serializer = InstanceOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        instance = InstanceService.request(user=request.user, template=data.pop("template_id"), **data)
        return Response({"success": True, "message": "Instance provisioning requested.", "data": {"instance": InstanceSerializer(instance).data}}, status=202)


class InstanceLaunchView(APIView):
    """GET /api/v1/instances/{id}/launch — Desktop Launch (07_REST_API.md
    Section 10, VS-034)."""

    permission_classes = [IsAuthenticated]

    def get(self, request, instance_id):
        url = InstanceService.launch(user=request.user, instance_id=instance_id)
        return Response({"success": True, "message": "Desktop launch URL generated.", "data": {"url": url}})


class InstanceStartView(APIView):
    """POST /api/v1/instances/{id}/start (VS-035)."""

    permission_classes = [IsAuthenticated]

    def post(self, request, instance_id):
        instance = InstanceService.start(instance_id=instance_id, actor=request.user)
        return Response({"success": True, "message": "Instance started.", "data": {"instance": InstanceSerializer(instance).data}})


class InstanceStopView(APIView):
    """POST /api/v1/instances/{id}/stop (VS-036)."""

    permission_classes = [IsAuthenticated]

    def post(self, request, instance_id):
        instance = InstanceService.stop(instance_id=instance_id, actor=request.user)
        return Response({"success": True, "message": "Instance stopped.", "data": {"instance": InstanceSerializer(instance).data}})


class InstanceRestartView(APIView):
    """POST /api/v1/instances/{id}/restart (VS-037)."""

    permission_classes = [IsAuthenticated]

    def post(self, request, instance_id):
        instance = InstanceService.restart(instance_id=instance_id, actor=request.user)
        return Response({"success": True, "message": "Instance restarted.", "data": {"instance": InstanceSerializer(instance).data}})


class InstanceDeleteView(APIView):
    """DELETE /api/v1/instances/{id} (VS-038). Deletion is asynchronous.
    Query parameter delete_data=true also removes the persistent volume
    (VS-043); by default the data is retained."""

    permission_classes = [IsAuthenticated]

    def delete(self, request, instance_id):
        delete_data = str(request.query_params.get("delete_data", "")).lower() == "true"
        instance = InstanceService.delete(instance_id=instance_id, actor=request.user, delete_data=delete_data)
        return Response({"success": True, "message": "Instance deletion queued.", "data": {"instance": InstanceSerializer(instance).data}}, status=202)


class AdminInstanceListView(APIView):
    """GET /api/v1/admin/instances/ — all instances (VS-051, Admin Only).
    Supports ?status=, ?search= (name/username), and pagination."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        from django.db.models import Q

        from api.pagination import pagination_meta, paginate

        instances = DesktopInstance.objects.select_related("user", "template").order_by("-created_at")
        status_filter = request.query_params.get("status", "").upper()
        if status_filter:
            instances = instances.filter(status=status_filter)
        search = request.query_params.get("search", "").strip()
        if search:
            instances = instances.filter(Q(name__icontains=search) | Q(user__username__icontains=search))
        page, page_size = paginate(request)
        total = instances.count()
        from .serializers import AdminInstanceSerializer
        data = [AdminInstanceSerializer(i).data for i in instances[(page - 1) * page_size : page * page_size]]
        return Response({"success": True, "message": "Instances retrieved successfully.", "data": {"instances": data, "pagination": pagination_meta(total, page, page_size)}})
