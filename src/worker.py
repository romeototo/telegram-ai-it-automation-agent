"""
Worker Node: Orchestrates the Planner and Executor.
Provides both single-request processing and full system health reports.
"""
from .agent_planner import AgentPlanner
from .executor import Executor
from .logger import log_event


class WorkerNode:
    def __init__(self, dry_run: bool = True, gemini_api_key: str = None):
        self.planner = AgentPlanner(gemini_api_key=gemini_api_key)
        self.executor = Executor(dry_run=dry_run)

    def process_request(self, user_request: str) -> str:
        """
        End-to-end processing of a user request.
        Returns Markdown-formatted output.
        """
        log_event("WORKER_RECEIVED_REQUEST", {"request": user_request})

        # 1. Plan
        steps = self.planner.plan(user_request)

        if not steps:
            return "⚠️ Planner could not generate any steps for this request."

        results = []
        status_counts = {"success": 0, "dry-run": 0, "blocked": 0, "error": 0, "timeout": 0}

        # 2. Execute each step
        for i, step in enumerate(steps, 1):
            result = self.executor.execute(step)
            status = result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

            # Format individual result
            if status == "success":
                output = result.get("output", "")
                # Truncate very long outputs
                if len(output) > 1500:
                    output = output[:1500] + "\n... (truncated)"
                results.append(f"*Step {i}:* `{step}`\n✅ Success\n```\n{output}\n```")
            elif status == "dry-run":
                results.append(f"*Step {i}:* {result['message']}")
            elif status == "blocked":
                results.append(f"*Step {i}:* {result['message']}")
            else:
                results.append(f"*Step {i}:* `{step}`\n{result.get('message', 'Unknown error')}")

        # 3. Summarize
        separator = "\n\n─────────────────\n\n"
        final_output = separator.join(results)

        # Add summary footer
        total = len(steps)
        mode = "🔒 DRY-RUN" if self.executor.dry_run else "⚡ LIVE"
        footer = f"\n\n📊 *Summary:* {total} step(s) | Mode: {mode}"
        if status_counts.get("blocked", 0) > 0:
            footer += f" | ⛔ {status_counts['blocked']} blocked"

        final_output += footer

        log_event("WORKER_COMPLETED", {
            "total_steps": total,
            "status_counts": status_counts,
        })

        return final_output

    def generate_health_report(self) -> str:
        """
        Generates a comprehensive system health report.
        Runs multiple diagnostic commands and formats the results.
        """
        log_event("HEALTH_REPORT_STARTED", {})

        checks = [
            ("🖥️ Hostname", "hostname"),
            ("🧠 CPU", "wmic cpu get loadpercentage,name"),
            ("💾 Memory", "wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /Value"),
            ("💿 Disk", "wmic logicaldisk get caption,size,freespace"),
            ("🌐 Network", "ipconfig"),
        ]

        report_parts = ["📋 *System Health Report*\n"]

        for label, cmd in checks:
            result = self.executor.execute(cmd)
            if result["status"] == "success":
                output = result.get("output", "N/A")
                # Trim long outputs
                if len(output) > 500:
                    output = output[:500] + "\n..."
                report_parts.append(f"*{label}*\n```\n{output}\n```")
            elif result["status"] == "dry-run":
                report_parts.append(f"*{label}*\n🔒 `{cmd}` (dry-run)")
            else:
                report_parts.append(f"*{label}*\n⚠️ {result.get('message', 'Failed')}")

        mode = "🔒 DRY-RUN" if self.executor.dry_run else "⚡ LIVE"
        report_parts.append(f"\n_Mode: {mode}_")

        log_event("HEALTH_REPORT_COMPLETED", {})
        return "\n\n".join(report_parts)
