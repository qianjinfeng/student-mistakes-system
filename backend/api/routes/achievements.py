"""
Achievements routes - handle user achievements and progress
"""

from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.routes.auth import get_current_user
from database.connection import get_db
from models.user import User
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's unlocked achievements"""
    achievements = db.query(Achievement).filter(
        Achievement.user_id == current_user.id
    ).order_by(Achievement.unlocked_at.desc()).all()

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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's comprehensive statistics"""
    stats = gamification.get_user_stats(db, str(current_user.id))
    return UserStatsResponse(**stats)


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