"""
Dual Logger: JSONL file + SQLite database for Auditing and Compliance.
Provides both append-only JSONL logs and queryable SQLite storage.
"""
import json
import logging
import sqlite3
from datetime import datetime, timezone
import os

# Ensure directories exist
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

JSONL_LOG_FILE = os.path.join(LOG_DIR, "execution_logs.jsonl")
SQLITE_DB_FILE = os.path.join(DATA_DIR, "audit.db")

# Standard logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telegram_agent")


def _init_db():
    """Initialize SQLite database with the audit_log table."""
    conn = sqlite3.connect(SQLITE_DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            user_name TEXT DEFAULT '',
            user_id TEXT DEFAULT '',
            command TEXT DEFAULT '',
            data TEXT DEFAULT '{}',
            status TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()


# Initialize DB on module load
_init_db()


def log_event(event_type: str, data: dict):
    """
    Logs an event to both JSONL file and SQLite database.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    event = {
        "timestamp": timestamp,
        "event_type": event_type,
        "data": data,
    }

    logger.info(f"[{event_type}] {json.dumps(data, ensure_ascii=False)}")

    # Write to JSONL (append-only)
    try:
        with open(JSONL_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Failed to write to JSONL log: {e}")

    # Write to SQLite
    try:
        conn = sqlite3.connect(SQLITE_DB_FILE)
        conn.execute(
            """INSERT INTO audit_log (timestamp, event_type, user_name, user_id, command, data, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                timestamp,
                event_type,
                data.get("user", ""),
                str(data.get("user_id", "")),
                data.get("command", ""),
                json.dumps(data, ensure_ascii=False),
                data.get("status", ""),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to write to SQLite log: {e}")


def get_recent_logs(limit: int = 10) -> list[dict]:
    """
    Retrieves the most recent audit log entries from SQLite.
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Failed to read from SQLite: {e}")
        return []


def get_log_stats() -> dict:
    """
    Returns summary statistics of the audit log.
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_FILE)
        total = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
        blocked = conn.execute(
            "SELECT COUNT(*) FROM audit_log WHERE event_type = 'EXECUTION_BLOCKED'"
        ).fetchone()[0]
        success = conn.execute(
            "SELECT COUNT(*) FROM audit_log WHERE event_type = 'EXECUTION_SUCCESS'"
        ).fetchone()[0]
        conn.close()
        return {"total_events": total, "blocked": blocked, "successful": success}
    except Exception as e:
        logger.error(f"Failed to get log stats: {e}")
        return {"total_events": 0, "blocked": 0, "successful": 0}
