import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "rate_limit.db"

def get_connection() -> sqlite3.Connection:
    # timeout=5 prevents immediate crashes if the DB is locked
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.row_factory = sqlite3.Row
    # WAL mode allows concurrent reads while writing
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS buckets (
                key TEXT PRIMARY KEY,
                tokens REAL NOT NULL,
                last_refill REAL NOT NULL
            )
        """)