import os
import time
import ctypes
import threading
from datetime import datetime, timezone

from usage_tracker import UsageTracker
from process_watcher import ProcessWatcher
from dns_proxy import DnsProxyServer
from ipc_server import IpcPipeServer
from local_storage import LocalStorage
from sync_worker import SyncWorker
from ws_client import WebSocketClient


def lock_screen():
    ctypes.windll.user32.LockWorkStation()


class AgentServiceCore:
    def __init__(self):
        self.storage = LocalStorage()

        # Load cached policies
        quota = self.storage.get_policy("daily_quota_sec", 7200)
        blocked_domains = set(self.storage.get_policy("blocked_domains", ["roblox.com", "discord.com"]))
        blocked_hashes = set(self.storage.get_policy("blocked_hashes", []))
        blocked_names = set(self.storage.get_policy("blocked_names", ["robloxplayer.exe", "discord.exe"]))

        # Restore accumulated daily usage from SQLite
        self.current_date_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        initial_used_sec = self.storage.get_daily_usage(self.current_date_key)

        # Core engines
        self.daily_quota_seconds = quota
        self.dns_proxy = DnsProxyServer(blocked_domains=blocked_domains)
        self.proc_watcher = ProcessWatcher(blocked_hashes=blocked_hashes, blocked_names=blocked_names)
        self.tracker = UsageTracker(initial_seconds=initial_used_sec)

        # IPC Server
        self.ipc_server = IpcPipeServer(on_request_callback=self._handle_ui_request)

        # Network Sync
        self.sync_worker = SyncWorker(
            storage=self.storage,
            on_policy_updated=self._apply_policy_update,
            on_command_received=self._execute_remote_command,
        )
        self.ws_client = WebSocketClient(on_command=self._execute_remote_command)

    def _handle_ui_request(self, event_type: str, payload: dict):
        self.storage.push_log(event_type, payload)

    def _apply_policy_update(self, policy: dict):
        if "daily_quota_sec" in policy:
            self.daily_quota_seconds = policy["daily_quota_sec"]
        if "blocked_domains" in policy:
            self.dns_proxy.blocked_domains = {d.lower().strip(".") for d in policy["blocked_domains"]}
        if "blocked_hashes" in policy:
            self.proc_watcher.blocked_hashes = set(policy["blocked_hashes"])
        if "blocked_names" in policy:
            self.proc_watcher.blocked_names = {n.lower().strip() for n in policy["blocked_names"]}

    def _execute_remote_command(self, action: str, payload: dict):
        if action == "LOCK_NOW":
            lock_screen()
        elif action == "EXTEND_TIME":
            added_sec = int(payload.get("minutes", 15)) * 60
            self.daily_quota_seconds += added_sec

    def run(self):
        threading.Thread(target=self.dns_proxy.start, daemon=True).start()
        self.ipc_server.start()
        self.sync_worker.start()
        self.ws_client.start()

        last_proc_scan = time.monotonic()

        try:
            while True:
                # Handle midnight date transition
                today_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                if today_key != self.current_date_key:
                    self.current_date_key = today_key
                    self.tracker.reset(0.0)

                used_sec = self.tracker.update()
                self.storage.update_daily_usage(today_key, used_sec)
                remaining_sec = max(0, self.daily_quota_seconds - used_sec)

                # Broadcast live status to TrayUI
                self.ipc_server.broadcast_status(
                    used_sec=used_sec,
                    remaining_sec=remaining_sec,
                    quota_sec=self.daily_quota_seconds,
                )

                # Scan processes every 2 seconds
                now = time.monotonic()
                if now - last_proc_scan >= 2.0:
                    killed = self.proc_watcher.scan_and_enforce()
                    for item in killed:
                        self.storage.push_log("PROCESS_KILLED", item)
                    last_proc_scan = now

                # Enforce lock when quota expires
                if remaining_sec <= 0:
                    lock_screen()
                    time.sleep(5)

                time.sleep(1)

        except KeyboardInterrupt:
            self.dns_proxy.stop()
            self.sync_worker.stop()
            self.ws_client.stop()


if __name__ == "__main__":
    service = AgentServiceCore()
    service.run()