import { FormEvent, useState } from "react";

import {
  EvaluateResponse,
  MultiLocaleEvaluateResponse,
  evaluateMultiLocale,
  evaluatePrompt
} from "../api/client";
import { ScoreBadge } from "../components/ScoreBadge";

const locales = ["en", "es", "fr", "de", "ja"];

export function SubmitPrompt() {
  const [promptText, setPromptText] = useState("");
  const [locale, setLocale] = useState("en");
  const [referenceAnswer, setReferenceAnswer] = useState("");
  const [singleResult, setSingleResult] = useState<EvaluateResponse | null>(null);
  const [multiResult, setMultiResult] = useState<MultiLocaleEvaluateResponse | null>(null);
  const [loading, setLoading] = useState<"single" | "multi" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function runSingle(event: FormEvent) {
    event.preventDefault();
    setLoading("single");
    setError(null);
    setMultiResult(null);
    try {
      const result = await evaluatePrompt({
        prompt_text: promptText,
        locale,
        reference_answer: referenceAnswer.trim() || null
      });
      setSingleResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Evaluation failed");
    } finally {
      setLoading(null);
    }
  }

  async function runMulti() {
    setLoading("multi");
    setError(null);
    setSingleResult(null);
    try {
      const result = await evaluateMultiLocale({
        prompt_text: promptText,
        locales: ["en", "es", "fr"],
        reference_answer: referenceAnswer.trim() || null
      });
      setMultiResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Multi-locale check failed");
    } finally {
      setLoading(null);
    }
  }

  return (
    <section className="page">
      <h2>Submit Prompt</h2>
      <form className="panel form-grid" onSubmit={runSingle}>
        <label>
          Prompt text
          <textarea
            value={promptText}
            onChange={(event) => setPromptText(event.target.value)}
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
        </div>
        <label>
          Reference answer
          <textarea
            value={referenceAnswer}
            onChange={(event) => setReferenceAnswer(event.target.value)}
          />
        </label>
        <div className="button-row">
          <button type="submit" disabled={loading !== null}>
            {loading === "single" ? "Running..." : "Run Single-Locale Evaluation"}
          </button>
          <button
            type="button"
            className="secondary"
            onClick={runMulti}
            disabled={loading !== null || !promptText.trim()}
          >
            {loading === "multi" ? "Running..." : "Run Multi-Locale Check (en/es/fr)"}
          </button>
        </div>
      </form>

      {error && <div className="error">{error}</div>}
      {singleResult && <SingleResult result={singleResult} />}
      {multiResult && <MultiResult result={multiResult} />}
    </section>
  );
}

function SingleResult({ result }: { result: EvaluateResponse }) {
  return (
    <section className="panel page">
      <div className={`status-banner ${result.passed ? "passed" : "failed"}`}>
        {result.passed ? "Passed" : "Failed"} · run #{result.run_id} · {result.latency_ms} ms
      </div>
      <p>{result.output_text}</p>
      <div className="score-grid">
        <ScoreBadge label="Correctness" score={result.scores.correctness} />
        <ScoreBadge label="Formatting" score={result.scores.formatting} />
        <ScoreBadge label="Locale coverage" score={result.scores.locale_coverage} />
        <ScoreBadge
          label="Regression"
          score={result.scores.regression_pass ? 1 : 0}
        />
        <ScoreBadge label="Overall" score={result.scores.overall} />
      </div>
      {result.failure_reasons.length > 0 && (
        <ul>
          {result.failure_reasons.map((reason) => (
            <li key={reason}>{reason}</li>
          ))}
        </ul>
      )}
    </section>
  );
}

function MultiResult({ result }: { result: MultiLocaleEvaluateResponse }) {
  return (
    <section className="panel page">
      <h3>Multi-locale consistency</h3>
      <ScoreBadge label="Consistency" score={result.consistency_score} />
      <p>{result.summary}</p>
      <div className="page">
        {result.results.map((localeResult) => (
          <div key={localeResult.locale} className="panel">
            <strong>{localeResult.locale}</strong>
            <div className="score-grid">
              <ScoreBadge label="Overall" score={localeResult.scores.overall} />
              <ScoreBadge label="Correctness" score={localeResult.scores.correctness} />
              <ScoreBadge label="Formatting" score={localeResult.scores.formatting} />
              <ScoreBadge
                label="Locale coverage"
                score={localeResult.scores.locale_coverage}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
