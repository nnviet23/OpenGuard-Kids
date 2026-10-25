"""Lưu bí mật (refresh token, khóa ký) khi nghỉ: DPAPI (phạm vi máy) trên Windows, quyền 0600 nơi khác."""
from __future__ import annotations

import base64
import sys


def protect(data: bytes) -> str:
    if sys.platform == "win32":
        import win32crypt  # type: ignore
        blob = win32crypt.CryptProtectData(data, "OpenGuardKids", None, None, None, 0x4)  # LOCAL_MACHINE
        return "dpapi:" + base64.b64encode(blob).decode()
    return "b64:" + base64.b64encode(data).decode()


def unprotect(text: str) -> bytes:
    kind, _, body = text.partition(":")
    raw = base64.b64decode(body)
    if kind == "dpapi":
        import win32crypt  # type: ignore
        return win32crypt.CryptUnprotectData(raw, None, None, None, 0x4)[1]
    return raw
