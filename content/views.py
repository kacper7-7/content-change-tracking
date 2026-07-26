from django.db.models import F
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from content.models import Content, Follow
from content.serializers import ContentSerializer, FollowSerializer


class ContentViewSet(viewsets.ModelViewSet):
    serializer_class = ContentSerializer
    queryset = Content.objects.all()

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
    serializer_class = FollowSerializer
    queryset = Follow.objects.select_related("user", "content")


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)