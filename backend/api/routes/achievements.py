"""
Achievements routes - handle user achievements and progress
"""

from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import get_db
from models.achievement import Achievement
from services.gamification import GamificationEngine

router = APIRouter()

gamification = GamificationEngine()


class AchievementResponse(BaseModel):
    id: str
    achievement_type: str
    achievement_name: str
    description: str
    points_awarded: int
    unlocked_at: str


class UserStatsResponse(BaseModel):
    current_streak: int
    longest_streak: int
    total_reviews: int
    total_points: int
    achievements_count: int
    last_review_date: Optional[str] = None


@router.get("/", response_model=List[AchievementResponse])
def get_user_achievements(
    db: Session = Depends(get_db)
):
    """Get all unlocked achievements"""
    achievements = db.query(Achievement).order_by(Achievement.unlocked_at.desc()).all()

    return [
        AchievementResponse(
            id=str(a.id),
            achievement_type=a.achievement_type,
            achievement_name=a.achievement_name,
            description=a.description or "",
            points_awarded=a.points_awarded,
            unlocked_at=a.unlocked_at.isoformat()
        )
        for a in achievements
    ]


@router.get("/stats", response_model=UserStatsResponse)
def get_user_stats(
    db: Session = Depends(get_db)
):
    """Get system-wide statistics"""
    # For anonymous system, return default stats
    return UserStatsResponse(
        current_streak=0,
        longest_streak=0,
        total_reviews=0,
        total_points=0,
        achievements_count=0,
        last_review_date=None
    )


@router.get("/available")
async def get_available_achievements():
    """Get all possible achievements that can be unlocked"""
    from config.settings import settings

    achievements_config = settings.gamification.achievements

    return {
        "streak_7_days": {
            "type": "streak",
            "name": achievements_config.streak_7_days.name,
            "description": achievements_config.streak_7_days.description,
            "points": achievements_config.streak_7_days.points
        },
        "streak_30_days": {
            "type": "streak",
            "name": achievements_config.streak_30_days.name,
            "description": achievements_config.streak_30_days.description,
            "points": achievements_config.streak_30_days.points
        },
        "total_reviews_100": {
            "type": "total_reviews",
            "name": achievements_config.total_reviews_100.name,
            "description": achievements_config.total_reviews_100.description,
            "points": achievements_config.total_reviews_100.points
        },
        "accuracy_90": {
            "type": "accuracy",
            "name": achievements_config.accuracy_90.name,
            "description": achievements_config.accuracy_90.description,
            "points": achievements_config.accuracy_90.points
        }
    }
