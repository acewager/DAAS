from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminRole
from services.template_service import TemplateService

from .models import DesktopTemplate
from .serializers import TemplateSerializer


class TemplateListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        templates = DesktopTemplate.objects.filter(enabled=True)
        return Response({"success": True, "message": "Templates retrieved successfully.", "data": {"templates": TemplateSerializer(templates, many=True).data}})

    def post(self, request):
        if not IsAdminRole().has_permission(request, self):
            self.permission_denied(request)
        serializer = TemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        template = TemplateService.create(actor=request.user, **serializer.validated_data)
        return Response({"success": True, "message": "Template created successfully.", "data": {"template": TemplateSerializer(template).data}}, status=201)


class TemplateDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, template_id):
        template = get_object_or_404(DesktopTemplate.objects.filter(enabled=True), pk=template_id)
        return Response({"success": True, "message": "Template retrieved successfully.", "data": {"template": TemplateSerializer(template).data}})

    def put(self, request, template_id):
        if not IsAdminRole().has_permission(request, self):
            self.permission_denied(request)
        template = get_object_or_404(DesktopTemplate, pk=template_id)
        serializer = TemplateSerializer(template, data=request.data)
        serializer.is_valid(raise_exception=True)
        template = TemplateService.update(actor=request.user, template=template, **serializer.validated_data)
        return Response({"success": True, "message": "Template updated successfully.", "data": {"template": TemplateSerializer(template).data}})

    def delete(self, request, template_id):
        if not IsAdminRole().has_permission(request, self):
            self.permission_denied(request)
        TemplateService.archive(actor=request.user, template=get_object_or_404(DesktopTemplate, pk=template_id))
        return Response(status=204)
