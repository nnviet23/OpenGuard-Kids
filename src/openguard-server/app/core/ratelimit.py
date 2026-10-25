from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from app.core.config import settings


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str, limit: int, window: float) -> bool:
        now = time.monotonic()
        with self._lock:
            q = self._hits[key]
            while q and now - q[0] > window:
                q.popleft()
            if len(q) >= limit:
                return False
            q.append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


limiter = SlidingWindowLimiter()


def client_ip(request: Request) -> str:
    if settings.TRUST_PROXY_HEADERS:
        xff = request.headers.get("x-forwarded-for")
        if xff:
            return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _dep(name: str, limit_attr: str, window: float):
    def dep(request: Request):
        if not limiter.allow(f"{name}:{client_ip(request)}", getattr(settings, limit_attr), window):
            raise HTTPException(429, "Quá nhiều yêu cầu, vui lòng thử lại sau")
    return dep


login_rate_limit = _dep("login", "RATE_LOGIN_PER_IP", 300)
general_rate_limit = _dep("general", "RATE_GENERAL_PER_IP", 60)
