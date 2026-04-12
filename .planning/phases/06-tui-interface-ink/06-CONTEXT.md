# Phase 06: TUI Interface (ink) - Context

**Gathered:** 2026-04-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the terminal interface using ink (React-in-terminal) that provides the `faircheck` CLI, renders scan results as tables, handles interactive prompts, triggers the FastAPI engine, and provides automated CI scanning capabilities.
</domain>

<decisions>
## Implementation Decisions

### JS/TS Architecture
- **D-01:** **Project Structure:** The Node.js Ink application will live in `tui/` at the repository root to keep it cleanly separated from the Python `src/faircheck/` backend.
- **D-02:** **CLI Framework:** Use **Commander.js** to parse commands, flags, and wrap the Ink application.

### Server Orchestration & Flow
- **D-03:** **Subprocess Lifecyle:** The Node CLI will silently spawn the FastAPI server as a background subprocess (on a random port), run the API flow, and kill it upon exit to provide a native CLI feel.
- **D-04:** **PDF Generation ([R] Hotkey):** Implement the `[R]` keyboard hotkey by actually making a `POST /api/report` API call to FastAPI, assuming it to be a 501 stub until Phase 7 fills out the PDF generation logic.

### UI / Rendering
- **D-05:** **Table Rendering:** Build custom flexbox rows natively in Ink rather than relying on strict `ink-table` components, ensuring better exact control over colors and warning highlights.
- **D-06:** **Interactive Fallbacks:** If the backend auto-detects zero protected attributes, or if the user rejects the detected attributes, Ink will display a multi-select prompt of all dataset columns rather than exiting with an error.
- **D-07:** **Continuous Integration (`--ci`):** When executed with the `--ci` flag, completely bypass Ink and output raw text/JSON results to the standard output, exiting with 1 upon failure, preventing messy ANSI escapes in CI environment logs.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Core Requirements
- `.planning/PROJECT.md` — Overall architecture constraints and goal (TUI for developers using Ink).
- `.planning/REQUIREMENTS.md` — Phase 6 requirements (TUI-01 to TUI-07).
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- The API wrapper built in Phase 4 is expected to be consumed here to do the actual data analysis (POST `/api/v1/scan` etc.).

### Established Patterns
- We are starting a clean Node.js Ink project at `tui/`.
- No existing front-end JS patterns constrain us yet.
</code_context>

<deferred>
## Deferred Ideas

- None.
</deferred>
