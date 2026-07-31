from django.contrib import admin

from notification.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "recipient", "content", "created_at"]
    search_fields = ["recipient", "content"]
    list_filter = ["created_at"]
