"""Kiểm thử đơn vị logic agent (chạy được trên Linux – không cần Windows)."""
import hashlib
import hmac
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import dns.flags
import dns.message
import dns.rcode
import dns.rdatatype
import dns.rrset

import policy_checker as pc
from app_control import AppController, ProcInfo, is_user_app
from clock_guard import ClockGuard
from dns_config import DnsGuard, parse_netsh_dns
from dns_proxy import DnsFilter
from domain_rules import decide
from offline_store import OfflineStore
from policy_integrity import verify_bundle, verify_policy_signature
from quota_warnings import GraceTimer, WarningScheduler
from usage_tracker import UsageTracker

VN = ZoneInfo("Asia/Ho_Chi_Minh")
MON_9AM = datetime(2026, 10, 19, 9, 0, tzinfo=VN)  # thứ Hai


def pol(**kw):
    base = {"enabled": True, "weekday_limit_minutes": 60, "weekend_limit_minutes": 120,
            "schedule": [[True] * 48 for _ in range(7)], "policy_id": "v3", "policy_version": 3,
            "safety_whitelist": ["edu.vn", "tongdai111.vn"], "doh_providers": ["dns.google", "cloudflare-dns.com"],
            "domain_categories": {"roblox.com": "games", "khanacademy.org": "education", "tiktok.com": "social"},
            "category_actions": {"games": "limit", "education": "allow", "social": "block", "uncategorized": "log"},
            "domain_overrides": {}, "safesearch_map": {"www.google.com": "forcesafesearch.google.com"}, "app_rules": []}
    base.update(kw)
    return base


# ---------- policy_checker.evaluate ----------
def test_evaluate_remaining_is_min_of_quota_and_schedule():
    sched = [[True] * 48 for _ in range(7)]
    sched[0][19] = False  # thứ Hai 09:30 bị cấm
    d = pc.evaluate(pol(schedule=sched), 0, MON_9AM)
    assert d["status"] == "ALLOWED" and d["cause"] == "schedule" and d["remaining_seconds"] == 1800
    d = pc.evaluate(pol(), 3000, MON_9AM)
    assert d["cause"] == "quota" and d["remaining_seconds"] == 600


def test_evaluate_bonus_extends_quota_and_forced_lock_wins():
    assert pc.evaluate(pol(), 3600, MON_9AM)["status"] == "QUOTA_EXCEEDED"
    d = pc.evaluate(pol(bonus_seconds_today=900), 3600, MON_9AM)
    assert d["status"] == "ALLOWED" and d["remaining_seconds"] == 900
    assert pc.evaluate(pol(forced_lock=True), 0, MON_9AM)["status"] == "FORCED_LOCK"


def test_evaluate_paused_and_group_budget():
    assert pc.evaluate(pol(paused_until="2026-10-19T10:00:00+07:00"), 99999, MON_9AM)["status"] == "POLICY_DISABLED"
    d = pc.evaluate(pol(group_budgets={"games": 30}), 0, MON_9AM, {"games": 1800})
    assert d["blocked_groups"] == ["games"]


def test_schedule_end_detection_across_midnight_and_always_allowed():
    sched = [[True] * 48 for _ in range(7)]
    assert pc.seconds_until_schedule_block(sched, MON_9AM) is None
    sched[1][0] = False  # thứ Ba 00:00 cấm
    late = datetime(2026, 10, 19, 23, 50, tzinfo=VN)
    assert pc.seconds_until_schedule_block(sched, late) == 600


# ---------- cảnh báo 10/5/1 + ân hạn ----------
def test_warnings_fire_once_per_threshold():
    w = WarningScheduler()
    fired = []
    for rem in range(700, 0, -1):
        fired += w.due("2026-10-19", "quota", rem)
    assert fired == [600, 300, 60]
    assert w.due("2026-10-19", "quota", 30) == []  # không lặp
    assert w.due("2026-10-20", "quota", 30) == [60]  # ngày mới thì cảnh báo lại


