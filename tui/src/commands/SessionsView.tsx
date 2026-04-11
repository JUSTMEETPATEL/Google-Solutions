/** SessionsView — session list command view (TUI-07). */

import React, { useState, useEffect } from "react";
import { Box, Text, useApp } from "ink";
import { SessionList } from "../components/SessionList.js";
import { listSessions } from "../api.js";

export function SessionsView() {
  const { exit } = useApp();
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listSessions()
      .then((data) => {
        setSessions(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to connect to FairCheck API");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <Box>
        <Text color="yellow"> ⏳ Loading sessions...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box flexDirection="column">
        <Text color="red"> ✗ Error: {error}</Text>
        <Text dimColor> Make sure the FairCheck API server is running.</Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column">
      <Box marginBottom={1}>
        <Text bold color="cyan">
          {"\n  ⚖  FairCheck Session History\n"}
        </Text>
      </Box>
      <SessionList sessions={sessions} />
    </Box>
  );
}
