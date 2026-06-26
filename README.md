# Polyglot Gate

Polyglot Gate is a lightweight quality gate for multilingual AI output. It combines evaluation scoring, moderation checks, globalization triage, regression fixtures, and a small React dashboard so teams can catch weak model responses before they ship.

## Why This Project

The project is organized around three named services. The Evaluation Service creates prompts, runs, and scores so a team can gate releases on correctness, formatting, locale coverage, and regression status. The Moderation Service checks generated or submitted text against YAML policy rules and writes policy issues for flagged content. The Globalization Triage Service classifies human-reported localization problems and routes them to internal queues such as `i18n-team`, `platform-team`, `trust-and-safety`, `model-quality`, and `content-design`.

## Quickstart

From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

For local development without an Anthropic API key, edit `backend/.env` so it includes:

```bash
LLM_PROVIDER=mock
DATABASE_URL=sqlite:///./app.db
LOG_LEVEL=INFO
```

Run the backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Seed dashboard data from another terminal:

```bash
cd backend
source .venv/bin/activate
python seed_data.py
```

Run backend tests:

```bash
cd backend
source .venv/bin/activate
LLM_PROVIDER=mock pytest -v
```

Install and run the frontend:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on `http://localhost:5173` and proxies `/api/*` calls to `http://localhost:8000`.

Build the frontend:

```bash
cd frontend
npm run build
```

## Documentation

- [Architecture](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Integration Guide](docs/integration-guide.md)

## Project Status / What's Intentionally Out Of Scope

This is an MVP implementation with deliberate simplifications:

- SQLite is used instead of a managed Postgres instance. The SQLAlchemy model/session layer keeps the database boundary clear so a Postgres swap is mostly configuration and dependency work.
- Moderation is regex-based through `backend/app/policies/moderation_rules.yaml`, not an ML policy classifier. This makes rules reviewable and deterministic for the first version.
- Locale coverage uses a heuristic, not real language detection. English passes automatically, Spanish checks for common Spanish characters, and other non-English locales use a simple non-empty/non-English-stopword fallback.
- `MockProvider` is first-class for CI, tests, seed data, and demos. Real Anthropic generation is available through `AnthropicProvider` when `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` is configured.
- Metrics are in-process and reset when the backend restarts. They are useful for local visibility and dashboard health, not long-term observability storage.
- Triage routing writes `Issue.routed_to` rather than calling a ticketing system. The route decision is persisted and ready for a future webhook integration.
