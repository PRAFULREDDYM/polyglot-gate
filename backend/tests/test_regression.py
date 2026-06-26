from app.services.llm_provider import MockProvider
from app.services.regression_runner import load_cases, run_suite


def test_regression_suite_runs_with_mock_provider(db):
    """Proves the regression suite runs with mock LLM output and reports fixture shape."""
    result = run_suite(db, MockProvider())
    cases = load_cases()

    assert result["total"] == len(cases)
    assert set(result) == {"total", "passed", "failed", "failures"}
    assert isinstance(result["passed"], int)
    assert isinstance(result["failed"], int)
    assert isinstance(result["failures"], list)
    assert result["passed"] + result["failed"] == result["total"]
