#!/usr/bin/env node
/**
 * FairCheck TUI — CLI entrypoint.
 *
 * Uses Commander.js to parse commands and Ink to render the terminal UI.
 *
 * Usage:
 *   faircheck scan model.pkl --dataset train.csv
 *   faircheck scan model.pkl --dataset train.csv --ci
 *   faircheck sessions
 */

import { Command } from "commander";
import React from "react";
import { render } from "ink";
import { App, runCiMode } from "./components/App.js";

const program = new Command();

program
  .name("faircheck")
  .description("AI Bias Detection & Fairness Analysis Tool")
  .version("0.1.0");

program
  .command("scan")
  .description("Run bias analysis on a model and dataset")
  .argument("<model>", "Path to the model file (.pkl, .joblib, .onnx)")
  .requiredOption("--dataset <path>", "Path to the dataset file (CSV, Parquet, JSON)")
  .option("--ci", "CI mode — raw text output, exit code 1 on failure", false)
  .action(async (model: string, options: { dataset: string; ci: boolean }) => {
    if (options.ci) {
      // CI mode bypasses Ink entirely
      await runCiMode(model, options.dataset);
      return;
    }

    // Interactive mode — render with Ink
    render(
      <App
        model={model}
        dataset={options.dataset}
        ci={false}
        command="scan"
      />,
    );
  });

program
  .command("sessions")
  .description("List past scan sessions")
  .action(() => {
    render(
      <App
        model=""
        dataset=""
        ci={false}
        command="sessions"
      />,
    );
  });

program.parse(process.argv);
