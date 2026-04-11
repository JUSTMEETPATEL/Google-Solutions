/**
 * MetricsTable — Custom flexbox metric rows rendered in Ink.
 *
 * Each row shows: metric name │ value │ threshold │ status (colored).
 */

import React from "react";
import { Box, Text } from "ink";

export interface MetricRow {
  name: string;
  value: number;
  threshold: number;
  status: "pass" | "warning" | "fail";
}

interface MetricsTableProps {
  metrics: MetricRow[];
}

const STATUS_COLORS: Record<string, string> = {
  pass: "green",
  warning: "yellow",
  fail: "red",
};

const STATUS_LABELS: Record<string, string> = {
  pass: "PASS",
  warning: "WARN",
  fail: "FAIL",
};

export function MetricsTable({ metrics }: MetricsTableProps): React.JSX.Element {
  const nameWidth = 30;
  const valueWidth = 12;
  const thresholdWidth = 12;
  const statusWidth = 8;

  return (
    <Box flexDirection="column" marginTop={1}>
      {/* Header row */}
      <Box>
        <Box width={nameWidth}>
          <Text bold underline>
            Metric
          </Text>
        </Box>
        <Box width={valueWidth}>
          <Text bold underline>
            Value
          </Text>
        </Box>
        <Box width={thresholdWidth}>
          <Text bold underline>
            Threshold
          </Text>
        </Box>
        <Box width={statusWidth}>
          <Text bold underline>
            Status
          </Text>
        </Box>
      </Box>

      {/* Separator */}
      <Box>
        <Text dimColor>{"─".repeat(nameWidth + valueWidth + thresholdWidth + statusWidth)}</Text>
      </Box>

      {/* Data rows */}
      {metrics.map((metric) => (
        <Box key={metric.name}>
          <Box width={nameWidth}>
            <Text>{metric.name}</Text>
          </Box>
          <Box width={valueWidth}>
            <Text>{metric.value.toFixed(4)}</Text>
          </Box>
          <Box width={thresholdWidth}>
            <Text dimColor>{metric.threshold.toFixed(2)}</Text>
          </Box>
          <Box width={statusWidth}>
            <Text color={STATUS_COLORS[metric.status]} bold>
              {STATUS_LABELS[metric.status]}
            </Text>
          </Box>
        </Box>
      ))}

      {/* Summary */}
      <Box marginTop={1}>
        <Text>
          Total: {metrics.length} metrics |{" "}
          <Text color="green">{metrics.filter((m) => m.status === "pass").length} passed</Text>
          {" | "}
          <Text color="yellow">{metrics.filter((m) => m.status === "warning").length} warnings</Text>
          {" | "}
          <Text color="red">{metrics.filter((m) => m.status === "fail").length} failed</Text>
        </Text>
      </Box>
    </Box>
  );
}
