from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
    """DELETE /api/v1/instances/{id} (VS-038). Deletion is asynchronous; the
    persistent volume is retained by default (Sprint 6, VS-043)."""

    permission_classes = [IsAuthenticated]

    def delete(self, request, instance_id):
        instance = InstanceService.delete(instance_id=instance_id, actor=request.user)
        return Response({"success": True, "message": "Instance deletion queued.", "data": {"instance": InstanceSerializer(instance).data}}, status=202)
