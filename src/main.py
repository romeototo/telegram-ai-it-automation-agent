"""
Main Entry Point.
Initializes and runs the Telegram Bot.
"""
from src.telegram_bot import get_application
from src.logger import log_event


def main():
    log_event("SYSTEM_STARTUP", {
        "message": "Initializing Telegram AI IT Automation Agent v2.0",
    })
    print("=" * 50)
    print("  🤖 Telegram AI IT Automation Agent v2.0")
    print("=" * 50)
    print("Starting bot... (Ensure TELEGRAM_BOT_TOKEN is set in .env)")

    app = get_application()

    try:
        app.run_polling()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user.")
        log_event("SYSTEM_SHUTDOWN", {"reason": "keyboard_interrupt"})
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        log_event("SYSTEM_ERROR", {"error": str(e)})


if __name__ == "__main__":
    main()
