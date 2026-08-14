from django.contrib import admin
from django.contrib.admin import ModelAdmin

from content.models import Content, Follow


@admin.register(Content)
class ContentAdmin(ModelAdmin):
    list_display = ("id", "title", "created_at", "updated_at")
    list_display_links = ("id", "title")
    search_fields = ("title", "body")
    list_filter = ("created_at", "updated_at")
    read_only_fields = ("created_at", "updated_at")


@admin.register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = ("id", "user", "content", "last_viewed_at")
    search_fields = ("user__email", "content__title")
    list_filter = ("last_viewed_at",)
    list_select_related = ("user", "content")
    read_only_fields = ("last_viewed_at",)
    raw_id_fields = ("user", "content")
