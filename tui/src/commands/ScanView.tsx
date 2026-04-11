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

  const handleWebOpen = () => {
    // TUI-04: Open web dashboard
    import("child_process").then(({ exec }) => {
      exec("open http://localhost:5173");
    });
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
