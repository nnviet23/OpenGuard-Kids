"""Bộ nhớ đệm cục bộ (SQLite): chính sách đã ký, mức dùng hôm nay, hàng đợi sự kiện chưa gửi.

Dữ liệu chỉ gồm những trường được phép (tên ứng dụng/tên miền/thời lượng/thời điểm). Có hàm purge()
để thực thi lệnh “xóa toàn bộ dữ liệu của con tôi”.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

MAX_QUEUE = 50_000


class OfflineStore:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._db = sqlite3.connect(self.path, check_same_thread=False)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS kv(k TEXT PRIMARY KEY, v TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS usage(d TEXT PRIMARY KEY, used INTEGER NOT NULL, groups TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS events(event_id TEXT PRIMARY KEY, payload TEXT NOT NULL, ts TEXT NOT NULL);
        """)
        if self.path != ":memory:":
            try:
                os.chmod(self.path, 0o600)
            except OSError:
                pass

    # ---- kv ----
    def set(self, key: str, value) -> None:
        with self._lock:
            self._db.execute("INSERT INTO kv(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v",
                             (key, json.dumps(value, ensure_ascii=False)))
            self._db.commit()

    def get(self, key: str, default=None):
        with self._lock:
            row = self._db.execute("SELECT v FROM kv WHERE k=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def delete(self, key: str) -> None:
        with self._lock:
            self._db.execute("DELETE FROM kv WHERE k=?", (key,))
            self._db.commit()

    # ---- usage ----
    def save_usage(self, date: str, used: int, groups: dict) -> None:
        with self._lock:
            self._db.execute("INSERT INTO usage(d,used,groups) VALUES(?,?,?) ON CONFLICT(d) DO UPDATE SET "
                             "used=MAX(used, excluded.used), groups=excluded.groups", (date, int(used), json.dumps(groups)))
            self._db.commit()

    def load_usage(self, date: str) -> tuple[int, dict]:
        with self._lock:
            row = self._db.execute("SELECT used, groups FROM usage WHERE d=?", (date,)).fetchone()
        return (row[0], json.loads(row[1])) if row else (0, {})

    # ---- events ----
    def queue_event(self, event: dict) -> None:
        with self._lock:
            n = self._db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            if n >= MAX_QUEUE:  # bỏ bản ghi cũ nhất để không phình đĩa
                self._db.execute("DELETE FROM events WHERE event_id IN (SELECT event_id FROM events ORDER BY ts LIMIT 1000)")
            self._db.execute("INSERT OR IGNORE INTO events(event_id,payload,ts) VALUES(?,?,?)",
                             (event["event_id"], json.dumps(event, ensure_ascii=False), event["ts"]))
            self._db.commit()

    def pending_events(self, limit: int = 200) -> list[dict]:
        with self._lock:
            rows = self._db.execute("SELECT payload FROM events ORDER BY ts LIMIT ?", (limit,)).fetchall()
        return [json.loads(r[0]) for r in rows]

    def mark_sent(self, event_ids: list[str]) -> None:
        with self._lock:
            self._db.executemany("DELETE FROM events WHERE event_id=?", [(i,) for i in event_ids])
            self._db.commit()

    def pending_count(self) -> int:
        with self._lock:
            return self._db.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    def purge_old(self, days: int = 90) -> None:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        cut_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        with self._lock:
            self._db.execute("DELETE FROM events WHERE ts < ?", (cutoff,))
            self._db.execute("DELETE FROM usage WHERE d < ?", (cut_date,))
            self._db.commit()

    def purge_usage_data(self) -> None:
        """Lệnh purge_local_data: xóa sự kiện + mức dùng; giữ cấu hình ghép cặp và chính sách."""
        with self._lock:
            self._db.execute("DELETE FROM events")
            self._db.execute("DELETE FROM usage")
            self._db.commit()

    def purge_all(self) -> None:
        with self._lock:
            for t in ("events", "usage", "kv"):
                self._db.execute(f"DELETE FROM {t}")
            self._db.commit()
            self._db.execute("VACUUM")

    def close(self) -> None:
        with self._lock:
            self._db.close()
