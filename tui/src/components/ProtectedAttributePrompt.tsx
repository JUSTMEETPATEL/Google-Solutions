/** ProtectedAttributePrompt — interactive confirmation of auto-detected attributes (TUI-03). */

import React, { useState } from "react";
import { Box, Text, useInput } from "ink";

interface DetectedAttribute {
  name: string;
  confidence: number;
}

interface ProtectedAttributePromptProps {
  attributes: DetectedAttribute[];
  onConfirm: (selected: string[]) => void;
}

export function ProtectedAttributePrompt({
  attributes,
  onConfirm,
}: ProtectedAttributePromptProps) {
  const [selected, setSelected] = useState<Set<string>>(
    new Set(attributes.map((a) => a.name))
  );
  const [cursor, setCursor] = useState(0);
  const [confirmed, setConfirmed] = useState(false);

  useInput((input, key) => {
    if (confirmed) return;

    if (key.upArrow || input === "k") {
      setCursor((c) => Math.max(0, c - 1));
    }
    if (key.downArrow || input === "j") {
      setCursor((c) => Math.min(attributes.length - 1, c + 1));
    }
    if (input === " ") {
      setSelected((prev) => {
        const next = new Set(prev);
        const name = attributes[cursor]!.name;
        if (next.has(name)) {
          next.delete(name);
        } else {
          next.add(name);
        }
        return next;
      });
    }
    if (key.return) {
      setConfirmed(true);
      onConfirm(Array.from(selected));
    }
  });

  if (confirmed) {
    return (
      <Box marginBottom={1}>
        <Text color="green">
          ✓ Protected attributes confirmed: {Array.from(selected).join(", ")}
        </Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column" marginBottom={1}>
      <Text bold color="blue">
        {" "}
        Detected Protected Attributes
      </Text>
      <Text dimColor> Use ↑↓ to navigate, Space to toggle, Enter to confirm</Text>
      {attributes.map((attr, i) => (
        <Box key={attr.name}>
          <Text color={i === cursor ? "cyan" : undefined}>
            {"  "}
            {i === cursor ? "▸" : " "}
            {selected.has(attr.name) ? " [✓]" : " [ ]"}
            {" " + attr.name}
          </Text>
          <Text dimColor> ({(attr.confidence * 100).toFixed(0)}% confidence)</Text>
        </Box>
      ))}
    </Box>
  );
}
