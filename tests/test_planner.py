"""
Unit tests for AgentPlanner (src/agent_planner.py).
Tests focus on the rule-based fallback (_plan_rule_based via plan()).
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch
from src.agent_planner import AgentPlanner


# Patch log_event globally so tests don't need real logging
@patch("src.agent_planner.log_event")
class TestPlannerRuleBased:
    """Tests for the rule-based fallback planner."""

    def _planner(self):
        """Create an AgentPlanner without Gemini (rule-based only)."""
        return AgentPlanner(gemini_api_key=None)

    # ── Return type ────────────────────────────
    def test_plan_returns_list(self, mock_log):
        planner = self._planner()
        result = planner.plan("check disk usage")
        assert isinstance(result, list)

    def test_plan_returns_list_of_strings(self, mock_log):
        planner = self._planner()
        result = planner.plan("check memory")
        for item in result:
            assert isinstance(item, str)

    # ── Disk intent ────────────────────────────
    def test_disk_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("check disk usage")
        assert len(result) >= 1
        assert any("logicaldisk" in cmd.lower() or "wmic" in cmd.lower() for cmd in result)

    def test_storage_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("how much storage is left")
        assert len(result) >= 1
        assert any("logicaldisk" in cmd.lower() or "wmic" in cmd.lower() for cmd in result)

    def test_space_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("check free space")
        assert len(result) >= 1
        assert any("logicaldisk" in cmd.lower() for cmd in result)

    # ── Memory intent ──────────────────────────
    def test_memory_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("check memory usage")
        assert len(result) >= 1
        assert any("memory" in cmd.lower() or "wmic" in cmd.lower() for cmd in result)

    def test_ram_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("how much ram is available")
        assert len(result) >= 1
        assert any("memory" in cmd.lower() for cmd in result)

    # ── CPU intent ─────────────────────────────
    def test_cpu_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("check cpu load")
        assert len(result) >= 1
        assert any("cpu" in cmd.lower() or "loadpercentage" in cmd.lower() for cmd in result)

    def test_processor_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("processor usage high")
        assert len(result) >= 1
        assert any("cpu" in cmd.lower() for cmd in result)

    def test_load_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("server load is high")
        assert len(result) >= 1
        assert any("cpu" in cmd.lower() or "load" in cmd.lower() for cmd in result)

    # ── Network intent ─────────────────────────
    def test_network_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("check network configuration")
        assert len(result) >= 1
        assert any("ipconfig" in cmd.lower() for cmd in result)

    def test_ip_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("show ip address")
        assert len(result) >= 1
        assert any("ipconfig" in cmd.lower() for cmd in result)

    # ── Ping intent ────────────────────────────
    def test_ping_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("ping 8.8.8.8")
        assert len(result) >= 1
        assert any("ping" in cmd.lower() for cmd in result)

    # ── Process / task intent ──────────────────
    def test_process_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("show running processes")
        assert len(result) >= 1
        assert any("tasklist" in cmd.lower() for cmd in result)

    def test_task_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("list active tasks")
        assert len(result) >= 1
        assert any("tasklist" in cmd.lower() for cmd in result)

    # ── Service intent ─────────────────────────
    def test_service_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("check windows service status")
        assert len(result) >= 1
        assert any("sc" in cmd.lower() for cmd in result)

    # ── DNS intent ─────────────────────────────
    def test_dns_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("dns lookup for google")
        assert len(result) >= 1
        assert any("nslookup" in cmd.lower() for cmd in result)

    # ── Hostname intent ────────────────────────
    def test_hostname_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("what is the hostname")
        assert len(result) >= 1
        assert any("hostname" in cmd.lower() for cmd in result)

    # ── Health / report intent ─────────────────
    def test_report_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("generate full system report")
        assert len(result) >= 2  # Should return multiple commands
        assert any("hostname" in cmd.lower() for cmd in result)

    def test_health_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("system health check")
        assert len(result) >= 2

    # ── Unknown intent ─────────────────────────
    def test_unknown_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("make me a sandwich")
        assert len(result) == 1
        assert "echo" in result[0].lower()
        assert "unrecognized" in result[0].lower() or "not supported" in result[0].lower()

    def test_empty_intent(self, mock_log):
        planner = self._planner()
        result = planner.plan("")
        assert isinstance(result, list)
        assert len(result) >= 1

    # ── Multiple keywords — first match wins ──
    def test_multiple_keywords_disk_first(self, mock_log):
        """When intent contains 'disk' and 'memory', disk should match first."""
        planner = self._planner()
        result = planner.plan("check disk and memory usage")
        assert len(result) >= 1
        # Disk should match first (elif chain)
        assert any("logicaldisk" in cmd.lower() or "wmic" in cmd.lower() for cmd in result)

    def test_multiple_keywords_cpu_before_ping(self, mock_log):
        """CPU intent should match before ping since CPU comes first in elif."""
        planner = self._planner()
        result = planner.plan("check cpu load and ping server")
        assert len(result) >= 1
        assert any("cpu" in cmd.lower() for cmd in result)

    # ── Plan always returns list ───────────────
    def test_plan_never_returns_none(self, mock_log):
        planner = self._planner()
        for intent in ["disk", "memory", "cpu", "ping", "process", "xyz", ""]:
            result = planner.plan(intent)
            assert result is not None, f"plan('{intent}') returned None"
            assert isinstance(result, list), f"plan('{intent}') returned {type(result)}"

    def test_plan_always_non_empty_list(self, mock_log):
        planner = self._planner()
        for intent in ["disk", "memory", "cpu", "network", "process", "unknown"]:
            result = planner.plan(intent)
            assert len(result) > 0, f"plan('{intent}') returned empty list"
