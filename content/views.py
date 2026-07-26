from django.db.models import F
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from content.models import Content, Follow
from content.permissions import AdminOrReadOnly
from content.serializers import ContentSerializer, FollowSerializer, ContentAdminSerializer


class ContentViewSet(viewsets.ModelViewSet):
    permission_classes = [AdminOrReadOnly]

    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return Content.objects.prefetch_related("followers")
        return Content.objects.prefetch_related("followers").filter(followers__user=self.request.user)


    def get_serializer_class(self):
        if self.request.user and self.request.user.is_staff:
            return ContentAdminSerializer
        return ContentSerializer



    @action(methods=["GET"], url_path="updated-contents", detail=False)
    def update_contents(self, request):
        updated_follows = Follow.objects.filter(
            user=request.user,
            content__updated_at__gt=F("last_viewed_at")
        )

        updated_contents = Content.objects.filter(
            followers__in=updated_follows
        )

        serializer = ContentSerializer(updated_contents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowViewSet(viewsets.ModelViewSet):
    permission_classes = [AdminOrReadOnly]
    serializer_class = FollowSerializer


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return Follow.objects.select_related("user", "content")
        return Follow.objects.select_related("user", "content").filter(user=self.request.user)
