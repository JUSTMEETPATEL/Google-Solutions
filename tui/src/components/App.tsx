/**
 * App.tsx — Root Ink application component.
 *
 * State machine: connecting → scanning → prompting → results
 * Hotkeys: [W] opens web dashboard (stub), [R] generates report.
 * CI mode: bypasses Ink entirely with raw stdout output.
 */

import React, { useState, useEffect } from "react";
import { Box, Text, useApp, useInput } from "ink";
import Spinner from "ink-spinner";

import { spawnServer, killServer } from "../orchestrator.js";
import {
  runScan,
  getSessions,
  generateReport,
  type ScanResult,
  type SessionSummary,
} from "../api.js";
import { MetricsTable, type MetricRow } from "./MetricsTable.js";
import { AttributePrompt } from "./AttributePrompt.js";
import { SessionList } from "./SessionList.js";

type AppState =
  | "connecting"
  | "scanning"
  | "prompting"
  | "results"
  | "sessions"
  | "error";

interface AppProps {
  model: string;
  dataset: string;
  ci: boolean;
  command: "scan" | "sessions";
}

/**
 * Convert raw API bias_metrics to MetricRow array.
 */
function toMetricRows(
  biasMetrics: ScanResult["bias_metrics"],
): MetricRow[] {
  return Object.entries(biasMetrics).map(([name, data]) => ({
    name,
    value: data.value,
    threshold: data.threshold,
    status: data.status,
  }));
}

/**
 * CI mode: print results to stdout and exit with appropriate code.
 * This function does NOT use React/Ink at all.
 */
export async function runCiMode(
  model: string,
  dataset: string,
): Promise<void> {
  try {
    process.stderr.write("Starting FairCheck server...\n");
    const port = await spawnServer();
    process.stderr.write(`Server ready on port ${port}\n`);

    const result = await runScan(port, model, dataset);
    const metrics = toMetricRows(result.bias_metrics);

    // Print results as structured text
    process.stdout.write("\n--- FairCheck Bias Scan Results ---\n\n");
    process.stdout.write(`Model: ${model}\n`);
    process.stdout.write(`Dataset: ${dataset}\n`);
    process.stdout.write(`Risk Level: ${result.risk_level}\n\n`);

    for (const m of metrics) {
      const status = m.status.toUpperCase().padEnd(4);
      process.stdout.write(
        `  ${m.name.padEnd(30)} ${m.value.toFixed(4).padStart(10)}  (threshold: ${m.threshold.toFixed(2)})  [${status}]\n`,
      );
    }

    const failures = metrics.filter((m) => m.status === "fail");
    process.stdout.write(`\nTotal: ${metrics.length} metrics | ${failures.length} failed\n`);

    // Also output JSON for machine parsing
    process.stdout.write(`\n${JSON.stringify(result, null, 2)}\n`);

    killServer();
    process.exit(failures.length > 0 ? 1 : 0);
  } catch (err) {
    process.stderr.write(
      `Error: ${err instanceof Error ? err.message : String(err)}\n`,
    );
    killServer();
    process.exit(1);
  }
}

/**
 * Interactive Ink application for TUI mode.
 */
export function App({ model, dataset, ci, command }: AppProps): React.JSX.Element {
  const { exit } = useApp();
  const [state, setState] = useState<AppState>(
    command === "sessions" ? "sessions" : "connecting",
  );
  const [port, setPort] = useState<number>(0);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [error, setError] = useState<string>("");
  const [reportStatus, setReportStatus] = useState<string>("");

  // Boot sequence: spawn server → run scan
  useEffect(() => {
    if (command === "sessions") {
      // Sessions mode: just list sessions
      (async () => {
        try {
          const p = await spawnServer();
          setPort(p);
          const sess = await getSessions(p);
          setSessions(sess);
          setState("sessions");
        } catch (err) {
          setError(err instanceof Error ? err.message : String(err));
          setState("error");
        }
      })();
      return;
    }

    // Scan mode
    (async () => {
      try {
        const p = await spawnServer();
        setPort(p);
        setState("scanning");

        const result = await runScan(p, model, dataset);
        setScanResult(result);
        setState("results");
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
        setState("error");
      }
    })();
  }, [model, dataset, command]);

  // Hotkeys — only active in results state
  useInput(
    (input, _key) => {
      if (state !== "results" || !scanResult) return;

      if (input === "w" || input === "W") {
        // [W] opens web dashboard — stub until Phase 11
        setReportStatus("🌐 Spawning Vite server at localhost:5173...");
      }

      if (input === "r" || input === "R") {
        // [R] generate report
        setReportStatus("📄 Generating report...");
        generateReport(port, scanResult.session_id)
          .then((res) => {
            setReportStatus(
              `✅ Report saved: ${res.path ?? "check server output"}`,
            );
          })
          .catch((err) => {
            setReportStatus(
              `❌ Report failed: ${err instanceof Error ? err.message : String(err)}`,
            );
          });
      }

      if (input === "q" || input === "Q") {
        killServer();
        exit();
      }
    },
  );

  // --- Render based on state ---

  if (state === "connecting") {
    return (
      <Box>
        <Text color="cyan">
          <Spinner type="dots" />{" "}
        </Text>
        <Text>Starting FairCheck server...</Text>
      </Box>
    );
  }

  if (state === "scanning") {
    return (
      <Box>
        <Text color="cyan">
          <Spinner type="dots" />{" "}
        </Text>
        <Text>
          Running bias scan on <Text bold>{model}</Text>...
        </Text>
      </Box>
    );
  }

  if (state === "error") {
    return (
      <Box flexDirection="column">
        <Text color="red" bold>
          ✗ Error
        </Text>
        <Text color="red">{error}</Text>
      </Box>
    );
  }

  if (state === "sessions") {
    return (
      <Box flexDirection="column">
        <SessionList sessions={sessions} />
        <Box marginTop={1}>
          <Text dimColor>Press q to quit</Text>
        </Box>
      </Box>
    );
  }

  // Results state
  if (state === "results" && scanResult) {
    const metrics = toMetricRows(scanResult.bias_metrics);

    return (
      <Box flexDirection="column">
        <Box marginBottom={1}>
          <Text bold color="cyan">
            ═══ FairCheck Bias Analysis ═══
          </Text>
        </Box>

        <Text>
          Model: <Text bold>{model}</Text>
        </Text>
        <Text>
          Dataset: <Text bold>{dataset}</Text>
        </Text>
        <Text>
          Risk Level:{" "}
          <Text
            bold
            color={
              scanResult.risk_level === "high"
                ? "red"
                : scanResult.risk_level === "medium"
                  ? "yellow"
                  : "green"
            }
          >
            {scanResult.risk_level.toUpperCase()}
          </Text>
        </Text>

        <MetricsTable metrics={metrics} />

        {/* Report status */}
        {reportStatus && (
          <Box marginTop={1}>
            <Text>{reportStatus}</Text>
          </Box>
        )}

        {/* Hotkey hints */}
        <Box marginTop={1}>
          <Text dimColor>
            [R] Generate Report  [W] Open Web Dashboard  [Q] Quit
          </Text>
        </Box>
      </Box>
    );
  }

  return <Text>Loading...</Text>;
}
