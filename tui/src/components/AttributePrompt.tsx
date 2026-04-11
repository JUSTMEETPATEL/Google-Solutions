/**
 * AttributePrompt — Interactive protected attribute selection.
 *
 * When the engine auto-detects protected attributes, this shows them
 * with confidence scores for user confirmation. If the user rejects
 * or none are detected, it falls back to a multi-select of all columns.
 */

import React, { useState } from "react";
import { Box, Text } from "ink";
import SelectInput from "ink-select-input";

export interface DetectedAttribute {
  name: string;
  confidence: number;
}

interface AttributePromptProps {
  detected: DetectedAttribute[];
  allColumns: string[];
  onConfirm: (selected: string[]) => void;
}

type PromptState = "confirm" | "manual-select";

export function AttributePrompt({
  detected,
  allColumns,
  onConfirm,
}: AttributePromptProps): React.JSX.Element {
  const [state, setState] = useState<PromptState>(
    detected.length > 0 ? "confirm" : "manual-select",
  );

  if (state === "confirm") {
    const items = [
      {
        label: `✓ Accept detected: ${detected.map((d) => `${d.name} (${(d.confidence * 100).toFixed(0)}%)`).join(", ")}`,
        value: "accept",
      },
      { label: "✗ Reject — choose manually", value: "reject" },
    ];

    return (
      <Box flexDirection="column" marginTop={1}>
        <Text bold color="cyan">
          Protected Attribute Detection
        </Text>
        <Text>
          The following columns were detected as protected attributes:
        </Text>
        {detected.map((attr) => (
          <Text key={attr.name}>
            {"  "}• <Text bold>{attr.name}</Text>{" "}
            <Text dimColor>(confidence: {(attr.confidence * 100).toFixed(0)}%)</Text>
          </Text>
        ))}
        <Box marginTop={1}>
          <SelectInput
            items={items}
            onSelect={(item) => {
              if (item.value === "accept") {
                onConfirm(detected.map((d) => d.name));
              } else {
                setState("manual-select");
              }
            }}
          />
        </Box>
      </Box>
    );
  }

  // Manual selection fallback
  const columnItems = allColumns.map((col) => ({
    label: col,
    value: col,
  }));

  return (
    <Box flexDirection="column" marginTop={1}>
      <Text bold color="cyan">
        Select Protected Attribute
      </Text>
      <Text dimColor>Choose a column to use as the protected attribute:</Text>
      <Box marginTop={1}>
        <SelectInput
          items={columnItems}
          onSelect={(item) => {
            onConfirm([item.value]);
          }}
        />
      </Box>
    </Box>
  );
}
