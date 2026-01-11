"""
Celery tasks for background processing
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import structlog
from celery import Celery

from config.settings import settings
from database.connection import init_db, close_db

logger = structlog.get_logger()

# Initialize Celery
celery_app = Celery(
    "student_mistakes",
    broker=settings.redis.url,
    backend=settings.redis.url
)

# Configure Celery
celery_app.conf.update(
    timezone="UTC",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    enable_utc=True,
)


@celery_app.task(name="send_daily_reminder")
def send_daily_reminder():
    """Send daily review reminders to users"""
    logger.info("Starting daily reminder task")

    async def _send_reminders():
        try:
            await init_db()

            # This would integrate with email/SMS service
            # For now, just log the reminder
            logger.info("Daily reminders sent to users")

        except Exception as e:
            logger.error("Failed to send daily reminders", error=str(e))
        finally:
            await close_db()

    # Run async function in sync context
    asyncio.run(_send_reminders())


@celery_app.task(name="schedule_initial_reviews")
def schedule_initial_reviews(user_id: str, mistake_id: str):
    """Schedule initial review for a new mistake"""
    logger.info("Scheduling initial review", user_id=user_id, mistake_id=mistake_id)

    async def _schedule_reviews():
        try:
            await init_db()

            from database.connection import AsyncSessionLocal
            from models.scheduled_review import ScheduledReview
            from services.review_scheduler import ReviewScheduler

            review_scheduler = ReviewScheduler()

            async with AsyncSessionLocal() as db:
                # Schedule first review (tomorrow)
                first_review_date = datetime.utcnow() + timedelta(days=1)

                scheduled_review = ScheduledReview(
                    mistake_id=mistake_id,
                    user_id=user_id,
                    scheduled_date=first_review_date,
                    interval_days=settings.spaced_repetition.initial_interval,
                    ease_factor=settings.spaced_repetition.initial_ease_factor,
                    repetitions=0
                )

                db.add(scheduled_review)
                await db.commit()

                logger.info(
                    "Initial review scheduled",
                    user_id=user_id,
                    mistake_id=mistake_id,
                    scheduled_date=first_review_date.isoformat()
                )

        except Exception as e:
            logger.error("Failed to schedule initial review", error=str(e))
        finally:
            await close_db()

    asyncio.run(_schedule_reviews())


@celery_app.task(name="cleanup_old_uploads")
def cleanup_old_uploads():
    """Clean up old uploaded files"""
    logger.info("Starting cleanup of old uploads")

    try:
        upload_dir = Path(settings.upload.upload_dir)
        if not upload_dir.exists():
            return

        # Keep files for 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        cleaned_count = 0
        for file_path in upload_dir.glob("*"):
            if file_path.is_file():
                # Check if file is older than cutoff
                stat = file_path.stat()
                file_date = datetime.fromtimestamp(stat.st_mtime)

                if file_date < cutoff_date:
                    file_path.unlink()
                    cleaned_count += 1

        logger.info("Cleanup completed", files_removed=cleaned_count)

    except Exception as e:
        logger.error("Failed to cleanup old uploads", error=str(e))


@celery_app.task(name="update_user_streaks")
def update_user_streaks():
    """Update user streaks and check for achievements"""
    logger.info("Starting user streak updates")

    async def _update_streaks():
        try:
            await init_db()

            from database.connection import AsyncSessionLocal
            from models.user import User
            from services.gamification import GamificationEngine

            gamification = GamificationEngine()

            async with AsyncSessionLocal() as db:
                # Get all active users
                result = await db.execute(db.query(User).filter(User.is_active == True))
                users = result.scalars().all()

                for user in users:
                    try:
                        # Update streak
                        await gamification.update_streak(db, str(user.id))

                        # Check achievements
                        new_achievements = await gamification.check_achievements(db, str(user.id))

                        if new_achievements:
                            logger.info(
                                "New achievements unlocked",
                                user_id=str(user.id),
                                achievements=len(new_achievements)
                            )

                    except Exception as e:
                        logger.error(
                            "Failed to update streak for user",
                            user_id=str(user.id),
                            error=str(e)
                        )

                await db.commit()

        except Exception as e:
            logger.error("Failed to update user streaks", error=str(e))
        finally:
            await close_db()

    asyncio.run(_update_streaks())


# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    'daily-reminder': {
        'task': 'services.tasks.send_daily_reminder',
        'schedule': 86400.0,  # 24 hours
    },
    'cleanup-uploads': {
        'task': 'services.tasks.cleanup_old_uploads',
        'schedule': 604800.0,  # 7 days
    },
    'update-streaks': {
        'task': 'services.tasks.update_user_streaks',
        'schedule': 86400.0,  # 24 hours
    },
}