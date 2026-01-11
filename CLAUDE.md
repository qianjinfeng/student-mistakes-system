# CLAUDE.md

## 🎯 Project Goal  
Build an **AI-powered Student Mistakes Management System** that helps learners improve by intelligently tracking, analyzing, and reviewing their mistakes—especially from handwritten or printed Chinese-language questions captured via images. The system combines **multimodal AI (OCR + LLM)**, **spaced repetition**, and **gamification** to boost engagement and long-term retention.

All user-facing content is in **Simplified Chinese**; code, docs, and internal logic use **English**.

---

## 🧱 Core Components

### 1. **Frontend** (`/frontend`)
- Built with **React (TypeScript) + Vite + Tailwind CSS**
- Allows image upload/capture of questions
- Displays mistake insights, review tasks, achievements, and streaks
- Communicates with backend via **Axios**

### 2. **OCR Layer** (`ocr_processor.py`)
- Uses **PaddleOCR_VL** for:
  - Robust Chinese text detection & recognition
  - Layout-aware segmentation of questions from images
- Outputs structured text + bounding boxes
- Stores raw OCR results for debugging/reprocessing

### 3. **AI Reasoning Layer** (`ai_analyzer.py`)
- Interfaces with **Qwen** (Qwen-VL or Qwen-Max via API/local)
- Input: OCR text + optional image context
- Functions:
  - Judge answer correctness
  - Classify error type (e.g., *conceptual*, *calculation*, *misreading*)
  - Generate personalized insights based on similar past mistakes
  - Optionally generate **similar practice questions**
- All prompts are **versioned and logged**

### 4. **Backend API** (`/api`, built with **FastAPI**)
- RESTful/GraphQL interface
- Orchestrates calls between OCR, AI, DB, and scheduler
- Handles auth (**OAuth2 / JWT**), file validation, and rate limiting
- Secure file upload: validate image type (PNG/JPG), limit size

### 5. **Database** (`database/schema.sql`, PostgreSQL)
Stores:
- `Mistake`: image_id, ocr_text, subject, error_type, timestamp, user_id
- `User`: progress, streak, total_points
- `ReviewHistory`: scheduled vs completed reviews
- `Achievement`: unlocked badges/rules
- *(Future)* Embeddings via `pgvector` for semantic similarity

### 6. **Review Engine** (`review_scheduler.py`)
- Implements **spaced repetition** (SM-2 or custom variant)
- Schedules daily review tasks per user based on:
  - Mistake frequency
  - Knowledge gap analysis
  - Time since last review
- Tasks include:
  - Original saved mistakes
  - AI-generated similar practice questions

### 7. **Gamification Module** (`gamification/engine.py`)
- Tracks user actions (reviews completed, streaks, etc.)
- Awards **points**, unlocks **achievements**, maintains **daily streaks**
- Rules are **configurable via settings** (no code changes needed)

---

## ⚙️ Key Files & Directories

| File / Dir                     | Purpose |
|-------------------------------|--------|
| `ocr_processor.py`            | Image → PaddleOCR_VL → structured text |
| `ai_analyzer.py`              | Qwen integration: error classification + insight generation |
| `review_scheduler.py`         | Spaced repetition logic + question selection |
| `models/`                     | ORM models (SQLAlchemy/Django): User, Mistake, Achievement, etc. |
| `database/schema.sql`         | PostgreSQL table definitions |
| `gamification/engine.py`      | Points, streaks, achievement triggers |
| `config/settings.yaml`        | Central config: model endpoints, DB creds, gamification rules |
| `/frontend`                   | React app (TypeScript + Tailwind) |
| `/api`                        | FastAPI routes and service orchestration |

---

## 📜 Development Guidelines

- ✅ **Modular design**: Clear separation between OCR, AI, storage, and business logic  
- ✅ **Typed interfaces**: Use **Pydantic models** for all inter-component data  
- ✅ **Reproducibility**: Version and log all LLM prompts  
- ✅ **Debuggability**: Store raw OCR output + AI reasoning traces  
- ✅ **User language**: UI strings/messages in **Simplified Chinese**; avoid “error” → use “mistake” or “question you missed”  
- ✅ **Security**: Validate/sanitize all image uploads  
- ✅ **Testing**:
  - Unit tests: classification, scheduling logic
  - Integration tests: OCR → LLM pipeline
- ✅ **Config over code**: Gamification rules must be editable via config

---

## 🔌 Dependencies

- **OCR**: `PaddleOCR_VL`
- **LLM**: `Qwen` (API or local)
- **DB**: `PostgreSQL` (+ optional `pgvector`)
- **Backend**: `FastAPI`, `Celery` (for daily reminders)
- **Frontend**: `React`, `TypeScript`, `Vite`, `Tailwind CSS`, `Axios`
- **Auth**: `OAuth2` / `JWT`
- **Deployment**: Dockerized services

---

> 💡 **Note for Claude**: When assisting with code, prioritize **modularity**, **type safety**, and **user experience in Chinese**. Always assume the system processes **Chinese-language academic questions from images** and aims to **turn mistakes into learning opportunities**.