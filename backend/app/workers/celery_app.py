from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "ecom_agent",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.tasks.monitor_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "run-competitor-monitor-hourly": {
            "task": "app.workers.tasks.monitor_tasks.run_scheduled_monitors",
            "schedule": 3600.0,
        },
    },
)
