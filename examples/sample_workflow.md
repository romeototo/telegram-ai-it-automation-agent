# Sample Workflow

This document illustrates how a user request flows through the Telegram AI IT Automation Agent system.

## 1. User Request (Telegram)
User sends: `/check_disk`

## 2. Bot Routing (`telegram_bot.py`)
The command is caught by the `check_disk` handler, which forwards the intent `"check disk usage"` to the Worker Node.

## 3. Agent Planning (`agent_planner.py`)
The Planner Agent receives `"check disk usage"`.
It maps this intent to a safe system command.
**Plan Output**: `["systeminfo"]` (or `"df -h"` on Linux)

## 4. Safety Check (`safety.py`)
The Worker sends the planned step to the Executor.
The Executor passes `"systeminfo"` to the Safety Engine.
`is_safe_command("systeminfo")` returns `True`.

## 5. Execution (`executor.py`)
- If `Dry-Run` is ON: Returns a simulated success message.
- If `Dry-Run` is OFF: Executes `systeminfo` on the host OS using `subprocess`.

## 6. Output & Audit (`logger.py` & Telegram)
- All steps are logged as JSONL lines for the audit trail.
- The Worker returns the final execution string back to the Telegram handler.
- The bot replies to the user with the command output.
