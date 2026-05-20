"""
Telegram Bot Interface.
Handles incoming commands, natural language messages, user authorization,
scheduled monitoring, and routes them to the Worker Node.
"""
import os
from datetime import datetime, timezone

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .config import config
from .worker import WorkerNode
from .logger import log_event, get_recent_logs, get_log_stats

worker = WorkerNode(
    dry_run=config.DRY_RUN_DEFAULT,
    gemini_api_key=config.GEMINI_API_KEY,
)


# ──────────────────────────────────────────────
# Authorization Middleware
# ──────────────────────────────────────────────
async def check_authorized(update: Update) -> bool:
    """Check if the user is in the allowed users list."""
    if not config.ALLOWED_USER_IDS:
        # If no whitelist configured, allow all (for development)
        return True

    user_id = update.effective_user.id
    if user_id not in config.ALLOWED_USER_IDS:
        log_event("UNAUTHORIZED_ACCESS", {
            "user": update.effective_user.name,
            "user_id": user_id,
        })
        await update.message.reply_text(
            "⛔ *Unauthorized Access*\n\n"
            f"Your Telegram ID (`{user_id}`) is not authorized.\n"
            "Contact your administrator to get access.",
            parse_mode="Markdown",
        )
        return False
    return True


# ──────────────────────────────────────────────
# Command Handlers
# ──────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start"""
    log_event("COMMAND_START", {
        "user": update.effective_user.name,
        "user_id": update.effective_user.id,
    })
    welcome = (
        "🤖 *Welcome to IT Automation Agent!*\n\n"
        "I help you manage and monitor your IT infrastructure safely.\n\n"
        "🔹 Use `/help` to see available commands\n"
        "🔹 Or just type naturally: _\"check disk space\"_\n\n"
        f"🔒 Dry-Run Mode: *{'ON' if worker.executor.dry_run else 'OFF'}*\n"
        f"🧠 AI Planner: *{'Gemini LLM' if worker.planner.use_llm else 'Rule-Based'}*"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /help"""
    log_event("COMMAND_HELP", {"user": update.effective_user.name})
    help_text = (
        "📖 *Available Commands*\n\n"
        "🔍 *Diagnostics*\n"
        "  /check\\_disk — Check disk usage\n"
        "  /check\\_memory — Check RAM usage\n"
        "  /check\\_cpu — Check CPU load\n"
        "  /check\\_network — Check network config\n"
        "  /report — Full system health report\n\n"
        "🛠️ *Tools*\n"
        "  /analyze\\_log — AI-powered log analysis\n"
        "  /make\\_sop — Generate SOPs\n\n"
        "⚙️ *System*\n"
        "  /status — Bot and system status\n"
        "  /history — Recent command history\n"
        "  /dry\\_run — Toggle dry-run mode\n\n"
        "💬 *Natural Language*\n"
        "  Just type naturally! e.g. _\"check disk space\"_"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /status — shows bot and system status."""
    if not await check_authorized(update):
        return

    log_event("COMMAND_STATUS", {"user": update.effective_user.name})
    stats = get_log_stats()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    status_text = (
        "📊 *Agent Status*\n\n"
        f"🟢 Status: *Online*\n"
        f"🔒 Dry-Run: *{'ON' if worker.executor.dry_run else 'OFF'}*\n"
        f"🧠 AI Mode: *{'Gemini LLM' if worker.planner.use_llm else 'Rule-Based'}*\n"
        f"⏰ Time: `{now}`\n\n"
        f"📈 *Statistics*\n"
        f"  Total events: {stats['total_events']}\n"
        f"  Successful: {stats['successful']}\n"
        f"  Blocked: {stats['blocked']}"
    )
    await update.message.reply_text(status_text, parse_mode="Markdown")


# ──────────────────────────────────────────────
# Intent-Based Handlers
# ──────────────────────────────────────────────
async def handle_intent(update: Update, intent: str):
    """Process an intent through the Worker pipeline."""
    if not await check_authorized(update):
        return

    log_event("INTENT_RECEIVED", {
        "user": update.effective_user.name,
        "user_id": update.effective_user.id,
        "intent": intent,
    })

    await update.message.reply_text(f"⏳ Processing: _{intent}_...", parse_mode="Markdown")

    result = worker.process_request(intent)

    # Telegram has a 4096 char limit per message
    if len(result) > 4000:
        # Split into chunks
        chunks = [result[i:i + 3900] for i in range(0, len(result), 3900)]
        for chunk in chunks:
            await update.message.reply_text(chunk, parse_mode="Markdown")
    else:
        await update.message.reply_text(result, parse_mode="Markdown")


async def check_disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /check_disk"""
    await handle_intent(update, "check disk usage")


async def check_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /check_memory"""
    await handle_intent(update, "check memory usage")


async def check_cpu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /check_cpu"""
    await handle_intent(update, "check cpu usage")


async def check_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /check_network"""
    await handle_intent(update, "check network configuration")


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /report — full system health report."""
    if not await check_authorized(update):
        return

    log_event("COMMAND_REPORT", {"user": update.effective_user.name})
    await update.message.reply_text("📊 Generating system health report...", parse_mode="Markdown")

    result = worker.generate_health_report()

    if len(result) > 4000:
        chunks = [result[i:i + 3900] for i in range(0, len(result), 3900)]
        for chunk in chunks:
            await update.message.reply_text(chunk, parse_mode="Markdown")
    else:
        await update.message.reply_text(result, parse_mode="Markdown")


async def analyze_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /analyze_log — analyze recent audit logs."""
    if not await check_authorized(update):
        return

    log_event("COMMAND_ANALYZE_LOG", {"user": update.effective_user.name})

    recent = get_recent_logs(20)
    if not recent:
        await update.message.reply_text("📭 No logs found to analyze.")
        return

    # Summarize log entries
    event_counts = {}
    for entry in recent:
        etype = entry.get("event_type", "UNKNOWN")
        event_counts[etype] = event_counts.get(etype, 0) + 1

    blocked = sum(1 for e in recent if e.get("event_type") == "EXECUTION_BLOCKED")
    errors = sum(1 for e in recent if "ERROR" in e.get("event_type", "") or "FAILED" in e.get("event_type", ""))

    summary_lines = [f"📋 *Log Analysis* (last {len(recent)} events)\n"]

    if blocked > 0:
        summary_lines.append(f"⛔ *{blocked} command(s) blocked* by Safety Engine")
    if errors > 0:
        summary_lines.append(f"❌ *{errors} error(s)/failure(s)* detected")
    if blocked == 0 and errors == 0:
        summary_lines.append("✅ No security blocks or errors detected")

    summary_lines.append("\n📊 *Event Breakdown:*")
    for etype, count in sorted(event_counts.items(), key=lambda x: -x[1]):
        emoji = "⛔" if "BLOCK" in etype else "❌" if "ERROR" in etype or "FAIL" in etype else "✅"
        summary_lines.append(f"  {emoji} `{etype}`: {count}")

    await update.message.reply_text("\n".join(summary_lines), parse_mode="Markdown")


async def make_sop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /make_sop — generate a basic SOP template."""
    if not await check_authorized(update):
        return

    log_event("COMMAND_MAKE_SOP", {"user": update.effective_user.name})

    # Generate SOP based on recent activity
    stats = get_log_stats()

    sop = (
        "📝 *Standard Operating Procedure*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "*SOP: System Health Check*\n\n"
        "*1. Pre-Check*\n"
        "  • Verify bot is online: `/status`\n"
        "  • Ensure Dry-Run is ON: `/dry_run`\n\n"
        "*2. Diagnostics*\n"
        "  • Check CPU: `/check_cpu`\n"
        "  • Check Memory: `/check_memory`\n"
        "  • Check Disk: `/check_disk`\n"
        "  • Check Network: `/check_network`\n"
        "  • Or run all at once: `/report`\n\n"
        "*3. Review & Act*\n"
        "  • Review output for anomalies\n"
        "  • If issues found → escalate to admin\n"
        "  • Log results: `/analyze_log`\n\n"
        "*4. Audit*\n"
        f"  • Total events logged: {stats['total_events']}\n"
        f"  • Commands blocked: {stats['blocked']}\n"
        "  • Review history: `/history`\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"_Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_"
    )
    await update.message.reply_text(sop, parse_mode="Markdown")


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /history — show recent command history."""
    if not await check_authorized(update):
        return

    log_event("COMMAND_HISTORY", {"user": update.effective_user.name})

    recent = get_recent_logs(10)
    if not recent:
        await update.message.reply_text("📭 No history found.")
        return

    lines = ["🕐 *Recent Activity* (last 10)\n"]
    for entry in recent:
        ts = entry.get("timestamp", "")[:19].replace("T", " ")
        etype = entry.get("event_type", "")
        cmd = entry.get("command", "")

        emoji = "⛔" if "BLOCK" in etype else "❌" if "ERROR" in etype else "✅"
        line = f"`{ts}` {emoji} {etype}"
        if cmd:
            line += f"\n     ↳ `{cmd}`"
        lines.append(line)

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def toggle_dry_run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /dry_run — toggle dry-run safety mode."""
    if not await check_authorized(update):
        return

    worker.executor.dry_run = not worker.executor.dry_run
    status_str = "ON ✅" if worker.executor.dry_run else "OFF ⚠️"
    log_event("TOGGLE_DRY_RUN", {
        "user": update.effective_user.name,
        "new_status": worker.executor.dry_run,
    })

    msg = f"🔒 Dry-Run mode is now: *{status_str}*\n\n"
    if not worker.executor.dry_run:
        msg += (
            "⚠️ *WARNING:* Commands will now execute on the real system!\n"
            "Use `/dry_run` again to re-enable safety mode."
        )
    else:
        msg += "Commands will be simulated. No changes to the system."

    await update.message.reply_text(msg, parse_mode="Markdown")


# ──────────────────────────────────────────────
# Natural Language Message Handler
# ──────────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle plain text messages as natural language intents."""
    user_text = update.message.text.strip()
    if not user_text:
        return

    log_event("NLP_MESSAGE", {
        "user": update.effective_user.name,
        "user_id": update.effective_user.id,
        "text": user_text,
    })

    await handle_intent(update, user_text)


# ──────────────────────────────────────────────
# Scheduled Monitoring
# ──────────────────────────────────────────────
async def monitor_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Periodic health check job. Sends alerts to admin if issues found.
    Runs according to MONITOR_INTERVAL config.
    """
    if not config.ADMIN_CHAT_ID:
        return

    log_event("MONITOR_CHECK", {"status": "running"})

    # Run a quick health check
    result = worker.generate_health_report()

    # Check for critical keywords
    critical_keywords = ["critical", "error", "fail", "0 free", "100%"]
    is_critical = any(kw in result.lower() for kw in critical_keywords)

    if is_critical:
        alert = f"🚨 *ALERT: System Health Issue Detected*\n\n{result}"
        try:
            await context.bot.send_message(
                chat_id=int(config.ADMIN_CHAT_ID),
                text=alert[:4000],
                parse_mode="Markdown",
            )
            log_event("MONITOR_ALERT_SENT", {"reason": "critical_detected"})
        except Exception as e:
            log_event("MONITOR_ALERT_FAILED", {"error": str(e)})
    else:
        log_event("MONITOR_CHECK", {"status": "ok"})


# ──────────────────────────────────────────────
# Application Builder
# ──────────────────────────────────────────────
def get_application():
    """Build and configure the Telegram bot application."""
    if not config.TELEGRAM_BOT_TOKEN:
        print("⚠️  Warning: TELEGRAM_BOT_TOKEN is not set in .env")

    token = config.TELEGRAM_BOT_TOKEN or "12345:dummy_token"
    app = ApplicationBuilder().token(token).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("check_disk", check_disk))
    app.add_handler(CommandHandler("check_memory", check_memory))
    app.add_handler(CommandHandler("check_cpu", check_cpu))
    app.add_handler(CommandHandler("check_network", check_network))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("analyze_log", analyze_log))
    app.add_handler(CommandHandler("make_sop", make_sop))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("dry_run", toggle_dry_run))

    # Natural language handler (must be last)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Schedule monitoring job
    if config.ADMIN_CHAT_ID and app.job_queue:
        app.job_queue.run_repeating(
            monitor_job,
            interval=config.MONITOR_INTERVAL,
            first=60,  # Start first check after 60 seconds
            name="health_monitor",
        )
        print(f"📡 Monitoring enabled (every {config.MONITOR_INTERVAL}s, alert → {config.ADMIN_CHAT_ID})")

    return app
