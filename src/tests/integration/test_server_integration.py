"""Kiểm thử tích hợp: gọi API thật qua TestClient với SQLite thật."""
import base64
import time
import uuid
from datetime import datetime, timedelta, timezone

from conftest import STRONG, enroll_device, login, make_child, make_parent
from app.core.security import verify_payload


def bearer(tok):
    return {"Authorization": f"Bearer {tok}"}


def ev(type_, subject, dur=0, days_ago=0, pid="v1"):
    return {"event_id": uuid.uuid4().hex, "ts": (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat(),
            "type": type_, "subject": subject, "duration_sec": dur, "policy_id": pid}


def test_login_lockout_after_5_failures_and_generic_error(client):
    make_parent(client)
    client.cookies.clear()
    msgs = set()
    for _ in range(5):
        r = client.post("/api/v1/auth/login", json={"email": "a@example.com", "password": "Sai-mat-khau-1A"})
        assert r.status_code == 401
        msgs.add(r.json()["detail"])
    unknown = client.post("/api/v1/auth/login", json={"email": "khong@example.com", "password": "Sai-mat-khau-1A"})
    assert {unknown.json()["detail"]} == msgs  # không lộ email có tồn tại hay không
    r = client.post("/api/v1/auth/login", json={"email": "a@example.com", "password": STRONG})
    assert r.status_code == 423  # đã bị khóa 15 phút dù mật khẩu đúng


def test_session_cookie_flags_csrf_and_server_side_logout(client):
    make_parent(client)
    r = client.post("/api/v1/auth/login", json={"email": "a@example.com", "password": STRONG})
    sc = [c for c in r.headers.get_list("set-cookie") if c.startswith("ogk_session")][0].lower()
    assert "httponly" in sc and "samesite=lax" in sc and "max-age=43200" in sc  # 12 giờ
    csrf = r.json()["csrf_token"]
    assert client.post("/api/v1/children", json={"name": "A"}).status_code == 403  # thiếu CSRF
    assert client.post("/api/v1/children", json={"name": "A"}, headers={"X-CSRF-Token": "sai"}).status_code == 403
    assert client.post("/api/v1/children", json={"name": "A"}, headers={"X-CSRF-Token": csrf}).status_code == 201
    old_cookie = client.cookies.get("ogk_session")
    assert client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf}).status_code == 200
    client.cookies.set("ogk_session", old_cookie)  # kẻ tấn công dùng lại cookie cũ
    assert client.get("/api/v1/auth/me").status_code == 401  # phiên đã bị hủy phía server


def test_enrollment_code_single_use_expiry_and_consent(client):
    h = make_parent(client)
    cid = make_child(client, h)
    bad = client.post(f"/api/v1/children/{cid}/enroll-code", json={"parent_consent": False, "child_informed": True}, headers=h)
    assert bad.status_code == 422  # thiếu đồng ý
    info, code = enroll_device(client, h, cid)
    assert len(code) == 8 and info["device_id"]
    again = client.post("/api/v1/agent/enroll", json={"code": code})
    assert again.status_code == 400  # mã chỉ dùng một lần
    # mã hết hạn
    from app.core.database import SessionLocal, utcnow
    from app.models import EnrollmentCode
    c2 = client.post(f"/api/v1/children/{cid}/enroll-code", json={"parent_consent": True, "child_informed": True}, headers=h).json()["code"]
    with SessionLocal() as db:
        for e in db.query(EnrollmentCode).all():
            e.expires_at = utcnow() - timedelta(seconds=1)
        db.commit()
    assert client.post("/api/v1/agent/enroll", json={"code": c2}).status_code == 400


def test_heartbeat_requires_auth_and_returns_verifiable_signed_policy(client):
    h = make_parent(client)
    cid = make_child(client, h)
    info, _ = enroll_device(client, h, cid)
    assert client.post("/api/v1/agent/heartbeat", json={}).status_code == 401
    assert client.post("/api/v1/agent/heartbeat", json={}, headers=bearer("rac")).status_code == 401
    r = client.post("/api/v1/agent/heartbeat", json={"used_seconds_today": 600}, headers=bearer(info["access_token"]))
    assert r.status_code == 200
    body = r.json()
    key = base64.b64decode(info["signing_key"])
    assert verify_payload(body["policy"], body["signature"], key)
    body["policy"]["weekday_limit_minutes"] = 9999  # sửa gói chính sách
    assert not verify_payload(body["policy"], body["signature"], key)
    assert r.json()["policy"]["used_seconds_today"] == 600