def test_grace_60s_for_quota_but_immediate_for_schedule():
    g = GraceTimer(60)
    assert not g.should_lock(0, "quota")
    assert not g.should_lock(59, "quota")
    assert g.should_lock(60, "quota")
    assert g.should_lock(0, "schedule") and g.should_lock(0, "forced")


# ---------- chống chỉnh đồng hồ ----------
class FakeTime:
    def __init__(self):
        self.t, self.m = 1_800_000_000.0, 5000.0
    wall = lambda self: self.t  # noqa: E731
    mono = lambda self: self.m  # noqa: E731

    def advance(self, s, wall_extra=0.0):
        self.t += s + wall_extra
        self.m += s


def test_clock_guard_detects_rollback_and_ignores_it():
    ft = FakeTime()
    cg = ClockGuard(ft.wall, ft.mono)
    before = cg.trusted_now()
    ft.advance(60)
    assert cg.check() == 0
    ft.advance(10, wall_extra=-86400)  # lùi 1 ngày
    assert cg.check() < -80000 and cg.tamper_count == 1
    assert (cg.trusted_now() - before).total_seconds() == 70  # đồng hồ tin cậy không đổi theo
    ft.advance(10, wall_extra=+86400)  # tiến 1 ngày để reset hạn mức
    assert cg.check() > 80000
    assert (cg.trusted_now() - before).total_seconds() == 80


def test_clock_guard_sync_to_server_time():
    ft = FakeTime()
    cg = ClockGuard(ft.wall, ft.mono)
    cg.sync_server_time(datetime(2026, 1, 1, tzinfo=VN))
    ft.advance(30)
    assert cg.trusted_now().isoformat().startswith("2025-12-31T17:00:30")


# ---------- kho offline ----------
def test_offline_store_events_usage_and_purge():
    s = OfflineStore(":memory:")
    ev = {"event_id": "e1", "ts": "2026-10-19T00:00:00+00:00", "type": "app_start"}
    s.queue_event(ev)
    s.queue_event(ev)  # trùng khóa idempotency
    assert s.pending_count() == 1
    s.save_usage("2026-10-19", 100, {})
    s.save_usage("2026-10-19", 50, {})  # không bao giờ giảm
    assert s.load_usage("2026-10-19")[0] == 100
    s.mark_sent(["e1"])
    assert s.pending_count() == 0
    s.queue_event({"event_id": "e2", "ts": "2026-10-19T00:00:00+00:00", "type": "app_start"})
    s.purge_usage_data()
    assert s.pending_count() == 0 and s.load_usage("2026-10-19") == (0, {})


