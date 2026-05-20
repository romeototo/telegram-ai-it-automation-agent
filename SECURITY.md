# Security Policy

## Supported Versions

Currently, only the latest `main` branch version is officially supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| v2.x.x  | :white_check_mark: |
| v1.x.x  | :x:                |

## Reporting a Vulnerability

Security is a core focus of the **Telegram AI IT Automation Agent**, as it executes system-level commands based on user inputs.

If you discover a potential vulnerability, **please do not disclose it publicly**. Instead, follow these steps:

1. **Email or Message the Maintainer**: Reach out privately to the repository owner.
2. **Provide Details**: Describe the vulnerability, how it can be exploited (steps to reproduce), and any potential mitigation strategies.
3. **Wait for Triage**: We will acknowledge your report within 48 hours and begin investigating the issue.

### In-Scope Vulnerabilities
We are particularly interested in reports concerning:
- Bypasses of the `src/safety.py` engine.
- Command Injection vulnerabilities.
- Authorization bypasses (users interacting with the bot despite not being in `ALLOWED_USER_IDS`).

### Out-of-Scope Vulnerabilities
- Issues requiring physical access to the host machine.
- Theoretical attacks without proof of concept.

Thank you for helping keep this project secure! 🛡️
