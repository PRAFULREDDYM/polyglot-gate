import { useEffect, useState } from "react";

import {
  EvaluationHistoryItem,
  MetricsResponse,
  getEvaluationHistory,
  getMetrics
} from "../api/client";
import { ScoreBadge } from "../components/ScoreBadge";

const localeFilters = ["", "en", "es", "fr", "de", "ja"];

export function EvaluationResults() {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [history, setHistory] = useState<EvaluationHistoryItem[]>([]);
  const [locale, setLocale] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(true);

  useEffect(() => {
    getMetrics()
      .then(setMetrics)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Unable to load metrics")
      )
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    setHistoryLoading(true);
    getEvaluationHistory(20, 0, locale || undefined)
      .then(setHistory)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Unable to load history")
      )
      .finally(() => setHistoryLoading(false));
  }, [locale]);

  const evaluate = metrics?.services.evaluate;

  return (
    <section className="page">
      <h2>Evaluation Overview / Health</h2>
      {loading && <p>Loading metrics...</p>}
      {error && <div className="error">{error}</div>}
      {evaluate && (
        <section className="panel">
          <div className="form-row">
            <Metric label="Total evaluations" value={evaluate.count} />
            <Metric label="Average latency" value={`${evaluate.avg_latency_ms} ms`} />
            <Metric label="Pass count" value={evaluate.pass_count} />
            <Metric label="Fail count" value={evaluate.fail_count} />
          </div>
        </section>
      )}
      {metrics && !evaluate && (
        <p className="muted">No evaluation traffic recorded yet.</p>
      )}
      {metrics && (
        <section className="panel">
          <h3>Failures by reason</h3>
          {Object.keys(metrics.failures_by_reason).length > 0 ? (
            <ul>
              {Object.entries(metrics.failures_by_reason).map(([reason, count]) => (
                <li key={reason}>
                  {reason}: {count}
                </li>
              ))}
            </ul>
          ) : (
            <p className="muted">No failure reasons recorded.</p>
          )}
        </section>
      )}
      <section className="panel">
        <div className="form-row">
          <div>
            <h3>Recent evaluation runs</h3>
            <p className="muted">Newest 20 scored runs from evaluation history.</p>
          </div>
          <label>
            Locale filter
            <select value={locale} onChange={(event) => setLocale(event.target.value)}>
              {localeFilters.map((option) => (
                <option key={option || "all"} value={option}>
                  {option || "all"}
                </option>
              ))}
            </select>
          </label>
        </div>
        {historyLoading ? (
          <p>Loading history...</p>
        ) : history.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>prompt_text</th>
                <th>locale</th>
                <th>overall</th>
                <th>passed</th>
                <th>created_at</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.run_id}>
                  <td title={item.prompt_text}>{truncate(item.prompt_text, 60)}</td>
                  <td>{item.locale}</td>
                  <td>
                    <ScoreBadge label="Overall" score={item.overall} />
                  </td>
                  <td>{item.passed ? "passed" : "failed"}</td>
                  <td>{new Date(item.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="muted">No evaluation runs found.</p>
        )}
      </section>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <p className="muted">{label}</p>
      <h3>{value}</h3>
    </div>
  );
}

function truncate(value: string, maxLength: number) {
  if (value.length <= maxLength) {
    return value;
  }
  return `${value.slice(0, maxLength - 1)}...`;
}
