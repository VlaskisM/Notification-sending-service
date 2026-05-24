import logging

from celery import Celery
from app.config.config_celery import settings as celery_settings

celery_app = Celery(
    "notification",
    broker=celery_settings.broker_url,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
)