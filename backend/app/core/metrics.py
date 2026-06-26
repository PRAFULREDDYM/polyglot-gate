from threading import Lock
from typing import Any, Dict, Optional


_LOCK = Lock()
_STATE: Dict[str, Any] = {
    "services": {},
    "failures_by_reason": {},
}


def record(
    service: str,
    latency_ms: int,
    passed: bool,
    failure_reason: Optional[str] = None,
) -> None:
    """Record request volume, latency, pass/fail counts, and failure reasons."""
    with _LOCK:
        service_state = _STATE["services"].setdefault(
            service,
            {
                "count": 0,
                "latency_sum_ms": 0,
                "pass_count": 0,
                "fail_count": 0,
            },
        )
        service_state["count"] += 1
        service_state["latency_sum_ms"] += max(0, int(latency_ms))
        if passed:
            service_state["pass_count"] += 1
        else:
            service_state["fail_count"] += 1

        if failure_reason:
            failures = _STATE["failures_by_reason"]
            failures[failure_reason] = failures.get(failure_reason, 0) + 1


def snapshot() -> Dict[str, Any]:
    """Return a JSON-serializable snapshot of in-process service metrics."""
    with _LOCK:
        services = {}
        for service, service_state in _STATE["services"].items():
            count = service_state["count"]
            avg_latency_ms = (
                round(service_state["latency_sum_ms"] / count, 3) if count else 0
            )
            services[service] = {
                "count": count,
                "avg_latency_ms": avg_latency_ms,
                "pass_count": service_state["pass_count"],
                "fail_count": service_state["fail_count"],
            }

        return {
            "services": services,
            "failures_by_reason": dict(_STATE["failures_by_reason"]),
        }
