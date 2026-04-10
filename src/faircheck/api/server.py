"""Programmatic server launcher with automatic port discovery.

Finds a free port, writes it to ``~/.faircheck/port`` so the TUI and
Web frontends can discover the running instance, then starts Uvicorn.

Usage::

    python -m faircheck.api.server
"""

from __future__ import annotations

import socket
from pathlib import Path

import uvicorn


def find_free_port() -> int:
    """Bind to port 0, let the OS assign a free port, and return it."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def serve() -> None:
    """Start the FairCheck API server on a random free port."""
    port = find_free_port()

    # Write the port file for TUI / Web discovery (API-01)
    port_file = Path.home() / ".faircheck" / "port"
    port_file.parent.mkdir(parents=True, exist_ok=True)
    port_file.write_text(str(port))

    uvicorn.run(
        "faircheck.api.main:app",
        host="127.0.0.1",
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    serve()
