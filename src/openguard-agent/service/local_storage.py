import os
import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

DB_FILE = os.getenv("OPENGUARD_DB_PATH", "agent_local.db")


class LocalStorage:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self):
        with self._lock, self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS policy_cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS offline_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS usage_state (
                    date_key TEXT PRIMARY KEY,
                    used_seconds INTEGER DEFAULT 0,
                    last_synced_at TEXT
                );
            """)

    def is_enrolled(self) -> bool:
        return self.get_policy("agent_token") is not None

    def save_credentials(self, device_id: str, token: str):
        self.set_policy("device_id", device_id)
        self.set_policy("agent_token", token)

    def get_credentials(self) -> tuple[str, str]:
        device_id = self.get_policy("device_id", "")
        token = self.get_policy("agent_token", "")
        return device_id, token

    def set_policy(self, key: str, value: Any):
        with self._lock, self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO policy_cache (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
                """,
                (key, json.dumps(value), datetime.now(timezone.utc).isoformat()),
            )

    def get_policy(self, key: str, default: Any = None) -> Any:
        with self._lock, self._get_connection() as conn:
            row = conn.execute(
                "SELECT value FROM policy_cache WHERE key = ?", (key,)
            ).fetchone()
            if row:
                return json.loads(row["value"])
            return default

    def push_log(self, event_type: str, payload: Dict[str, Any]):
        with self._lock, self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO offline_logs (event_type, payload, created_at)
                VALUES (?, ?, ?)
                """,
                (event_type, json.dumps(payload), datetime.now(timezone.utc).isoformat()),
            )

    def pull_pending_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock, self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, event_type, payload, created_at
                FROM offline_logs
                ORDER BY id ASC LIMIT ?
                """,
                (limit,),
            ).fetchall()

            return [
                {
                    "id": r["id"],
                    "event_type": r["event_type"],
                    "payload": json.loads(r["payload"]),
                    "created_at": r["created_at"],
                }
                for r in rows
            ]

    def delete_logs(self, log_ids: List[int]):
        if not log_ids:
            return
        placeholders = ",".join("?" for _ in log_ids)
        with self._lock, self._get_connection() as conn:
            conn.execute(
                f"DELETE FROM offline_logs WHERE id IN ({placeholders})",
                log_ids,
            )

    def update_daily_usage(self, date_key: str, used_seconds: int):
        with self._lock, self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO usage_state (date_key, used_seconds, last_synced_at)
                VALUES (?, ?, ?)
                ON CONFLICT(date_key) DO UPDATE SET
                    used_seconds = excluded.used_seconds,
                    last_synced_at = excluded.last_synced_at
                """,
                (date_key, used_seconds, datetime.now(timezone.utc).isoformat()),
            )

    def get_daily_usage(self, date_key: str) -> int:
        with self._lock, self._get_connection() as conn:
            row = conn.execute(
                "SELECT used_seconds FROM usage_state WHERE date_key = ?", (date_key,)
            ).fetchone()
            return row["used_seconds"] if row else 0