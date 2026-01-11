# AGENTS.md - Development Guide for AI-Powered Student Mistakes Management System

## 🚀 Build/Lint/Test Commands

### Development Environment Setup
```bash
# Start full stack development environment
docker-compose up -d

# Start all services including Celery worker
docker-compose up -d --scale celery=1

# Start only backend and database for API development
docker-compose up backend postgres redis

# View logs for specific service
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f celery

# Stop all services
docker-compose down

# Rebuild specific service after code changes
docker-compose up -d --build backend
```

### Frontend (React/TypeScript + Vite + Tailwind)
```bash
# Development
npm run dev                    # Start dev server (http://localhost:3000)
npm run build                  # Production build
npm run preview               # Preview production build

# Code Quality
npm run lint                  # ESLint check
npm run typecheck             # TypeScript type checking

# Testing
npm test                      # Run all Jest tests
npm test -- --watch           # Run tests in watch mode
npm test -- --coverage        # Run tests with coverage report
npm test -- --testNamePattern="UploadComponent"  # Run single test
npm test -- --testPathPattern="components"       # Run tests in directory
```

### Backend (FastAPI + Python)
```bash
# Development Server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Testing
pytest                        # Run all tests
pytest --cov=src             # Run with coverage
pytest --cov-report=html     # Generate HTML coverage report
pytest tests/test_ai_analyzer.py  # Run specific test file
pytest tests/test_ai_analyzer.py::test_classify_error  # Run single test
pytest tests/ -k "classification"  # Run tests matching pattern
pytest --tb=short            # Shorter traceback format

# Code Quality
ruff check .                  # Lint Python code
ruff format .                 # Format Python code
ruff check --fix .           # Auto-fix linting issues
isort .                       # Sort imports
mypy .                        # Type checking (if configured)
```

### AI/OCR Local Setup
```bash
# PaddleOCR Setup
pip install paddlepaddle-gpu  # GPU version (if CUDA available)
pip install paddlepaddle      # CPU version
pip install "paddleocr>=2.0.1"

# Download OCR models
python -c "from paddleocr import PaddleOCR; PaddleOCR(use_gpu=False, lang='ch')"

# Qwen Model Setup (Local)
pip install transformers torch
pip install modelscope         # For Qwen models

# Download Qwen-VL model
python -c "from modelscope import snapshot_download; snapshot_download('qwen/Qwen-VL-Chat', cache_dir='./models')"

# Run Qwen inference locally
python ai_analyzer.py --model local --model-path ./models/qwen-vl-chat
```

## 📏 Code Style Guidelines

### Python Guidelines
- **Mandatory type hints** for all function parameters and return values
- **Pydantic v2** models for all data structures and API responses
- Create custom exception classes for domain-specific errors
- Use async for all I/O operations (API calls, database queries, file operations)
- Enable mypy strict mode in `pyproject.toml`

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class MistakeAnalysis(BaseModel):
    error_type: str = Field(..., description="Type of error")
    confidence: float = Field(..., ge=0.0, le=1.0)
    insights: List[str] = Field(default_factory=list)

def process_image(image_path: str) -> MistakeAnalysis:
    try:
        ocr_result = ocr_processor.process(image_path)
        return ai_analyzer.classify(ocr_result)
    except OCRProcessingError as e:
        logger.error("OCR processing failed", image_path=image_path, error=str(e))
        raise
```

#### Import Organization
```python
# Standard library imports
import asyncio, json
from pathlib import Path
from typing import List, Optional

# Third-party imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import structlog

# Local imports
from .config import settings
from .models.user import User
from .services.ai_analyzer import AIAnalyzer
```

### TypeScript/React Guidelines
- Use functional components with hooks
- Define prop interfaces for all components
- Use custom hooks for reusable logic
- Implement error boundaries for error handling
- Use Tailwind CSS utility-first approach
- Strict TypeScript configuration

```typescript
interface MistakeUploadProps {
  onAnalysisComplete: (result: MistakeAnalysis) => void;
  maxFileSize?: number;
}

const MistakeUpload: React.FC<MistakeUploadProps> = ({ onAnalysisComplete }) => {
  // Component implementation with hooks and error boundaries
};
```

#### API Integration
- Use Axios with interceptors for authentication and error handling
- Type API responses and implement proper loading states

```typescript
class ApiClient {
  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    });
    this.setupInterceptors();
  }
}
```

### Project Architecture Principles
- **Modular Design**: Clear separation between OCR, AI analysis, scheduling, gamification
- **Configuration over Code**: Gamification rules in `config/settings.yaml`, no hardcoding
- **Chinese UI Language**: All user-facing strings in Simplified Chinese, English for code
- **Security**: Validate file uploads, parameterized queries, JWT/OAuth2 auth, env vars for secrets

### Testing Strategy
- **Unit Tests**: Business logic isolation, mock dependencies, edge cases
- **Integration Tests**: OCR → AI → Database pipeline, test fixtures
- **Frontend Tests**: React Testing Library, mock APIs, accessibility

### Development Workflow
- **Git**: Conventional commits (`feat:`, `fix:`), feature branches, PR reviews required
- **Code Review**: CI must pass (lint, test, type check), one approval minimum
- **Environment Setup**: Clone repo → copy `.env.example` → `docker-compose up -d` → install deps → run tests

---

*This guide follows the project specifications in CLAUDE.md and ensures consistent, high-quality development across all components of the AI-powered student mistakes management system.*