def test_refresh_token_rotation_and_revocation(client):
    h = make_parent(client)
    cid = make_child(client, h)
    info, _ = enroll_device(client, h, cid)
    r = client.post("/api/v1/agent/token/refresh", json={"device_id": info["device_id"], "refresh_token": info["refresh_token"]})
    assert r.status_code == 200
    reuse = client.post("/api/v1/agent/token/refresh", json={"device_id": info["device_id"], "refresh_token": info["refresh_token"]})
    assert reuse.status_code == 401  # token cũ đã bị xoay vòng
    assert client.delete(f"/api/v1/devices/{info['device_id']}", headers=h).status_code == 200
    assert client.post("/api/v1/agent/heartbeat", json={}, headers=bearer(r.json()["access_token"])).status_code == 401


def test_event_ingestion_is_idempotent_and_minimised(client):
    h = make_parent(client)
    cid = make_child(client, h)
    info, _ = enroll_device(client, h, cid)
    tok = bearer(info["access_token"])
    batch = [ev("domain_query", "khanacademy.org"), ev("app_stop", "chrome.exe", 600),
             ev("blocked_domain", "roblox.com", pid="v1:category:games"),
             ev("domain_query", "https://khanacademy.org/video?id=1")]
    r1 = client.post("/api/v1/agent/events", json={"events": batch}, headers=tok).json()
    assert r1["accepted"] == 3 and len(r1["rejected"]) == 1  # URL đầy đủ bị từ chối
    r2 = client.post("/api/v1/agent/events", json={"events": batch}, headers=tok).json()  # gửi lại sau offline
    assert r2["accepted"] == 0 and r2["duplicates"] == 3
    rep = client.get(f"/api/v1/children/{cid}/report").json()
    assert rep["top_apps"][0] == {"name": "chrome.exe", "seconds": 600}
    assert rep["blocked_total"] == 1
    b = rep["blocks"][0]
    assert "Trò chơi" in b["why"] and b["rule_set_by"]  # NT4: có lý do + ai đặt quy tắc
    evs = client.get(f"/api/v1/children/{cid}/events").json()
    assert set(evs[0].keys()) == {"event_id", "ts", "device_id", "child_id", "type", "subject", "duration_sec", "policy_id"}


def test_idor_other_parent_cannot_access_child_or_device(client):
    ha = make_parent(client, "a@example.com")
    cid = make_child(client, ha)
    info, _ = enroll_device(client, ha, cid)
    client.cookies.clear()
    hb = make_parent(client, "b@example.com")
    for method, url, kw in [
        ("get", f"/api/v1/children/{cid}", {}), ("get", f"/api/v1/children/{cid}/policy", {}),
        ("put", f"/api/v1/children/{cid}/policy", {"json": {"weekday_limit_minutes": 1}}),
        ("get", f"/api/v1/children/{cid}/report", {}), ("get", f"/api/v1/children/{cid}/events.csv", {}),
        ("get", f"/api/v1/children/{cid}/rule-log", {}),
        ("post", f"/api/v1/children/{cid}/lock", {"json": {"lock": True}}),
        ("post", f"/api/v1/children/{cid}/enroll-code", {"json": {"parent_consent": True, "child_informed": True}}),
        ("delete", f"/api/v1/children/{cid}/data", {"json": {"confirm": "XOA DU LIEU"}}),
        ("delete", f"/api/v1/devices/{info['device_id']}", {}),
    ]:
        r = client.request(method.upper(), url, headers=hb, **kw)
        assert r.status_code == 404, (method, url, r.status_code)
    assert client.get("/api/v1/children").json() == []
    assert client.get("/api/v1/devices").json() == []


