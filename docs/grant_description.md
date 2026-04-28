# AI Token Grant Application: IT Automation Agent

**Project Name**: Telegram AI IT Automation Agent
**Focus Area**: Operations & Infrastructure Automation
**Applicant Name**: Romeo

## Project Abstract
This project proposes a secure, multi-agent AI system designed to automate Level 1 and Level 2 IT support tasks. It provides a native Telegram interface where IT administrators can issue natural language commands. The AI agents interpret these requests, generate a plan of action, and execute system commands safely.

## Problem Statement
IT administrators spend significant time running routine diagnostics and pulling logs. While traditional scripts solve some of this, they lack flexibility. Combining LLMs with terminal execution is powerful but inherently dangerous without strict guardrails.

## Solution
This prototype demonstrates the "safe orchestration" of AI. It implements:
1. **Agent Planner**: LLM-driven intent parsing.
2. **Safety Engine**: Hardcoded guards (Allow/Deny lists) preventing AI hallucinations from causing system damage.
3. **Dry-Run Mode**: State-safe simulations by default.
4. **Auditability**: Complete JSONL logging of all AI reasoning and CLI executions.

## Funding Request
The token grant will be utilized to:
1. Upgrade the Planner Agent to use advanced models (e.g. GPT-4, Gemini 1.5 Pro) for higher reasoning capabilities.
2. Develop the "Analyzer Agent" to summarize log files and generate SOPs automatically.
3. Pay for infrastructure to host a live, sandboxed demo environment.
