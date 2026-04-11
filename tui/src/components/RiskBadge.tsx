/** RiskBadge — overall risk level display. */

import React from "react";
import { Box, Text } from "ink";

interface RiskBadgeProps {
  level: string;
}

const RISK_COLORS: Record<string, string> = {
  high: "red",
  medium: "yellow",
  low: "green",
  unknown: "gray",
};

export function RiskBadge({ level }: RiskBadgeProps) {
  const color = RISK_COLORS[level.toLowerCase()] || "gray";
  return (
    <Box marginBottom={1}>
      <Text bold> Overall Risk: </Text>
      <Text color={color as any} bold>
        {"█ " + level.toUpperCase() + " █"}
      </Text>
    </Box>
  );
}
