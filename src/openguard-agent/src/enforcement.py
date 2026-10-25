"""Opt-in Windows policy enforcement for OpenGuard Kids.

Real workstation locking is disabled by default. Set OPENGUARD_ENFORCE_LOCK=1
only on a test Windows account after reviewing the schedule and quota.
"""
from __future__ import annotations

import os
import sys
from typing import Callable

BLOCKING_STATUSES = {"QUOTA_EXCEEDED", "OUTSIDE_ALLOWED_SCHEDULE", "FORCED_LOCK"}

def enforcement_enabled(value: str | None = None) -> bool:
    raw = os.getenv("OPENGUARD_ENFORCE_LOCK", "0") if value is None else value
    return raw.strip().lower() in {"1", "true", "yes", "on"}

def request_workstation_lock(lock_function: Callable[[], bool] | None = None) -> bool:
    """Request Windows lock; returns False on non-Windows or API failure."""
    if lock_function is not None:
        try:
            return bool(lock_function())
        except Exception:
            return False
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        return bool(ctypes.windll.user32.LockWorkStation())
    except Exception:
        return False

def apply_policy_status(
    status: str,
    *,
    enabled: bool,
    already_locked: bool,
    lock_function: Callable[[], bool] | None = None,
) -> str:
    """Apply only explicit blocking statuses; never unlock Windows automatically."""
    if not enabled:
        return "DRY_RUN"
    if status in BLOCKING_STATUSES:
        if already_locked:
            return "LOCKED_ALREADY"
        return "LOCK_REQUESTED" if request_workstation_lock(lock_function) else "LOCK_FAILED"
    if status in {"ALLOWED", "POLICY_DISABLED"}:
        return "NO_LOCK_REQUIRED"
    # Invalid/missing policy does not trigger a workstation lock in this build.
    return "POLICY_REVIEW_REQUIRED"


def lock_active_session() -> bool:
    """Dành cho tiến trình dịch vụ (SYSTEM, session 0): ngắt phiên console đang hoạt động → về màn hình đăng nhập.

    LockWorkStation() chỉ hiệu lực trong phiên người dùng, nên dịch vụ dùng WTSDisconnectSession.
    Tiến trình khay (UI) chạy trong phiên người dùng gọi request_workstation_lock() trực tiếp.
    """
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        sid = ctypes.windll.kernel32.WTSGetActiveConsoleSessionId()
        if sid == 0xFFFFFFFF:
            return False
        return bool(ctypes.windll.wtsapi32.WTSDisconnectSession(None, sid, False))
    except Exception:
        return False
