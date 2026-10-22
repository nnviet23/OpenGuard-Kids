import ctypes
import time
from ctypes import wintypes
from lock_monitor import LockMonitor

IDLE_THRESHOLD_SECONDS = 5 * 60


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("dwTime", wintypes.DWORD),
    ]


def get_idle_seconds() -> float:
    info = LASTINPUTINFO()
    info.cbSize = ctypes.sizeof(LASTINPUTINFO)

    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
        raise ctypes.WinError()

    current_tick = ctypes.windll.kernel32.GetTickCount64()
    last_input_tick = info.dwTime
    elapsed_ms = (int(current_tick) - last_input_tick) & 0xFFFFFFFF
    return elapsed_ms / 1000.0


class UsageTracker:
    def __init__(self, initial_seconds: float = 0.0) -> None:
        self.total_seconds = float(initial_seconds)
        self._last_check = time.monotonic()
        self.lock_monitor = LockMonitor()
        self.lock_monitor.start()

    def reset(self, new_seconds: float = 0.0) -> None:
        self.total_seconds = float(new_seconds)
        self._last_check = time.monotonic()

    def update(self) -> int:
        now = time.monotonic()
        elapsed = max(0.0, now - self._last_check)
        self._last_check = now

        if self.lock_monitor.is_locked:
            return int(self.total_seconds)

        if get_idle_seconds() <= IDLE_THRESHOLD_SECONDS:
            self.total_seconds += elapsed

        return int(self.total_seconds)