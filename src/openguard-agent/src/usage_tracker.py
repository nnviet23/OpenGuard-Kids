"""Đếm thời gian sử dụng THỰC: loại trừ lúc khóa màn hình và lúc nhàn rỗi > 5 phút."""
from __future__ import annotations

import ctypes
import sys
import time
from typing import Callable

IDLE_THRESHOLD_SECONDS = 5 * 60


def get_idle_seconds() -> float:
    """Số giây từ lần nhập phím/chuột cuối (Windows). Ở nền tảng khác trả 0 (coi là đang dùng)."""
    if sys.platform != "win32":
        return 0.0
    from ctypes import wintypes

    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]

    info = LASTINPUTINFO()
    info.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
        raise ctypes.WinError()
    current_tick = ctypes.windll.kernel32.GetTickCount64()
    return ((int(current_tick) - info.dwTime) & 0xFFFFFFFF) / 1000.0


class UsageTracker:
    def __init__(self, idle_fn: Callable[[], float] | None = None, locked_fn: Callable[[], bool] | None = None,
                 mono: Callable[[], float] = time.monotonic, idle_threshold: float = IDLE_THRESHOLD_SECONDS,
                 start_seconds: float = 0.0) -> None:
        self._idle_fn = idle_fn or get_idle_seconds
        self._mono = mono
        self.idle_threshold = idle_threshold
        self.total_seconds = float(start_seconds)
        self._last = mono()
        self._monitor = None
        if locked_fn is None and sys.platform == "win32":
            from lock_monitor import LockMonitor  # chỉ nạp trên Windows (cần pywin32)
            self._monitor = LockMonitor()
            self._monitor.start()
            locked_fn = lambda: self._monitor.is_locked  # noqa: E731
        self._locked_fn = locked_fn or (lambda: False)
        self.last_active = True

    def update(self) -> int:
        now = self._mono()
        elapsed = max(0.0, now - self._last)
        self._last = now
        locked = bool(self._locked_fn())
        idle = self._idle_fn()
        self.last_active = (not locked) and idle <= self.idle_threshold
        if self.last_active:
            self.total_seconds += elapsed
        return int(self.total_seconds)

    def reset(self, start_seconds: float = 0.0) -> None:
        self.total_seconds = float(start_seconds)
        self._last = self._mono()

    def raise_to(self, seconds: float) -> None:
        """Đồng bộ lên nếu server ghi nhận mức dùng cao hơn (ví dụ sau cài lại agent). Không bao giờ giảm."""
        self.total_seconds = max(self.total_seconds, float(seconds))

    @property
    def is_locked(self) -> bool:
        return bool(self._locked_fn())
