# Telegram AI IT Automation Agent

A GitHub-ready Python prototype demonstrating an AI agent workflow for IT support automation using Telegram.
This project is built as a **Proof-of-Work** for an AI Token Grant Application, prioritizing **Safety, Audibility, and Automation**.

## Features
- **Telegram Interface**: Interact with the automation system natively via Telegram (/start, /status, /check_disk, etc.).
- **Agent Planner**: Uses LLMs to understand complex user intents and break them down into actionable steps.
- **Worker Node Logic**: Executes the planned steps asynchronously.
- **Strict Safety Engine**: Denylist and Allowlist for shell commands to prevent destructive operations (rm, sudo, format).
- **Dry-Run by Default**: Safe mode is ON by default. Commands are planned but not executed unless explicitly permitted.
- **JSONL Auditing**: All interactions, agent plans, and command executions are securely logged in JSONL format.

## Getting Started

1. **Clone the repository**
2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment**:
   Copy `.env.example` to `.env` and fill in your keys.
   ```bash
   cp .env.example .env
   ```
4. **Run the Application**:
   ```bash
   python src/main.py
   ```

## Demo Commands
- `/start` - Start the bot
- `/help` - Show available commands
- `/status` - Check agent system status
- `/check_disk` - Check disk usage safely
- `/check_memory` - Check system memory safely
- `/analyze_log` - Analyze system logs using AI
- `/make_sop` - Generate Standard Operating Procedures
- `/dry_run` - Toggle dry-run mode (Default is ON)

## Safety Notice
Safety is paramount. The system will **never** bypass `src/safety.py`. Hardcoded secrets are avoided. Please review `docs/safety_policy.md` for more details.
