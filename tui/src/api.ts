/** FairCheck TUI — API client for FastAPI backend. */

import { readFileSync, existsSync } from "fs";
import { homedir } from "os";
import { join } from "path";

const DEFAULT_PORT = 8000;

export function getBaseUrl(): string {
  try {
    const portFile = join(homedir(), ".faircheck", "port");
    if (existsSync(portFile)) {
      const port = parseInt(readFileSync(portFile, "utf-8").trim(), 10);
      if (!isNaN(port)) return `http://localhost:${port}`;
    }
  } catch {
    // fall through
  }
  return `http://localhost:${DEFAULT_PORT}`;
}

export async function healthCheck(): Promise<boolean> {
  try {
    const url = getBaseUrl();
    const res = await fetch(`${url}/api/health`);
    return res.ok;
  } catch {
    return false;
  }
}

export async function runScan(
  modelPath: string,
  datasetPath: string,
  config?: Record<string, unknown>
): Promise<Record<string, unknown>> {
  const url = getBaseUrl();
  const formData = new FormData();

  const modelBuf = readFileSync(modelPath);
  const datasetBuf = readFileSync(datasetPath);
  const modelBlob = new Blob([modelBuf]);
  const datasetBlob = new Blob([datasetBuf]);

  formData.append("model", modelBlob, modelPath.split("/").pop()!);
  formData.append("dataset", datasetBlob, datasetPath.split("/").pop()!);
  if (config) {
    formData.append("config", JSON.stringify(config));
  }

  const res = await fetch(`${url}/api/scan`, {
    method: "POST",
    body: formData,
  });
  return res.json() as Promise<Record<string, unknown>>;
}

export async function listSessions(): Promise<Record<string, unknown>[]> {
  const url = getBaseUrl();
  const res = await fetch(`${url}/api/sessions`);
  return res.json() as Promise<Record<string, unknown>[]>;
}

export async function getSession(
  id: string
): Promise<Record<string, unknown>> {
  const url = getBaseUrl();
  const res = await fetch(`${url}/api/sessions/${id}`);
  return res.json() as Promise<Record<string, unknown>>;
}

export async function generateReport(
  sessionId: string,
  format: string = "pdf"
): Promise<Record<string, unknown>> {
  const url = getBaseUrl();
  const res = await fetch(`${url}/api/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, format }),
  });
  return res.json() as Promise<Record<string, unknown>>;
}
