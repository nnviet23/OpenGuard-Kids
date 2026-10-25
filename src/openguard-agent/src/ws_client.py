"""Kênh WebSocket nhận lệnh khẩn (khóa ngay/làm mới chính sách) – độ trễ vài giây."""
from __future__ import annotations

import json
import logging
import threading
import time

log = logging.getLogger("og.ws")


def run_ws(core, stop: threading.Event, connect=None) -> None:
    """Vòng lặp kết nối lại với backoff. `connect` chỉ để thử nghiệm."""
    if connect is None:
        from websockets.sync.client import connect as ws_connect
        connect = ws_connect
    backoff = 1.0
    while not stop.is_set():
        try:
            url = core.cfg.server_url.replace("https://", "wss://").replace("http://", "ws://") + "/agent/ws"
            with connect(url, open_timeout=10, max_size=1 << 20) as ws:
                ws.send(json.dumps({"token": core.api.access_token_for_ws()}))
                backoff = 1.0
                while not stop.is_set():
                    try:
                        raw = ws.recv(timeout=20)
                    except TimeoutError:
                        ws.send(json.dumps({"ping": 1}))
                        continue
                    msg = json.loads(raw)
                    if msg.get("type") == "command":
                        core.enqueue_command({"id": msg["id"], "command": msg["command"], "payload": msg.get("payload", {})})
        except Exception as e:  # mất mạng, token hết hạn...
            log.info("WS ngắt (%s), thử lại sau %.0fs", type(e).__name__, backoff)
            stop.wait(backoff)
            backoff = min(backoff * 2, 60)
