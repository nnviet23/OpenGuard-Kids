"""Lõi agent: đếm giờ → đánh giá chính sách đã ký → cảnh báo → khóa; đồng bộ, offline, lệnh khẩn."""
from __future__ import annotations

import collections
import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import policy_checker
from api_client import ApiClient, ApiError, DeviceRevoked, NetworkError, PinMismatch
from app_control import AppController
from clock_guard import ClockGuard
from domain_rules import normalize
from enforcement import BLOCKING_STATUSES, apply_policy_status, lock_active_session, request_workstation_lock
from offline_store import OfflineStore
from policy_integrity import verify_bundle
from quota_warnings import GraceTimer, WarningScheduler

log = logging.getLogger("og.agent")
VN = ZoneInfo("Asia/Ho_Chi_Minh")
AGENT_VERSION = "1.0.0"
PURGE_DAYS = 90

# Chính sách an toàn dùng khi chưa từng đồng bộ hoặc gói đã hết hạn quá lâu (fail-safe, không khóa vô hạn
# và cũng không mở vô hạn): hạn mức mặc định + khung 06:00–21:00 + nhóm mặc định cho trẻ 6–11.
DEFAULT_POLICY = {
    "policy_id": "v0-default", "policy_version": 0, "enabled": True,
    "weekday_limit_minutes": 120, "weekend_limit_minutes": 180,
    "schedule": [[12 <= s < 42 for s in range(48)] for _ in range(7)],
    "group_budgets": {}, "category_actions": {"education": "allow", "entertainment": "limit", "social": "block",
                                               "games": "limit", "inappropriate": "block", "uncategorized": "log"},
    "domain_overrides": {}, "app_rules": [], "domain_categories": {}, "safety_whitelist": ["edu.vn", "gov.vn", "tongdai111.vn"],
    "doh_providers": ["dns.google", "cloudflare-dns.com", "dns.quad9.net"], "safesearch_map": {},
    "bonus_seconds_today": 0, "heartbeat_interval": 60, "offline_fail_mode": "closed", "offline_fail_days": 3,
}


@dataclass
class AgentConfig:
    data_dir: str
    server_url: str = "http://127.0.0.1:8000/api/v1"
    enforce_lock: bool = False
    enforce_apps: bool = False
    manage_dns: bool = False
    heartbeat_interval: int = 60
    app_scan_interval: int = 5
    dns_check_interval: int = 30
    pin_sha256: str | None = None
    ca_file: str | None = None
    dns_port: int = 53
    upstream_dns: str = "8.8.8.8"

    @classmethod
    def from_env(cls) -> "AgentConfig":
        def flag(n): return os.getenv(n, "0").strip().lower() in {"1", "true", "yes", "on"}
        default_dir = os.path.join(os.getenv("PROGRAMDATA", os.path.expanduser("~/.openguard")), "OpenGuardKids")
        return cls(data_dir=os.getenv("OPENGUARD_DATA_DIR", default_dir),
                   server_url=os.getenv("OPENGUARD_SERVER_URL", "http://127.0.0.1:8000/api/v1"),
                   enforce_lock=flag("OPENGUARD_ENFORCE_LOCK"), enforce_apps=flag("OPENGUARD_ENFORCE_APPS"),
                   manage_dns=flag("OPENGUARD_MANAGE_DNS"), pin_sha256=os.getenv("OPENGUARD_PIN_SHA256") or None,
                   ca_file=os.getenv("OPENGUARD_CA_FILE") or None, dns_port=int(os.getenv("OPENGUARD_DNS_PORT", "53")),
                   upstream_dns=os.getenv("OPENGUARD_UPSTREAM_DNS", "8.8.8.8"))


class Notifier:
    """Hàng đợi thông báo hiển thị cho trẻ qua khay hệ thống (NT1/NT4)."""

    def __init__(self) -> None:
        self._items: collections.deque = collections.deque(maxlen=50)
        self._seq = 0
        self._last: dict[str, float] = {}

    def push(self, title: str, body: str, kind: str = "info", dedupe_key: str | None = None, min_gap: float = 0) -> None:
        if dedupe_key and time.monotonic() - self._last.get(dedupe_key, -1e9) < min_gap:
            return
        if dedupe_key:
            self._last[dedupe_key] = time.monotonic()
        self._seq += 1
        self._items.append({"id": self._seq, "title": title, "body": body, "kind": kind,
                            "ts": datetime.now(timezone.utc).isoformat()})

    def since(self, last_id: int) -> list[dict]:
        return [i for i in self._items if i["id"] > last_id]


