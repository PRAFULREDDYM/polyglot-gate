import { FormEvent, useState } from "react";

import { ModerateResponse, moderateText } from "../api/client";

const locales = ["en", "es", "fr", "de", "ja"];

export function ModerationFlags() {
  const [text, setText] = useState("");
  const [locale, setLocale] = useState("en");
  const [context, setContext] = useState("");
  const [result, setResult] = useState<ModerateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      setResult(
        await moderateText({
          text,
          locale,
          context: context.trim() || null
        })
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Moderation check failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="page">
      <h2>Moderation Flags</h2>
      <form className="panel form-grid" onSubmit={submit}>
        <label>
          Text
          <textarea
            value={text}
            onChange={(event) => setText(event.target.value)}
            required
          />
        </label>
        <div className="form-row">
          <label>
            Locale
            <select value={locale} onChange={(event) => setLocale(event.target.value)}>
              {locales.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <label>
            Context
            <input
              value={context}
              onChange={(event) => setContext(event.target.value)}
              placeholder="Optional"
            />
          </label>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? "Checking..." : "Check Moderation"}
        </button>
      </form>

      {error && <div className="error">{error}</div>}
      {result && (
        <section className="panel page">
          <div className={`status-banner ${result.action}`}>
            {result.is_safe ? "Safe to allow" : `Action: ${result.action}`}
          </div>
          {result.policy_violations.length > 0 ? (
            <ul>
              {result.policy_violations.map((violation) => (
                <li key={violation.rule_id}>
                  <strong>{violation.rule_id}</strong> · {violation.rule_name} ·{" "}
                  {violation.severity}
                </li>
              ))}
            </ul>
          ) : (
            <p className="muted">No policy violations matched.</p>
          )}
        </section>
      )}
      {/* TODO Stage 14+: add GET /api/moderate/audits to list recent audit_log rows. */}
    </section>
  );
}
