"""WebSocket hub: đẩy lệnh khẩn tới agent trong vài giây (yêu cầu F4: ≤5 s)."""
from __future__ import annotations

import asyncio
import threading

from fastapi import WebSocket


class Hub:
    def __init__(self) -> None:
        self._conns: dict[str, WebSocket] = {}
        self._lock = threading.Lock()
        self.loop: asyncio.AbstractEventLoop | None = None

    def register(self, device_id: str, ws: WebSocket) -> None:
        with self._lock:
            self._conns[device_id] = ws
        self.loop = asyncio.get_running_loop()

    def unregister(self, device_id: str, ws: WebSocket) -> None:
        with self._lock:
            if self._conns.get(device_id) is ws:
                self._conns.pop(device_id, None)

    def connected(self, device_id: str) -> bool:
        return device_id in self._conns

    def notify(self, device_id: str, message: dict) -> bool:
        """Gọi được từ luồng đồng bộ. Trả True nếu đã xếp hàng gửi."""
        ws, loop = self._conns.get(device_id), self.loop
        if not ws or not loop or loop.is_closed():
            return False
        try:
            asyncio.run_coroutine_threadsafe(ws.send_json({"type": "command", **message}), loop)
            return True
        except Exception:
            return False


hub = Hub()