class AgentCore:
    def __init__(self, cfg: AgentConfig, store: OfflineStore, api: ApiClient, tracker, clock: ClockGuard | None = None,
                 apps: AppController | None = None, dns_guard=None, mono=time.monotonic,
                 lock_fn=None) -> None:
        self.cfg, self.store, self.api, self.tracker = cfg, store, api, tracker
        self.clock = clock or ClockGuard()
        self.apps = apps or AppController(enforce=cfg.enforce_apps)
        self.dns_guard, self._mono = dns_guard, mono
        self.lock_fn = lock_fn  # test hook; mặc định chọn theo nền tảng
        self.notifier = Notifier()
        self.warn, self.grace = WarningScheduler(), GraceTimer()
        self.group_seconds: dict[str, float] = {}
        self.forced_lock_local = False
        self.date = self._today()
        self.decision: dict = {"status": "INVALID_POLICY", "remaining_seconds": None, "cause": None, "blocked_groups": []}
        self.online, self.last_contact_wall = False, self.store.get("last_contact")
        self.unenrolled = False
        self._handled: collections.deque = collections.deque(self.store.get("handled_cmds", []), maxlen=200)
        self._locked_episode, self._last_lock_try, self._last_sync = False, -1e9, -1e9
        self._last_app_scan, self._last_dns_check, self._last_save = -1e9, -1e9, -1e9
        self.commands: collections.deque = collections.deque()
        self._lock = threading.RLock()
        self.sync_wakeup = threading.Event()
        self.last_enforcement = "DRY_RUN"
        self.rejected_bundles = 0
        # khôi phục mức dùng hôm nay sau khi khởi động lại
        used, groups = self.store.load_usage(self.date)
        self.tracker.raise_to(used)
        self.group_seconds = {k: float(v) for k, v in groups.items()}

    # ------------------------------------------------------------------ helpers
    def _today(self) -> str:
        return self.clock.trusted_now().astimezone(VN).strftime("%Y-%m-%d")

    @property
    def policy(self) -> dict:
        """Chính sách đang hiệu lực: gói đã xác minh còn hạn, ngược lại chính sách an toàn mặc định."""
        bundle = self.store.get("bundle")
        if bundle:
            p = bundle["policy"]
            try:
                if datetime.fromisoformat(p["valid_until"]) > self.clock.trusted_now():
                    return p
            except (KeyError, ValueError):
                pass
            return {**DEFAULT_POLICY, "safety_whitelist": p.get("safety_whitelist", DEFAULT_POLICY["safety_whitelist"]),
                    "domain_categories": p.get("domain_categories", {}), "child_name": p.get("child_name", ""),
                    "policy_id": "v0-expired"}
        return DEFAULT_POLICY

    def emit(self, type_: str, subject: str, duration: int = 0, policy_id: str | None = None) -> None:
        creds = self.api.creds or {}
        self.store.queue_event({
            "event_id": uuid.uuid4().hex, "ts": self.clock.trusted_now().isoformat(),
            "device_id": creds.get("device_id", ""), "child_id": creds.get("child_id", ""), "type": type_,
            "subject": subject[:255], "duration_sec": int(duration), "policy_id": policy_id or self.policy.get("policy_id", "")})

    def on_dns_event(self, kind: str, domain: str, policy_id: str) -> None:
        self.emit(kind, domain, 0, policy_id)
        if kind == "blocked_domain":
            self.notifier.push("Trang này bị chặn", self.explain(domain, policy_id), "block", dedupe_key=domain, min_gap=300)

    def explain(self, subject: str, policy_id: str) -> str:
        """NT4: nói rõ vì sao bị chặn và ai đặt quy tắc."""
        p = self.policy
        _, _, reason = policy_id.partition(":")
        kind, _, detail = reason.partition(":")
        why = {"category": f"nhóm “{detail}” đang bị chặn", "override": "phụ huynh đã chặn riêng trang này" if detail != "doh" else "kênh DNS mã hóa bị tắt để bộ lọc hoạt động",
               "app": "ứng dụng này nằm trong danh sách chặn", "group_budget": f"đã hết thời gian cho nhóm “{detail}”"}.get(kind, "quy tắc của phụ huynh")
        who = p.get("rule_set_by") or "Phụ huynh"
        return f"{subject}: {why}. Quy tắc do {who} đặt (phiên bản {p.get('policy_version', 0)}). Con nghĩ bị chặn nhầm? Bấm “Báo chặn nhầm” ở khay hệ thống."

    def group_exceeded(self, group: str) -> bool:
        budget = (self.policy.get("group_budgets") or {}).get(group)
        return budget is not None and self.group_seconds.get(group, 0) >= int(budget) * 60

    # ------------------------------------------------------------------ vòng 1 giây
    def tick(self) -> dict:
        with self._lock:
            now_m = self._mono()
            jump = self.clock.check()
            if jump:
                log.warning("Phát hiện chỉnh đồng hồ hệ thống (%.0f giây); dùng đồng hồ tin cậy", jump)
                self.notifier.push("Đồng hồ máy bị thay đổi", "OpenGuard vẫn dùng giờ chuẩn từ máy chủ.", "warn", "clock", 600)
            today = self._today()
            if today != self.date:
                self._rollover(today)
            used = self.tracker.update()
            policy = self.policy
            if self.forced_lock_local:
                policy = {**policy, "forced_lock": True}
            now_local = self.clock.trusted_now().astimezone(VN)
            self.decision = policy_checker.evaluate(policy, used, now_local, {k: int(v) for k, v in self.group_seconds.items()})
            status, cause, remaining = self.decision["status"], self.decision["cause"], self.decision["remaining_seconds"]

            for t in self.warn.due(self.date, cause, remaining):
                mins = max(1, round((remaining or t) / 60))
                self.notifier.push("Sắp hết giờ", f"Còn khoảng {mins} phút nữa máy sẽ khóa" + (" (hết khung giờ)" if cause == "schedule" else ""), "warn")
                self.emit("quota_warning", f"{t // 60}min", t)

            if status in BLOCKING_STATUSES:
                if cause == "quota" and self.grace.started_at is None:
                    self.notifier.push("Đã hết thời gian", "Máy sẽ khóa sau 60 giây. Hãy lưu bài của con nhé.", "warn")
                if self.grace.should_lock(now_m, cause):
                    self._lock_workstation(now_m, cause or "policy", status)
            else:
                self.grace.clear()
                self._locked_episode = False

            if now_m - self._last_app_scan >= self.cfg.app_scan_interval:
                self._last_app_scan = now_m
                self._scan_apps()
            if self.dns_guard and now_m - self._last_dns_check >= self.cfg.dns_check_interval:
                self._last_dns_check = now_m
                for iface in self.dns_guard.check_and_repair():
                    self.notifier.push("DNS đã được khôi phục", f"Cấu hình DNS của {iface} bị đổi và đã được đặt lại.", "warn")
            if now_m - self._last_save >= 10:
                self._last_save = now_m
                self.store.save_usage(self.date, used, {k: int(v) for k, v in self.group_seconds.items()})
            return self.decision

    def _rollover(self, new_date: str) -> None:
        self.store.save_usage(self.date, int(self.tracker.total_seconds), {k: int(v) for k, v in self.group_seconds.items()})
        for e in self.apps.close_all():
            self.emit(e[0], e[1], e[2], e[3] or None)
        self.date = new_date
        self.tracker.reset(0)
        self.group_seconds = {}
        self.warn.reset()
        self.grace.clear()
        self.forced_lock_local = False
        self._locked_episode = False
        self.sync_wakeup.set()  # lấy chính sách + mức dùng của ngày mới

    def _lock_workstation(self, now_m: float, cause: str, status: str) -> None:
        if self.tracker.is_locked:
            self._locked_episode = True
            return
        if not self._locked_episode:
            self.emit("locked", cause)
            self.notifier.push("Máy đã khóa", {"quota": "Hết thời gian dùng máy hôm nay", "schedule": "Ngoài khung giờ được phép",
                                              "forced": "Phụ huynh đã khóa máy"}.get(cause, "Theo quy tắc của phụ huynh"), "lock")
            self._locked_episode = True
        if now_m - self._last_lock_try >= 30:  # nhắc lại mỗi 30 giây nếu người dùng mở khóa mà vẫn bị chặn
            self._last_lock_try = now_m
            fn = self.lock_fn or (lambda: lock_active_session() or request_workstation_lock())
            self.last_enforcement = apply_policy_status(status, enabled=self.cfg.enforce_lock, already_locked=False, lock_function=fn)

    def _scan_apps(self) -> None:
        policy = self.policy
        res = self.apps.scan(policy, user_active=self.tracker.last_active, blocked_groups=self.decision.get("blocked_groups"))
        for typ, subject, dur, pid in res["events"]:
            self.emit(typ, subject, dur, pid)
        for name, why, _killed in res["blocked"]:
            self.notifier.push("Ứng dụng bị chặn", self.explain(name, why), "block", dedupe_key="app:" + name, min_gap=300)
        for g, sec in res["group_delta"].items():
            self.group_seconds[g] = self.group_seconds.get(g, 0.0) + sec

    # ------------------------------------------------------------------ đồng bộ
    def sync(self) -> bool:
        """Heartbeat + chính sách + đẩy sự kiện. Trả True nếu liên lạc được server."""
        with self._lock:
            payload = {"used_seconds_today": int(self.tracker.total_seconds),
                       "group_seconds_today": {k: int(v) for k, v in self.group_seconds.items()},
                       "agent_date": self.date, "agent_version": AGENT_VERSION,
                       "policy_version": self.policy.get("policy_version", 0), "locked": self.tracker.is_locked,
                       "dns_ok": True, "clock_tamper_count": self.clock.tamper_count,
                       "clock_skew_seconds": int(self.clock.skew_vs_trusted())}
        try:
            hb = self.api.heartbeat(payload)
        except (DeviceRevoked,):
            self._handle_revoked()
            return False
        except PinMismatch as e:
            log.error("%s", e)
            self.notifier.push("Kết nối không an toàn", "Chứng chỉ máy chủ không khớp; OpenGuard dùng chính sách đã lưu.", "warn", "pin", 3600)
            self.online = False
            return False
        except (NetworkError, ApiError):
            self.online = False
            return False
        with self._lock:
            self.online = True
            self.last_contact_wall = datetime.now(timezone.utc).isoformat()
            self.store.set("last_contact", self.last_contact_wall)
            self._accept_bundle({"policy": hb["policy"], "signature": hb["signature"]})
            for c in hb.get("commands", []):
                self.commands.append(c)
        self.flush_events()
        self.process_commands()
        self.store.purge_old(PURGE_DAYS)
        return True

    def _accept_bundle(self, bundle: dict) -> None:
        key = self.api.signing_key
        if not verify_bundle(bundle, key, self.api.device_id):
            self.rejected_bundles += 1
            log.error("Gói chính sách sai chữ ký – bỏ qua, tiếp tục dùng gói đã lưu")
            self.notifier.push("Chính sách không hợp lệ", "Gói chính sách sai chữ ký đã bị từ chối.", "warn", "sig", 600)
            return
        new, old = bundle["policy"], (self.store.get("bundle") or {}).get("policy")
        if old and new["policy_version"] < old["policy_version"]:
            log.error("Từ chối gói chính sách cũ hơn (chống phát lại)")
            return
        try:
            self.clock.sync_server_time(datetime.fromisoformat(new["server_time"]))
        except (KeyError, ValueError):
            pass
        self.store.set("bundle", bundle)
        if new.get("heartbeat_interval"):
            self.cfg.heartbeat_interval = int(new["heartbeat_interval"])
        if old and new.get("bonus_seconds_today", 0) > old.get("bonus_seconds_today", 0) and new.get("child_id") == old.get("child_id"):
            gained = (new["bonus_seconds_today"] - old["bonus_seconds_today"]) // 60
            self.emit("override_granted", f"{gained}min", gained * 60, new["policy_id"])
            self.notifier.push("Ba/mẹ đã cho thêm giờ", f"Con được thêm {gained} phút.", "ok")
        if old and new["policy_version"] > old["policy_version"]:
            self.notifier.push("Quy tắc đã thay đổi", f"Phiên bản {new['policy_version']}. Xem chi tiết ở “Nhật ký thay đổi quy tắc”.", "info")
        if new.get("forced_lock") is False:
            self.forced_lock_local = False
        if new.get("server_time", "")[:10] and self._today() == self.date:
            self.tracker.raise_to(new.get("used_seconds_today", 0))
            for k, v in (new.get("group_seconds_today") or {}).items():
                self.group_seconds[k] = max(self.group_seconds.get(k, 0.0), float(v))

    def flush_events(self, batch: int = 200) -> int:
        sent = 0
        while True:
            events = self.store.pending_events(batch)
            if not events:
                return sent
            try:
                res = self.api.post_events(events)
            except (NetworkError, ApiError, PinMismatch):
                return sent
            except DeviceRevoked:
                self._handle_revoked()
                return sent
            # đã nhận (mới/trùng) hoặc bị từ chối vĩnh viễn -> đều xóa khỏi hàng đợi để không kẹt
            self.store.mark_sent([e["event_id"] for e in events])
            sent += len(events)
            if len(events) < batch:
                return sent

    # ------------------------------------------------------------------ lệnh khẩn
    def enqueue_command(self, cmd: dict) -> None:
        self.commands.append(cmd)
        self.sync_wakeup.set()

    def process_commands(self) -> None:
        while self.commands:
            c = self.commands.popleft()
            if c["id"] in self._handled:
                continue
            self._handled.append(c["id"])
            self.store.set("handled_cmds", list(self._handled))
            self.handle_command(c)
            try:
                self.api.ack(c["id"])
            except Exception:
                pass

    def handle_command(self, c: dict) -> None:
        cmd = c.get("command")
        with self._lock:
            if cmd == "lock_now":
                self.forced_lock_local = True
                self.notifier.push("Phụ huynh đã khóa máy", "Máy sẽ khóa ngay.", "lock")
                self.tick()
            elif cmd == "unlock":
                self.forced_lock_local = False
                self.grace.clear()
                self._locked_episode = False
                self.sync_wakeup.set()
            elif cmd == "refresh_policy":
                self.sync_wakeup.set()
            elif cmd == "purge_local_data":
                self.store.purge_usage_data()
                self.notifier.push("Đã xóa dữ liệu", "Dữ liệu sử dụng lưu trên máy đã được xóa theo yêu cầu của ba/mẹ.", "ok")
            elif cmd == "unenroll":
                self._handle_revoked()

    def _handle_revoked(self) -> None:
        if self.unenrolled:
            return
        self.unenrolled = True
        log.warning("Thiết bị bị thu hồi/gỡ ghép cặp: khôi phục DNS và xóa dữ liệu cục bộ")
        if self.dns_guard:
            self.dns_guard.restore()
        self.store.purge_all()
        self.notifier.push("OpenGuard đã được gỡ khỏi máy này", "Máy không còn bị quản lý.", "info")

    # ------------------------------------------------------------------ giao diện
    def ui_status(self, since: int = 0) -> dict:
        p, d = self.policy, self.decision
        limit = (p["weekend_limit_minutes"] if datetime.now(VN).weekday() >= 5 else p["weekday_limit_minutes"]) * 60 + int(p.get("bonus_seconds_today", 0))
        return {"enrolled": bool(self.api.creds) and not self.unenrolled, "child_name": p.get("child_name", ""),
                "status": d["status"], "cause": d["cause"], "remaining_seconds": d["remaining_seconds"],
                "used_seconds": int(self.tracker.total_seconds), "limit_seconds": limit, "online": self.online,
                "policy_version": p.get("policy_version", 0), "policy_expired": p.get("policy_id") == "v0-expired",
                "grace_left": self.grace.seconds_left(self._mono()) if self.grace.started_at is not None else None,
                "enforce_lock": self.cfg.enforce_lock, "enforce_apps": self.cfg.enforce_apps,
                "dns_filter": self.cfg.manage_dns, "last_contact": self.last_contact_wall,
                "pending_events": self.store.pending_count(),
                "notifications": self.notifier.since(since),
                "should_lock": d["status"] in BLOCKING_STATUSES and self.grace.should_lock(self._mono(), d["cause"]) and self.cfg.enforce_lock}

    # ------------------------------------------------------------------ vòng chạy
    def run_forever(self, stop: threading.Event) -> None:
        self.notifier.push("OpenGuard Kids đang hoạt động", "Ba/mẹ đặt giới hạn thời gian dùng máy. Con có thể xem mọi thứ OpenGuard ghi lại ở biểu tượng khay hệ thống.", "info")
        self.sync()
        self._last_sync = self._mono()
        while not stop.is_set() and not self.unenrolled:
            started = self._mono()
            try:
                self.tick()
                if self.sync_wakeup.is_set() or started - self._last_sync >= self.cfg.heartbeat_interval:
                    self.sync_wakeup.clear()
                    self._last_sync = started
                    self.sync()
                self.process_commands()
            except Exception:  # vòng chính không bao giờ chết
                log.exception("lỗi trong vòng chính")
            stop.wait(max(0.0, 1.0 - (self._mono() - started)))
        self.store.save_usage(self.date, int(self.tracker.total_seconds), {k: int(v) for k, v in self.group_seconds.items()})
        self.flush_events()
