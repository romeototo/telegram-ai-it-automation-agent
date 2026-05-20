# Changelog

All notable changes to the **Telegram AI IT Automation Agent** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-05-20

### Added
- **Gemini 2.0 Flash Integration**: Replaced the mock planner with a real LLM using `google-genai` SDK to process natural language intents.
- **Natural Language Interface**: Users can now type regular sentences like "check disk space" without using slash commands.
- **User Authorization Whitelist**: Added `ALLOWED_USER_IDS` to restrict bot usage to authorized Telegram users only.
- **Scheduled Monitoring**: Proactive health checks run automatically based on `MONITOR_INTERVAL`, alerting `ADMIN_CHAT_ID` if critical conditions are met.
- **Dual Logging System**: Logs are now securely saved to both JSONL (for raw append-only audit) and SQLite (for queryable history).
- **New Commands**: Added `/report`, `/history`, `/check_cpu`, and `/check_network`.
- **Markdown Formatting**: Bot responses are now beautifully formatted using Telegram Markdown (e.g., bolding, code blocks, emojis).
- **Docker Readiness**: Added `Dockerfile` and `docker-compose.yml` for instant, isolated deployment.
- **Comprehensive Unit Tests**: Introduced 128 tests using `pytest`, covering Safety, Planner, and Executor nodes.
- **Community Standards**: Added `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, and `CHANGELOG.md`.

### Changed
- **Safety Engine**: Drastically improved `is_safe_command` with `contains_injection()` to block `&&`, `|`, `;` and other shell metacharacters. Expanded the allowlist to 20+ commands.
- **Executor Output**: The executor now clearly separates statuses into `success`, `error`, `blocked`, `dry-run`, and `timeout` with localized error handling.
- **Environment Variables**: Overhauled `.env.example` to incorporate new AI and Security variables.
- **Startup Sequence**: Added a v2.0 console banner and graceful shutdown handler to `main.py`.

### Fixed
- Fixed `/analyze_log` and `/make_sop` commands, migrating them from hardcoded mocked strings to functional, data-driven outputs based on SQLite logs.
- Handled Telegram's 4096-character message limits by chunking long outputs (e.g., for extensive system reports).

## [1.0.0] - 2026-04-28

### Added
- **Initial Prototype**: Basic multi-agent architecture (Planner, Worker, Executor).
- **Telegram Bot Interface**: Basic routing for commands like `/start`, `/help`, `/status`, `/check_disk`, and `/check_memory`.
- **Safety Prototype**: Initial denylist and allowlist logic in `safety.py`.
- **Dry-Run Default**: The agent operates in `DRY_RUN_DEFAULT=True` by default to prevent accidental executions.
- **Audit Logger**: Basic JSONL logging mechanism for all user interactions.
- **Bilingual Documentation**: Built-in English and Thai README files.
