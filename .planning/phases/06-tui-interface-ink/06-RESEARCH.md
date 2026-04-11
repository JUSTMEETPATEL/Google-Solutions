# Phase 06: TUI Interface (ink) - Research

## Objective
Research how to build the Terminal UI (TUI) for FairCheck using Ink, integrating with the FastAPI backend, and structuring the node project effectively.

## 1. Node.js Project Structure
We are building a React-in-terminal app using `ink` and `commander` within a monorepo setup where the Python backend is in `src/faircheck`.
Per the context decisions, the JS project lives in `tui/`.
- **Files needed:** `package.json`, `tsconfig.json`.
- **Dependencies:** `ink`, `ink-text-input`, `ink-select-input`, `ink-spinner`, `commander`, `node-fetch`, `@types/react`.

## 2. Server Orchestration (Subprocess Lifecycle)
The CLI must seamlessly invoke the Python backend.
- Python server launch command: `uv run python -m faircheck.api.server`
- Port discovery: The server writes the assigned port to `~/.faircheck/port`.
- Readiness polling: The Node CLI must poll `http://127.0.0.1:<port>/api/v1/health` until it returns a `200 OK` before proceeding with requests.
- When the CLI terminates, it must gracefully kill the spawned subprocess to prevent zombie Python servers.

## 3. The `faircheck scan` Flow
1. User runs the executable or `tsx src/cli.ts scan model.pkl --dataset data.csv`.
2. Spawns FastAPI server.
3. Node reads `~/.faircheck/port` and waits for `/api/v1/health`.
4. Uploads files using `FormData` to `POST /api/v1/scan`.
5. Receives `status`, `protected_attributes`, `bias_metrics`.
6. **If no protected attributes or user rejection:** Fallback to showing `ink-select-input` with all dataset columns.
7. Renders custom Flexbox rows in Ink to display metrics, thresholds, and Passes/Fails with ANSI colors.

## 4. CI Mode
- When `--ci` is provided, Ink is bypassed entirely.
- The app executes the exact same orchestration but prints the resultant JSON horizontally or in a simple flat table.
- Use `process.exit(1)` if any metric fails.

## 5. Hotkeys
- **`[R]`:** A standard keypress hook in Ink (`useInput`) can detect 'r' and make a `fetch('http://127.0.0.1:<port>/api/v1/report', { method: 'POST' })` request.

## RESEARCH COMPLETE
This provides all necessary blueprints to write accurate, specific plans for Phase 6. Let's proceed.
