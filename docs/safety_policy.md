# Safety Policy

As an AI-driven automation agent, safety is the absolute priority. This document outlines the security controls implemented in this prototype.

## 1. Dry-Run by Default
By default, the `Executor` operates in a simulation mode. It will log the intended commands and return a success message without ever touching the underlying OS. This must be explicitly disabled via an authorized `/dry_run` command.

## 2. Strict Allowlist & Denylist
The `Safety Engine` (`src/safety.py`) evaluates the base binary of every command before execution.
- **Denylist**: Commands like `rm`, `sudo`, `format` are explicitly blocked.
- **Allowlist**: Only commands like `ping`, `df`, `free`, `systeminfo`, `dir` are permitted.
- If a command is not on the Allowlist, it is blocked.

## 3. Immutability of Safety Check
The Worker node CANNOT bypass `safety.py`. The design enforces that the string passed to `subprocess.run` has first been approved by `is_safe_command()`.

## 4. No Hardcoded Secrets
API keys and bot tokens must be injected via environment variables (e.g., `.env`). Code containing secrets will not be committed.

## 5. JSONL Auditing
Every request, plan, execution attempt, and safety block is logged centrally in `logs/execution_logs.jsonl` with an immutable timestamp.
