"""
Safety Engine for IT Automation Agent
Never bypass this module.
"""

DANGEROUS_COMMANDS_DENYLIST = [
    "rm", "del", "format", "sudo", "su", "chmod", "chown", "mkfs", "reboot", "shutdown"
]

SAFE_COMMANDS_ALLOWLIST = [
    "ping", "df", "free", "systeminfo", "tasklist", "ipconfig", "dir", "ls", "echo"
]

def is_safe_command(command: str) -> bool:
    """
    Checks if a command is safe to execute.
    """
    cmd_parts = command.lower().split()
    if not cmd_parts:
        return False
    
    base_cmd = cmd_parts[0]
    
    for dangerous in DANGEROUS_COMMANDS_DENYLIST:
        if dangerous in cmd_parts:
            return False

    # For safety prototype, only allow strictly listed commands
    if base_cmd not in SAFE_COMMANDS_ALLOWLIST:
        return False
        
    return True
