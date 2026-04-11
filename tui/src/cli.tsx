#!/usr/bin/env node

/**
 * FairCheck TUI — Terminal interface for AI bias analysis.
 *
 * Usage:
 *   faircheck scan model.pkl --dataset train.csv [--ci]
 *   faircheck sessions
 *   faircheck health
 */

import { Command } from "commander";
import React from "react";
import { render } from "ink";
import { ScanView } from "./commands/ScanView.js";
import { SessionsView } from "./commands/SessionsView.js";
import { runScan, healthCheck, listSessions } from "./api.js";

const program = new Command();

program
  .name("faircheck")
  .description("⚖  FairCheck — AI Bias Detection & Fairness Platform")
  .version("0.1.0");

// TUI-01: scan command
program
  .command("scan <model>")
  .description("Run bias analysis on a model")
  .requiredOption("--dataset <path>", "Path to dataset file (CSV/Parquet/JSON)")
  .option("--ci", "CI mode: exit with code 1 if any metric fails (TUI-06)", false)
  .option("--domain <domain>", "Domain context: hiring, lending, healthcare")
  .option("--format <format>", "Report format: pdf, md, docx", "pdf")
  .action(async (model: string, options: Record<string, any>) => {
    const ciMode = options.ci || false;

    if (!ciMode) {
      console.log("\n  ⚖  FairCheck — Scanning...\n");
    }

    try {
      const results = await runScan(model, options.dataset, {
        domain: options.domain,
      });

      const analysisResults = (results as any)?.analysis_results || results;
      const sessionId = (results as any)?.session_id || "";

      const { waitUntilExit } = render(
        React.createElement(ScanView, {
          results: analysisResults,
          sessionId,
          ciMode,
        })
      );

      await waitUntilExit();
    } catch (err: any) {
      if (ciMode) {
        console.error(`Error: ${err.message}`);
        process.exit(2);
      }

      // Offline mode: show error and suggest starting server
      console.error(`\n  ✗ Could not connect to FairCheck API: ${err.message}`);
      console.error("  → Start the server: python -m faircheck.api\n");
      process.exit(1);
    }
  });

// TUI-07: sessions command
program
  .command("sessions")
  .description("List past scan sessions")
  .action(async () => {
    const { waitUntilExit } = render(
      React.createElement(SessionsView, {})
    );
    await waitUntilExit();
  });

// Health check
program
  .command("health")
  .description("Check API server health")
  .action(async () => {
    const ok = await healthCheck();
    if (ok) {
      console.log("  ✓ FairCheck API is healthy");
      process.exit(0);
    } else {
      console.log("  ✗ FairCheck API is not reachable");
      process.exit(1);
    }
  });

program.parse();
