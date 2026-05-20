"""
Agent Planner: Breaks down user requests into safe CLI steps.

Supports two modes:
1. LLM Mode — Uses Google Gemini Flash to intelligently parse natural language.
2. Rule-Based Fallback — Keyword matching when LLM is unavailable.
"""
import json
import re
from .logger import log_event
from .safety import SAFE_COMMANDS_ALLOWLIST

# Try to import Gemini SDK (optional dependency)
try:
    from google import genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AgentPlanner:
    def __init__(self, gemini_api_key: str = None):
        self.use_llm = False
        self.client = None

        if gemini_api_key and GEMINI_AVAILABLE:
            try:
                self.client = genai.Client(api_key=gemini_api_key)
                self.use_llm = True
                log_event("PLANNER_INIT", {"mode": "gemini-llm"})
            except Exception as e:
                log_event("PLANNER_INIT_FAILED", {"error": str(e), "fallback": "rule-based"})
                self.use_llm = False
        else:
            log_event("PLANNER_INIT", {"mode": "rule-based"})

    def plan(self, user_intent: str) -> list[str]:
        """
        Translates user intent into a sequence of CLI commands.
        Tries LLM first, falls back to rule-based matching.
        """
        log_event("PLANNING_STARTED", {"user_intent": user_intent})

        if self.use_llm:
            try:
                plan = self._plan_with_llm(user_intent)
                if plan:
                    log_event("PLANNING_COMPLETED", {"plan": plan, "method": "llm"})
                    return plan
            except Exception as e:
                log_event("LLM_PLANNING_FAILED", {"error": str(e), "fallback": "rule-based"})

        # Fallback to rule-based planning
        plan = self._plan_rule_based(user_intent)
        log_event("PLANNING_COMPLETED", {"plan": plan, "method": "rule-based"})
        return plan

    def _plan_with_llm(self, user_intent: str) -> list[str]:
        """
        Uses Gemini to convert natural language into safe CLI commands.
        """
        allowlist_str = ", ".join(SAFE_COMMANDS_ALLOWLIST)
        prompt = f"""You are an IT automation assistant. Convert this user request into safe Windows CLI commands.

RULES:
- Only use commands from this allowlist: [{allowlist_str}]
- Return ONLY a valid JSON array of command strings
- Each command must be a single, complete CLI command
- Do NOT use shell chaining (&&, ||, ;, |)
- Maximum 5 commands per plan
- If the request doesn't map to any safe command, return ["echo Request not supported"]

User request: "{user_intent}"

Return JSON array only, no explanation:"""

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        text = response.text.strip()

        # Extract JSON from potential markdown code blocks
        json_match = re.search(r"\[.*\]", text, re.DOTALL)
        if json_match:
            commands = json.loads(json_match.group())
            if isinstance(commands, list) and all(isinstance(c, str) for c in commands):
                return commands[:5]  # Safety limit

        return []

    def _plan_rule_based(self, user_intent: str) -> list[str]:
        """
        Simple keyword-based planning fallback.
        """
        intent = user_intent.lower()
        plan = []

        if "disk" in intent or "storage" in intent or "space" in intent:
            plan.append("wmic logicaldisk get caption,size,freespace")
        elif "memory" in intent or "ram" in intent:
            plan.append("wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /Value")
        elif "cpu" in intent or "processor" in intent or "load" in intent:
            plan.append("wmic cpu get loadpercentage,name")
        elif "network" in intent or "ip" in intent or "net" in intent:
            plan.append("ipconfig /all")
        elif "ping" in intent:
            plan.append("ping 8.8.8.8 -n 4")
        elif "process" in intent or "task" in intent:
            plan.append("tasklist /fo table /nh")
        elif "service" in intent:
            plan.append("sc query type= service state= all")
        elif "dns" in intent:
            plan.append("nslookup google.com")
        elif "hostname" in intent or "who" in intent:
            plan.append("hostname")
        elif "report" in intent or "health" in intent or "all" in intent:
            # Comprehensive system report
            plan.extend([
                "hostname",
                "wmic cpu get loadpercentage,name",
                "wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /Value",
                "wmic logicaldisk get caption,size,freespace",
                "ipconfig",
            ])
        else:
            plan.append(
                "echo Unrecognized command intent. Supported: disk, memory, cpu, network, ping, process, service, dns, report"
            )

        return plan
