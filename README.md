# 🎬 Reel2Meal

> Discover food through short videos — a TikTok-style food reels platform.

## Stack
| Layer | Tech |
|-------|------|
| Backend | FastAPI + SQLAlchemy (async) + PostgreSQL |
| Migrations | Alembic |
| Frontend | React 18 + Vite 4 + Tailwind CSS 3 |
| State | Zustand |
| Auth | JWT (python-jose + bcrypt) |
| DevOps | Docker Compose |

---

## Quick Start (Local Dev)

### Prerequisites
- Python 3.11+
- Node 18+ (or 16 with Vite 4)
- PostgreSQL 15+ (or use Docker)

### 1. Start the database
```bash
docker compose up db -d
```

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # edit DATABASE_URL, SECRET_KEY
uvicorn app.main:app --reload
```
API available at: http://localhost:8000  
Swagger docs: http://localhost:8000/docs

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```
App available at: http://localhost:5173

---

## Run Everything with Docker
```bash
docker compose up --build
```
| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/docs |
| pgAdmin | http://localhost:5050 (admin@reel2meal.local / admin) |

---

## Run Tests
```bash
cd backend
# Ensure a test DB exists: createdb reel2meal_test
pytest --cov=app tests/ -v
```

---

## Project Structure
```
reel2meal/
├── backend/        # FastAPI + SQLAlchemy
├── frontend/       # React + Vite + Tailwind
└── docker-compose.yml
```

---

## Phase 1 Features
- ✅ JWT authentication (register / login / /me)
- ✅ Snap-scroll vertical reels feed
- ✅ Video autoplay when in viewport
- ✅ Like & Save (optimistic updates)
- ✅ Food menu drawer (categorised, veg/non-veg indicators)
- ✅ Restaurant badges linking to Google Maps
- ✅ Public user profiles
- ✅ Cursor-based pagination

## Phase 2 Roadmap
- [ ] Video upload to Cloudinary
- [ ] Following / Followers
- [ ] Comments panel
- [ ] Search & discovery
- [ ] Push notifications
