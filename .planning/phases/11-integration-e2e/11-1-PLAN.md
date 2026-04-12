---
phase: 11
plan: 1
title: "Server Lifecycle & Port/PID Management"
wave: 1
depends_on: []
files_modified:
  - src/faircheck/api/server.py
  - src/faircheck/api/lifecycle.py
  - tests/api/test_lifecycle.py
requirements: [INT-02, INT-03, INT-04]
autonomous: true
---

# Plan 11-1: Server Lifecycle & Port/PID Management

<objective>
Harden the FastAPI server launcher with PID file management to prevent duplicate instances,
atomic port file writing, and a health check poller utility for TUI/Web consumers.
</objective>

## Tasks

<task id="11-1-1" title="Create lifecycle module">
<action>
Create `src/faircheck/api/lifecycle.py`:

- `write_port_file(port: int)` — atomically writes port to `~/.faircheck/port`
- `read_port_file() -> int | None` — reads port, returns None if missing/stale
- `write_pid_file()` — writes current PID to `~/.faircheck/server.pid` (INT-04)
- `read_pid_file() -> int | None` — reads PID, returns None if missing
- `is_server_running() -> bool` — checks if PID in file is a live process
- `cleanup_files()` — removes port + pid files (atexit handler)
- `poll_health(port: int, timeout: float = 10.0) -> bool` — polls GET /api/health
  until 200 or timeout (INT-03)

Update `server.py`:
- Use `write_pid_file()` before starting uvicorn
- Use `is_server_running()` to prevent duplicate instances (INT-04)
- Register `cleanup_files()` via `atexit`
</action>

<acceptance_criteria>
- PID file prevents double-launch
- Health poller returns True when API responds
- Cleanup removes files on shutdown
</acceptance_criteria>
</task>

<task id="11-1-2" title="Unit tests for lifecycle">
<action>
Create `tests/api/test_lifecycle.py`:
1. `write_port_file` creates file with correct port
2. `read_port_file` returns None when file missing
3. `write_pid_file` writes current PID
4. `is_server_running` returns True for own PID
5. `is_server_running` returns False for dead PID (99999999)
6. `cleanup_files` removes both files
</action>
</task>

<verification>
- `pytest tests/api/test_lifecycle.py -v` — all tests pass
- `pytest tests/ -q` — no regressions
</verification>