# ---------- toàn vẹn chính sách ----------
def test_bundle_signature_and_device_binding():
    p = {"device_id": "d1", "x": 1}
    sig = hmac.new(b"k", json.dumps(p, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(), hashlib.sha256).hexdigest()
    assert verify_policy_signature(p, sig, b"k") and not verify_policy_signature(p, sig, b"other")
    assert verify_bundle({"policy": p, "signature": sig}, b"k", "d1")
    assert not verify_bundle({"policy": p, "signature": sig}, b"k", "d2")  # gói của máy khác
    assert not verify_bundle({"policy": {**p, "x": 2}, "signature": sig}, b"k")
    assert not verify_bundle(None, b"k") and not verify_policy_signature(p, "", b"k")


# ---------- quy tắc tên miền + DNS proxy ----------
def test_decide_domain_priority():
    assert decide("a.b.roblox.com", pol())[:2] == ("limit", "games")
    assert decide("truong.edu.vn", pol(domain_overrides={"truong.edu.vn": "block"}))[2] == "safety_whitelist"
    assert decide("roblox.com", pol(domain_overrides={"roblox.com": "block"}))[2] == "override:roblox.com"


def make_query(name, rdtype="A"):
    return dns.message.make_query(name, rdtype).to_wire()


def fake_upstream(wire):
    q = dns.message.from_wire(wire)
    r = dns.message.make_response(q)
    name = q.question[0].name
    if q.question[0].rdtype == dns.rdatatype.A:
        r.answer.append(dns.rrset.from_text(name, 60, "IN", "A", "203.0.113.7"))
    return r.to_wire()


def run_filter(name, policy=None, rdtype="A"):
    events = []
    f = DnsFilter(lambda: policy or pol(), fake_upstream, lambda *a: events.append(a))
    return dns.message.from_wire(f.handle(make_query(name, rdtype))), events


def test_dns_blocks_category_and_subdomains():
    r, ev = run_filter("cdn.static.tiktok.com")
    assert r.rcode() == dns.rcode.NXDOMAIN
    assert ev[0] == ("blocked_domain", "cdn.static.tiktok.com", "v3:category:social")


def test_dns_allows_and_logs_only_domain():
    r, ev = run_filter("www.khanacademy.org")
    assert r.rcode() == dns.rcode.NOERROR and r.answer
    assert ev[0][0] == "domain_query" and "/" not in ev[0][1]


def test_dns_never_blocks_safety_whitelist_even_if_category_blocked():
    p = pol(category_actions={"education": "block", "uncategorized": "block"}, domain_overrides={"tongdai111.vn": "block"})
    r, ev = run_filter("tongdai111.vn", p)
    assert r.rcode() == dns.rcode.NOERROR
    r, _ = run_filter("hcmus.edu.vn", p)
    assert r.rcode() == dns.rcode.NOERROR


def test_dns_safesearch_returns_cname_to_forcesafesearch():
    r, _ = run_filter("www.google.com")
    cname = [x for x in r.answer if x.rdtype == dns.rdatatype.CNAME][0]
    assert str(cname[0].target).rstrip(".") == "forcesafesearch.google.com"
    assert any(x.rdtype == dns.rdatatype.A for x in r.answer)


def test_dns_doh_providers_and_canary_blocked():
    assert run_filter("dns.google")[0].rcode() == dns.rcode.NXDOMAIN
    assert run_filter("mozilla.cloudflare-dns.com")[0].rcode() == dns.rcode.NXDOMAIN
    assert run_filter("use-application-dns.net")[0].rcode() == dns.rcode.NXDOMAIN


def test_dns_group_budget_exceeded_blocks_limit_category_and_upstream_failure_is_servfail():
    f = DnsFilter(lambda: pol(), fake_upstream, group_exceeded=lambda g: g == "games")
    assert dns.message.from_wire(f.handle(make_query("roblox.com"))).rcode() == dns.rcode.NXDOMAIN

    def boom(_):
        raise TimeoutError()
    f2 = DnsFilter(lambda: pol(), boom)
    assert dns.message.from_wire(f2.handle(make_query("khanacademy.org"))).rcode() == dns.rcode.SERVFAIL
    assert f2.handle(b"rac") == b""


def test_dns_event_dedup_within_30s():
    t = [0.0]
    ev = []
    f = DnsFilter(lambda: pol(), fake_upstream, lambda *a: ev.append(a), mono=lambda: t[0])
    for _ in range(5):
        f.handle(make_query("khanacademy.org"))
    t[0] = 31
    f.handle(make_query("khanacademy.org"))
    assert len(ev) == 2


# ---------- phát hiện/khôi phục đổi DNS ----------
NETSH = '''Configuration for interface "Wi-Fi"
    Statically Configured DNS Servers:    127.0.0.1
Configuration for interface "Ethernet"
    DNS servers configured through DHCP:  8.8.8.8
                                          8.8.4.4
'''


def test_parse_netsh_and_repair_drift():
    assert parse_netsh_dns(NETSH) == {"Wi-Fi": ["127.0.0.1"], "Ethernet": ["8.8.8.8", "8.8.4.4"]}
    calls = []
    g = DnsGuard(runner=lambda cmd: (calls.append(cmd), NETSH)[1])
    assert g.check_and_repair() == ["Ethernet"]
    assert any("name=Ethernet" in c for cmd in calls for c in cmd)
    calls.clear()
    g.restore()
    assert any("dhcp" in cmd for cmd in calls)  # gỡ cài đặt trả DNS về tự động


# ---------- kiểm soát ứng dụng ----------
def test_app_block_by_name_and_by_hash_even_if_renamed():
    procs = [ProcInfo(1, "game.exe", "C:\\Games\\game.exe"), ProcInfo(2, "renamed.exe", "C:\\Temp\\renamed.exe"),
             ProcInfo(3, "winword.exe", "C:\\Office\\winword.exe")]
    killed = []
    hashes = {"C:\\Games\\game.exe": "a" * 64, "C:\\Temp\\renamed.exe": "b" * 64, "C:\\Office\\winword.exe": "c" * 64}
    ac = AppController(lambda: procs, hashes.get, lambda pid: killed.append(pid) or True, enforce=True)
    policy = pol(app_rules=[{"name": "Game.EXE", "action": "block"}, {"name": "x.exe", "sha256": "b" * 64, "action": "block"}])
    res = ac.scan(policy)
    assert sorted(killed) == [1, 2]
    assert {e[1] for e in res["events"] if e[0] == "blocked_app"} == {"game.exe", "renamed.exe"}
    assert any(e[0] == "app_start" and e[1] == "winword.exe" for e in res["events"])


def test_app_dry_run_does_not_kill_and_start_stop_duration():
    t = [100.0]
    procs = [ProcInfo(3, "winword.exe", "C:\\Office\\winword.exe")]
    killed = []
    ac = AppController(lambda: procs, lambda p: None, lambda pid: killed.append(pid), enforce=False, mono=lambda: t[0])
    ac.scan(pol(app_rules=[{"name": "winword.exe", "action": "block"}]))
    assert killed == []  # chế độ thử: chỉ ghi nhận
    ac2 = AppController(lambda: procs, lambda p: None, lambda pid: True, mono=lambda: t[0])
    ac2.scan(pol())
    t[0] = 400.0
    procs.clear()
    stop = [e for e in ac2.scan(pol())["events"] if e[0] == "app_stop"][0]
    assert stop[1] == "winword.exe" and stop[2] == 300


def test_app_group_budget_accumulates_only_when_user_active_and_blocks_when_exceeded():
    t = [0.0]
    procs = [ProcInfo(9, "mc.exe", "C:\\G\\mc.exe")]
    ac = AppController(lambda: procs, lambda p: None, lambda pid: True, enforce=True, mono=lambda: t[0])
    policy = pol(app_rules=[{"name": "mc.exe", "action": "limit", "group": "games"}])
    ac.scan(policy)
    t[0] = 60
    assert ac.scan(policy, user_active=True)["group_delta"] == {"games": 60.0}
    t[0] = 120
    assert ac.scan(policy, user_active=False)["group_delta"] == {}
    t[0] = 121
    res = ac.scan(policy, blocked_groups=["games"])
    assert res["blocked"] and "group_budget:games" in res["blocked"][0][1]


def test_system_processes_are_ignored():
    assert not is_user_app(ProcInfo(1, "svchost.exe", "C:\\Windows\\System32\\svchost.exe"))
    assert not is_user_app(ProcInfo(1, "foo.exe", "C:\\Windows\\foo.exe"))
    assert is_user_app(ProcInfo(1, "minecraft.exe", "C:\\Games\\minecraft.exe"))


# ---------- đếm thời gian thực ----------
def test_usage_excludes_idle_over_5_minutes_and_lock():
    m = [0.0]
    idle = [0.0]
    locked = [False]
    u = UsageTracker(lambda: idle[0], lambda: locked[0], lambda: m[0])
    m[0] = 100
    assert u.update() == 100
    idle[0] = 301  # nhàn rỗi > 5 phút -> không tính
    m[0] = 200
    assert u.update() == 100
    idle[0], locked[0] = 0, True  # khóa màn hình -> không tính
    m[0] = 300
    assert u.update() == 100
    locked[0] = False
    m[0] = 330
    assert u.update() == 130
    u.raise_to(50)  # không bao giờ giảm
    assert u.total_seconds == 130
