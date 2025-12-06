# FastAPI + Vite Starter

This repository contains the scaffolding for a local-first web application composed of a FastAPI backend and a Vite/React frontend. It includes sensible tooling defaults, environment configuration templates, and workflow scripts so you can focus on building features.

## Project structure

```
.
├── backend/             # FastAPI application code
│   ├── app/
│   │   ├── api/         # API routers (health check, etc.)
│   │   ├── core/        # Settings & logging helpers
│   │   └── main.py      # FastAPI entrypoint
│   ├── requirements*.txt
│   └── static/          # Uploaded/static assets (served at /static)
├── frontend/            # Vite + React app
│   ├── src/
│   ├── tsconfig*.json
│   └── package.json
├── .env.example         # Shared backend/env defaults
├── package.json         # Convenience scripts for running both apps
└── README.md
```

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm 9+

## Environment variables

1. Copy the provided template and update the secrets:
   ```bash
   cp .env.example .env
   cp frontend/.env.example frontend/.env
   ```
2. The backend reads variables from the root `.env` file (Gmail OAuth + OpenAI keys, log level, etc.).
3. The frontend uses `VITE_API_BASE_URL` to know how to reach the FastAPI API (defaults to `http://localhost:8000/api`).

## Backend setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
# Optional tooling
pip install -r backend/requirements-dev.txt
```

### Running the backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend exposes:
- `GET /api/health` — health check endpoint
- `GET /` — root status message
- Static uploads served from `backend/static` at `/static`
- CORS enabled for origins configured via `BACKEND_CORS_ORIGINS`

## Frontend setup

```bash
cd frontend
npm install
```

### Running the frontend

```bash
npm run dev
```

This launches Vite on http://localhost:5173 and fetches backend data using the configurable API base URL.

## Running both services together

Install the root dev dependency and then leverage the helper scripts:

```bash
npm install
npm run dev          # Starts backend + frontend concurrently
npm run dev:backend  # Backend only
npm run dev:frontend # Frontend only
```

## Tooling

- **Backend** — formatted with [Black](https://black.readthedocs.io/) and linted with [Ruff](https://docs.astral.sh/ruff/). Configuration lives in `backend/pyproject.toml`.
- **Frontend** — linted with ESLint + TypeScript and formatted with Prettier. See `frontend/.eslintrc.cjs` and `frontend/.prettierrc`.

You're ready to start iterating on features 🚀
