# Architecture

Polyglot Gate is a small FastAPI and React system organized around three backend services. The Evaluation Service writes `Prompt`, `Run`, and `Score` rows to track model outputs and score quality over time. The Moderation Service applies YAML-backed policy rules, writes every check to `audit_logs`, and creates `Issue` rows when content should be flagged or blocked. The Globalization Triage Service also writes `Issue` rows, but uses them as routed work items for translation, formatting, policy, tone, hallucination, unsupported-locale, and general follow-up. That shared `Issue` table is the bridge between automated moderation failures and human-reported globalization triage, while the shared `Prompt`/`Run`/`Score` tables are the evaluation history that powers release gating, regression checks, and the dashboard.

```text
Frontend (Vite React)
        |
        | fetch("/api/...")
        v
FastAPI (3 routers: evaluation, moderation, triage)
        |
        | SQLAlchemy sessions
        v
SQLite app.db
        |
        | generation through LLMProvider
        v
(Anthropic API | MockProvider)
```

The Metrics router is an auxiliary operational endpoint rather than a domain service; it exposes in-process counters recorded by the three service functions.

## Why These Design Choices

SQLAlchemy 2.0 keeps the SQLite MVP close to a production database shape. The models use standard columns, foreign keys, `SessionLocal`, and `Base.metadata.create_all`, so switching `DATABASE_URL` from `sqlite:///./app.db` to a Postgres URL mainly changes configuration and driver dependencies rather than application code. The current SQLite setup is useful for local development, tests, CI, and seeded dashboard demos.

`LLMProvider` exists so generation is not hard-wired to Anthropic. `AnthropicProvider` handles the real SDK call and API key validation, while `MockProvider` gives deterministic output for tests, CI, seed data, and local demos without credentials or network calls. Routers depend on `get_llm_provider`, which means service code can be exercised with either provider through the same interface.

Regression cases live in `backend/tests/fixtures/regression_cases.json` because they are source-controlled release gates, not user-generated data. Keeping them as JSON makes code review easy, lets CI run the same suite on every branch, and avoids coupling the regression harness to whatever happens to be present in a developer's local database.
