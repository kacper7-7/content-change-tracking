import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "content_change_tracking.settings")

app = Celery("content_change_trackin")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()