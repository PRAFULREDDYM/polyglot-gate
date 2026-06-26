from app.models.audit_log import AuditLog


def test_moderate_flags_email_pii(client):
    """Proves POST /moderate flags email-address-like text."""
    response = client.post(
        "/api/moderate",
        json={"text": "Contact test@example.com for details.", "locale": "en"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "flag"
    assert data["is_safe"] is False
    assert "PII_EMAIL" in data["labels"]


def test_moderate_allows_clean_text(client):
    """Proves POST /moderate allows text with no matching rules."""
    response = client.post(
        "/api/moderate",
        json={"text": "This is a clean product update.", "locale": "en"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "allow"
    assert data["is_safe"] is True
    assert data["labels"] == []


def test_moderate_creates_audit_log_row(client, db):
    """Proves moderation writes an audit log row for every request."""
    response = client.post(
        "/api/moderate",
        json={"text": "This is a clean product update.", "locale": "en"},
    )

    assert response.status_code == 200
    audit_id = response.json()["audit_id"]
    audit_log = db.get(AuditLog, audit_id)
    assert audit_log is not None
    assert audit_log.action == "allow"
