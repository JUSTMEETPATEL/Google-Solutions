---
wave: 1
depends_on: []
files_modified:
  - tui/package.json
  - tui/tsconfig.json
  - tui/src/cli.tsx
  - tui/src/orchestrator.ts
  - tui/src/api.ts
  - tui/src/components/App.tsx
  - tui/src/components/MetricsTable.tsx
  - tui/src/components/AttributePrompt.tsx
autonomous: true
---

# Phase 06: TUI Interface (ink) - Plan 1

## Goal
Build the terminal interface using ink with scan command, metric table rendering, protected attribute confirmation, session list, CI mode, and [W]/[R] hotkeys.

## Tasks

```xml
<task id="06-01-01">
  <title>Initialize TUI Node.js Project (TUI-01)</title>
  <read_first>
    - .planning/phases/06-tui-interface-ink/06-CONTEXT.md
  </read_first>
  <action>
    Create a new Node.js project in `tui/`.
    Create `tui/package.json` with ESM type:
    `{ "name": "faircheck-tui", "version": "0.1.0", "type": "module", "scripts": { "build": "tsup src/cli.tsx --format esm", "dev": "tsx src/cli.tsx", "start": "node dist/cli.js" } }`
    Add dependencies: `npm install ink react ink-spinner ink-select-input commander form-data dotenv`
    Add dev dependencies: `npm install -D typescript @types/node @types/react tsup tsx`
    Create `tui/tsconfig.json` with strict type checking and `"moduleResolution": "bundler"`, `"jsx": "react-jsx"`.
  </action>
  <acceptance_criteria>
    `cat tui/package.json` contains `ink` and `commander`.
    `cat tui/tsconfig.json` exists.
  </acceptance_criteria>
</task>

<task id="06-01-02">
  <title>Build Python Server Orchestrator (TUI-01)</title>
  <read_first>
    - tui/package.json
  </read_first>
  <action>
    Create `tui/src/orchestrator.ts`.
    Implement `spawnServer()` that:
    1. Uses `child_process.spawn("uv", ["run", "python", "-m", "faircheck.api.server"], { cwd: "..", detached: true })`.
    2. Reads `~/.faircheck/port` with a retry delay until it exists.
    3. Polls `http://127.0.0.1:<port>/api/v1/health` until it returns a 200 HTTP status.
    4. Handles process exits to ensure the Python process is killed (e.g. `child.kill()`).
  </action>
  <acceptance_criteria>
    `tui/src/orchestrator.ts` exports `spawnServer`.
    `grep spawn tui/src/orchestrator.ts` exists.
    It reads `.faircheck/port` and polls `/api/v1/health`.
  </acceptance_criteria>
</task>

<task id="06-01-03">
  <title>Build API Client wrapper</title>
  <read_first>
    - tui/src/orchestrator.ts
  </read_first>
  <action>
    Create `tui/src/api.ts`.
    Implement methods to talk to the backend on the dynamically loaded port from the Orchestrator:
    - `runScan(modelPath: string, datasetPath: string): Promise<any>` using `FormData` with Node.js `fs.createReadStream()`.
    - `getSessions(): Promise<any>` calling `GET /api/v1/sessions`.
    - `generateReport(sessionId: string): Promise<any>` calling `POST /api/v1/report`.
    Use global `fetch` (available in Node 18+).
  </action>
  <acceptance_criteria>
    `tui/src/api.ts` exports `runScan`, `getSessions`, and `generateReport`.
    It uses `FormData` correctly for file uploads.
  </acceptance_criteria>
</task>

<task id="06-01-04">
  <title>Build Metrics and Components for React Ink (TUI-02, TUI-03, TUI-07)</title>
  <read_first>
    - tui/package.json
  </read_first>
  <action>
    Create Ink components:
    - `tui/src/components/MetricsTable.tsx`: Renders custom `Flex` rows using `ink` Components (`Box`, `Text`). Shows metric name, value, threshold (e.g. `Text color="green" / "red" / "yellow"` based on pass/fail thresholds).
    - `tui/src/components/AttributePrompt.tsx`: Uses `ink-select-input` to prompt user for "Select Protected Attribute" if none is detected.
    - `tui/src/components/SessionList.tsx`: Displays past session data returned by `getSessions()`.
  </action>
  <acceptance_criteria>
    `tui/src/components/MetricsTable.tsx` exists and uses `Box` and `Text`.
    `tui/src/components/AttributePrompt.tsx` uses `SelectInput`.
  </acceptance_criteria>
</task>

<task id="06-01-05">
  <title>Build Ink Application Root & Hotkeys (TUI-04, TUI-05, TUI-06)</title>
  <read_first>
    - tui/src/components/MetricsTable.tsx
  </read_first>
  <action>
    Create `tui/src/components/App.tsx`.
    Implement main state machine: `connecting` -> `scanning` / `prompting` -> `results`.
    Use the Orchestrator to ensure backend is ready. Then invoke `runScan`.
    If `options.ci` is true, completely bypass React Ink and output the raw JSON from `runScan` to `process.stdout.write`, exiting with `1` if any metrics breached.
    Implement hotkeys via `useInput` hook:
    - `[W]`: Spawn the Vite server (stub logic to `console.log('Spawning Vite server at localhost:5173')`).
    - `[R]`: Call `api.generateReport(currentSessionId)`.
  </action>
  <acceptance_criteria>
    `tui/src/components/App.tsx` exists.
    `useInput` is implemented for `W` and `R`.
    `--ci` flag causes `process.exit(1)` upon failure.
  </acceptance_criteria>
</task>

<task id="06-01-06">
  <title>Build Commander CLI Entrypoint (TUI-01)</title>
  <read_first>
    - tui/src/components/App.tsx
  </read_first>
  <action>
    Create `tui/src/cli.tsx`.
    Setup Commander:
    `program.command('scan <model> --dataset <data>').option('--ci')`
    On execution, it runs `render(<App model={..} dataset={..} ci={..} />)` natively via Ink.
  </action>
  <acceptance_criteria>
    `tui/src/cli.tsx` uses `commander`.
    The `scan` command is defined.
  </acceptance_criteria>
</task>
```

## Must Haves
- Runs completely via Node.js entry point using Ink React.
- Subprocesses FastAPI seamlessly.
- Includes `--ci` flag logic.
- Implements hotkeys [W]/[R].
- Renders colored threshold tables.

## Requirements Covered
- TUI-01
- TUI-02
- TUI-03
- TUI-04
- TUI-05
- TUI-06
- TUI-07
