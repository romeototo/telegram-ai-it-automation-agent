"""
JSONL Logger for Auditing and Compliance.
"""
import json
import logging
from datetime import datetime
import os

# Ensure logs directory exists
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
JSONL_LOG_FILE = os.path.join(LOG_DIR, "execution_logs.jsonl")

# Standard logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telegram_agent")

def log_event(event_type: str, data: dict):
    """
    Logs an event in JSONL format for auditing.
    """
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "data": data
    }
    
    logger.info(f"[{event_type}] {json.dumps(data)}")
    
    try:
        with open(JSONL_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        logger.error(f"Failed to write to JSONL log: {e}")
