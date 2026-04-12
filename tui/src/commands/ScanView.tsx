/** ScanView — main scan results view combining all components. */

import React, { useState, useEffect } from "react";
import { Box, Text, useApp } from "ink";
import { MetricsTable, parseMetrics } from "../components/MetricsTable.js";
import { RiskBadge } from "../components/RiskBadge.js";
import { HotkeyBar } from "../components/HotkeyBar.js";

interface ScanViewProps {
  results: Record<string, any>;
  sessionId?: string;
  ciMode?: boolean;
}

export function ScanView({ results, sessionId, ciMode }: ScanViewProps) {
  const { exit } = useApp();
  const riskLevel = results?.overall_risk_level || "unknown";
  const analysisResults = results?.results || {};
  const parsed = parseMetrics(analysisResults);

  // CI mode: exit immediately with code based on results (TUI-06)
  useEffect(() => {
    if (ciMode) {
      const hasFailure = parsed.some((p) =>
        p.metrics.some((m) => m.status === "fail")
      );
      // Exit after render
      setTimeout(() => {
        process.exit(hasFailure ? 1 : 0);
      }, 100);
    }
  }, [ciMode, parsed]);

  const handleWebOpen = async () => {
    // INT-01: TUI→Web handoff with port discovery and session pre-loading
    try {
      const { getBaseUrl } = await import("../api.js");
      const { readFileSync, existsSync } = await import("fs");
      const { homedir } = await import("os");
      const { join } = await import("path");
      const { exec } = await import("child_process");

      // Read port from ~/.faircheck/port (INT-02)
      const portFile = join(homedir(), ".faircheck", "port");
      let webUrl = "http://localhost:5173";
      if (existsSync(portFile)) {
        const port = readFileSync(portFile, "utf-8").trim();
        // Poll health before opening (INT-03)
        const apiUrl = `http://localhost:${port}/api/health`;
        try {
          await fetch(apiUrl, { signal: AbortSignal.timeout(3000) });
        } catch {
          // Server may not be ready yet, open anyway
        }
      }

      // Open with session_id in URL for pre-loading
      const url = sessionId
        ? `${webUrl}?session=${sessionId}`
        : webUrl;
      exec(`open "${url}"`);
    } catch {
      // Fallback: open default URL
      import("child_process").then(({ exec }) => {
        exec("open http://localhost:5173");
      });
    }
  };

  const handleReport = async () => {
    // TUI-05: Generate report via API
    if (sessionId) {
      try {
        const { generateReport } = await import("../api.js");
        await generateReport(sessionId, "pdf");
      } catch {
        // API may not be available
      }
    }
  };

  const handleQuit = () => {
    exit();
  };

  return (
    <Box flexDirection="column">
      <Box marginBottom={1}>
        <Text bold color="cyan">
          {"\n  ⚖  FairCheck Bias Analysis Results\n"}
        </Text>
      </Box>

      <RiskBadge level={riskLevel} />

      {parsed.map((p) => (
        <MetricsTable
          key={p.attribute}
          title={`Protected Attribute: ${p.attribute}`}
          metrics={p.metrics}
        />
      ))}

      {parsed.length === 0 && (
        <Box marginBottom={1}>
          <Text dimColor> No analysis results to display.</Text>
        </Box>
      )}

      {sessionId && (
        <Box marginBottom={1}>
          <Text dimColor> Session: {sessionId}</Text>
        </Box>
      )}

      {!ciMode && (
        <HotkeyBar
          onWebOpen={handleWebOpen}
          onReport={handleReport}
          onQuit={handleQuit}
        />
      )}
    </Box>
  );
}
