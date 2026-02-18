"""
Shared logging utility for CLI Guard

Provides consistent log formatting across all application layers.
All log entries are appended to Logs.txt with timestamps and source labels.

Usage:
    from logger import log

    log("AUTH", "User john signed in successfully")
    log("DATABASE", "Inserted password for Gmail")
    log("TUI", "Password created for account Twitter")
    log("CLI", "Command: get --user admin --account prod-db")
    log("ERROR", "Failed to decrypt password", exc_info=True)
"""

import os
import traceback
from datetime import datetime


# Log file lives in the project root
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logs.txt")


def log(source: str, message: str, exc_info: bool = False) -> None:
    """
    Write a timestamped log entry to Logs.txt

    Args:
        source: Which layer generated the log (AUTH, DATABASE, TUI, CLI, VALIDATION, ERROR)
        message: Human-readable description of what happened
        exc_info: If True, appends the current exception traceback (use in except blocks)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {source}: {message}\n")

            if exc_info:
                tb = traceback.format_exc()
                if tb and tb.strip() != "NoneType: None":
                    f.write(f"[{timestamp}] {source}: TRACEBACK:\n{tb}\n")
    except OSError:
        # If we can't write to the log file, fail silently
        # (we don't want logging failures to crash the app)
        pass
