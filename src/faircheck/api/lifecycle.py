"""Server lifecycle management — port/PID files, health polling, cleanup.

Provides utilities for:
- Atomic port file writing (INT-02)
- Health check polling (INT-03)
- PID file management to prevent duplicate instances (INT-04)
- Cleanup on shutdown via atexit
"""

from __future__ import annotations

import atexit
import logging
import os
import signal
import time
from pathlib import Path

logger = logging.getLogger(__name__)

FAIRCHECK_DIR = Path.home() / ".faircheck"
PORT_FILE = FAIRCHECK_DIR / "port"
PID_FILE = FAIRCHECK_DIR / "server.pid"


def _ensure_dir() -> None:
    """Ensure ~/.faircheck/ exists."""
    FAIRCHECK_DIR.mkdir(parents=True, exist_ok=True)


# ─── Port File (INT-02) ───────────────────────────────────


def write_port_file(port: int) -> Path:
    """Atomically write the server port to ~/.faircheck/port.

    Uses write-to-temp + rename for atomicity.
    """
    _ensure_dir()
    tmp = PORT_FILE.with_suffix(".tmp")
    tmp.write_text(str(port))
    tmp.rename(PORT_FILE)
    logger.info("Port file written: %s -> %d", PORT_FILE, port)
    return PORT_FILE


def read_port_file() -> int | None:
    """Read the port from ~/.faircheck/port.

    Returns None if the file is missing or contains invalid content.
    """
    try:
        text = PORT_FILE.read_text().strip()
        return int(text)
    except (FileNotFoundError, ValueError):
        return None


# ─── PID File (INT-04) ────────────────────────────────────


def write_pid_file() -> Path:
    """Write the current process PID to ~/.faircheck/server.pid."""
    _ensure_dir()
    PID_FILE.write_text(str(os.getpid()))
    logger.info("PID file written: %s -> %d", PID_FILE, os.getpid())
    return PID_FILE


def read_pid_file() -> int | None:
    """Read the PID from ~/.faircheck/server.pid.

    Returns None if file is missing or contains invalid content.
    """
    try:
        text = PID_FILE.read_text().strip()
        return int(text)
    except (FileNotFoundError, ValueError):
        return None


def _is_pid_alive(pid: int) -> bool:
    """Check whether a process with the given PID is alive (cross-platform)."""
    if os.name == "nt":
        # Windows: use ctypes to call OpenProcess — safe, no side-effects.
        import ctypes
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION, False, pid
        )
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        return False
    else:
        # Unix: signal 0 checks existence without affecting the process.
        try:
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, PermissionError):
            return False


def is_server_running() -> bool:
    """Check if a FairCheck server is already running.

    Reads the PID file and checks if that process is alive.
    Returns False if PID file is missing or process is dead.
    """
    pid = read_pid_file()
    if pid is None:
        return False
    # Don't consider ourselves as "already running"
    if pid == os.getpid():
        return False
    return _is_pid_alive(pid)


# ─── Health Polling (INT-03) ──────────────────────────────


def poll_health(port: int, timeout: float = 10.0, interval: float = 0.5) -> bool:
    """Poll GET /api/health until 200 or timeout.

    Parameters
    ----------
    port : int
        Port to poll.
    timeout : float
        Max seconds to wait. Default 10.
    interval : float
        Seconds between polls. Default 0.5.

    Returns
    -------
    bool
        True if health endpoint responded 200 within timeout.
    """
    import urllib.request
    import urllib.error

    url = f"http://127.0.0.1:{port}/api/health"
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            req = urllib.request.urlopen(url, timeout=2)
            if req.status == 200:
                return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(interval)

    return False


# ─── Cleanup ──────────────────────────────────────────────


def cleanup_files() -> None:
    """Remove port and PID files. Registered as atexit handler."""
    for f in (PORT_FILE, PID_FILE):
        try:
            f.unlink(missing_ok=True)
            logger.debug("Cleaned up: %s", f)
        except OSError:
            pass


def register_cleanup() -> None:
    """Register cleanup_files as an atexit handler."""
    atexit.register(cleanup_files)
