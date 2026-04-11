/**
 * Python FastAPI server orchestrator.
 *
 * Silently spawns the FairCheck FastAPI backend as a child process,
 * waits for it to be ready via port file + health polling, and
 * provides graceful shutdown on process exit.
 */

import { spawn, type ChildProcess } from "node:child_process";
import { readFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";

const FAIRCHECK_DIR = join(homedir(), ".faircheck");
const PORT_FILE = join(FAIRCHECK_DIR, "port");
const POLL_INTERVAL_MS = 300;
const MAX_WAIT_MS = 30_000;

let serverProcess: ChildProcess | null = null;

/**
 * Read the port file written by the FastAPI server.
 * Retries until the file exists or timeout.
 */
async function readPortFile(deadline: number): Promise<number> {
  while (Date.now() < deadline) {
    try {
      const raw = await readFile(PORT_FILE, "utf-8");
      const port = parseInt(raw.trim(), 10);
      if (!isNaN(port) && port > 0) return port;
    } catch {
      // File doesn't exist yet — keep waiting.
    }
    await sleep(POLL_INTERVAL_MS);
  }
  throw new Error(`Timed out waiting for port file at ${PORT_FILE}`);
}

/**
 * Poll the health endpoint until it returns 200.
 */
async function waitForHealth(port: number, deadline: number): Promise<void> {
  const url = `http://127.0.0.1:${port}/api/v1/health`;
  while (Date.now() < deadline) {
    try {
      const res = await fetch(url);
      if (res.ok) return;
    } catch {
      // Server not ready yet — keep polling.
    }
    await sleep(POLL_INTERVAL_MS);
  }
  throw new Error(`Timed out waiting for health check at ${url}`);
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Spawn the FairCheck FastAPI server and wait until it is ready.
 *
 * @returns The port the server is listening on.
 */
export async function spawnServer(): Promise<number> {
  const deadline = Date.now() + MAX_WAIT_MS;

  // Resolve the project root (one level above tui/)
  const projectRoot = join(import.meta.dirname ?? process.cwd(), "..");

  serverProcess = spawn("uv", ["run", "python", "-m", "faircheck.api.server"], {
    cwd: projectRoot,
    detached: true,
    stdio: "ignore",
  });

  // Ensure the child doesn't keep us alive if the parent exits
  serverProcess.unref();

  // Register cleanup handlers
  const cleanup = () => killServer();
  process.on("exit", cleanup);
  process.on("SIGINT", cleanup);
  process.on("SIGTERM", cleanup);

  // Wait for the port file and health check
  const port = await readPortFile(deadline);
  await waitForHealth(port, deadline);

  return port;
}

/**
 * Kill the spawned server process, if any.
 */
export function killServer(): void {
  if (serverProcess && !serverProcess.killed) {
    // Kill the entire process group (detached: true created a new group)
    try {
      process.kill(-serverProcess.pid!, "SIGTERM");
    } catch {
      // Process may already be gone.
      serverProcess.kill("SIGTERM");
    }
    serverProcess = null;
  }
}
