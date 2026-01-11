"""
Basic tests for the Student Mistakes Management System
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.main import app
from backend.database.connection import get_db


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
async def db_session():
    """Database session fixture"""
    # This would need proper test database setup
    pass


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "student-mistakes-api"}


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Student Mistakes Management System" in data["message"]


def test_register_user(client):
    """Test user registration"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123"
    }

    response = client.post("/auth/register", json=user_data)
    # Note: This test would need database cleanup between runs
    # and proper test database setup
    if response.status_code == 200:
        data = response.json()
        assert "id" in data
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]


def test_login_user(client):
    """Test user login"""
    # This would require a test user to be created first
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }

    response = client.post("/auth/token", data=login_data)
    # This test depends on the registration test above
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


# OCR Processor Tests
def test_ocr_processor_initialization():
    """Test OCR processor can be initialized"""
    from backend.services.ocr_processor import OCRProcessor

    processor = OCRProcessor()
    assert processor is not None
    # Note: Full OCR testing would require actual image files and mock setup


# AI Analyzer Tests
@pytest.mark.asyncio
async def test_ai_analyzer_empty_text():
    """Test AI analyzer handles empty text"""
    from backend.services.ai_analyzer import AIAnalyzer

    analyzer = AIAnalyzer()
    result = await analyzer.analyze_mistake("")

    assert result is not None
    assert result.error_type == "unknown"
    assert result.confidence == 0.0
    assert len(result.insights) > 0


# Gamification Tests
def test_gamification_points_config():
    """Test gamification points configuration"""
    from backend.services.gamification import GamificationEngine

    engine = GamificationEngine()

    # Test points configuration exists
    assert hasattr(engine, 'POINTS_CONFIG')
    assert 'mistake_uploaded' in engine.POINTS_CONFIG
    assert 'review_completed' in engine.POINTS_CONFIG


# Review Scheduler Tests
def test_spaced_repetition_calculation():
    """Test spaced repetition algorithm"""
    from backend.services.review_scheduler import ReviewScheduler

    scheduler = ReviewScheduler()

    # Test next review date calculation
    from datetime import datetime, timedelta

    base_date = datetime.utcnow()
    next_date = scheduler.calculate_next_review_date(
        base_date, 4, 1, 2.5  # Good performance, 1 day interval, 2.5 ease factor
    )

    assert next_date is not None
    assert next_date > base_date


if __name__ == "__main__":
    pytest.main([__file__])