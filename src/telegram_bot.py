"""
Telegram Bot Interface.
Handles incoming commands and routes them to the Worker Node.
"""
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from .config import config
from .worker import WorkerNode
from .logger import log_event

worker = WorkerNode(dry_run=config.DRY_RUN_DEFAULT)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start"""
    log_event("COMMAND_START", {"user": update.effective_user.name})
    await update.message.reply_text("Hello! I am the IT Automation Agent. Send /help to see what I can do.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /help"""
    log_event("COMMAND_HELP", {"user": update.effective_user.name})
    help_text = (
        "/start - Start the bot\n"
        "/help - Show this message\n"
        "/status - Check agent system status\n"
        "/check_disk - Check disk usage safely\n"
        "/check_memory - Check system memory safely\n"
        "/analyze_log - Analyze system logs using AI\n"
        "/make_sop - Generate SOPs\n"
        "/dry_run - Toggle dry-run mode (Default is ON)"
    )
    await update.message.reply_text(help_text)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_event("COMMAND_STATUS", {})
    await update.message.reply_text(f"Agent Status: Online\nDry Run Mode: {worker.executor.dry_run}")

async def handle_intent(update: Update, intent: str):
    await update.message.reply_text(f"Processing request: {intent}...")
    result = worker.process_request(intent)
    await update.message.reply_text(f"Result:\n{result}")

async def check_disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_intent(update, "check disk usage")

async def check_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_intent(update, "check memory usage")

async def analyze_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Mock: Log analysis feature not fully implemented in prototype.")

async def make_sop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Mock: Generating SOP...")

async def toggle_dry_run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # In a real system, you'd want authorization here
    worker.executor.dry_run = not worker.executor.dry_run
    status_str = "ON" if worker.executor.dry_run else "OFF"
    log_event("TOGGLE_DRY_RUN", {"new_status": worker.executor.dry_run})
    await update.message.reply_text(f"Dry Run mode is now {status_str}.")

def get_application():
    if not config.TELEGRAM_BOT_TOKEN:
        print("Warning: TELEGRAM_BOT_TOKEN is not set in .env")
        # Return dummy app if we want it to instantiate safely in tests without real token
        
    app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN or "12345:dummy_token").build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("check_disk", check_disk))
    app.add_handler(CommandHandler("check_memory", check_memory))
    app.add_handler(CommandHandler("analyze_log", analyze_log))
    app.add_handler(CommandHandler("make_sop", make_sop))
    app.add_handler(CommandHandler("dry_run", toggle_dry_run))
    
    return app
