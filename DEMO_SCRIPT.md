# Demo Script

Use this as a 5-minute walkthrough for a live presentation.

1. Start with the backend health and docs.
   Run the backend with `LLM_PROVIDER=mock uvicorn app.main:app --reload --port 8000`, then open `http://localhost:8000/health` and `http://localhost:8000/docs`. Explain that the API is split into evaluation, moderation, triage, and metrics routes under `/api`.

2. Show the React dashboard.
   Start the frontend with `cd frontend && npm run dev`, then open `http://localhost:5173`. Point out the four top-level workflows: Submit Prompt, Evaluation Results, Moderation Flags, and Triage Dashboard.

3. Submit a multi-locale prompt.
   On Submit Prompt, enter `Summarize the checkout error in one sentence.`, leave the locale selector on `en`, optionally enter `The checkout failed because payment could not be completed.` as the reference answer, and click `Run Multi-Locale Check (en/es/fr)`. Narrate the `consistency_score`, the worst locale, and how each locale gets its own score row while sharing one prompt.

4. Demonstrate moderation.
   On Moderation Flags, submit `Please contact reviewer@example.com for escalation.` with locale `en`. Show that the page returns `flag`, lists `PII_EMAIL`, and creates an audit row plus a policy issue behind the scenes. Mention that the rules come from `backend/app/policies/moderation_rules.yaml`.

5. Demonstrate globalization triage.
   On Triage Dashboard, submit prompt text `Write a checkout error in Spanish.`, output text `Checkout failed`, locale `es`, and reported issue `untranslated strings remain`. Show the classifier result, suggested fix, and route to `i18n-team`, then point out the new row in the issue history table.

6. Show evaluation health and metrics.
   On Evaluation Results, show the aggregate evaluation metrics plus the recent run-by-run history table. Also open `http://localhost:8000/api/metrics` and explain that this is an in-process stand-in for production monitoring such as Prometheus, logs, or a managed observability platform.

7. Close with architecture and next steps.
   Open `docs/architecture.md` and walk through the ASCII diagram: Frontend -> FastAPI routers -> SQLite -> Anthropic API or MockProvider. Close by naming the obvious next production investments: swap SQLite for managed Postgres, add real language detection for locale coverage, and replace heuristic triage with an ML-backed classifier or reviewer model.
