from app.models.run import Run


def test_evaluate_basic_prompt_returns_scores(client):
    """Proves POST /evaluate returns generated text and score details."""
    response = client.post(
        "/api/evaluate",
        json={
            "prompt_text": "hello world",
            "locale": "en",
            "reference_answer": "hello world",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["output_text"] == "[MOCK-en] hello world"
    assert data["scores"]["overall"] >= 0
    assert data["latency_ms"] == 10


def test_evaluate_empty_prompt_returns_422(client):
    """Proves POST /evaluate rejects whitespace-only prompts."""
    response = client.post(
        "/api/evaluate",
        json={"prompt_text": "   ", "locale": "en"},
    )

    assert response.status_code == 422


def test_evaluate_multi_locale_returns_one_result_per_locale(client):
    """Proves POST /evaluate/multi-locale returns one result per requested locale."""
    locales = ["en", "es", "fr"]
    response = client.post(
        "/api/evaluate/multi-locale",
        json={"prompt_text": "hello world", "locales": locales},
    )

    assert response.status_code == 200
    data = response.json()
    assert [result["locale"] for result in data["results"]] == locales
    assert len(data["results"]) == len(locales)


def test_evaluate_multi_locale_shares_one_prompt_id(client, db):
    """Proves multi-locale evaluation stores every run under one prompt row."""
    response = client.post(
        "/api/evaluate/multi-locale",
        json={"prompt_text": "shared prompt", "locales": ["en", "es", "fr"]},
    )

    assert response.status_code == 200
    prompt_id = response.json()["prompt_id"]
    run_prompt_ids = {run.prompt_id for run in db.query(Run).all()}
    assert run_prompt_ids == {prompt_id}


def test_evaluation_history_returns_recent_runs_ordered_correctly(client):
    """Proves GET /evaluate/history returns newest scored runs first."""
    first = client.post(
        "/api/evaluate",
        json={"prompt_text": "first history prompt", "locale": "en"},
    )
    second = client.post(
        "/api/evaluate",
        json={"prompt_text": "second history prompt", "locale": "fr"},
    )

    response = client.get("/api/evaluate/history?limit=10&offset=0")
    filtered = client.get("/api/evaluate/history?limit=10&offset=0&locale=fr")

    assert first.status_code == 200
    assert second.status_code == 200
    assert response.status_code == 200
    items = response.json()
    assert [item["run_id"] for item in items[:2]] == [
        second.json()["run_id"],
        first.json()["run_id"],
    ]
    assert items[0]["prompt_text"] == "second history prompt"
    assert items[0]["overall"] >= 0
    assert "created_at" in items[0]

    assert filtered.status_code == 200
    filtered_items = filtered.json()
    assert len(filtered_items) == 1
    assert filtered_items[0]["locale"] == "fr"
