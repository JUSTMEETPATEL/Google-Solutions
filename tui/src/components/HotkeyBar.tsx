/** HotkeyBar — bottom bar with [W] and [R] hotkeys (TUI-04, TUI-05). */

import React from "react";
import { Box, Text, useInput } from "ink";

interface HotkeyBarProps {
  onWebOpen: () => void;
  onReport: () => void;
  onQuit: () => void;
}

export function HotkeyBar({ onWebOpen, onReport, onQuit }: HotkeyBarProps) {
  useInput((input, key) => {
    if (input === "w" || input === "W") onWebOpen();
    if (input === "r" || input === "R") onReport();
    if (input === "q" || input === "Q" || key.escape) onQuit();
  });

  return (
    <Box marginTop={1} borderStyle="single" borderColor="gray" paddingX={1}>
      <Text>
        <Text color="cyan" bold>[W]</Text>
        <Text> Open Web </Text>
        <Text dimColor>│</Text>
        <Text> </Text>
        <Text color="magenta" bold>[R]</Text>
        <Text> Generate Report </Text>
        <Text dimColor>│</Text>
        <Text> </Text>
        <Text color="red" bold>[Q]</Text>
        <Text> Quit</Text>
      </Text>
    </Box>
  );
}
