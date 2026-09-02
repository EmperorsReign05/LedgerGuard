# LedgerGuard

An AI finance controller that reconciles settlement records, investigates exceptions using evidence, and automatically resolves only cases that meet explicit confidence and policy requirements.

## Architecture

The project consists of three main components:
1. **Database**: PostgreSQL (hosted on NeonDB)
2. **API Backend**: FastAPI python service handling the core deterministic matcher and the Groq LLM integration.
3. **Frontend Dashboard**: A Next.js web application.

## How to Run Locally

You will need two terminal windows to run both the frontend and the backend.

### 1. Start the FastAPI Backend
```bash
cd ledgerguard/apps/api

# Run uvicorn directly using the virtual environment's python executable
.\venv\bin\python.exe -m uvicorn app.main:app --port 8001
```

### 2. Start the Next.js Frontend
```bash
cd ledgerguard/apps/web

# Install dependencies if you haven't already
npm install

# Start the dev server on port 3000
npm run dev
```

Finally, open your browser and navigate to `http://localhost:3000`.

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
