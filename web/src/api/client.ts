/** API client for FairCheck FastAPI backend. */

const BASE = '/api';

export async function fetchHealth(): Promise<{ status: string }> {
  const res = await fetch(`${BASE}/health`);
  return res.json();
}

export async function fetchSessions(): Promise<SessionSummary[]> {
  const res = await fetch(`${BASE}/sessions`);
  return res.json();
}

export async function fetchSession(id: string): Promise<SessionDetail> {
  const res = await fetch(`${BASE}/sessions/${id}`);
  return res.json();
}

export async function runScan(model: File, dataset: File, config?: Record<string, unknown>): Promise<ScanResult> {
  const fd = new FormData();
  fd.append('model', model);
  fd.append('dataset', dataset);
  if (config) fd.append('config', JSON.stringify(config));
  const res = await fetch(`${BASE}/scan`, { method: 'POST', body: fd });
  return res.json();
}

export async function submitOversight(sessionId: string, data: OversightData): Promise<{ success: boolean }> {
  const res = await fetch(`${BASE}/oversight`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, ...data }),
  });
  return res.json();
}

export async function generateReport(sessionId: string, format: string): Promise<Blob> {
  const res = await fetch(`${BASE}/report`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, format }),
  });
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
  session_id: string;
  analysis_results: Record<string, any>;
}

export interface OversightData {
  reviewer: string;
  date: string;
  decision: string;
  notes?: string;
}
