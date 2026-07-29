from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import F, Case, When, Value
from django.db.models.fields import BooleanField
from django.template.defaultfilters import default
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from content.models import Content, Follow
from user.permissions import AdminOrReadOnly
from content.serializers import ContentSerializer, FollowSerializer, ContentAdminSerializer, FollowCreateSerializer


class ContentViewSet(viewsets.ModelViewSet):
    permission_classes = [AdminOrReadOnly, IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Content.objects.none()

        queryset = Content.objects.prefetch_related("followers", "edit_history")
        if self.request.user and self.request.user.is_staff:
            return queryset
        return queryset.filter(followers__user=self.request.user)


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
    def destroy(self, request, *args, **kwargs):
        follow = self.get_object()
        if follow.user != request.user and request.user.is_staff == False:
            return Response({"error": "You can delete only your owns follows"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Follow.objects.select_related("user", "content").annotate(
            has_new_changes = Case(
                When(content__updated_at__gt=F("last_viewed_at"),
                     then=Value(True)), default=Value(False),
                     output_field=BooleanField()
            )
        )

        if self.request.user and self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return FollowCreateSerializer
        return FollowSerializer

    @action(methods=["DELETE"], detail=True, url_path="unfollow")
    def unfollow(self, request, pk=None):
        follow = self.get_object()
        follow_id = follow.id
        follow.delete()
        return Response({"message": f"Follow wit id {follow_id} deleted"}, status=status.HTTP_200_OK)