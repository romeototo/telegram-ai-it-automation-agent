"""
Worker Node: Orchestrates the Planner and Executor.
"""
from .agent_planner import AgentPlanner
from .executor import Executor
from .logger import log_event

class WorkerNode:
    def __init__(self, dry_run: bool = True):
        self.planner = AgentPlanner()
        self.executor = Executor(dry_run=dry_run)

    def process_request(self, user_request: str) -> str:
        """
        End-to-end processing of a user request.
        """
        log_event("WORKER_RECEIVED_REQUEST", {"request": user_request})
        
        # 1. Plan
        steps = self.planner.plan(user_request)
        
        if not steps:
            return "Planner could not generate any steps."

        results = []
        # 2. Execute
        for step in steps:
            result = self.executor.execute(step)
            results.append(f"Command: {step}\nStatus: {result['status']}\nOutput: {result.get('output', result.get('message', ''))}")
        
        # 3. Summarize
        final_output = "\n\n".join(results)
        log_event("WORKER_COMPLETED", {"final_output_length": len(final_output)})
        
        return final_output
