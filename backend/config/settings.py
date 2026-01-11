"""
Configuration settings for the Student Mistakes Management System
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic.types import SecretStr


class DatabaseSettings(BaseSettings):
    """Database configuration"""
    url: str = Field(default="postgresql://postgres:postgres@localhost:5432/student_mistakes")

    class Config:
        env_prefix = "DATABASE_"


class RedisSettings(BaseSettings):
    """Redis configuration"""
    url: str = Field(default="redis://localhost:6379/0")
    db: int = Field(default=0)

    class Config:
        env_prefix = "REDIS_"


class AISettings(BaseSettings):
    """AI model configuration"""
    qwen_api_key: Optional[SecretStr] = Field(default=None, env="QWEN_API_KEY")
    qwen_base_url: str = Field(default="https://dashscope.aliyuncs.com/api/v1", env="QWEN_BASE_URL")
    qwen_model: str = Field(default="qwen-vl-chat")
    qwen_temperature: float = Field(default=0.7)
    qwen_max_tokens: int = Field(default=1000)
    local_models_path: str = Field(default="./models")


class OCRSettings(BaseSettings):
    """OCR configuration"""
    use_gpu: bool = Field(default=False)
    lang: str = Field(default="ch")
    det_db_thresh: float = Field(default=0.3)
    det_db_box_thresh: float = Field(default=0.6)
    det_db_unclip_ratio: float = Field(default=1.5)


class SecuritySettings(BaseSettings):
    """Security configuration"""
    secret_key: SecretStr = Field(default="your-secret-key-here", env="SECRET_KEY")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)


class UploadSettings(BaseSettings):
    """File upload configuration"""
    max_file_size: int = Field(default=5242880)  # 5MB
    allowed_extensions: List[str] = Field(default=[".png", ".jpg", ".jpeg"])
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")


class GamificationSettings(BaseSettings):
    """Gamification configuration"""
    class PointsSettings(BaseSettings):
        mistake_uploaded: int = Field(default=10)
        review_completed: int = Field(default=5)
        correct_answer: int = Field(default=15)

    class AchievementSettings(BaseSettings):
        streak_7_days: dict = Field(default_factory=lambda: {"name": "连续学习7天", "description": "连续7天完成复习任务", "points": 50})
        streak_30_days: dict = Field(default_factory=lambda: {"name": "学习达人", "description": "连续30天完成复习任务", "points": 200})
        total_reviews_100: dict = Field(default_factory=lambda: {"name": "百题达人", "description": "完成100次复习", "points": 150})
        accuracy_90: dict = Field(default_factory=lambda: {"name": "精准学习者", "description": "平均正确率达到90%", "points": 100})

    points: PointsSettings = PointsSettings()
    achievements: AchievementSettings = AchievementSettings()


class APISettings(BaseSettings):
    """API configuration"""
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=True, env="DEBUG")
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://127.0.0.1:3000"])


class Settings(BaseSettings):
    """Main application settings"""
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    ai: AISettings = AISettings()
    ocr: OCRSettings = OCRSettings()
    security: SecuritySettings = SecuritySettings()
    upload: UploadSettings = UploadSettings()
    gamification: GamificationSettings = GamificationSettings()
    api: APISettings = APISettings()

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()