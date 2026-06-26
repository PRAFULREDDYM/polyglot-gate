import { FormEvent, useEffect, useState } from "react";

import { TriageIssueSummary, listIssues, triagePrompt } from "../api/client";

const locales = ["en", "es", "fr", "de", "ja", "pt"];

export function TriageDashboard() {
  const [issues, setIssues] = useState<TriageIssueSummary[]>([]);
  const [promptText, setPromptText] = useState("");
  const [outputText, setOutputText] = useState("");
  const [locale, setLocale] = useState("en");
  const [reportedIssue, setReportedIssue] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refreshIssues() {
    setIssues(await listIssues(50, 0));
  }

  useEffect(() => {
    refreshIssues().catch((err) =>
      setError(err instanceof Error ? err.message : "Unable to load issues")
    );
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await triagePrompt({
        prompt_text: promptText,
        output_text: outputText,
        locale,
        reported_issue: reportedIssue.trim() || null
      });
      setPromptText("");
      setOutputText("");
      setReportedIssue("");
      await refreshIssues();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Triage submission failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="page">
      <h2>Triage Dashboard</h2>
      <form className="panel form-grid" onSubmit={submit}>
        <label>
          Prompt text
          <textarea
            value={promptText}
            onChange={(event) => setPromptText(event.target.value)}
            required
          />
        </label>
        <label>
          Output text
          <textarea
            value={outputText}
            onChange={(event) => setOutputText(event.target.value)}
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
            Reported issue
            <input
              value={reportedIssue}
              onChange={(event) => setReportedIssue(event.target.value)}
              placeholder="Optional"
            />
          </label>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? "Submitting..." : "Submit for Triage"}
        </button>
      </form>

      {error && <div className="error">{error}</div>}
      <section className="panel">
        <h3>Issue history</h3>
        {/* TODO Stage 14+: extend GET /api/triage/issues to include status and created_at from Issue rows. */}
        <table>
          <thead>
            <tr>
              <th>id</th>
              <th>category</th>
              <th>confidence</th>
              <th>suggested_fix</th>
              <th>route_to</th>
              <th>status</th>
              <th>created_at</th>
            </tr>
          </thead>
          <tbody>
            {issues.map((issue) => (
              <tr key={issue.issue_id}>
                <td>{issue.issue_id}</td>
                <td>
                  <span className={`category-badge category-${issue.issue_category}`}>
                    <span className="category-dot" />
                    {issue.issue_category}
                  </span>
                </td>
                <td>{Math.round(issue.confidence * 100)}%</td>
                <td>{issue.suggested_fix}</td>
                <td>{issue.route_to}</td>
                <td>{issue.status ?? "not exposed"}</td>
                <td>{issue.created_at ?? "not exposed"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {issues.length === 0 && <p className="muted">No issues found.</p>}
      </section>
    </section>
  );
}
