"""Retained-volume endpoints (VS-043 — the "Keep my data" re-attach flow)."""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from services.volume_service import VolumeService


class VolumeListView(APIView):
    """GET /api/v1/volumes/ — the user's retained volumes awaiting
    re-attachment (their owning instance was deleted with data retained)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        volumes = VolumeService.retained_volumes(request.user)
        data = [
            {
                "id": str(volume.id),
                "host_path": volume.host_path,
                "original_instance": volume.instance.name,
                "released_at": volume.updated_at.isoformat(),
            }
            for volume in volumes
        ]
        return Response({"success": True, "message": "Retained volumes retrieved successfully.", "data": {"volumes": data}})
