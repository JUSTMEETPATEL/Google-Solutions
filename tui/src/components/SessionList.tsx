/**
 * SessionList — Display past scan history.
 *
 * Shows a table of the last N sessions with model name, date, and risk level.
 */

import React from "react";
import { Box, Text } from "ink";
import type { SessionSummary } from "../api.js";

interface SessionListProps {
  sessions: SessionSummary[];
  maxItems?: number;
}

const RISK_COLORS: Record<string, string> = {
  high: "red",
  medium: "yellow",
  low: "green",
};

export function SessionList({
  sessions,
  maxItems = 10,
}: SessionListProps): React.JSX.Element {
  const display = sessions.slice(0, maxItems);

  if (display.length === 0) {
    return (
      <Box marginTop={1}>
        <Text dimColor>No scan sessions found.</Text>
      </Box>
    );
  }

  const idWidth = 12;
  const modelWidth = 30;
  const dateWidth = 20;
  const riskWidth = 10;

  return (
    <Box flexDirection="column" marginTop={1}>
      <Text bold color="cyan">
        Recent Scan Sessions
      </Text>

      {/* Header */}
      <Box marginTop={1}>
        <Box width={idWidth}>
          <Text bold underline>
            ID
          </Text>
        </Box>
        <Box width={modelWidth}>
          <Text bold underline>
            Model
          </Text>
        </Box>
        <Box width={dateWidth}>
          <Text bold underline>
            Date
          </Text>
        </Box>
        <Box width={riskWidth}>
          <Text bold underline>
            Risk
          </Text>
        </Box>
      </Box>

      {/* Separator */}
      <Box>
        <Text dimColor>
          {"─".repeat(idWidth + modelWidth + dateWidth + riskWidth)}
        </Text>
      </Box>

      {/* Data rows */}
      {display.map((session) => {
        const modelName = session.model_path.split("/").pop() ?? session.model_path;
        const risk = (session.risk_level ?? "unknown").toLowerCase();
        const date = new Date(session.created_at).toLocaleString();

        return (
          <Box key={session.id}>
            <Box width={idWidth}>
              <Text>{session.id.slice(0, 8)}…</Text>
            </Box>
            <Box width={modelWidth}>
              <Text>{modelName}</Text>
            </Box>
            <Box width={dateWidth}>
              <Text dimColor>{date}</Text>
            </Box>
            <Box width={riskWidth}>
              <Text color={RISK_COLORS[risk] ?? "white"} bold>
                {risk.toUpperCase()}
              </Text>
            </Box>
          </Box>
        );
      })}

      <Box marginTop={1}>
        <Text dimColor>
          Showing {display.length} of {sessions.length} sessions
        </Text>
      </Box>
    </Box>
  );
}
