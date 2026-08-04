from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from notification.models import Notification
from notification.serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Notification.objects.none()

        return Notification.objects.prefetch_related("recipient", "content").filter(
            recipient=self.request.user
        )
