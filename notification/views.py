from rest_framework import viewsets
from notification.models import Notification
from notification.serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.prefetch_related("recipient", "content").filter(recipient=self.request.user)