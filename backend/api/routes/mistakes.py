"""
Mistakes routes - handle mistake upload, analysis, and retrieval
"""

import uuid
from pathlib import Path
from typing import List, Optional
import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from database.connection import get_db
from models.mistake import Mistake
from services.ai_analyzer import AIAnalyzer
from services.gamification import GamificationEngine

router = APIRouter()

# Initialize services
ai_analyzer = AIAnalyzer()
gamification = GamificationEngine()


class MistakeAnalysis(BaseModel):
    error_type: str
    confidence: float
    insights: List[str]
    questions_found: Optional[List[str]] = None
    correct_answers: Optional[List[str]] = None
    root_cause: Optional[str] = None
    similar_questions: Optional[List[str]] = None


class MistakeResponse(BaseModel):
    id: str
    image_path: str
    subject: Optional[str] = None
    error_type: Optional[str] = None
    confidence: Optional[float] = None
    ai_insights: Optional[dict] = None
    created_at: str


class MistakeUploadResponse(BaseModel):
    mistake: MistakeResponse
    analysis: MistakeAnalysis
    points_awarded: int


@router.post("/upload", response_model=MistakeUploadResponse)
async def upload_mistake(
    file: UploadFile = File(...),
    subject: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Upload and analyze a mistake image"""

    # Validate file
    if not file.filename.lower().endswith(tuple(settings.upload.allowed_extensions)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {settings.upload.allowed_extensions}"
        )

    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.upload.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.upload.max_file_size} bytes"
        )

    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = Path(settings.upload.upload_dir) / unique_filename

    # Ensure upload directory exists
    Path(settings.upload.upload_dir).mkdir(exist_ok=True)

    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_content)

    try:
        # Direct AI Analysis (no OCR step) - temporarily disabled for testing
        # analysis = await ai_analyzer.analyze_image(str(file_path))
        # Mock analysis for testing
        analysis = MistakeAnalysis(
            error_type="test",
            confidence=0.8,
            insights=["Test analysis - AI temporarily disabled"],
            questions_found=["Sample question"],
            correct_answers=["Sample answer"],
            root_cause="Test analysis"
        )

        # Create mistake record
        mistake = Mistake(
            id="test-id-123",
            image_path=str(file_path),
            subject=subject,
            error_type=analysis.error_type,
            confidence=analysis.confidence,
            ai_insights={
                "insights": analysis.insights,
                "questions_found": analysis.questions_found,
                "correct_answers": analysis.correct_answers,
                "root_cause": analysis.root_cause,
                "similar_questions": analysis.similar_questions
            }
        )

        # db.add(mistake)
        # await db.commit()
        # await db.refresh(mistake)

        # Award points for mistake upload
        # points_awarded = await gamification.award_points(
        #     db, "anonymous", "mistake_uploaded"
        # )
        points_awarded = 10  # Mock points for testing

        return MistakeUploadResponse(
            mistake=MistakeResponse(
                id=mistake.id,
                image_path=mistake.image_path,
                subject=mistake.subject,
                error_type=mistake.error_type,
                confidence=mistake.confidence,
                ai_insights=mistake.ai_insights,
                created_at="2024-01-01T00:00:00"
            ),
            analysis=analysis,
            points_awarded=points_awarded
        )

    except Exception as e:
        # Clean up file if processing failed
        if file_path.exists():
            file_path.unlink()
        # Log the full error for debugging
        import structlog
        logger = structlog.get_logger()
        logger.error("Upload processing failed", error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process image: {str(e)}"
        )


@router.get("/", response_model=List[MistakeResponse])
async def get_user_mistakes(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get all mistakes"""
    result = await db.execute(
        db.query(Mistake)
        .order_by(Mistake.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    mistakes = result.scalars().all()

    return [
        MistakeResponse(
            id=str(m.id),
            image_path=m.image_path,
            subject=m.subject,
            error_type=m.error_type,
            confidence=float(m.confidence) if m.confidence else None,
            ai_insights=m.ai_insights,
            created_at=m.created_at.isoformat()
        )
        for m in mistakes
    ]


@router.get("/{mistake_id}", response_model=MistakeResponse)
async def get_mistake(
    mistake_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get specific mistake"""
    result = await db.execute(
        db.query(Mistake)
        .filter(Mistake.id == mistake_id)
    )
    mistake = result.scalars().first()

    if not mistake:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mistake not found"
        )

    return MistakeResponse(
        id=str(mistake.id),
        image_path=mistake.image_path,
        subject=mistake.subject,
        error_type=mistake.error_type,
        confidence=float(mistake.confidence) if mistake.confidence else None,
        ai_insights=mistake.ai_insights,
        created_at=mistake.created_at.isoformat()
    )


@router.delete("/{mistake_id}")
async def delete_mistake(
    mistake_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a mistake"""
    result = await db.execute(
        db.query(Mistake)
        .filter(Mistake.id == mistake_id)
    )
    mistake = result.scalars().first()

    if not mistake:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mistake not found"
        )

    # Delete the image file
    if Path(mistake.image_path).exists():
        Path(mistake.image_path).unlink()

    # Delete from database
    await db.delete(mistake)
    await db.commit()

    return {"message": "Mistake deleted successfully"}


@router.get("/{mistake_id}/image")
async def get_mistake_image(
    mistake_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get mistake image file"""
    result = await db.execute(
        db.query(Mistake)
        .filter(Mistake.id == mistake_id)
    )
    mistake = result.scalars().first()

    if not mistake:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mistake not found"
        )

    if not Path(mistake.image_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found"
        )

    return FileResponse(mistake.image_path)
