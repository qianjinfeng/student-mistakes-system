"""
Gamification Engine
"""

from datetime import date
from typing import Dict, List
from sqlalchemy import and_, func

from models.achievement import Achievement
from models.user_progress import UserProgress
from models.review_history import ReviewHistory


class GamificationEngine:
    """Manages user progress, achievements, and point system"""

    POINTS_CONFIG = {
        "mistake_uploaded": 10,
        "review_completed": 5,
        "correct_answer": 15,
    }

    def award_points(self, db, user_id: str, action: str, multiplier: int = 1) -> int:
        """Award points for user action"""
        base_points = self.POINTS_CONFIG.get(action, 0)
        total_points = base_points * multiplier

        if total_points > 0:
            progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()

            if not progress:
                progress = UserProgress(user_id=user_id)
                db.add(progress)

            progress.total_points += total_points
            db.commit()

        return total_points

    def update_streak(self, db, user_id: str):
        """Update user review streak"""
        today = date.today()

        recent_reviews = db.query(ReviewHistory).filter(
            and_(
                ReviewHistory.user_id == user_id,
                func.date(ReviewHistory.review_date) >= today
            )
        ).order_by(ReviewHistory.review_date.desc()).all()

        progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()

        if not progress:
            progress = UserProgress(user_id=user_id)
            db.add(progress)

        if recent_reviews:
            progress.last_review_date = today
            progress.current_streak = min(progress.current_streak + 1, 365)
            progress.longest_streak = max(progress.longest_streak, progress.current_streak)
        else:
            progress.current_streak = 0

        db.commit()

    def check_achievements(self, db, user_id: str) -> List[Dict]:
        """Check and award achievements"""
        new_achievements = []
        progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()

        if not progress:
            return new_achievements

        if progress.current_streak >= 7:
            self._award_achievement(db, user_id, "streak_7_days")
            new_achievements.append({"type": "streak", "name": "连续学习7天", "points": 50})

        if progress.current_streak >= 30:
            self._award_achievement(db, user_id, "streak_30_days")
            new_achievements.append({"type": "streak", "name": "学习达人", "points": 200})

        if progress.total_reviews >= 100:
            self._award_achievement(db, user_id, "total_reviews_100")
            new_achievements.append({"type": "total_reviews", "name": "百题达人", "points": 150})

        return new_achievements

    def _award_achievement(self, db, user_id: str, achievement_type: str):
        """Award achievement if not already earned"""
        existing = db.query(Achievement).filter(
            and_(Achievement.user_id == user_id, Achievement.achievement_type == achievement_type)
        ).first()

        if not existing:
            achievement = Achievement(
                user_id=user_id,
                achievement_type=achievement_type,
                achievement_name=f"Achievement {achievement_type}",
                description=f"Earned {achievement_type} achievement",
                points_awarded=50
            )
            db.add(achievement)
            db.commit()

    def get_user_stats(self, db, user_id: str) -> Dict:
        """Get comprehensive user statistics"""
        progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()

        if not progress:
            return {
                "current_streak": 0,
                "longest_streak": 0,
                "total_reviews": 0,
                "total_points": 0,
                "achievements_count": 0
            }

        achievements_count = db.query(func.count(Achievement.id)).filter(Achievement.user_id == user_id).scalar()

        return {
            "current_streak": progress.current_streak,
            "longest_streak": progress.longest_streak,
            "total_reviews": progress.total_reviews,
            "total_points": progress.total_points,
            "achievements_count": achievements_count or 0,
            "last_review_date": progress.last_review_date.isoformat() if progress.last_review_date else None
        }