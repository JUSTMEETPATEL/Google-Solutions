"""Tests for server lifecycle — port/PID files, health polling, cleanup."""

import os

import pytest

from faircheck.api.lifecycle import (
    PORT_FILE,
    PID_FILE,
    cleanup_files,
    is_server_running,
    read_pid_file,
    read_port_file,
    write_pid_file,
    write_port_file,
)


@pytest.fixture(autouse=True)
def _clean_files():
    """Ensure port/pid files are cleaned up after each test."""
    yield
    for f in (PORT_FILE, PID_FILE):
        try:
            f.unlink(missing_ok=True)
        except OSError:
            pass


class TestPortFile:
    def test_write_and_read(self):
        write_port_file(8042)
        assert read_port_file() == 8042

    def test_read_missing_returns_none(self):
        PORT_FILE.unlink(missing_ok=True)
        assert read_port_file() is None

    def test_atomic_write(self):
        """Temp file should not remain after write."""
        write_port_file(9999)
        tmp = PORT_FILE.with_suffix(".tmp")
        assert not tmp.exists()
        assert PORT_FILE.exists()


class TestPidFile:
    def test_write_and_read(self):
        write_pid_file()
        assert read_pid_file() == os.getpid()

    def test_read_missing_returns_none(self):
        PID_FILE.unlink(missing_ok=True)
        assert read_pid_file() is None


class TestIsServerRunning:
    def test_own_pid_not_considered_running(self):
        """Our own PID should not block us."""
        write_pid_file()
        assert is_server_running() is False

    def test_dead_pid_not_running(self):
        """A non-existent PID should return False."""
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        PID_FILE.write_text("99999999")
        assert is_server_running() is False

    def test_missing_file_not_running(self):
        PID_FILE.unlink(missing_ok=True)
        assert is_server_running() is False


class TestCleanup:
    def test_cleanup_removes_files(self):
        write_port_file(8000)
        write_pid_file()
        assert PORT_FILE.exists()
        assert PID_FILE.exists()
        cleanup_files()
        assert not PORT_FILE.exists()
        assert not PID_FILE.exists()

    def test_cleanup_no_error_when_missing(self):
        """Should not raise if files don't exist."""
        PORT_FILE.unlink(missing_ok=True)
        PID_FILE.unlink(missing_ok=True)
        cleanup_files()  # Should not raise
