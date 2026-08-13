from django.conf import settings
from django.db import models
from django.utils import timezone


class Content(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="contents", on_delete=models.CASCADE
    )
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_count = models.IntegerField(default=0)
    version = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Follow(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="follows"
    )

    content = models.ForeignKey(
        Content, on_delete=models.CASCADE, related_name="followers"
    )

    last_viewed_at = models.DateTimeField(default=timezone.now, db_index=True)
    last_seen_version = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content"], name="user_unique_content_follow"
            )
        ]

    def __str__(self):
        return f"{self.user} follows {self.content}"


class ContentEditHistory(models.Model):
    content = models.ForeignKey(
        "Content", on_delete=models.CASCADE, related_name="edit_history"
    )

    edited_at = models.DateTimeField(auto_now_add=True)
