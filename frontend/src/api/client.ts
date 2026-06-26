export interface EvaluateRequest {
  prompt_text: string;
  locale?: string;
  reference_answer?: string | null;
  model_name?: string | null;
}

export interface ScoreBreakdown {
  correctness: number;
  formatting: number;
  locale_coverage: number;
  regression_pass: boolean;
  overall: number;
}

export interface EvaluateResponse {
  run_id: number;
  prompt_id: number;
  output_text: string;
  locale: string;
  latency_ms: number;
  scores: ScoreBreakdown;
  passed: boolean;
  failure_reasons: string[];
}

export interface EvaluationHistoryItem {
  run_id: number;
  prompt_id: number;
  prompt_text: string;
  locale: string;
  output_text: string;
  overall: number;
  passed: boolean;
  created_at: string;
}

export interface MultiLocaleEvaluateRequest {
  prompt_text: string;
  locales?: string[];
  reference_answer?: string | null;
}

export interface LocaleResult {
  locale: string;
  run_id: number;
  scores: ScoreBreakdown;
  passed: boolean;
}

export interface MultiLocaleEvaluateResponse {
  prompt_id: number;
  results: LocaleResult[];
  consistency_score: number;
  worst_locale: string;
  summary: string;
}

export interface ModerateRequest {
  text: string;
  locale?: string;
  context?: string | null;
}

export interface PolicyViolation {
  rule_id: string;
  rule_name: string;
  severity: string;
}

export interface ModerateResponse {
  audit_id: number;
  is_safe: boolean;
  labels: string[];
  policy_violations: PolicyViolation[];
  action: "allow" | "flag" | "block";
}

export interface TriageRequest {
  run_id?: number | null;
  prompt_text: string;
  output_text: string;
  locale?: string;
  reported_issue?: string | null;
}

export interface TriageResponse {
  issue_id: number;
  issue_category: string;
  confidence: number;
  suggested_fix: string;
  route_to: string;
}

export interface TriageIssueSummary extends TriageResponse {
  status?: string;
  created_at?: string;
}

export interface ServiceMetrics {
  count: number;
  avg_latency_ms: number;
  pass_count: number;
  fail_count: number;
}

export interface MetricsResponse {
  services: Record<string, ServiceMetrics>;
  failures_by_reason: Record<string, number>;
}

export async function evaluatePrompt(
  req: EvaluateRequest
): Promise<EvaluateResponse> {
  return postJson("/api/evaluate", req);
}

export async function evaluateMultiLocale(
  req: MultiLocaleEvaluateRequest
): Promise<MultiLocaleEvaluateResponse> {
  return postJson("/api/evaluate/multi-locale", req);
}

export async function moderateText(
  req: ModerateRequest
): Promise<ModerateResponse> {
  return postJson("/api/moderate", req);
}

export async function triagePrompt(
  req: TriageRequest
): Promise<TriageResponse> {
  return postJson("/api/triage", req);
}

export async function listIssues(
  limit = 50,
  offset = 0
): Promise<TriageIssueSummary[]> {
  return getJson(`/api/triage/issues?limit=${limit}&offset=${offset}`);
}

export async function getMetrics(): Promise<MetricsResponse> {
  return getJson("/api/metrics");
}

export async function getEvaluationHistory(
  limit = 50,
  offset = 0,
  locale?: string
): Promise<EvaluationHistoryItem[]> {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset)
  });
  if (locale) {
    params.set("locale", locale);
  }

  return getJson(`/api/evaluate/history?${params.toString()}`);
}

async function postJson<TResponse, TRequest>(
  path: string,
  body: TRequest
): Promise<TResponse> {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });

  return parseJsonResponse<TResponse>(response);
}

async function getJson<TResponse>(path: string): Promise<TResponse> {
  const response = await fetch(path);
  return parseJsonResponse<TResponse>(response);
}

async function parseJsonResponse<TResponse>(
  response: Response
): Promise<TResponse> {
  if (!response.ok) {
    const body = await response.text();
    throw new Error(
      `API request failed with status ${response.status}: ${body || response.statusText}`
    );
  }

  return response.json() as Promise<TResponse>;
}
