"""Kênh cục bộ giữa dịch vụ (SYSTEM) và giao diện khay (phiên người dùng).

HTTP chỉ nghe 127.0.0.1, bắt buộc header X-OG-Token (token ngẫu nhiên ghi vào ipc.json), kiểm tra Host để
chống DNS-rebinding; giao diện chỉ ĐỌC trạng thái và GỬI yêu cầu của trẻ – không có API nào đổi chính sách.
"""
from __future__ import annotations

import hmac
import json
import os
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from api_client import ApiError, DeviceRevoked, NetworkError


class IpcServer:
    def __init__(self, core, data_dir: str, port: int = 0) -> None:
        self.core, self.token = core, secrets.token_urlsafe(24)
        outer = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):  # im lặng
                pass

            def _send(self, code: int, obj) -> None:
                body = json.dumps(obj, ensure_ascii=False).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)

            def _authorized(self) -> bool:
                host = (self.headers.get("Host") or "").split(":")[0]
                tok = self.headers.get("X-OG-Token", "")
                return host in ("127.0.0.1", "localhost") and hmac.compare_digest(tok, outer.token)

            def do_GET(self):
                if not self._authorized():
                    return self._send(403, {"detail": "forbidden"})
                u = urlparse(self.path)
                try:
                    if u.path == "/status":
                        return self._send(200, outer.core.ui_status(int(parse_qs(u.query).get("since", ["0"])[0])))
                    if u.path == "/transparency":
                        return self._send(200, outer.core.api.transparency())
                    if u.path == "/requests":
                        return self._send(200, outer.core.api.my_requests())
                except (NetworkError, ApiError, DeviceRevoked) as e:
                    return self._send(502, {"detail": f"Không kết nối được máy chủ: {e}"})
                self._send(404, {"detail": "not found"})

            def do_POST(self):
                if not self._authorized():
                    return self._send(403, {"detail": "forbidden"})
                n = min(int(self.headers.get("Content-Length", "0")), 4096)
                try:
                    data = json.loads(self.rfile.read(n) or b"{}")
                except ValueError:
                    return self._send(400, {"detail": "bad json"})
                if urlparse(self.path).path == "/request":
                    try:
                        r = outer.core.api.create_request(str(data.get("kind", "")), str(data.get("subject", ""))[:255],
                                                          int(data.get("minutes", 0) or 0), str(data.get("message", ""))[:500])
                        return self._send(201, r)
                    except ApiError as e:
                        return self._send(e.status, {"detail": e.detail})
                    except (NetworkError, DeviceRevoked) as e:
                        return self._send(502, {"detail": str(e)})
                self._send(404, {"detail": "not found"})

        self.httpd = ThreadingHTTPServer(("127.0.0.1", port), H)
        self.port = self.httpd.server_address[1]
        path = Path(data_dir) / "ipc.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"port": self.port, "token": self.token}))
        # Windows: thư mục dữ liệu cho phép nhóm Users ĐỌC ipc.json (installer đặt ACL) để UI của trẻ kết nối được
        try:
            os.chmod(path, 0o644 if os.name == "nt" else 0o600)
        except OSError:
            pass

    def start(self) -> threading.Thread:
        t = threading.Thread(target=self.httpd.serve_forever, daemon=True, name="og-ipc")
        t.start()
        return t

    def stop(self) -> None:
        self.httpd.shutdown()
