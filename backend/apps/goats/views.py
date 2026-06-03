"""DRF views for the goats app.

Standard Django/DRF: a ModelViewSet using the ORM directly. The only domain
touch is generating a QR on registration / on demand (apps/qr/qrcode.py).
"""

from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.goats.models import Area, Goat
from apps.goats.serializers import (
    AreaSerializer,
    GoatCreateSerializer,
    GoatProfileSerializer,
    GoatSerializer,
    GoatTransferSerializer,
)
from apps.qr import qrcode


class GoatViewSet(viewsets.ModelViewSet):
    """Goat registry.

    - ``retrieve`` is public (worker QR scan → goat profile).
    - everything else requires admin JWT auth.
    """

    queryset = Goat.objects.all()

    def get_permissions(self):
        if self.action == "retrieve":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return GoatCreateSerializer
        if self.action == "retrieve":
            return GoatProfileSerializer
        return GoatSerializer

    def get_queryset(self):
        queryset = Goat.objects.all()
        params = self.request.query_params
        if status_ := params.get("status"):
            queryset = queryset.filter(status=status_)
        if sex := params.get("sex"):
            queryset = queryset.filter(sex=sex)
        if search := params.get("search"):
            queryset = queryset.filter(
                Q(tag_number__icontains=search) | Q(name__icontains=search)
            )
        return queryset

    def perform_create(self, serializer):
        goat = serializer.save()
        qrcode.generate_qr(goat)

    @action(detail=True, methods=["post"], url_path="qr")
    def regenerate_qr(self, request, pk=None):
        """Generate or regenerate this goat's QR tag (admin)."""
        goat = self.get_object()
        record = qrcode.generate_qr(goat)
        return Response(
            {
                "id": str(record.id),
                "goat": str(goat.id),
                "image_path": record.image_path,
                "is_active": record.is_active,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="transfer")
    def transfer(self, request, pk=None):
        """Move this goat to another area (admin).

        Returns the lineage risk level — advisory only, the move always
        proceeds and is always logged.
        """
        goat = self.get_object()
        area = _get_area_or_none(request.data.get("target_area_id"))
        if area is None:
            return Response(
                {"detail": "Area not found."}, status=status.HTTP_404_NOT_FOUND
            )
        result = goat.transfer_to(
            area,
            reason=request.data.get("reason", ""),
            by=getattr(request.user, "username", "admin"),
        )
        return Response(GoatTransferSerializer(result).data)


def _get_area_or_none(area_id):
    if not area_id:
        return None
    try:
        return Area.objects.filter(pk=area_id).first()
    except (ValueError, ValidationError):  # malformed UUID
        return None


class AreaViewSet(viewsets.ModelViewSet):
    """Areas (pens). Admin only."""

    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticated]
