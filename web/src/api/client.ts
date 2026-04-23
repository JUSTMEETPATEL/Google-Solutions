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

// Types
export interface SessionSummary {
  id: string;
  model_name: string;
  created_at: string;
  risk_level: string;
}

export interface SessionDetail extends SessionSummary {
  analysis_results: Record<string, any>;
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
}

export interface OversightData {
  reviewer: string;
  date: string;
  decision: string;
  notes?: string;
}

