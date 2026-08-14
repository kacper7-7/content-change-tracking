from rest_framework import serializers
from content.models import Content, Follow, ContentEditHistory


class ContentEditHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentEditHistory
        fields = ["content", "edited_at"]


class ContentListSerializer(serializers.ModelSerializer):
    is_hot = serializers.BooleanField(read_only=True)
    is_followed_by_me = serializers.BooleanField(read_only=True)
    last_edit_date = serializers.DateTimeField(read_only=True)
    followers_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Content
        fields = [
            "id",
            "title",
            "body",
            "author",
            "edited_count",
            "is_followed_by_me",
            "last_edit_date",
            "is_hot",
            "followers_count",
        ]

        read_only_fields = [
            "author",
            "created_at",
            "updated_at",
            "edited_count",
            "edit_history",
            "is_followed_by_me",
            "followers_count",
            "is_hot",
            "recent_edits_count",
            "last_edit_date",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get("request")

        if request and request.user and not request.user.is_staff:

            if not getattr(instance, "is_followed_by_me", False):
                return {
                    "id": data.get("id"),
                    "title": data.get("title"),
                    "created_at": data.get("created_at"),
                    "message": "To see more info, follow this content!",
                }
        return data


class ContentDetailSerializer(ContentListSerializer):
    edit_history = ContentEditHistorySerializer(many=True, read_only=True)
    followers_count = serializers.IntegerField(read_only=True)
    recent_edits_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Content
        fields = [
            "id",
            "title",
            "body",
            "author",
            "created_at",
            "updated_at",
            "edited_count",
            "edit_history",
            "is_followed_by_me",
            "followers_count",
            "is_hot",
            "recent_edits_count",
            "last_edit_date",
        ]

        read_only_fields = [
            "author",
            "created_at",
            "updated_at",
            "edited_count",
            "edit_history",
            "is_followed_by_me",
            "followers_count",
            "is_hot",
            "recent_edits_count",
            "last_edit_date",
        ]


class ContentAdminListSerializer(ContentListSerializer):
    followers = serializers.SlugRelatedField(
        slug_field="user.pk", many=True, read_only=True
    )

    class Meta:
        model = Content
        fields = [
            "id",
            "title",
            "body",
            "author",
            "edited_count",
            "is_followed_by_me",
            "last_edit_date",
            "is_hot",
            "followers",
        ]
        read_only_fields = ["edited_count"]


class ContentAdminDetailSerializer(ContentDetailSerializer):
    followers = serializers.SlugRelatedField(
        slug_field="user.pk", many=True, read_only=True
    )

    class Meta:
        model = Content
        fields = [
            "id",
            "title",
            "body",
            "author",
            "created_at",
            "updated_at",
            "edited_count",
            "edit_history",
            "is_followed_by_me",
            "followers_count",
            "is_hot",
            "recent_edits_count",
            "last_edit_date",
            "followers",
        ]


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="email", read_only=True)
    content = serializers.SlugRelatedField(slug_field="title", read_only=True)
    has_new_changes = serializers.BooleanField(read_only=True)
    missed_edits_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Follow
        fields = [
            "id",
            "user",
            "content",
            "last_viewed_at",
            "has_new_changes",
            "missed_edits_count",
        ]


class FollowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ["content"]
        read_only_fields = ["id", "user", "last_viewed_at"]
