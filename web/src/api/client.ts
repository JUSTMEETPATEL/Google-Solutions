/** API client for FairCheck FastAPI backend. */

const BASE = '/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || body.message || JSON.stringify(body);
    } catch { /* body wasn't JSON */ }
    throw new Error(`API Error ${res.status}: ${detail}`);
  }
  return res.json();
}

export async function fetchHealth(): Promise<{ status: string }> {
  const res = await fetch(`${BASE}/health`);
  return handleResponse(res);
}

export async function fetchSessions(): Promise<SessionSummary[]> {
  const res = await fetch(`${BASE}/sessions/`);
  const data = await handleResponse<{ sessions: SessionSummary[] }>(res);
  return data.sessions ?? [];
}

export async function fetchSession(id: string): Promise<SessionDetail> {
  const res = await fetch(`${BASE}/sessions/${id}`);
  return handleResponse(res);
}

export async function runScan(model: File, dataset: File, config?: Record<string, unknown>): Promise<ScanResult> {
  const fd = new FormData();
  fd.append('model', model);
  fd.append('dataset', dataset);
  if (config) fd.append('config', JSON.stringify(config));
  const res = await fetch(`${BASE}/scan/`, { method: 'POST', body: fd });
  return handleResponse(res);
}

export async function submitOversight(sessionId: string, data: OversightData): Promise<{ success: boolean }> {
  const res = await fetch(`${BASE}/oversight/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, ...data }),
  });
  return handleResponse(res);
}

export async function generateReport(sessionId: string, format: string): Promise<Blob> {
  const res = await fetch(`${BASE}/reports/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, format }),
  });
  if (!res.ok) {
    throw new Error(`Report generation failed: ${res.status}`);
  }
  return res.blob();
}

// ─── New Endpoints ────────────────────────────────────────

export async function fetchMitigationRecommendations(sessionId: string): Promise<MitigationResponse> {
  const res = await fetch(`${BASE}/mitigate/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId }),
  });
  return handleResponse(res);
}

export async function applyMitigation(sessionId: string, algorithm: string): Promise<MitigationResponse> {
  const res = await fetch(`${BASE}/mitigate/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, algorithm }),
  });
  return handleResponse(res);
}

export async function compareSessions(baselineId: string, currentId: string): Promise<DriftResult> {
  const res = await fetch(`${BASE}/drift/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ baseline_session_id: baselineId, current_session_id: currentId }),
  });
  return handleResponse(res);
}

export async function fetchModelHistory(modelName: string): Promise<ModelHistory> {
  const res = await fetch(`${BASE}/drift/history/${encodeURIComponent(modelName)}`);
  return handleResponse(res);
}

// ─── Types ────────────────────────────────────────────────

export interface SessionSummary {
  id: string;
  model_name: string;
  created_at: string;
  risk_level: string;
}

export interface SessionDetail extends SessionSummary {
  analysis_results: Record<string, any>;
  explanations?: Record<string, Record<string, MetricExplanation>>;
  intersectional_analysis?: IntersectionalAnalysis | null;
  confidence_intervals?: Record<string, Record<string, ConfidenceInterval>> | null;
  feature_attribution?: FeatureAttribution | null;
  recommendations?: MitigationRecommendation[];
  mitigation_history?: any[];
  oversight_decision?: string | null;
  model_metadata?: Record<string, any>;
  dataset_metadata?: Record<string, any>;
}

export interface ScanResult {
  session_id?: string;
  status?: string;
  model_name?: string;
  model_file?: string;
  dataset_file?: string;
  message?: string;
  analysis_results?: Record<string, any>;
  explanations?: Record<string, Record<string, MetricExplanation>>;
  intersectional_analysis?: IntersectionalAnalysis | null;
  confidence_intervals?: Record<string, Record<string, ConfidenceInterval>> | null;
  feature_attribution?: FeatureAttribution | null;
  recommendations?: MitigationRecommendation[];
}

export interface OversightData {
  reviewer: string;
  date: string;
  decision: string;
  notes?: string;
}

export interface MetricExplanation {
  summary: string;
  detail: string;
  recommendation: string;
  severity: string;
}

export interface IntersectionalAnalysis {
  intersections: IntersectionResult[];
  most_disadvantaged: {
    group: string;
    intersection: string;
    predicted_positive_rate: number;
    count: number;
  } | null;
}

export interface IntersectionResult {
  intersection: string;
  metrics: Record<string, any>;
  performance_breakdown: Record<string, any>;
  group_rates: Record<string, { count: number; predicted_positive_rate: number; actual_positive_rate: number }>;
  n_valid_groups: number;
}

export interface ConfidenceInterval {
  point_estimate: number | null;
  ci_lower: number | null;
  ci_upper: number | null;
  is_significant: boolean;
  n_bootstrap: number;
  confidence_level: number;
  note?: string;
}

export interface FeatureAttribution {
  global_importance: Record<string, { importance_mean: number; importance_std: number }>;
  per_group_importance: Record<string, Record<string, Record<string, number>>>;
  bias_drivers: BiasDriver[];
}

export interface BiasDriver {
  feature: string;
  attribute: string;
  importance_spread: number;
  most_affected_group: string;
  least_affected_group: string;
  explanation: string;
}

export interface MitigationRecommendation {
  algorithm: string;
  category: string;
  confidence: string;
  rationale: string;
  addresses: string[];
  priority: number;
  target_attributes?: string[];
}

export interface MitigationResponse {
  status: string;
  session_id: string;
  algorithm_applied?: string | null;
  recommendations: MitigationRecommendation[];
  message: string;
}

export interface DriftResult {
  baseline_session_id: string;
  current_session_id: string;
  overall_drift: string;
  risk_change: string;
  baseline_risk_level: string;
  current_risk_level: string;
  per_attribute: Record<string, any>;
  alerts: DriftAlert[];
  summary: string;
  stats: {
    metrics_improved: number;
    metrics_degraded: number;
    metrics_stable: number;
  };
}

export interface DriftAlert {
  attribute: string;
  metric: string;
  severity: string;
  message: string;
}

export interface ModelHistory {
  model_name: string;
  total_audits: number;
  history: { session_id: string; date: string; risk_level: string }[];
}
