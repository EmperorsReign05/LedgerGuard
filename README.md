# LedgerGuard

LedgerGuard is an Agentic AI financial reconciliation platform built for enterprise scale. 

Modern financial systems process millions of transactions, yet companies still waste thousands of human hours manually reconciling edge cases (e.g., missing payments, tax discrepancies, hidden fee deductions, truncated bank references). LedgerGuard solves this by deploying a hybrid reconciliation engine. It utilizes a lightning-fast deterministic rules engine for standard matches, and routes ambiguous exceptions to an autonomous, AI-powered Finance Controller.

## Core Features

- Hybrid Matching Engine: Processes standard exact-matches via deterministic SQL queries, ensuring zero latency and zero cost for the 80% happy path.
- Agentic AI Investigator: Ambiguous matches (exceptions) are routed to an LLM agent that autonomously investigates the discrepancy, mathematically evaluates the evidence, and issues a decision (Resolve, Reject, or Escalate).
- Immutable Audit Trail: Every AI decision is permanently logged in the database alongside the exact prompt trace and evidence used, ensuring regulatory compliance and solving the "black box AI" problem.
- Enterprise SaaS Dashboard: A Next.js frontend featuring high-level ROI metrics, queue management, and a deep-dive case viewer.
- Human-in-the-Loop Chat: Reviewers can challenge AI decisions via an interactive chat interface that maintains case-specific memory.

## Architecture Stack

```mermaid
graph TD
    User([Finance Reviewer])
    
    subgraph Frontend [Next.js Web App]
        Dash[Enterprise Dashboard]
        Queue[Investigation Queue]
        Chat[Case Chat UI]
    end

    subgraph Backend [FastAPI Service]
        API[REST Endpoints]
        Tasks[Background Tasks]
        Rules[Deterministic Matcher]
    end
    
    subgraph AI [Agentic AI Controller]
        Groq[LLM / Groq API]
        Tools[Evidence Retrieval Tools]
        Parse[Pydantic Schema Engine]
    end
    
    subgraph Database [PostgreSQL]
        DB[(NeonDB)]
        Data[Payments & Settlements]
        Logs[Immutable Audit Logs]
    end

    User -->|"Interacts with"| Frontend
    Frontend -->|"HTTP / REST"| API
    API -->|"Spawns"| Tasks
    Tasks -->|"Pass 1: Exact Match"| Rules
    Rules -->|"Queries"| DB
    Tasks -->|"Pass 2: Route Exceptions"| AI
    Groq <-->|"Uses"| Tools
    Tools <-->|"Reads Evidence"| Data
    Groq -->|"Structured JSON"| Parse
    Parse -->|"Writes Decision & Trace"| Logs
```

- Frontend: Next.js 15, React 19, Tailwind CSS v4, Lucide React, Recharts.
- Backend API: Python, FastAPI, SQLAlchemy, Alembic (for migrations), Uvicorn.
- AI Engine: Groq API (llama-3.1-8b-instant or openai/gpt-oss-120b), Pydantic for schema enforcement.
- Database: PostgreSQL (NeonDB).

## Prerequisites

- Node.js 18+
- Python 3.10+
- A PostgreSQL database (e.g., NeonDB, Supabase, or local)
- A Groq API Key

## Setup Instructions

### 1. Environment Configuration

Clone the repository and configure your environment variables.

```bash
cp .env.example .env
```

Edit the `.env` file and provide your PostgreSQL connection string and Groq API key:
```env
DATABASE_URL="postgresql://user:password@host/dbname"
GROQ_API_KEY="your_groq_api_key_here"
```

### 2. Backend Setup (FastAPI)

Navigate to the API directory, create a virtual environment, install dependencies, and run database migrations.

```bash
cd apps/api

# Create and activate a virtual environment
python -m venv venv

# Windows (MSYS2/Git Bash):
.\venv\bin\activate
# Windows (PowerShell/CMD standard):
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head
```

### 3. Frontend Setup (Next.js)

Open a new terminal window, navigate to the web directory, and install dependencies.

```bash
cd apps/web
npm install
```

## Running the Application Locally

You will need two terminal windows running simultaneously.

### Start the Backend

```bash
cd apps/api
# Ensure your virtual environment is active
# Start the Uvicorn server on port 8001
uvicorn app.main:app --port 8001
```

### Start the Frontend

```bash
cd apps/web
npm run dev
```

Navigate to `http://localhost:3000` in your browser. 

## Synthetic Data Generation

If you are running the application for the first time, you will need data to test the reconciliation engine. A script is provided to generate and seed realistic financial anomalies into your database.

```bash
# In the root directory, ensure your python virtual environment is active
python scripts/seed_database.py
```

This will populate the Payments and Settlements tables with exact matches, candidate matches with discrepancies, and completely orphaned records for the AI to investigate.
