"""
Application Configuration.
Loads all settings from environment variables via .env file.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # AI / LLM
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Security: Comma-separated Telegram user IDs allowed to use the bot
    ALLOWED_USER_IDS = [
        int(uid.strip())
        for uid in os.getenv("ALLOWED_USER_IDS", "").split(",")
        if uid.strip().isdigit()
    ]

    # Admin chat ID for proactive alerts
    ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")

    # Monitoring interval in seconds (default: 30 minutes)
    MONITOR_INTERVAL = int(os.getenv("MONITOR_INTERVAL", "1800"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Dry run is True by default for safety
    DRY_RUN_DEFAULT = os.getenv("DRY_RUN_DEFAULT", "True").lower() in (
        "true",
        "1",
        "yes",
    )


config = Config()
