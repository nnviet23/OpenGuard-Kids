import os
import ssl
import json
import asyncio
import threading
from typing import Callable, Optional
import websockets

WS_SERVER_URL = os.getenv("OPENGUARD_WS_URL", "wss://127.0.0.1:8000/api/v1/agent/ws")
DEVICE_ID = os.getenv("OPENGUARD_DEVICE_ID", "child_device_001")


class WebSocketClient:
    def __init__(self, on_command: Callable[[str, dict], None]):
        self.on_command = on_command
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _run_event_loop(self):
        asyncio.run(self._listen_loop())

    def _get_ssl_context(self) -> Optional[ssl.SSLContext]:
        if not WS_SERVER_URL.startswith("wss://"):
            return None
        
        ctx = ssl.create_default_context()
        # Allow self-signed certs in dev/LAN environments if specified
        if os.getenv("OPENGUARD_INSECURE_TLS", "0") == "1":
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        return ctx

    async def _listen_loop(self):
        endpoint = f"{WS_SERVER_URL}/{DEVICE_ID}"
        ssl_ctx = self._get_ssl_context()

        while self._running:
            try:
                async with websockets.connect(
                    endpoint,
                    ssl=ssl_ctx,
                    ping_interval=20,
                    ping_timeout=10
                ) as ws:
                    while self._running:
                        raw_data = await ws.recv()
                        msg = json.loads(raw_data)
                        cmd_type = msg.get("action")
                        payload = msg.get("payload", {})

                        if cmd_type and self.on_command:
                            self.on_command(cmd_type, payload)

            except (websockets.ConnectionClosed, OSError):
                await asyncio.sleep(5)