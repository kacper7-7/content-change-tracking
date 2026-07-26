from django.urls import include, path
from rest_framework.routers import DefaultRouter

from content.views import ContentViewSet, FollowViewSet

router = DefaultRouter()
router.register("content", ContentViewSet, basename="content")
router.register("follows", FollowViewSet, basename="follow")


urlpatterns = [
    path("", include(router.urls))
]

app_name = "content"