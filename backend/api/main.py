"""
Student Mistakes Management System - FastAPI Backend
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import uvicorn

from api.routes import auth, mistakes, reviews, achievements
from config.settings import settings
from database.connection import init_db
from services.celery_app import celery_app

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info("Starting Student Mistakes Management System")
    await init_db()
    logger.info("Database initialized")

    # Initialize Celery
    celery_app.conf.update(
        broker_url=settings.redis.url,
        result_backend=settings.redis.url,
    )
    logger.info("Celery initialized")

    yield

    # Shutdown
    logger.info("Shutting down Student Mistakes Management System")

# Create FastAPI application
app = FastAPI(
    title="Student Mistakes Management System API",
    description="AI-powered system for tracking and improving student mistakes",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", exc_info=exc, path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(mistakes.router, prefix="/mistakes", tags=["Mistakes"])
app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
app.include_router(achievements.router, prefix="/achievements", tags=["Achievements"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "student-mistakes-api"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Student Mistakes Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.debug,
        log_level="info"
    )