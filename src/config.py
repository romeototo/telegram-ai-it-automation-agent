import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Dry run is True by default for safety
    DRY_RUN_DEFAULT = os.getenv("DRY_RUN_DEFAULT", "True").lower() in ("true", "1", "yes")

config = Config()
