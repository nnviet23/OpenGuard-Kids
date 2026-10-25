"""Chống chỉnh đồng hồ: quyết định dựa trên đồng hồ tin cậy (neo theo giờ server + monotonic)."""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

TOLERANCE_SECONDS = 120


class ClockGuard:
    def __init__(self, wall=time.time, mono=time.monotonic) -> None:
        self._wall, self._mono = wall, mono
        self._anchor_wall = wall()   # thời điểm tin cậy (epoch)
        self._anchor_mono = mono()
        self._last_wall, self._last_mono = wall(), mono()
        self.server_anchored = False
        self.tamper_count = 0

    def trusted_now(self) -> datetime:
        return datetime.fromtimestamp(self._anchor_wall + (self._mono() - self._anchor_mono), tz=timezone.utc)

    def sync_server_time(self, server_dt: datetime) -> None:
        if server_dt.tzinfo is None:
            server_dt = server_dt.replace(tzinfo=timezone.utc)
        self._anchor_wall, self._anchor_mono = server_dt.timestamp(), self._mono()
        self.server_anchored = True

    def check(self) -> float:
        """Trả độ lệch (giây) giữa đồng hồ hệ thống và đồng hồ tin cậy nếu vượt ngưỡng, ngược lại 0.

        Khi lệch, agent KHÔNG nhảy theo đồng hồ hệ thống – tiếp tục dùng đồng hồ tin cậy cho đến khi
        đồng bộ lại được với server. Điều này chặn cả lùi giờ (kéo dài ngày) lẫn tiến giờ (reset hạn mức).
        """
        wall_delta = self._wall() - self._last_wall
        mono_delta = self._mono() - self._last_mono
        self._last_wall, self._last_mono = self._wall(), self._mono()
        jump = wall_delta - mono_delta
        if abs(jump) > TOLERANCE_SECONDS:
            self.tamper_count += 1
            return jump
        return 0.0

    def skew_vs_trusted(self) -> float:
        return self._wall() - self.trusted_now().timestamp()
