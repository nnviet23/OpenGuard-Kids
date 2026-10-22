import os
import time
import threading
from datetime import datetime, timezone
from typing import Callable, Optional

import httpx
from local_storage import LocalStorage

SERVER_URL = os.getenv("OPENGUARD_SERVER_URL", "http://127.0.0.1:8000/api/v1")
DEVICE_ID = os.getenv("OPENGUARD_DEVICE_ID", "child_device_001")
HEARTBEAT_INTERVAL = 60


class SyncWorker:
    def __init__(
        self,
        storage: LocalStorage,
        on_policy_updated: Optional[Callable[[dict], None]] = None,
        on_command_received: Optional[Callable[[str, dict], None]] = None,
    ):
        self.storage = storage
        self.on_policy_updated = on_policy_updated
        self.on_command_received = on_command_received
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _run_loop(self):
        while self._running:
            self._sync_heartbeat()
            self._sync_offline_logs()
            time.sleep(HEARTBEAT_INTERVAL)

    def enroll_device(server_url: str, pairing_pin: str) -> tuple[bool, str, dict]:
        import platform
        payload = {
            "pairing_pin": pairing_pin,
            "hostname": platform.node(),
            "os_version": f"{platform.system()} {platform.release()}",
        }
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(f"{server_url}/agent/enroll", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    # data = {"device_id": "...", "agent_token": "...", "policy": {...}}
                    return True, "Thành công", data
                return False, res.json().get("detail", "Mã PIN không hợp lệ"), {}
        except Exception as e:
            return False, f"Không thể kết nối đến máy chủ: {e}", {}

    def _sync_heartbeat(self):
        today_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        used_seconds = self.storage.get_daily_usage(today_key)
        local_version = self.storage.get_policy("policy_version", 0)

        payload = {
            "device_id": DEVICE_ID,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "used_screen_time_sec": used_seconds,
            "policy_version": local_version,
            "agent_status": "active",
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(f"{SERVER_URL}/agent/heartbeat", json=payload)
                if res.status_code != 200:
                    return

                data = res.json()
                server_version = data.get("latest_policy_version", local_version)

                # Fetch full policy if outdated
                if server_version > local_version:
                    self._fetch_full_policy(client, server_version)

                # Execute server commands
                for cmd in data.get("pending_commands", []):
                    if self.on_command_received:
                        self.on_command_received(cmd.get("action"), cmd.get("payload", {}))

        except (httpx.RequestError, httpx.HTTPStatusError):
            pass

    def _fetch_full_policy(self, client: httpx.Client, new_version: int):
        try:
            res = client.get(
                f"{SERVER_URL}/agent/policy",
                params={"device_id": DEVICE_ID},
                timeout=10.0,
            )
            if res.status_code == 200:
                policy_data = res.json()
                self.storage.set_policy("policy_version", new_version)
                self.storage.set_policy("blocked_domains", policy_data.get("blocked_domains", []))
                self.storage.set_policy("blocked_hashes", policy_data.get("blocked_hashes", []))
                self.storage.set_policy("daily_quota_sec", policy_data.get("daily_quota_sec", 7200))

                if self.on_policy_updated:
                    self.on_policy_updated(policy_data)
        except Exception:
            pass

    def _sync_offline_logs(self):
        logs = self.storage.pull_pending_logs(limit=50)
        if not logs:
            return

        payload = {"device_id": DEVICE_ID, "logs": logs}
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(f"{SERVER_URL}/agent/logs", json=payload)
                if res.status_code == 200:
                    sent_ids = [item["id"] for item in logs]
                    self.storage.delete_logs(sent_ids)
        except Exception:
            pass