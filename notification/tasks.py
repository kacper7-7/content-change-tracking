from celery import shared_task
from django.db.models import Model

from content.models import Content
from notification.models import Notification


@shared_task
def create_notification_for_followers_content(content_id):

    try:
        content = Content.objects.prefetch_related("followers__user").get(id=content_id)
    except Content.DoesNotExist:
        return

    notifications_to_create = [
        Notification(
            recipient=follower.user,
            content=content,
            message=f"Content {content.id} is updated!"
        ) for follower in content.followers.all()
    ]

    Notification.objects.bulk_create(notifications_to_create)