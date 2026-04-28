"""
Command Executor Node.
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
        """
        log_event("EXECUTION_REQUESTED", {"command": command, "dry_run": self.dry_run})

        if not is_safe_command(command):
            error_msg = f"Command '{command}' blocked by Safety Engine."
            log_event("EXECUTION_BLOCKED", {"command": command, "reason": "Not in allowlist or contains denylisted keywords."})
            return {"status": "error", "message": error_msg}

        if self.dry_run:
            log_event("EXECUTION_DRY_RUN", {"command": command})
            return {"status": "success", "message": f"[DRY-RUN] Simulated execution of: {command}"}

        try:
            log_event("EXECUTION_STARTED", {"command": command})
            result = subprocess.run(
                command, 
                shell=True, 
                text=True, 
                capture_output=True,
                timeout=10 # Prevent hanging
            )
            
            if result.returncode == 0:
                log_event("EXECUTION_SUCCESS", {"command": command})
                return {"status": "success", "output": result.stdout.strip()}
            else:
                log_event("EXECUTION_FAILED", {"command": command, "error": result.stderr.strip()})
                return {"status": "error", "message": result.stderr.strip()}
                
        except Exception as e:
            log_event("EXECUTION_EXCEPTION", {"command": command, "error": str(e)})
            return {"status": "error", "message": str(e)}
