"""
Reviews routes - handle spaced repetition and review scheduling
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_

from database.connection import get_db
from models.scheduled_review import ScheduledReview
from models.review_history import ReviewHistory
from services.review_scheduler import ReviewScheduler
from services.gamification import GamificationEngine

router = APIRouter()

# Initialize services
review_scheduler = ReviewScheduler()
gamification = GamificationEngine()


class ReviewSession(BaseModel):
    mistake_id: str
    performance_rating: int  # 0-5 scale
    time_spent_seconds: Optional[int] = None
    notes: Optional[str] = None


class ReviewResponse(BaseModel):
    id: str
    mistake_id: str
    scheduled_date: str
    interval_days: int
    ease_factor: float
    repetitions: int
    is_completed: bool
    next_review_date: Optional[str] = None


class DailyReviewPlan(BaseModel):
    date: str
    reviews: List[ReviewResponse]
    total_count: int


@router.get("/daily-plan", response_model=DailyReviewPlan)
async def get_daily_review_plan(
    date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get scheduled reviews for today or specified date"""
    if date:
        try:
            target_date = datetime.fromisoformat(date).date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format (YYYY-MM-DD)"
            )
    else:
        target_date = datetime.utcnow().date()

    # Get scheduled reviews for the date
    result = await db.execute(
        db.query(ScheduledReview)
        .filter(
            and_(
                ScheduledReview.scheduled_date >= target_date,
                ScheduledReview.scheduled_date < target_date.replace(day=target_date.day + 1),
                ScheduledReview.is_completed == False
            )
        )
        .order_by(ScheduledReview.scheduled_date)
    )
    scheduled_reviews = result.scalars().all()

    reviews = []
    for sr in scheduled_reviews:
        # Calculate next review date using spaced repetition
        next_date = review_scheduler.calculate_next_review_date(
            sr.scheduled_date,
            sr.performance_rating or 3,  # Default to good performance
            sr.interval_days,
            sr.ease_factor
        )

        reviews.append(ReviewResponse(
            id=str(sr.id),
            mistake_id=str(sr.mistake_id),
            scheduled_date=sr.scheduled_date.isoformat(),
            interval_days=sr.interval_days,
            ease_factor=float(sr.ease_factor),
            repetitions=sr.repetitions,
            is_completed=sr.is_completed,
            next_review_date=next_date.isoformat() if next_date else None
        ))

    return DailyReviewPlan(
        date=target_date.isoformat(),
        reviews=reviews,
        total_count=len(reviews)
    )


@router.post("/complete")
async def complete_reviews(
    review_sessions: List[ReviewSession],
    db: AsyncSession = Depends(get_db)
):
    """Complete review sessions and update spaced repetition schedule"""
    completed_reviews = []

    for session in review_sessions:
        # Find the scheduled review
        result = await db.execute(
            db.query(ScheduledReview)
            .filter(
                and_(
                    ScheduledReview.mistake_id == session.mistake_id,
                    ScheduledReview.is_completed == False
                )
            )
        )
        scheduled_review = result.scalars().first()

        if not scheduled_review:
            continue

        # Update spaced repetition algorithm
        new_interval, new_ease_factor, new_repetitions = review_scheduler.update_spaced_repetition(
            current_interval=scheduled_review.interval_days,
            ease_factor=float(scheduled_review.ease_factor),
            repetitions=scheduled_review.repetitions,
            performance_rating=session.performance_rating
        )

        # Calculate next review date
        next_review_date = review_scheduler.calculate_next_review_date(
            datetime.utcnow(),
            session.performance_rating,
            new_interval,
            new_ease_factor
        )

        # Mark current review as completed
        scheduled_review.is_completed = True
        scheduled_review.updated_at = datetime.utcnow()

        # Create new scheduled review if needed
        if next_review_date:
            new_scheduled_review = ScheduledReview(
                mistake_id=scheduled_review.mistake_id,
                scheduled_date=next_review_date,
                interval_days=new_interval,
                ease_factor=new_ease_factor,
                repetitions=new_repetitions
            )
            db.add(new_scheduled_review)

        # Record review history
        review_history = ReviewHistory(
            mistake_id=scheduled_review.mistake_id,
            performance_rating=session.performance_rating,
            time_spent_seconds=session.time_spent_seconds,
            notes=session.notes
        )
        db.add(review_history)

        # Award points for review completion
        points_awarded = await gamification.award_points(
            db, "anonymous", "review_completed"
        )

        # Update streak
        await gamification.update_streak(db, "anonymous")

        # Check for achievements
        new_achievements = await gamification.check_achievements(db, "anonymous")

        completed_reviews.append({
            "mistake_id": session.mistake_id,
            "points_awarded": points_awarded,
            "new_achievements": new_achievements,
            "next_review_date": next_review_date.isoformat() if next_review_date else None
        })

    await db.commit()

    return {
        "completed_reviews": completed_reviews,
        "total_points_awarded": sum(r["points_awarded"] for r in completed_reviews)
    }


@router.get("/history", response_model=List[dict])
async def get_review_history(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get all review history"""
    result = await db.execute(
        db.query(ReviewHistory)
        .order_by(ReviewHistory.review_date.desc())
        .offset(skip)
        .limit(limit)
    )
    reviews = result.scalars().all()

    return [
        {
            "id": str(r.id),
            "mistake_id": str(r.mistake_id),
            "review_date": r.review_date.isoformat(),
            "performance_rating": r.performance_rating,
            "time_spent_seconds": r.time_spent_seconds,
            "notes": r.notes
        }
        for r in reviews
    ]
