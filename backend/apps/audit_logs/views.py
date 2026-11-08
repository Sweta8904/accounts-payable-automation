from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListView(ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = AuditLog.objects.select_related("user").order_by("-created_at")

        action = self.request.query_params.get("action")
        entity_type = self.request.query_params.get("entity_type")
        search = self.request.query_params.get("search")

        if action:
            queryset = queryset.filter(action__icontains=action)

        if entity_type:
            queryset = queryset.filter(entity_type__icontains=entity_type)

        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(description__icontains=search)
                | Q(entity_id__icontains=search)
                | Q(user__username__icontains=search)
            )

        return queryset