<div align="center">

```
  ██████╗  ██████╗ ██╗  ██╗   ██╗ ██████╗ ██╗      ██████╗ ████████╗
  ██╔══██╗██╔═══██╗██║  ╚██╗ ██╔╝██╔════╝ ██║     ██╔═══██╗╚══██╔══╝
  ██████╔╝██║   ██║██║   ╚████╔╝ ██║  ███╗██║     ██║   ██║   ██║   
  ██╔═══╝ ██║   ██║██║    ╚██╔╝  ██║   ██║██║     ██║   ██║   ██║   
  ██║     ╚██████╔╝███████╗██║   ╚██████╔╝███████╗╚██████╔╝   ██║   
  ╚═╝      ╚═════╝ ╚══════╝╚═╝    ╚═════╝ ╚══════╝ ╚═════╝    ╚═╝   
          ██████╗  █████╗ ████████╗███████╗
         ██╔════╝ ██╔══██╗╚══██╔══╝██╔════╝
         ██║  ███╗███████║   ██║   █████╗  
         ██║   ██║██╔══██║   ██║   ██╔══╝  
         ╚██████╔╝██║  ██║   ██║   ███████╗
          ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝
```

**Zero-overhead, local-first quality gate and moderation layer for multilingual LLM applications.**

[![License: MIT](https://img.shields.io/badge/License-MIT-a6e3a1.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-89b4fa.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-v18.3-61dafb.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-v5.0%2B-3178c6.svg)](https://www.typescriptlang.org)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-v2.0%2B-red.svg)](https://www.sqlalchemy.org)

</div>

---

Polyglot Gate is an extensible, lightweight quality gate and operational observability harness designed to validate, moderate, and triage multilingual LLM outputs. It sits between your raw generation layer and downstream systems to catch formatting errors, incorrect locales, policy violations, and regression failures before they reach production.

It offers a robust FastAPI backend backed by SQLite/SQLAlchemy 2.0, coupled with an interactive React/TypeScript dashboard powered by Vite.

---

## 🚀 Key Features

*   **Multilingual Evaluation Service**: Scores generated LLM output across four dimensions:
    *   *Correctness*: Token-based Jaccard similarity against reference answers.
    *   *Formatting*: Checks for unclosed Markdown styling (`**`, ```` ``` ````) and truncated outputs.
    *   *Locale Coverage*: Heuristic-based language validation (e.g., verifying Spanish characters).
    *   *Regression Gates*: Validates outputs against source-controlled regression suites.
*   **YAML-Driven Moderation**: Regex-based policy engine matching text against customizable threat rules (PII, profanities, medical claims) using deterministic, reviewable, and version-controlled criteria.
*   **Globalization Triage Service**: Automatically classifies reported translation/localization bugs (hallucinations, unsupported locales, tone formality, etc.) and routes them to target team queues (`i18n-team`, `platform-team`, `trust-and-safety`, `model-quality`, `content-design`).
*   **Developer-First Testing & CI**: Includes a zero-token `MockProvider` to support offline development, unit tests, and CI/CD pipelines without incurring LLM API costs or dependency on external servers.
*   **Operational Telemetry**: Memory-local prometheus-style dashboard counters tracking latency, failure categories, and overall pass rates.

---

## 📊 Comparison Matrix

| Feature | Polyglot Gate | Production Observability (Datadog/Prometheus) |
|---|---|---|
| **Primary Focus** | Quality, formatting, safety, and translation correctness | Server metrics, hardware throughput, and raw error rates |
| **Gating Ability** | Direct evaluation/moderation endpoints with CI release suites | Metric-based alerts and post-facto notifications |
| **Setup Cost** | 🆓 Local-first, zero configuration (runs on SQLite) | 💰 High cost, agent/collector cluster configurations |
| **Token Cost** | Zero during mock mode / tests, standard during live runs | Zero (monitors logs/requests asynchronously) |
| **Policy Updates** | Declarative YAML rules versioned within the codebase | Dashboard filters or configuration panel overrides |

---

## 📐 System Architecture

```
                       ┌──────────────────────────────┐
                       │   React Dashboard (Vite)     │
                       └──────────────┬───────────────┘
                                      │
                                      │ REST API / JSON
                                      ▼
                       ┌──────────────────────────────┐
                       │    FastAPI Application       │
                       └──────────────┬───────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
┌───────────────────┐        ┌───────────────────┐        ┌───────────────────┐
│Evaluation Service │        │Moderation Service │        │  Triage Service   │
│ - Correctness     │        │ - YAML Policy Rules│        │ - Classify Issue  │
│ - Formatting      │        │ - Safe/Flag/Block │        │ - Formulate Fix   │
│ - Locale Fit      │        │ - Audit Logging   │        │ - Queue Routing   │
└────────┬──────────┘        └────────┬──────────┘        └────────┬──────────┘
         │                            │                            │
         └────────────────────────────┼────────────────────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │  SQLAlchemy ORM (SQLite DB)  │
                       └──────────────┬───────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │      LLMProvider Interface   │
                       └──────────────┬───────────────┘
                                      │
                      ┌───────────────┴───────────────┐
                      ▼                               ▼
            ┌───────────────────┐           ┌───────────────────┐
            │   MockProvider    │           │ AnthropicProvider │
            │ (Deterministic,   │           │   (Claude API,    │
            │  zero token cost) │           │   live calls)     │
            └───────────────────┘           └───────────────────┘
```

---

## 📂 Project Structure

```
polyglot-gate/
├── backend/
│   ├── app/
│   │   ├── core/              # Metrics trackers and configuration helpers
│   │   ├── models/            # SQLAlchemy schemas (Prompt, Run, Score, Issue, AuditLog)
│   │   ├── policies/          # Yaml moderation rules definition (moderation_rules.yaml)
│   │   ├── routers/           # FastAPI routers (evaluation, moderation, triage, metrics)
│   │   ├── schemas/           # Pydantic v2 validation models
│   │   ├── services/          # Services implementing scoring, policies, and LLM interfaces
│   │   │   ├── evaluation_service.py
│   │   │   ├── llm_provider.py
│   │   │   ├── moderation_service.py
│   │   │   ├── regression_runner.py
│   │   │   └── triage_service.py
│   │   ├── database.py        # Connection setup and SessionLocal instance
│   │   └── main.py            # FastAPI main entrypoint and middlewares
│   ├── tests/                 # Unit & integration tests
│   │   └── fixtures/          # JSON regression data files
│   ├── .env.example           # Configuration template
│   ├── requirements.txt       # Python backend dependencies
│   └── seed_data.py           # Populates local db with mockup data
├── docs/                      # Technical specification files
│   ├── api-reference.md       # API endpoint details and curl examples
│   ├── architecture.md        # Core backend and design considerations
│   └── integration-guide.md   # Setup procedures for external/internal clients
├── frontend/
│   ├── src/
│   │   ├── api/               # API connection/fetch actions
│   │   ├── components/        # Modular UI units (Layout, Navigation, Cards)
│   │   ├── pages/             # Route modules (SubmitPrompt, EvaluationResults, etc.)
│   │   ├── App.tsx            # Main component & react-router router definitions
│   │   └── index.css          # Design system & stylesheet definitions
│   ├── package.json           # Frontend dependency config
│   └── vite.config.ts         # Vite server settings & proxy config
├── DEMO_SCRIPT.md             # Walkthrough guide for live reviews
└── README.md                  # This file
```

---

## ⚙️ Configuration & Environment Variables

Create a `backend/.env` file from the provided template:
```bash
cp backend/.env.example backend/.env
```

Customize the system variables in `backend/.env`:

| Variable | Default Value | Allowed Values | Purpose |
|---|---|---|---|
| `LLM_PROVIDER` | `mock` | `mock` / `anthropic` | Sets whether backend uses Claude API or deterministic mock generation. |
| `ANTHROPIC_API_KEY` | `""` | Any valid Anthropic key | Required when `LLM_PROVIDER=anthropic`. |
| `DATABASE_URL` | `sqlite:///./app.db` | Any SQLAlchemy SQL URL | Connection string for database storage. |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | Sets verbosity for application logs. |

---

## 🛠️ Getting Started

### Prerequisites

Ensure you have the following installed:
*   Python 3.10+
*   Node.js 18+ & npm

---

### Step 1: Set Up and Run the Backend

1. Navigate to the `backend` folder, set up a virtual environment, and install dependencies:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Initialize your `.env` configuration file:
   ```bash
   cp .env.example .env
   ```

3. Seed the local SQLite database with dummy data to populate the charts and tables:
   ```bash
   python seed_data.py
   ```

4. Run the Uvicorn application server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *   The server will run on: `http://localhost:8000`
   *   Swagger docs are accessible at: `http://localhost:8000/docs`
   *   Health endpoint is located at: `http://localhost:8000/health`

---

### Step 2: Set Up and Run the Frontend Dashboard

1. Open a new terminal and navigate to the `frontend` directory:
   ```bash
   cd frontend
   npm install
   ```

2. Run the Vite development server:
   ```bash
   npm run dev
   ```
   *   The dashboard will spin up at: `http://localhost:5173`
   *   Calls to `/api/*` are configured to automatically proxy to your backend at `http://localhost:8000/api/*`.

---

### Step 3: Run Backend Tests

Verify your installation by running the Pytest suite under mock conditions:
```bash
cd backend
source .venv/bin/activate
LLM_PROVIDER=mock pytest -v
```

---

## 🛰️ API Quick Reference

### 1. Evaluate Single Locale
*   **Endpoint**: `POST /api/evaluate`
*   **Payload**:
    ```json
    {
      "prompt_text": "Write a concise greeting for a new user.",
      "locale": "en",
      "reference_answer": "Welcome to your new account."
    }
    ```
*   **Response**:
    ```json
    {
      "run_id": 1,
      "prompt_id": 1,
      "output_text": "[MOCK-en] Write a concise greeting for a new user.",
      "locale": "en",
      "latency_ms": 10,
      "scores": {
        "correctness": 0.083,
        "formatting": 1.0,
        "locale_coverage": 1.0,
        "regression_pass": true,
        "overall": 0.633
      },
      "passed": false,
      "failure_reasons": ["correctness below threshold (0.08)"]
    }
    ```

### 2. Multi-Locale Consistency Evaluation
*   **Endpoint**: `POST /api/evaluate/multi-locale`
*   **Payload**:
    ```json
    {
      "prompt_text": "Summarize the checkout error in one sentence.",
      "locales": ["en", "es", "fr"],
      "reference_answer": "The checkout failed because payment could not be completed."
    }
    ```
*   **Response**:
    ```json
    {
      "prompt_id": 2,
      "results": [
        { "locale": "en", "run_id": 2, "scores": { "overall": 0.653 }, "passed": false },
        { "locale": "es", "run_id": 3, "scores": { "overall": 0.453 }, "passed": false },
        { "locale": "fr", "run_id": 4, "scores": { "overall": 0.653 }, "passed": false }
      ],
      "consistency_score": 0.8,
      "worst_locale": "es",
      "summary": "es scored 0.20 lower than en"
    }
    ```

### 3. Apply Moderation Rules
*   **Endpoint**: `POST /api/moderate`
*   **Payload**:
    ```json
    {
      "text": "Please contact reviewer@example.com for escalation.",
      "locale": "en",
      "context": "support reply"
    }
    ```
*   **Response**:
    ```json
    {
      "audit_id": 1,
      "is_safe": false,
      "labels": ["PII_EMAIL"],
      "policy_violations": [
        { "rule_id": "PII_EMAIL", "rule_name": "Email address", "severity": "medium" }
      ],
      "action": "flag"
    }
    ```

### 4. Route Globalization Triage
*   **Endpoint**: `POST /api/triage`
*   **Payload**:
    ```json
    {
      "prompt_text": "Write a checkout error in Spanish.",
      "output_text": "Checkout failed",
      "locale": "es",
      "reported_issue": "untranslated fallback text"
    }
    ```
*   **Response**:
    ```json
    {
      "issue_id": 2,
      "issue_category": "translation",
      "confidence": 0.8,
      "suggested_fix": "Re-run generation with an explicit instruction to respond only in es and verify no English fallback strings remain.",
      "route_to": "i18n-team"
    }
    ```

### 5. Fetch Telemetry Metrics
*   **Endpoint**: `GET /api/metrics`
*   **Response**:
    ```json
    {
      "services": {
        "evaluate": { "count": 4, "avg_latency_ms": 10.0, "pass_count": 0, "fail_count": 4 },
        "moderate": { "count": 1, "avg_latency_ms": 10.0, "pass_count": 0, "fail_count": 1 },
        "triage": { "count": 1, "avg_latency_ms": 4.0, "pass_count": 1, "fail_count": 0 }
      },
      "failures_by_reason": {
        "correctness below threshold (0.08)": 1,
        "correctness below threshold (0.13)": 3,
        "PII_EMAIL": 1
      }
    }
    ```

---

## 🔍 Scoring Details & Heuristics

### Correctness
Evaluated using token overlap Jaccard coefficient:
$$\text{Correctness} = \frac{|\text{Tokens}_{\text{output}} \cap \text{Tokens}_{\text{reference}}|}{|\text{Tokens}_{\text{output}} \cup \text{Tokens}_{\text{reference}}|}$$
*If no reference answer is provided, returns `1.0` if response length exceeds 3 characters, else `0.0`.*

### Formatting
Reduces score by `0.25` for each layout violation found:
*   Odd count of Markdown strong tags (`**`).
*   Odd count of code blocks (`` ``` ``).
*   Truncation detection (evaluates whether the last character of the response is a valid terminal punctuation mark: `.`, `!`, `?`, `。`, `？`, `！`, `…`, `)`, `]`, `}`, `"`).

### Locale Fit
*   For **English (`en`)**: Always returns `1.0`.
*   For **Spanish (`es`)**: Returns `1.0` if output contains Spanish markers (`ñ`, accented letters, `ü`, `¿`, `¡`), else `0.0`.
*   For **Other Locales**: Returns `1.0` if output is non-empty and contains words outside common English stopwords, else `0.0`.

---

## 🛡️ Moderation Policy Violations

Rules are managed in `backend/app/policies/moderation_rules.yaml`. You can update, add, or delete policies easily:

```yaml
- id: PII_EMAIL
  name: Email address
  severity: medium
  pattern: '\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'
  description: Detects email-address-like text.
```

### Action Resolutions:
*   `high` severity rule matched: Output status resolved as `"block"`.
*   `medium` or `low` severity rule matched: Output status resolved as `"flag"`.
*   No matches found: Output status resolved as `"allow"`.

---

## 🤝 Contributing

We welcome additions to validation heuristics, rules, and dashboard layouts!

1. **Adding Moderation Rules**:
   Add rules directly to `backend/app/policies/moderation_rules.yaml`. The schema requires `id`, `name`, `severity` (`low`, `medium`, or `high`), `pattern` (regular expression), and a description.
2. **Onboarding New Locales**:
   Insert a new locale using the `Locale` DB model or update your seed scripts to include new ISO language codes.
3. **Writing Tests**:
   Ensure any service extensions are backed by appropriate unit tests in the `backend/tests/` folder. Run code style linting before push.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
