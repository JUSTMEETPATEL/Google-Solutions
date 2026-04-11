/**
 * FairCheck API client for the TUI.
 *
 * Wraps HTTP calls to the local FastAPI backend.
 * All methods expect the server to already be running on the given port.
 */

import { createReadStream } from "node:fs";
import { basename } from "node:path";

/** Base URL builder for the local API. */
function baseUrl(port: number): string {
  return `http://127.0.0.1:${port}/api/v1`;
}

// ---------- Scan ----------

export interface ScanResult {
  session_id: string;
  status: string;
  protected_attributes: Array<{
    name: string;
    confidence: number;
  }>;
  bias_metrics: Record<string, {
    value: number;
    threshold: number;
    status: "pass" | "warning" | "fail";
  }>;
  risk_level: string;
  [key: string]: unknown;
}

/**
 * Upload model + dataset and run a bias scan.
 *
 * Uses the Web Fetch API with a FormData body.
 * Node 18+ supports fetch and FormData natively.
 */
export async function runScan(
  port: number,
  modelPath: string,
  datasetPath: string,
): Promise<ScanResult> {
  // Node 20+ has a global File constructor. For older versions we fall back
  // to Blob-from-stream. Using the File web API keeps this browser-compat.
  const modelBlob = new Blob([await streamToBuffer(modelPath)]);
  const datasetBlob = new Blob([await streamToBuffer(datasetPath)]);

  const form = new FormData();
  form.append("model", modelBlob, basename(modelPath));
  form.append("dataset", datasetBlob, basename(datasetPath));

  const res = await fetch(`${baseUrl(port)}/scan`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Scan failed (${res.status}): ${text}`);
  }

  return (await res.json()) as ScanResult;
}

// ---------- Sessions ----------

export interface SessionSummary {
  id: string;
  model_path: string;
  risk_level: string;
  created_at: string;
  [key: string]: unknown;
}

/**
 * List past scan sessions.
 */
export async function getSessions(port: number): Promise<SessionSummary[]> {
  const res = await fetch(`${baseUrl(port)}/sessions`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to list sessions (${res.status}): ${text}`);
  }
  return (await res.json()) as SessionSummary[];
}

// ---------- Report ----------

export interface ReportResult {
  path?: string;
  message?: string;
  [key: string]: unknown;
}

/**
 * Request PDF report generation for a session.
 */
export async function generateReport(
  port: number,
  sessionId: string,
): Promise<ReportResult> {
  const res = await fetch(`${baseUrl(port)}/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Report generation failed (${res.status}): ${text}`);
  }

  return (await res.json()) as ReportResult;
}

// ---------- Helpers ----------

/**
 * Read a file into a Buffer via a readable stream.
 */
async function streamToBuffer(filePath: string): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    const stream = createReadStream(filePath);
    stream.on("data", (chunk) => chunks.push(Buffer.from(chunk as Buffer)));
    stream.on("end", () => resolve(Buffer.concat(chunks)));
    stream.on("error", reject);
  });
}
