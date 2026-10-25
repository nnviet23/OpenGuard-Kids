"""Tích hợp agent ↔ server thật (TestClient): ghép cặp, chính sách ký, hết giờ → khóa, offline, lệnh khẩn."""
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from conftest import enroll_device, make_child, make_parent
from agent_core import AgentConfig, AgentCore
from api_client import ApiClient
from clock_guard import ClockGuard
from offline_store import OfflineStore
from usage_tracker import UsageTracker


class FakeTime:
    def __init__(self):
        import time
        self.t, self.m = time.time(), 5000.0
    wall = lambda self: self.t  # noqa: E731
    mono = lambda self: self.m  # noqa: E731

    def advance(self, s):
        self.t += s
        self.m += s


class FlakyHttp:
    """Bọc TestClient để mô phỏng mất mạng."""
    def __init__(self, inner):
        self.inner, self.down = inner, False

    def request(self, method, url, **kw):
        if self.down:
            raise httpx.ConnectError("offline")
        return self.inner.request(method, url, **kw)


@pytest.fixture()
def env(client, tmp_path):
    from app.main import app
    h = make_parent(client)
    cid = make_child(client, h)
    assert client.put(f"/api/v1/children/{cid}/policy", headers=h, json={
        "weekday_limit_minutes": 2, "weekend_limit_minutes": 2, "schedule": [[True] * 48 for _ in range(7)]}).status_code == 200
    info, code = enroll_device(client, h, cid)
    agent_http = FlakyHttp(TestClient(app))  # client riêng: không dính cookie phụ huynh
    ft = FakeTime()
    store = OfflineStore(tmp_path / "agent.db")
    api = ApiClient("http://testserver/api/v1", store, http=agent_http)
    # agent tự ghép cặp bằng mã mới
    code2 = client.post(f"/api/v1/children/{cid}/enroll-code", headers=h, json={"parent_consent": True, "child_informed": True}).json()["code"]
    api.enroll(code2, "Máy test", "fp", "test")
    idle, locked = [0.0], [False]
    tracker = UsageTracker(lambda: idle[0], lambda: locked[0], ft.mono)
    locks = []
    cfg = AgentConfig(data_dir=str(tmp_path), enforce_lock=True)
    core = AgentCore(cfg, store, api, tracker, clock=ClockGuard(ft.wall, ft.mono), mono=ft.mono,
                     lock_fn=lambda: locks.append(ft.m) or True,
                     apps=__import__("app_control").AppController(lambda: [], lambda p: None, lambda p: True, mono=ft.mono))
    return type("E", (), dict(client=client, h=h, cid=cid, core=core, ft=ft, store=store, http=agent_http, locks=locks, idle=idle, locked=locked))


def run_seconds(e, n):
    for _ in range(n):
        e.ft.advance(1)
        e.core.tick()


def test_enroll_sync_verifies_signature_and_applies_policy(env):
    assert env.core.sync() is True
    assert env.core.policy["weekday_limit_minutes"] == 2
    assert env.core.policy["child_name"] == "Bé An"
    assert env.core.online


def test_quota_exhaustion_warns_then_locks_after_60s_grace_and_reports_events(env):
    env.core.sync()
    run_seconds(env, 119)
    assert env.core.decision["status"] == "ALLOWED" and not env.locks
    assert any("Sắp hết giờ" in n["title"] for n in env.core.notifier.since(0))  # cảnh báo trước
    run_seconds(env, 2)  # hết hạn mức
    assert env.core.decision["status"] == "QUOTA_EXCEEDED" and not env.locks  # còn trong ân hạn 60 giây
    run_seconds(env, 60)
    assert env.locks, "phải gọi khóa máy sau ân hạn"
    env.core.sync()
    types = {e["type"] for e in env.client.get(f"/api/v1/children/{env.cid}/events", params={"limit": 50}).json()}
    assert {"quota_warning", "locked"} <= types
    # mức dùng lên server
    assert env.client.get(f"/api/v1/children/{env.cid}/today").json()["used_minutes"] >= 2


