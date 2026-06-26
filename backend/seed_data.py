from app.database import SessionLocal, init_db
from app.models.audit_log import AuditLog
from app.models.issue import Issue
from app.models.locale import Locale
from app.models.prompt import Prompt
from app.models.run import Run
from app.models.score import Score
from app.schemas.evaluate import EvaluateRequest
from app.schemas.moderate import ModerateRequest
from app.schemas.triage import TriageRequest
from app.services.evaluation_service import evaluate
from app.services.llm_provider import MockProvider
from app.services.moderation_service import moderate
from app.services.triage_service import triage


LOCALES = [
    {"code": "en", "name": "English", "is_supported": True},
    {"code": "es", "name": "Spanish", "is_supported": True},
    {"code": "fr", "name": "French", "is_supported": True},
    {"code": "de", "name": "German", "is_supported": True},
    {"code": "ja", "name": "Japanese", "is_supported": False},
]

EVALUATION_CASES = [
    {
        "prompt_text": "Write a concise welcome message for a new account.",
        "locale": "en",
        "reference_answer": "Welcome to your new account.",
    },
    {
        "prompt_text": "Resume la política de devoluciones en una frase clara.",
        "locale": "es",
        "reference_answer": "La política de devoluciones es clara y fácil.",
    },
    {
        "prompt_text": "Rédige une confirmation courte pour une réservation.",
        "locale": "fr",
        "reference_answer": "Votre réservation est confirmée.",
    },
    {
        "prompt_text": "Erstelle eine kurze Lieferstatusmeldung.",
        "locale": "de",
        "reference_answer": "Die Lieferung verzögert sich leicht.",
    },
    {
        "prompt_text": "Explain how to reset a password in two steps.",
        "locale": "en",
        "reference_answer": "Reset your password using account settings.",
    },
    {
        "prompt_text": "Hi",
        "locale": "en",
        "reference_answer": "This reference intentionally will not overlap.",
    },
    {
        "prompt_text": "Redacta una alerta breve para pago fallido.",
        "locale": "es",
        "reference_answer": "El pago no se pudo completar.",
    },
]

MODERATION_CASES = [
    {"text": "This release note is clean and ready.", "locale": "en"},
    {"text": "Please contact reviewer@example.com for escalation.", "locale": "en"},
    {"text": "Call +1 (555) 123-4567 for account recovery.", "locale": "en"},
]

TRIAGE_CASES = [
    {
        "prompt_text": "Write a checkout error in Spanish.",
        "output_text": "Checkout failed",
        "locale": "es",
        "reported_issue": "untranslated fallback text",
    },
    {
        "prompt_text": "Write a formatted support answer.",
        "output_text": "**Broken markdown",
        "locale": "en",
        "reported_issue": "broken markdown in the response",
    },
    {
        "prompt_text": "Write a greeting for a new locale.",
        "output_text": "Hello there",
        "locale": "pt",
        "reported_issue": None,
    },
]


def seed_locales(db):
    """Insert locale rows while avoiding Locale.code uniqueness collisions."""
    for locale_data in LOCALES:
        existing = db.query(Locale).filter(Locale.code == locale_data["code"]).first()
        if existing:
            existing.name = locale_data["name"]
            existing.is_supported = locale_data["is_supported"]
            continue
        db.add(Locale(**locale_data))
    db.commit()


def seed_evaluations(db, llm):
    """Create prompt/run/score rows through the evaluation service."""
    for case in EVALUATION_CASES:
        evaluate(db, llm, EvaluateRequest(**case))


def seed_moderation(db):
    """Create audit logs and policy issues through the moderation service."""
    for case in MODERATION_CASES:
        moderate(db, ModerateRequest(**case))


def seed_triage(db):
    """Create routed issue rows through the triage service."""
    for case in TRIAGE_CASES:
        triage(db, TriageRequest(**case))


def print_summary(db):
    """Print dashboard seed row counts in a compact, readable format."""
    counts = {
        "prompts": db.query(Prompt).count(),
        "runs": db.query(Run).count(),
        "scores": db.query(Score).count(),
        "issues": db.query(Issue).count(),
        "audit_logs": db.query(AuditLog).count(),
    }

    print("Seed data complete.")
    for name, count in counts.items():
        print(f"{name}: {count}")


def main():
    """Seed local dashboard data using app services without starting the API server."""
    init_db()
    db = SessionLocal()
    try:
        llm = MockProvider()
        seed_locales(db)
        seed_evaluations(db, llm)
        seed_moderation(db)
        seed_triage(db)
        print_summary(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
