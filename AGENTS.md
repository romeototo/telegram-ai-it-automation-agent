# Agents Architecture

This repository uses a multi-agent architectural pattern to automate IT tasks safely. 
Here is an overview of the conceptual agents operating within this system:

## 1. Planner Agent
- **Role**: Interprets the raw user request from Telegram.
- **Responsibility**: Breaks down high-level requests ("Server is slow") into a sequence of actionable CLI or script operations ("check_cpu", "check_memory").
- **Constraint**: Cannot execute anything. It only produces an execution plan.

## 2. Worker Agent
- **Role**: Executes the individual steps from the Planner Agent's plan.
- **Responsibility**: Takes a single step, validates it against the `Safety Engine`, and attempts to execute it on the host machine.
- **Constraint**: Must NEVER bypass the Safety Check. Operates in `Dry-Run` mode by default.

## 3. Analyzer / Reporter Agent
- **Role**: Consumes the output from the Worker Agent.
- **Responsibility**: Translates raw terminal outputs, logs, and errors into human-readable, beginner-friendly explanations sent back to the Telegram user.
- **Constraint**: Strips sensitive data from the final output before sending.
