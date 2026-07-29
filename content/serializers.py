from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from rest_framework import serializers
from content.models import Content, Follow, ContentEditHistory


class ContentEditHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentEditHistory
        fields = ["content", "edited_at"]

class ContentSerializer(serializers.ModelSerializer):
    edit_history = ContentEditHistorySerializer(many=True, read_only=True)
    class Meta:
        model = Content
        fields = ["id", "title", "body", "created_at", "updated_at", "edited_count", "edit_history"]
        read_only_fields = ["edited_count"]


    def update(self, instance, validated_data):
        instance.updated_at = timezone.now()
        ContentEditHistory.objects.create(
            content=instance,
        )
        instance.edited_count += 1
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get("request")

        if request and request.user and not request.user.is_staff:
            is_following = any(follow.user.id == request.user.id for follow in instance.followers.all())

            if not is_following:
                return {
                    "id": data.get("id"),
                    "title": data.get("title"),
                    "created_at": data.get("created_at")
                }
        return data


class ContentAdminSerializer(ContentSerializer):
    followers = serializers.SlugRelatedField(slug_field="user.pk", many=True, read_only=True)

    class Meta:
        model = Content
        fields = ["id", "title", "body", "created_at", "updated_at", "followers",  "edited_count", "edit_history"]
        read_only_fields = ["edited_count"]

class ContentNotFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ["id", "title", "created_at"]

class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="email", read_only=True)
    content = serializers.SlugRelatedField(slug_field="title", read_only=True)
    has_new_changes = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Follow
        fields = ["id", "user", "content", "last_viewed_at", "has_new_changes"]


class FollowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ["content"]
        read_only_fields = ["id", "user", "last_viewed_at"]

