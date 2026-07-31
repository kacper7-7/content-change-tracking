from django.urls import path, include
from rest_framework.routers import DefaultRouter

from notification.views import NotificationViewSet

router = DefaultRouter()
router.register("notifications", NotificationViewSet, basename="notification")


urlpatterns = [
    path("", include(router.urls))
]


app_name = "notification"