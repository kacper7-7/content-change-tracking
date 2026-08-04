from datetime import timedelta

from django.db.models import (
    F,
    Case,
    When,
    Value,
    Model,
    Exists,
    OuterRef,
    Count,
    Q,
    Max,
)
from django.db.models.fields import BooleanField
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from content.models import Content, Follow, ContentEditHistory
from notification.tasks import create_notification_for_followers_content
from content.serializers import (
    ContentSerializer,
    FollowSerializer,
    ContentAdminSerializer,
    FollowCreateSerializer,
)
from django.core.cache import cache


class ContentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Content.objects.none()
        queryset = (
            Content.objects.select_related("author")
            .prefetch_related("edit_history")
            .annotate(
                is_followed_by_me=Exists(
                    Follow.objects.filter(
                        content=OuterRef("pk"), user=self.request.user
                    )
                ),
                followers_count=Count(F("followers"), distinct=True),
                is_hot=Case(
                    When(
                        Q(followers_count__gt=5) | Q(edited_count__gt=10),
                        then=Value(True),
                    ),
                    default=False,
                    output_field=BooleanField(),
                ),
                recent_edits_count=Count(
                    "edit_history",
                    filter=Q(
                        edit_history__edited_at__gte=timezone.now() - timedelta(days=7)
                    ),
                ),
                last_edit_date=Max("edit_history__edited_at"),
            )
        )

        if self.request.user.is_staff:
            queryset = queryset.prefetch_related("followers")

        return queryset

    def get_serializer_class(self):

        if self.request.user and self.request.user.is_staff:
            return ContentAdminSerializer
        return ContentSerializer

    def perform_create(self, serializer):
        new_content = serializer.save(author=self.request.user)
        Follow.objects.create(user=self.request.user, content=new_content)

    def retrieve(self, request, *args, **kwargs):
        content = self.get_object()
        follow = content.followers.filter(user=request.user).first()

        if follow:
            follow.last_viewed_at = timezone.now()
            follow.save(update_fields=["last_viewed_at"])

        if hasattr(cache, "delete_pattern"):
            cache.delete_pattern(f"updated_contents_user_{request.user.pk}_page_*")
        else:
            cache.clear()
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        content = self.get_object()

        if request.user != content.author:
            return Response(
                {"error": "You can only update your own posts."},
                status=status.HTTP_403_FORBIDDEN,
            )

        response = super().update(request, *args, **kwargs)
        create_notification_for_followers_content.delay(content.pk)

        return response

    def destroy(self, request, *args, **kwargs):
        content = self.get_object()

        if request.user != content.author:
            return Response(
                {"error": "You can only delete your own posts."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        instance = serializer.save()

        ContentEditHistory.objects.create(
            content=instance,
        )

        instance.edited_count = F("edited_count") + 1
        instance.save(update_fields=["edited_count"])

        if hasattr(cache, "delete_pattern"):
            cache.delete_pattern(f"updated_contents_user_{self.request.user.pk}_page_*")
        else:
            cache.clear()

    @action(methods=["GET"], url_path="updated-contents", detail=False)
    def update_contents(self, request):
        page_number = request.query_params.get("page", 1)
        cache_key = f"updated_contents_user_{request.user.pk}_page_{page_number}"

        cache_data = cache.get(cache_key)

        if cache_data:
            return Response(cache_data, status=status.HTTP_200_OK)

        updated_follows = Follow.objects.filter(
            user=request.user, content__updated_at__gt=F("last_viewed_at")
        )

        updated_contents = Content.objects.filter(
            followers__in=updated_follows
        ).order_by("-updated_at")

        page = self.paginate_queryset(updated_contents)
        if page is not None:
            serializer = ContentSerializer(
                page, many=True, context=self.get_serializer_context()
            )
            response_data = self.get_paginated_response(serializer.data).data
        else:
            serializer = ContentSerializer(
                updated_contents, many=True, context=self.get_serializer_context()
            )
            response_data = serializer.data

        cache.set(cache_key, response_data, timeout=300)

        return Response(response_data, status=status.HTTP_200_OK)


class FollowViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "delete", "head", "options"]
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        follow = self.get_object()
        if follow.user != request.user and request.user.is_staff == False:
            return Response(
                {"error": "You can delete only your owns follows"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        content = serializer.validated_data.get("content")

        if Follow.objects.filter(user=self.request.user, content=content).exists():
            raise ValidationError({"detail": "You are already following this content!"})

        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Follow.objects.select_related("user", "content").annotate(
            has_new_changes=Case(
                When(content__updated_at__gt=F("last_viewed_at"), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            missed_edits_count=Count(
                "content__edit_history",
                filter=Q(content__edit_history__edited_at__gt=F("last_viewed_at")),
            ),
        )

        if self.request.user and self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return FollowCreateSerializer
        return FollowSerializer