def test_child_view_is_read_only_and_scoped(client):
    h = make_parent(client)
    cid, cid2 = make_child(client, h, "An"), make_child(client, h, "Bình")
    assert client.post(f"/api/v1/children/{cid}/viewer", json={"email": "an@example.com", "password": "Be-An-Mat-Khau-1"}, headers=h).status_code == 201
    client.cookies.clear()
    hc = login(client, "an@example.com", "Be-An-Mat-Khau-1")
    assert client.get(f"/api/v1/children/{cid}/today").status_code == 200
    assert client.get(f"/api/v1/children/{cid}/rule-log").status_code == 200  # trẻ xem được nhật ký quy tắc (NT5)
    assert client.get(f"/api/v1/children/{cid2}/today").status_code == 404  # anh/chị em khác
    assert client.put(f"/api/v1/children/{cid}/policy", json={"weekday_limit_minutes": 999}, headers=hc).status_code == 403
    assert client.post(f"/api/v1/children/{cid}/lock", json={"lock": True}, headers=hc).status_code == 403
    assert len(client.get("/api/v1/children").json()) == 1


def test_policy_update_versions_audit_log_and_commands(client):
    h = make_parent(client)
    cid = make_child(client, h)
    info, _ = enroll_device(client, h, cid)
    tok = bearer(info["access_token"])
    p = client.put(f"/api/v1/children/{cid}/policy", json={"weekday_limit_minutes": 90, "expected_version": 1}, headers=h)
    assert p.status_code == 200 and p.json()["version"] == 2
    assert client.put(f"/api/v1/children/{cid}/policy", json={"weekday_limit_minutes": 30, "expected_version": 1}, headers=h).status_code == 409
    assert client.put(f"/api/v1/children/{cid}/policy", json={"schedule": [[True] * 48]}, headers=h).status_code == 422
    assert client.put(f"/api/v1/children/{cid}/policy", json={"domain_overrides": {"khong hop le": "block"}}, headers=h).status_code == 422
    log = client.get(f"/api/v1/children/{cid}/rule-log").json()
    top = log[0]
    assert top["action"] == "policy_updated" and top["ip"] and '"weekday_limit_minutes": 90' in top["new"] and '"weekday_limit_minutes": 120' in top["old"]
    hb = client.post("/api/v1/agent/heartbeat", json={}, headers=tok).json()
    assert hb["policy"]["policy_version"] == 2 and hb["policy"]["weekday_limit_minutes"] == 90
    assert any(c["command"] == "refresh_policy" for c in hb["commands"])


def test_more_time_request_approval_adds_bonus_and_unblock_adds_override(client):
    h = make_parent(client)
    cid = make_child(client, h)
    info, _ = enroll_device(client, h, cid)
    tok = bearer(info["access_token"])
    r = client.post("/api/v1/agent/requests", json={"kind": "more_time", "minutes": 20, "message": "xin thêm"}, headers=tok)
    assert r.status_code == 201
    u = client.post("/api/v1/agent/requests", json={"kind": "unblock", "subject": "https://x.com/abc"}, headers=tok)
    assert u.status_code == 422  # chỉ nhận tên miền
    u = client.post("/api/v1/agent/requests", json={"kind": "unblock", "subject": "roblox.com"}, headers=tok)
    pend = client.get("/api/v1/requests?status=pending").json()
    assert len(pend) == 2
    for rq in pend:
        assert client.post(f"/api/v1/requests/{rq['id']}/decide", json={"approve": True, "note": "ok"}, headers=h).status_code == 200
        assert client.post(f"/api/v1/requests/{rq['id']}/decide", json={"approve": True}, headers=h).status_code == 409
    pol = client.post("/api/v1/agent/heartbeat", json={}, headers=tok).json()["policy"]
    assert pol["bonus_seconds_today"] == 20 * 60
    assert pol["domain_overrides"] == {"roblox.com": "allow"}
    mine = client.get("/api/v1/agent/requests", headers=tok).json()
    assert {m["status"] for m in mine} == {"approved"}


