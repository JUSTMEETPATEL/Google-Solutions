"""Programmatic server launcher with lifecycle management.

Finds a free port, writes port + PID files, prevents duplicate instances,
registers cleanup, then starts Uvicorn.

Usage::

    python -m faircheck.api.server
"""

from __future__ import annotations

import socket
import sys

import uvicorn

from faircheck.api.lifecycle import (
    cleanup_files,
    is_server_running,
    register_cleanup,
    write_pid_file,
    write_port_file,
)


def find_free_port() -> int:
    """Bind to port 0, let the OS assign a free port, and return it."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def serve() -> None:
    """Start the FairCheck API server on a random free port."""
    # INT-04: Prevent duplicate instances
    if is_server_running():
        print("⚠ FairCheck server is already running. Exiting.")
        sys.exit(0)

    port = find_free_port()

    # INT-02: Write port file for TUI/Web discovery
    write_port_file(port)

    # INT-04: Write PID file
    write_pid_file()

    # Register cleanup for graceful shutdown
    register_cleanup()

    print(f"  [FairCheck] API starting on http://127.0.0.1:{port}")

    uvicorn.run(
        "faircheck.api.main:app",
        host="127.0.0.1",
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    serve()
