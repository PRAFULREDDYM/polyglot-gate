def test_triage_classifies_translation_issue_from_report_text(client):
    """Proves POST /triage routes reporter translation wording to i18n."""
    response = client.post(
        "/api/triage",
        json={
            "prompt_text": "Write a welcome message.",
            "output_text": "Bonjour",
            "locale": "fr",
            "reported_issue": "wrong language translation issue",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["issue_category"] == "translation"
    assert data["confidence"] == 0.8
    assert data["route_to"] == "i18n-team"


def test_triage_unsupported_locale_detected(client):
    """Proves POST /triage detects locales outside the supported set."""
    response = client.post(
        "/api/triage",
        json={
            "prompt_text": "Write a welcome message.",
            "output_text": "Welcome",
            "locale": "zz",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["issue_category"] == "unsupported_locale"
    assert data["confidence"] == 0.9
    assert data["route_to"] == "i18n-team"


def test_triage_list_issues_endpoint_returns_created_issue(client):
    """Proves GET /triage/issues returns issues created through POST /triage."""
    created = client.post(
        "/api/triage",
        json={
            "prompt_text": "Write a product title.",
            "output_text": "**Broken title",
            "locale": "en",
            "reported_issue": "markdown broken layout",
        },
    )
    listed = client.get("/api/triage/issues?limit=50&offset=0")

    assert created.status_code == 200
    assert listed.status_code == 200
    issues = listed.json()
    assert issues[0]["issue_id"] == created.json()["issue_id"]
    assert issues[0]["issue_category"] == "formatting"
