/** MetricsTable — colored terminal table of fairness metrics (TUI-02). */

import React from "react";
import { Box, Text } from "ink";

interface MetricRow {
  name: string;
  threshold: number | string;
  value: number | string;
  status: "pass" | "warning" | "fail" | "skipped";
}

interface MetricsTableProps {
  title: string;
  metrics: MetricRow[];
}

const STATUS_COLORS: Record<string, string> = {
  pass: "green",
  warning: "yellow",
  fail: "red",
  skipped: "gray",
};

const STATUS_ICONS: Record<string, string> = {
  pass: "✓",
  warning: "⚠",
  fail: "✗",
  skipped: "—",
};

export function MetricsTable({ title, metrics }: MetricsTableProps) {
  const colWidths = { name: 32, threshold: 12, value: 12, status: 10 };

  return (
    <Box flexDirection="column" marginBottom={1}>
      <Text bold color="blue">
        {" "}
        ━━ {title} ━━
      </Text>
      <Box>
        <Text bold>
          {"  "}
          {"Metric".padEnd(colWidths.name)}
          {"Threshold".padEnd(colWidths.threshold)}
          {"Value".padEnd(colWidths.value)}
          {"Status".padEnd(colWidths.status)}
        </Text>
      </Box>
      <Text dimColor>{"  " + "─".repeat(colWidths.name + colWidths.threshold + colWidths.value + colWidths.status)}</Text>
      {metrics.map((m, i) => (
        <Box key={i}>
          <Text>
            {"  "}
            {m.name.padEnd(colWidths.name)}
            {String(m.threshold).padEnd(colWidths.threshold)}
            {(typeof m.value === "number" ? m.value.toFixed(4) : String(m.value)).padEnd(colWidths.value)}
          </Text>
          <Text color={STATUS_COLORS[m.status] as any} bold>
            {STATUS_ICONS[m.status]} {m.status.toUpperCase()}
          </Text>
        </Box>
      ))}
    </Box>
  );
}

/** Parse API response into MetricRow[] */
export function parseMetrics(
  results: Record<string, any>
): { attribute: string; metrics: MetricRow[] }[] {
  const output: { attribute: string; metrics: MetricRow[] }[] = [];

  for (const [attr, data] of Object.entries(results)) {
    const metrics: MetricRow[] = [];
    const metricsData = (data as any)?.metrics || {};

    for (const [name, m] of Object.entries(metricsData)) {
      const md = m as any;
      metrics.push({
        name: name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
        threshold: md.threshold ?? "—",
        value: md.value ?? "N/A",
        status: md.status ?? "skipped",
      });
    }

    output.push({ attribute: attr, metrics });
  }

  return output;
}
