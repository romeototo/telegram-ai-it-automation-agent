"""
Unit tests for the Executor class (src/executor.py).
Tests cover dry-run mode, safety blocking, live execution, and timeout handling.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock
import subprocess
from src.executor import Executor


# ──────────────────────────────────────────────
# Dry-run mode
# ──────────────────────────────────────────────
@patch("src.executor.log_event")
class TestDryRunMode:
    """Executor in dry-run mode should simulate without running anything."""

    def test_dry_run_returns_success_status(self, mock_log):
        executor = Executor(dry_run=True)
        result = executor.execute("ping 8.8.8.8")
        assert result["status"] == "dry-run"

    def test_dry_run_contains_command_in_message(self, mock_log):
        executor = Executor(dry_run=True)
        result = executor.execute("hostname")
        assert "hostname" in result["message"]

    def test_dry_run_contains_dry_run_label(self, mock_log):
        executor = Executor(dry_run=True)
        result = executor.execute("echo hello")
        assert "DRY-RUN" in result["message"]

    def test_dry_run_includes_command_key(self, mock_log):
        executor = Executor(dry_run=True)
        result = executor.execute("whoami")
        assert result["command"] == "whoami"

    def test_dry_run_default_is_true(self, mock_log):
        executor = Executor()
        assert executor.dry_run is True

    def test_dry_run_does_not_call_subprocess(self, mock_log):
        executor = Executor(dry_run=True)
        with patch("src.executor.subprocess.run") as mock_run:
            executor.execute("ping 8.8.8.8")
            mock_run.assert_not_called()


# ──────────────────────────────────────────────
# Safety blocking
# ──────────────────────────────────────────────
@patch("src.executor.log_event")
class TestSafetyBlocking:
    """Unsafe commands must be blocked regardless of dry_run flag."""

    def test_unsafe_command_blocked(self, mock_log):
        executor = Executor(dry_run=False)
        result = executor.execute("rm -rf /")
        assert result["status"] == "blocked"

    def test_unsafe_command_blocked_in_dry_run(self, mock_log):
        executor = Executor(dry_run=True)
        result = executor.execute("shutdown /s")
        assert result["status"] == "blocked"

    def test_blocked_message_contains_command(self, mock_log):
        executor = Executor(dry_run=True)
        result = executor.execute("del /f C:\\*")
        assert "del /f C:\\*" in result["message"]

    def test_unknown_command_blocked(self, mock_log):
        executor = Executor(dry_run=False)
        result = executor.execute("curl http://evil.com")
        assert result["status"] == "blocked"

    def test_injection_blocked(self, mock_log):
        executor = Executor(dry_run=False)
        result = executor.execute("ping 8.8.8.8 && rm -rf /")
        assert result["status"] == "blocked"

    def test_empty_command_blocked(self, mock_log):
        executor = Executor(dry_run=False)
        result = executor.execute("")
        assert result["status"] == "blocked"

    def test_blocked_does_not_call_subprocess(self, mock_log):
        executor = Executor(dry_run=False)
        with patch("src.executor.subprocess.run") as mock_run:
            executor.execute("rm -rf /")
            mock_run.assert_not_called()


# ──────────────────────────────────────────────
# Live execution (dry_run=False)
# ──────────────────────────────────────────────
@patch("src.executor.log_event")
class TestLiveExecution:
    """Test actual command execution with safe commands."""

    def test_echo_succeeds(self, mock_log):
        executor = Executor(dry_run=False)
        result = executor.execute("echo test")
        assert result["status"] == "success"
        assert "test" in result["output"]

    def test_hostname_succeeds(self, mock_log):
        executor = Executor(dry_run=False)
        result = executor.execute("hostname")
        assert result["status"] == "success"
        assert len(result["output"]) > 0

    def test_success_includes_command_key(self, mock_log):
        executor = Executor(dry_run=False)
        result = executor.execute("echo hello")
        assert result["command"] == "echo hello"

    def test_failed_command_returns_error(self, mock_log):
        """Simulate a command failure via mocking."""
        executor = Executor(dry_run=False)
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "simulated error"
        mock_result.stdout = ""
        with patch("src.executor.subprocess.run", return_value=mock_result):
            result = executor.execute("echo test")
            assert result["status"] == "error"


# ──────────────────────────────────────────────
# Timeout handling
# ──────────────────────────────────────────────
@patch("src.executor.log_event")
class TestTimeoutHandling:
    """Verify that timed-out commands are handled gracefully."""

    def test_timeout_returns_timeout_status(self, mock_log):
        executor = Executor(dry_run=False)
        with patch(
            "src.executor.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="ping", timeout=15),
        ):
            result = executor.execute("ping 8.8.8.8")
            assert result["status"] == "timeout"

    def test_timeout_message_mentions_timeout(self, mock_log):
        executor = Executor(dry_run=False)
        with patch(
            "src.executor.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="ping", timeout=15),
        ):
            result = executor.execute("ping 8.8.8.8")
            assert "timed out" in result["message"].lower() or "timeout" in result["message"].lower()

    def test_generic_exception_returns_error(self, mock_log):
        executor = Executor(dry_run=False)
        with patch(
            "src.executor.subprocess.run",
            side_effect=OSError("file not found"),
        ):
            result = executor.execute("echo test")
            assert result["status"] == "error"
            assert "file not found" in result["message"].lower()


# ──────────────────────────────────────────────
# Toggle dry_run flag
# ──────────────────────────────────────────────
@patch("src.executor.log_event")
class TestToggleDryRun:
    """Verify that dry_run flag can be toggled at runtime."""

    def test_toggle_from_dry_to_live(self, mock_log):
        executor = Executor(dry_run=True)
        assert executor.dry_run is True
        executor.dry_run = False
        assert executor.dry_run is False

    def test_toggle_from_live_to_dry(self, mock_log):
        executor = Executor(dry_run=False)
        executor.dry_run = True
        result = executor.execute("echo test")
        assert result["status"] == "dry-run"

    def test_initial_dry_run_false(self, mock_log):
        executor = Executor(dry_run=False)
        assert executor.dry_run is False
