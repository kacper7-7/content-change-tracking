from django.utils import timezone
from rest_framework import serializers
from content.models import Content, Follow


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ["id", "title", "body", "created_at", "updated_at"]

    def update(self, instance, validated_data):
        instance.updated_at = timezone.now()
        return super().update(instance, validated_data)


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="email", read_only=True)
    content = serializers.SlugRelatedField(slug_field="title", read_only=True)

    class Meta:
        model = Follow
        fields = ["id", "user", "content", "last_viewed_at"]