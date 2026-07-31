from datetime import timedelta

from django.utils import timezone
from celery import shared_task
from content.models import Content


@shared_task
def delete_content_older_than_one_year():
    one_year_ago = timezone.now() - timedelta(days=365)

    deleted_count, _ = Content.objects.filter(updated_at__lt=one_year_ago).delete()

    return f"Deleted non-active contents (older than 1 year)"
