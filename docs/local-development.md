# Local Development Guide

This guide describes how to run and test MindOS locally during development.

---

## Prerequisites

- **Python**: 3.12+
- **Node.js**: v20+ (with npm 10+)
- **Git**
- **PostgreSQL**: (Optional for initial bootstrap; required once data persistence is enabled)

---

## Project Structure

```text
mindos/
├── backend/            # FastAPI modular monolith application
│   ├── alembic/        # Database migrations
│   ├── app/            # Application code (core, api/v1, models, schemas, services)
│   ├── tests/          # Pytest suite
│   ├── pyproject.toml  # Project configuration
│   └── requirements.txt
├── frontend/           # React + TypeScript + Vite UI
│   ├── src/            # Components, hooks, styles
│   ├── package.json
│   └── vite.config.ts
├── docs/               # Architecture and technical guides
├── .gitignore          # Repository git ignore rules
├── .env.example        # Reference environment variables
└── README.md
```

---

## 1. Backend Setup

### Create and Activate Virtual Environment

From the project root:

```bash
cd backend
python -m venv .venv

# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# On macOS/Linux:
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Configure Environment Variables

```bash
cp .env.example .env
```

### Run the Backend

```bash
uvicorn app.main:app --reload --port 8000
```

- API Root: `http://localhost:8000`
- Health Endpoint: `http://localhost:8000/api/v1/health`
- Interactive API Docs (Swagger): `http://localhost:8000/docs`

### Run Backend Tests

```bash
pytest
```

---

## 2. Frontend Setup

### Install Dependencies

From the project root:

```bash
cd frontend
npm install
```

### Configure Environment Variables

```bash
cp .env.example .env
```

### Run the Development Server

```bash
npm run dev
```

- Web Interface: `http://localhost:5173`

### Run Frontend Tests and Build

```bash
npm test
npm run build
```

---

## 3. Database & Migrations (PostgreSQL)

When running a local PostgreSQL instance:

1. Ensure the PostgreSQL service is active and the `mindos` database is created.
2. Verify `DATABASE_URL` in `backend/.env`.
3. Apply migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```
