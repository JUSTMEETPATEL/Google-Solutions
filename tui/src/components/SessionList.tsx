/** SessionList — displays past scans (TUI-07). */

import React from "react";
import { Box, Text } from "ink";

interface Session {
  id: string;
  model_name: string;
  created_at: string;
  risk_level: string;
}

interface SessionListProps {
  sessions: Session[];
}

const RISK_COLORS: Record<string, string> = {
  high: "red",
  medium: "yellow",
  low: "green",
};

export function SessionList({ sessions }: SessionListProps) {
  if (sessions.length === 0) {
    return (
      <Box marginBottom={1}>
        <Text dimColor> No scan sessions found.</Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column" marginBottom={1}>
      <Text bold color="blue">
        {" "}
        ━━ Recent Sessions ━━
      </Text>
      <Box>
        <Text bold>
          {"  "}
          {"#".padEnd(4)}
          {"Model".padEnd(24)}
          {"Date".padEnd(14)}
          {"Risk".padEnd(10)}
        </Text>
      </Box>
      <Text dimColor>{"  " + "─".repeat(52)}</Text>
      {sessions.slice(0, 10).map((s, i) => (
        <Box key={s.id}>
          <Text>
            {"  "}
            {String(i + 1).padEnd(4)}
            {(s.model_name || "Unknown").slice(0, 22).padEnd(24)}
            {(s.created_at || "").slice(0, 10).padEnd(14)}
          </Text>
          <Text color={(RISK_COLORS[s.risk_level?.toLowerCase()] || "gray") as any} bold>
            {(s.risk_level || "—").toUpperCase()}
          </Text>
        </Box>
      ))}
    </Box>
  );
}
