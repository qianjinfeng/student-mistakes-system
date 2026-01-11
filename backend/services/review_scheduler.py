"""
Review Scheduler - Spaced Repetition Algorithm
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import structlog

from config.settings import settings

logger = structlog.get_logger()


class ReviewScheduler:
    """Spaced repetition scheduler using SM-2 algorithm"""

    def calculate_next_review_date(
        self,
        last_review_date: datetime,
        performance_rating: int,
        current_interval: int,
        ease_factor: float
    ) -> Optional[datetime]:
        """
        Calculate next review date using spaced repetition

        Args:
            last_review_date: When the item was last reviewed
            performance_rating: User's performance rating (0-5)
            current_interval: Current interval in days
            ease_factor: Current ease factor

        Returns:
            Next review date or None if item should be retired
        """
        if performance_rating < 3:
            # Failed - reset to minimum interval
            next_interval = settings.spaced_repetition.initial_interval
        else:
            # Success - apply spaced repetition formula
            next_interval = current_interval * ease_factor

            # Apply performance multiplier
            if performance_rating == 3:  # Good
                next_interval *= settings.spaced_repetition.good_multiplier
            elif performance_rating == 4:  # Easy
                next_interval *= settings.spaced_repetition.easy_multiplier

        # Cap maximum interval (optional)
        next_interval = min(next_interval, 365)  # Max 1 year

        next_date = last_review_date + timedelta(days=int(next_interval))
        return next_date

    def update_spaced_repetition(
        self,
        current_interval: int,
        ease_factor: float,
        repetitions: int,
        performance_rating: int
    ) -> Tuple[int, float, int]:
        """
        Update spaced repetition parameters based on performance

        Args:
            current_interval: Current interval in days
            ease_factor: Current ease factor
            repetitions: Number of successful repetitions
            performance_rating: Performance rating (0-5)

        Returns:
            Tuple of (new_interval, new_ease_factor, new_repetitions)
        """
        # Update ease factor based on performance
        if performance_rating >= 3:
            # Success - increase ease factor
            new_ease_factor = ease_factor + (0.1 - (5 - performance_rating) * (0.08 + (5 - performance_rating) * 0.02))
            new_ease_factor = max(new_ease_factor, settings.spaced_repetition.min_ease_factor)
            new_repetitions = repetitions + 1
        else:
            # Failure - decrease ease factor
            new_ease_factor = max(ease_factor - 0.2, settings.spaced_repetition.min_ease_factor)
            new_repetitions = 0

        # Cap ease factor
        new_ease_factor = min(new_ease_factor, settings.spaced_repetition.max_ease_factor)

        # Calculate new interval
        if new_repetitions == 1:
            new_interval = settings.spaced_repetition.initial_interval
        elif new_repetitions == 2:
            new_interval = 6  # 6 days for second review
        else:
            new_interval = current_interval * new_ease_factor

        return int(new_interval), new_ease_factor, new_repetitions

    def should_review_today(
        self,
        scheduled_date: datetime,
        current_streak: int = 0
    ) -> bool:
        """
        Determine if an item should be reviewed today

        Args:
            scheduled_date: Scheduled review date
            current_streak: User's current streak (for bonus reviews)

        Returns:
            True if item should be reviewed today
        """
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        scheduled_today = scheduled_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Always review if scheduled for today
        if scheduled_today <= today:
            return True

        # Bonus reviews during streaks (every 7 days during long streaks)
        if current_streak >= 30 and (current_streak % 7) == 0:
            days_diff = (scheduled_today - today).days
            return days_diff <= 1  # Review early during streaks

        return False

    def get_optimal_review_schedule(
        self,
        total_items: int,
        user_streak: int = 0
    ) -> dict:
        """
        Get optimal daily review schedule

        Args:
            total_items: Total items to review
            user_streak: User's current streak

        Returns:
            Schedule configuration
        """
        # Base daily limit
        base_limit = 20

        # Increase limit for users with good streaks
        if user_streak >= 30:
            base_limit = 50
        elif user_streak >= 7:
            base_limit = 35

        return {
            "daily_limit": min(base_limit, total_items),
            "priority_new_items": True,
            "allow_overdue_reviews": True
        }