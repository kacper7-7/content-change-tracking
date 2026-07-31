from celery import shared_task


@shared_task
def create_notification_for_followers_content()