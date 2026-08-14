import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "content_change_tracking.settings")

app = Celery("content_change_tracking")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


app.conf.beat_schedule = {
    "delete-inactive-content-every-night": {
        "task": "content.tasks.delete_content_older_than_one_year",
        "schedule": crontab(minute=0, hour=0),
    }
}
