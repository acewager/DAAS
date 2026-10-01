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
