# LedgerGuard

An AI finance controller that reconciles settlement records, investigates exceptions using evidence, and automatically resolves only cases that meet explicit confidence and policy requirements.

## Architecture & Product Thesis

**Don't build an AI that always acts. Build an AI finance controller that knows when it has enough evidence to act.**

LedgerGuard uses deterministic logic wherever it is appropriate, and AI only where ambiguity requires reasoning. Every automated decision is gated by explicit confidence thresholds and policies.

See `context.md` for a complete breakdown of the product definition and current state.

## Setup Instructions

### Prerequisites
- Node.js (for frontend)
- Python 3.10+ (for backend)
- NeonDB (PostgreSQL)

### 1. Environment Configuration
Copy `.env.example` to `.env` and fill in the required values:
```bash
cp .env.example .env
```

### 2. Frontend Setup (Next.js)
```bash
cd apps/web
npm install
npm run dev
```
The frontend will run on `http://localhost:3000`.

### 3. Backend Setup (FastAPI)
```bash
cd apps/api
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
The backend API will run on `http://localhost:8000`.

## Testing
- **Backend**: Run `pytest` inside the `apps/api` directory.