def test_erase_all_child_data_and_purge_command(client):
    h = make_parent(client)
    cid = make_child(client, h)
    info, _ = enroll_device(client, h, cid)
    tok = bearer(info["access_token"])
    client.post("/api/v1/agent/events", json={"events": [ev("app_stop", "chrome.exe", 60)]}, headers=tok)
    client.post("/api/v1/agent/heartbeat", json={"used_seconds_today": 100}, headers=tok)
    assert client.request("DELETE", f"/api/v1/children/{cid}/data", json={"confirm": "sai"}, headers=h).status_code == 422
    r = client.request("DELETE", f"/api/v1/children/{cid}/data", json={"confirm": "XOA DU LIEU"}, headers=h)
    assert r.status_code == 200 and r.json()["deleted"]["events"] == 1
    assert client.get(f"/api/v1/children/{cid}/events").json() == []
    hb = client.post("/api/v1/agent/heartbeat", json={}, headers=tok).json()
    assert hb["policy"]["used_seconds_today"] == 0
    assert any(c["command"] == "purge_local_data" for c in hb["commands"])  # agent xóa cache cục bộ
    assert client.get(f"/api/v1/children/{cid}/rule-log").json()[0]["action"] == "data_erased"


def test_retention_purges_data_older_than_90_days(client):
    h = make_parent(client)
    cid = make_child(client, h)
    info, _ = enroll_device(client, h, cid)
    from app.core.database import SessionLocal
    from app.models import Event
    from app.retention import purge_expired
    old = ev("app_stop", "chrome.exe", 60, days_ago=89)
    client.post("/api/v1/agent/events", json={"events": [old, ev("app_stop", "a.exe", 5)]}, headers=bearer(info["access_token"]))
    with SessionLocal() as db:
        e = db.get(Event, old["event_id"])
        e.ts = datetime.now(timezone.utc) - timedelta(days=91)  # “qua đêm” – đã quá 90 ngày
        db.commit()
        res = purge_expired(db)
        assert res["events"] == 1
        assert db.query(Event).count() == 1


def test_websocket_urgent_lock_delivered_within_5_seconds(client):
    h = make_parent(client)
    cid = make_child(client, h)
    info, _ = enroll_device(client, h, cid)
    with client.websocket_connect("/api/v1/agent/ws") as ws:
        ws.send_json({"token": info["access_token"]})
        assert ws.receive_json()["type"] == "hello"
        t0 = time.monotonic()
        assert client.post(f"/api/v1/children/{cid}/lock", json={"lock": True}, headers=h).status_code == 200
        msg = ws.receive_json()
        got = [msg] if msg.get("command") == "lock_now" else []
        assert got and time.monotonic() - t0 < 5
        ws.send_json({"ack": got[0]["id"]})
    bad = client.websocket_connect("/api/v1/agent/ws")
    with bad as ws2:
        ws2.send_json({"token": "sai"})
        try:
            ws2.receive_json()
            assert False, "phải bị đóng"
        except Exception:
            pass


def test_totp_login_flow(client):
    h = make_parent(client)
    from app.core.security import totp_now
    s = client.post("/api/v1/auth/totp/setup", headers=h).json()["secret"]
    assert client.post("/api/v1/auth/totp/enable", json={"code": "000000"}, headers=h).status_code == 422
    assert client.post("/api/v1/auth/totp/enable", json={"code": totp_now(s)}, headers=h).status_code == 200
    client.cookies.clear()
    assert client.post("/api/v1/auth/login", json={"email": "a@example.com", "password": STRONG}).status_code == 401  # thiếu mã
    time.sleep(0.01)


def test_security_headers_and_admin_cannot_read_child_data(client):
    r = client.get("/api/v1/health")
    assert r.headers["x-content-type-options"] == "nosniff" and r.headers["x-frame-options"] == "DENY"
    h = make_parent(client)
    cid = make_child(client, h)
    from app.core.database import SessionLocal
    from app.core.security import hash_password
    from app.models import Account
    with SessionLocal() as db:
        db.add(Account(email="root@example.com", password_hash=hash_password(STRONG), role="admin"))
        db.commit()
    client.cookies.clear()
    ha = login(client, "root@example.com")
    assert client.get(f"/api/v1/children/{cid}/report").status_code == 404
    assert client.get("/api/v1/admin/audit/verify").json()["ok"] is True
    assert client.get("/api/v1/children").json() == []
