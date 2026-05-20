"""
Command Executor Node.
Executes commands after safety validation and supports dry-run simulation.
"""
import subprocess
from .safety import is_safe_command
from .logger import log_event


class Executor:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run

    def execute(self, command: str) -> dict:
        """
        Executes a command safely. Checks safety policies first.
        Returns a dict with keys: status, message/output, command.
        """
        log_event("EXECUTION_REQUESTED", {
            "command": command,
            "dry_run": self.dry_run,
        })

        if not is_safe_command(command):
            error_msg = f"⛔ Command blocked by Safety Engine: `{command}`"
            log_event("EXECUTION_BLOCKED", {
                "command": command,
                "reason": "Not in allowlist or contains denylisted/injection patterns.",
                "status": "blocked",
            })
            return {"status": "blocked", "message": error_msg, "command": command}

        if self.dry_run:
            log_event("EXECUTION_DRY_RUN", {"command": command, "status": "dry-run"})
            return {
                "status": "dry-run",
                "message": f"🔒 *[DRY-RUN]* Would execute:\n`{command}`",
                "command": command,
            }

        try:
            log_event("EXECUTION_STARTED", {"command": command})
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True,
                timeout=15,  # Prevent hanging
            )

            if result.returncode == 0:
                output = result.stdout.strip() or "(no output)"
                log_event("EXECUTION_SUCCESS", {
                    "command": command,
                    "status": "success",
                })
                return {
                    "status": "success",
                    "output": output,
                    "command": command,
                }
            else:
                error = result.stderr.strip() or f"Exit code: {result.returncode}"
                log_event("EXECUTION_FAILED", {
                    "command": command,
                    "error": error,
                    "status": "error",
                })
                return {
                    "status": "error",
                    "message": f"❌ Error: {error}",
                    "command": command,
                }

        except subprocess.TimeoutExpired:
            log_event("EXECUTION_TIMEOUT", {
                "command": command,
                "status": "timeout",
            })
            return {
                "status": "timeout",
                "message": f"⏱️ Command timed out after 15s: `{command}`",
                "command": command,
            }
        except Exception as e:
            log_event("EXECUTION_EXCEPTION", {
                "command": command,
                "error": str(e),
                "status": "error",
            })
            return {
                "status": "error",
                "message": f"❌ Exception: {str(e)}",
                "command": command,
            }
