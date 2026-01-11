"""
Celery application configuration
"""

from celery import Celery
from config.settings import settings

celery_app = Celery(
    "student_mistakes",
    broker=settings.redis.url,
    backend=settings.redis.url,
    include=["services.tasks"]
)

# Celery configuration
celery_app.conf.update(
    timezone="UTC",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    enable_utc=True,
)

if __name__ == "__main__":
    celery_app.start()