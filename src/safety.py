"""
Safety Engine for IT Automation Agent.
Never bypass this module.

This module provides two layers of protection:
1. Command Allowlist/Denylist — only pre-approved commands can execute.
2. Injection Detection — blocks shell metacharacters that could chain commands.
"""

# Commands that are NEVER allowed, regardless of context
DANGEROUS_COMMANDS_DENYLIST = [
    "rm", "del", "format", "sudo", "su", "chmod", "chown",
    "mkfs", "reboot", "shutdown", "kill", "pkill", "killall",
    "dd", "fdisk", "passwd", "useradd", "userdel", "reg",
    "powershell", "cmd",
]

# Commands that ARE allowed for safe IT diagnostics
SAFE_COMMANDS_ALLOWLIST = [
    "ping", "df", "free", "systeminfo", "tasklist", "ipconfig",
    "dir", "ls", "echo", "hostname", "whoami", "wmic", "netstat",
    "nslookup", "tracert", "type", "findstr", "sc", "net",
    "Get-Process", "Get-Service", "Get-WmiObject", "Get-CimInstance",
]

# Shell metacharacters used for command injection
INJECTION_PATTERNS = ["&&", "||", ";", "|", "`", "$(", "${", "\n", "\r"]


def contains_injection(command: str) -> bool:
    """
    Detects common shell injection patterns in a command string.
    Returns True if injection is detected.
    """
    for pattern in INJECTION_PATTERNS:
        if pattern in command:
            return True
    return False


def is_safe_command(command: str) -> bool:
    """
    Checks if a command is safe to execute.
    A command must:
      1. Not be empty
      2. Not contain injection patterns
      3. Have its base command in the allowlist
      4. Not contain any denylisted keywords
    """
    if not command or not command.strip():
        return False

    # Check for command injection first
    if contains_injection(command):
        return False

    cmd_parts = command.strip().split()
    base_cmd = cmd_parts[0].lower()

    # Check denylist (any part of the command)
    for dangerous in DANGEROUS_COMMANDS_DENYLIST:
        if dangerous == base_cmd:
            return False

    # Check allowlist (base command must be in the list, case-insensitive)
    allowlist_lower = [cmd.lower() for cmd in SAFE_COMMANDS_ALLOWLIST]
    if base_cmd not in allowlist_lower:
        return False

    return True