def test_offline_mode_keeps_enforcing_and_flushes_events_idempotently(env):
    env.core.sync()
    env.http.down = True
    run_seconds(env, 125)
    assert env.core.sync() is False and not env.core.online
    assert env.core.decision["status"] == "QUOTA_EXCEEDED"  # vẫn thực thi bằng chính sách đã lưu
    pending = env.store.pending_count()
    assert pending > 0
    env.http.down = False
    assert env.core.sync() is True
    assert env.store.pending_count() == 0
    n = len(env.client.get(f"/api/v1/children/{env.cid}/events", params={"limit": 500}).json())
    # gửi lại cùng lô (giả lập retry) không tạo bản ghi trùng
    for ev in [{"event_id": "dup-0000001", "ts": env.core.clock.trusted_now().isoformat(), "type": "app_start", "subject": "a.exe"}] * 2:
        env.store.queue_event(ev)
    env.core.flush_events()
    assert len(env.client.get(f"/api/v1/children/{env.cid}/events", params={"limit": 500}).json()) == n + 1


def test_tampered_policy_bundle_is_rejected_and_old_one_kept(env):
    env.core.sync()
    good = env.store.get("bundle")
    forged = json.loads(json.dumps(good))
    forged["policy"]["weekday_limit_minutes"] = 1440
    forged["policy"]["weekend_limit_minutes"] = 1440
    env.core._accept_bundle(forged)
    assert env.core.rejected_bundles == 1
    assert env.core.policy["weekday_limit_minutes"] == 2
    old = json.loads(json.dumps(good))  # gói cũ hợp lệ nhưng version thấp hơn -> chống phát lại
    env.client.put(f"/api/v1/children/{env.cid}/policy", headers=env.h, json={"weekday_limit_minutes": 5, "weekend_limit_minutes": 5})
    env.core.sync()
    assert env.core.policy["weekday_limit_minutes"] == 5
    env.core._accept_bundle(old)
    assert env.core.policy["weekday_limit_minutes"] == 5


def test_urgent_lock_command_and_parent_extra_time(env):
    env.core.sync()
    run_seconds(env, 125)
    # phụ huynh cho thêm 10 phút -> bị khóa/ân hạn được gỡ ở lần đồng bộ kế tiếp
    assert env.client.post(f"/api/v1/children/{env.cid}/grant-time", headers=env.h, json={"minutes": 10}).status_code == 200
    env.core.sync()
    run_seconds(env, 1)
    assert env.core.decision["status"] == "ALLOWED" and env.core.decision["remaining_seconds"] > 400
    server_types = {e["type"] for e in env.client.get(f"/api/v1/children/{env.cid}/events", params={"limit": 100}).json()}
    assert "override_granted" in server_types
    # khóa khẩn
    env.client.post(f"/api/v1/children/{env.cid}/lock", headers=env.h, json={"lock": True})
    env.core.sync()
    run_seconds(env, 1)
    assert env.core.decision["status"] == "FORCED_LOCK" and env.locks  # khóa ngay, không ân hạn
    env.client.post(f"/api/v1/children/{env.cid}/lock", headers=env.h, json={"lock": False})
    env.core.sync()
    run_seconds(env, 1)
    assert env.core.decision["status"] == "ALLOWED"


def test_purge_command_clears_local_cache_and_revocation_unenrolls(env):
    env.core.sync()
    run_seconds(env, 5)
    env.core.emit("app_start", "a.exe")
    assert env.store.pending_count() >= 1
    env.client.request("DELETE", f"/api/v1/children/{env.cid}/data", headers=env.h, json={"confirm": "XOA DU LIEU"})
    env.core.sync()
    assert env.store.pending_count() == 0 and env.core.rejected_bundles == 0
    devs = env.client.get("/api/v1/devices").json()
    dev_id = env.core.api.device_id
    env.client.delete(f"/api/v1/devices/{dev_id}", headers=env.h)
    assert env.core.sync() is False and env.core.unenrolled
    assert env.core.api.creds is None  # đã xóa sạch dữ liệu cục bộ


def test_clock_rollback_cannot_extend_the_day(env):
    env.core.sync()
    run_seconds(env, 100)
    used_before = int(env.core.tracker.total_seconds)
    env.ft.t -= 86400  # lùi đồng hồ hệ thống 1 ngày
    run_seconds(env, 5)
    assert env.core.clock.tamper_count == 1
    assert int(env.core.tracker.total_seconds) >= used_before  # hạn mức không bị reset
    assert env.core.date == env.core._today()
