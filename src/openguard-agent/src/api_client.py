"""Client HTTPS của agent: token thiết bị 15 phút + refresh xoay vòng, ghim chứng chỉ (cert pinning)."""
from __future__ import annotations

import hashlib
import json
import socket
import ssl
import time
from typing import Any
from urllib.parse import urlparse

import secrets_store


class ApiError(Exception):
    def __init__(self, status: int, detail: str = "") -> None:
        super().__init__(f"HTTP {status}: {detail}")
        self.status, self.detail = status, detail


class NetworkError(Exception):
    pass


class DeviceRevoked(Exception):
    pass


class PinMismatch(Exception):
    pass


def server_cert_sha256(host: str, port: int, ca_file: str | None = None, timeout: float = 5.0) -> str:
    """SHA-256 của chứng chỉ lá mà server đang trình ra (để so với giá trị đã ghim)."""
    ctx = ssl.create_default_context(cafile=ca_file) if ca_file else ssl.create_default_context()
    ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE  # chỉ để LẤY chứng chỉ; việc tin cậy do pin quyết định
    with socket.create_connection((host, port), timeout=timeout) as raw, ctx.wrap_socket(raw, server_hostname=host) as s:
        return hashlib.sha256(s.getpeercert(binary_form=True)).hexdigest()


class ApiClient:
    def __init__(self, base_url: str, store, http=None, pin_sha256: str | None = None, ca_file: str | None = None,
                 pin_recheck_seconds: float = 600.0, mono=time.monotonic) -> None:
        self.base_url = base_url.rstrip("/")
        self.store, self.pin, self.pin_recheck, self._mono = store, (pin_sha256 or "").lower() or None, pin_recheck_seconds, mono
        self._pin_checked_at = -1e9
        if http is None:
            import httpx
            http = httpx.Client(timeout=10.0, verify=ca_file or True)
        self.http = http

    # ---- credentials ----
    @property
    def creds(self) -> dict | None:
        c = self.store.get("creds")
        return c if c else None

    def _save_creds(self, **upd) -> None:
        c = self.creds or {}
        c.update(upd)
        self.store.set("creds", c)

    @property
    def device_id(self) -> str | None:
        return (self.creds or {}).get("device_id")

    @property
    def signing_key(self) -> bytes | None:
        c = self.creds
        return secrets_store.unprotect(c["signing_key"]) if c and c.get("signing_key") else None

    # ---- pinning ----
    def _check_pin(self) -> None:
        if not self.pin or not self.base_url.startswith("https"):
            return
        if self._mono() - self._pin_checked_at < self.pin_recheck:
            return
        u = urlparse(self.base_url)
        try:
            actual = server_cert_sha256(u.hostname, u.port or 443)
        except OSError as e:
            raise NetworkError(str(e)) from e
        if actual.lower() != self.pin:
            raise PinMismatch("Chứng chỉ server không khớp giá trị đã ghim – từ chối kết nối")
        self._pin_checked_at = self._mono()

    # ---- low-level ----
    def _request(self, method: str, path: str, *, json_body: Any = None, auth: bool = True, _retry: bool = True) -> Any:
        self._check_pin()
        headers = {}
        if auth:
            headers["Authorization"] = f"Bearer {self._access_token()}"
        try:
            resp = self.http.request(method, self.base_url + path, json=json_body, headers=headers)
        except Exception as e:  # httpx.TransportError, v.v.
            if type(e).__module__.startswith("httpx"):
                raise NetworkError(str(e)) from e
            raise
        if resp.status_code == 401 and auth:
            if _retry:
                self._refresh()
                return self._request(method, path, json_body=json_body, auth=auth, _retry=False)
            raise DeviceRevoked("Thiết bị đã bị thu hồi hoặc không còn tồn tại")
        if resp.status_code >= 400:
            try:
                detail = resp.json().get("detail", "")
            except Exception:
                detail = resp.text[:200]
            raise ApiError(resp.status_code, str(detail))
        return resp.json()

    def _access_token(self) -> str:
        c = self.creds
        if not c:
            raise DeviceRevoked("Chưa ghép cặp")
        if not c.get("access_token") or c.get("access_exp", 0) - time.time() < 60:
            self._refresh()
            c = self.creds
        return c["access_token"]

    def _refresh(self) -> None:
        c = self.creds
        if not c:
            raise DeviceRevoked("Chưa ghép cặp")
        self._check_pin()
        try:
            resp = self.http.request("POST", self.base_url + "/agent/token/refresh",
                                     json={"device_id": c["device_id"],
                                           "refresh_token": secrets_store.unprotect(c["refresh_token"]).decode()})
        except Exception as e:
            if type(e).__module__.startswith("httpx"):
                raise NetworkError(str(e)) from e
            raise
        if resp.status_code in (401, 403):
            raise DeviceRevoked("Refresh token bị từ chối")
        if resp.status_code >= 400:
            raise ApiError(resp.status_code, resp.text[:200])
        d = resp.json()
        self._save_creds(access_token=d["access_token"], access_exp=time.time() + d["expires_in"],
                         refresh_token=secrets_store.protect(d["refresh_token"].encode()))

    # ---- API ----
    def enroll(self, code: str, device_name: str, fingerprint: str, agent_version: str) -> dict:
        d = self._request("POST", "/agent/enroll", auth=False, json_body={
            "code": code.strip().upper(), "device_name": device_name, "fingerprint": fingerprint,
            "agent_version": agent_version})
        self.store.set("creds", {
            "device_id": d["device_id"], "child_id": d["child_id"], "access_token": d["access_token"],
            "access_exp": time.time() + d["expires_in"],
            "refresh_token": secrets_store.protect(d["refresh_token"].encode()),
            "signing_key": secrets_store.protect(__import__("base64").b64decode(d["signing_key"]))})
        return d

    def heartbeat(self, payload: dict) -> dict:
        return self._request("POST", "/agent/heartbeat", json_body=payload)

    def post_events(self, events: list[dict]) -> dict:
        return self._request("POST", "/agent/events", json_body={"events": events})

    def ack(self, command_id: str) -> None:
        self._request("POST", f"/agent/commands/{command_id}/ack")

    def create_request(self, kind: str, subject: str = "", minutes: int = 0, message: str = "") -> dict:
        return self._request("POST", "/agent/requests", json_body={"kind": kind, "subject": subject, "minutes": minutes, "message": message})

    def my_requests(self) -> list:
        return self._request("GET", "/agent/requests")

    def transparency(self) -> dict:
        return self._request("GET", "/agent/transparency")

    def uninstall_notice(self, reason: str = "") -> dict:
        return self._request("POST", "/agent/uninstall-notice", json_body={"reason": reason})

    def access_token_for_ws(self) -> str:
        return self._access_token()
