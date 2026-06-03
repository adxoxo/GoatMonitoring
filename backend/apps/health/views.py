"""DRF views for the health app — standard ModelViewSet + ORM directly.

Worker logging lives on GoatViewSet.log (public); these are all admin-only.
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.health.models import HealthRecord, VaccinationSchedule
from apps.health.serializers import (
    HealthRecordCreateSerializer,
    HealthRecordSerializer,
    VaccinationScheduleSerializer,
)


class HealthRecordViewSet(viewsets.ModelViewSet):
    """Health records. Admin only. Filterable by ?goat= and ?record_type=."""

    queryset = HealthRecord.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return HealthRecordCreateSerializer
        return HealthRecordSerializer

    def get_queryset(self):
        queryset = HealthRecord.objects.all()
        params = self.request.query_params
        if goat := params.get("goat"):
            queryset = queryset.filter(goat_id=goat)
        if record_type := params.get("record_type"):
            queryset = queryset.filter(record_type=record_type)
        return queryset


class VaccinationScheduleViewSet(viewsets.ModelViewSet):
    """Vaccine definitions used to compute next-due dates. Admin only."""

    queryset = VaccinationSchedule.objects.all()
    serializer_class = VaccinationScheduleSerializer
    permission_classes = [IsAuthenticated]


class AlertsView(APIView):
    """Overdue + upcoming health alerts feed. Admin only.

    Excludes inactive goats (sold/deceased); overdue first, then due-soon,
    each ordered most-urgent-first (handled by the manager).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        feed = HealthRecord.objects.alerts_feed(days=7)
        return Response(
            {
                "overdue": HealthRecordSerializer(feed["overdue"], many=True).data,
                "due_soon": HealthRecordSerializer(feed["due_soon"], many=True).data,
            }
        )
