# Integration Guide

This guide is written for internal teams that want to use Polyglot Gate without changing its core service boundaries.

## If Your Team Wants To Use The Evaluation Service To Gate A Release

Call either `POST /api/evaluate` for a single target locale or `POST /api/evaluate/multi-locale` for consistency across locales. In CI, set `LLM_PROVIDER=mock` if you want deterministic checks without an Anthropic key, or use `LLM_PROVIDER=anthropic` with `ANTHROPIC_API_KEY` for real model output. The release gate should inspect `passed`: fail the build when it is `false`, and print `failure_reasons` so the owning team can see what score failed.

Single-locale curl example:

```bash
curl -s -X POST http://localhost:8000/api/evaluate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt_text": "Write a concise greeting for a new user.",
    "locale": "en",
    "reference_answer": "Welcome to your new account."
  }'
```

Multi-locale curl example:

```bash
curl -s -X POST http://localhost:8000/api/evaluate/multi-locale \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt_text": "Summarize the checkout error in one sentence.",
    "locales": ["en", "es", "fr"],
    "reference_answer": "The checkout failed because payment could not be completed."
  }'
```

For a branch-level regression check, call `GET /api/evaluate/regression-suite`. That endpoint runs the JSON fixture suite from `backend/tests/fixtures/regression_cases.json` and returns `total`, `passed`, `failed`, and a `failures` array.

## If Your Team Wants To Add A New Moderation Rule

Edit `backend/app/policies/moderation_rules.yaml`. Each rule is a YAML object with these fields:

```yaml
- id: PII_EMAIL
  name: Email address
  severity: medium
  pattern: '\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'
  description: Detects email-address-like text.
```

Required fields:

- `id`: stable machine-readable label returned in `labels`, for example `PII_PHONE`.
- `name`: human-readable rule name returned in `policy_violations`.
- `severity`: one of `low`, `medium`, or `high`; any `high` match blocks, lower severities flag.
- `pattern`: a case-insensitive regular expression. For non-regex rules such as `LOCALE_MISMATCH`, leave it empty and handle it in code.
- `description`: short explanation for maintainers.

`load_rules()` in `backend/app/services/moderation_service.py` is decorated with `@lru_cache(maxsize=1)`, so a running process will not automatically re-read YAML edits. Restart the backend process after changing the file. In a Python shell or test, you can also call `load_rules.cache_clear()` before the next moderation call, but production-style usage should restart the service.

## If Your Team Wants To Add A New Locale

Add a row through the `Locale` model. The seed script shows the intended pattern:

```python
from app.database import SessionLocal, init_db
from app.models.locale import Locale

init_db()
db = SessionLocal()
if not db.query(Locale).filter(Locale.code == "it").first():
    db.add(Locale(code="it", name="Italian", is_supported=True))
    db.commit()
db.close()
```

The current evaluation heuristic does not consult the `Locale` table when scoring locale coverage. Its behavior is intentionally simple: `en` always scores `1.0`; `es` scores `1.0` only if the output contains Spanish marker characters such as `ñ`, accented vowels, `ü`, `¿`, or `¡`; other non-English locales score `1.0` when the output is non-empty and not only a tiny set of English stopwords. This is an MVP heuristic, not language detection. Adding a locale row helps dashboards and future routing, but true language validation should eventually use a language-detection library or locale-specific reviewer model.

## If Your Team Wants To Feed Triage Results Into Your Own Ticketing System

Triage writes all routed work to the shared `Issue` table. The important fields for downstream systems are:

- `category`: the classifier result, such as `translation`, `formatting`, or `unsupported_locale`.
- `description`: the reporter text or generated description.
- `suggested_fix`: the concrete remediation text from `suggest_fix()`.
- `status`: currently set to `routed` by `triage()`.
- `routed_to`: the internal queue from `route()`, such as `i18n-team`, `platform-team`, or `trust-and-safety`.
- `confidence`: the rule-based classifier confidence.

To send tickets to an external system, add the webhook/API call in `backend/app/services/triage_service.py` inside `triage()`, after `category`, `suggested_fix`, and `routed_to` are computed and before the response is returned. A practical implementation would commit the `Issue` row first so it has a durable `issue.id`, then call the external ticketing API with that ID and update `status` to reflect delivery if needed.
