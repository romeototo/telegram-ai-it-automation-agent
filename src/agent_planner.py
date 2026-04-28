"""
Agent Planner: Breaks down user requests into safe steps.
"""
from .logger import log_event

class AgentPlanner:
    def __init__(self):
        # In a real app, you would initialize OpenAI client here
        pass

    def plan(self, user_intent: str) -> list[str]:
        """
        Translates user intent into a sequence of CLI commands.
        (Mock implementation for prototype)
        """
        log_event("PLANNING_STARTED", {"user_intent": user_intent})
        
        intent = user_intent.lower()
        plan = []

        if "disk" in intent:
            # On windows, we might use 'dir' or similar. Assuming Windows based on env.
            plan.append("systeminfo") 
        elif "memory" in intent:
            plan.append("systeminfo")
        elif "ping" in intent:
            plan.append("ping 8.8.8.8 -n 4")
        else:
            plan.append("echo 'Unrecognized command intent. Please ask to check disk, memory, or ping.'")

        log_event("PLANNING_COMPLETED", {"plan": plan})
        return plan
