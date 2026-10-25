"""Tổng hợp báo cáo cho phụ huynh và màn hình minh bạch “Hôm nay em đã dùng gì”."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import classification as cls
from app.core.database import utcnow
from app.models import AuditLog, Child, ChildPolicy, ChildRequest, DailyUsage, Event
from app.policy_service import VN_TZ, get_or_create_policy, local_date_str

POLICY_ACTIONS = ("policy_updated", "override_granted", "lock_now", "unlock_now", "request_decided",
                  "child_created", "enroll_code_created", "device_enrolled", "device_revoked", "data_erased", "agent_uninstalled",
                  "clock_tamper_detected", "viewer_created")


def _vn_date(dt: datetime) -> str:
    return dt.astimezone(VN_TZ).strftime("%Y-%m-%d")


def rule_setter(db: Session, child_id: str, version: int) -> dict:
    rows = db.execute(select(AuditLog).where(AuditLog.child_id == child_id, AuditLog.action == "policy_updated")
                      .order_by(AuditLog.id.desc())).scalars().all()
    for r in rows:
        if r.new_value and f'"version": {version}' in r.new_value:
            return {"name": r.actor_name or "Phụ huynh", "at": r.ts.isoformat()}
    return {"name": "Phụ huynh", "at": None}


def explain_block(db: Session, child_id: str, event: Event) -> dict:
    """NT4: mọi lần chặn đều giải thích được vì sao và ai đặt quy tắc."""
    ver_s, _, reason = (event.policy_id or "").partition(":")
    version = int(ver_s[1:]) if ver_s.startswith("v") and ver_s[1:].isdigit() else 0
    who = rule_setter(db, child_id, version)
    kind, _, detail = reason.partition(":")
    if kind == "category":
        why = f"Nhóm “{cls.CATEGORY_LABELS_VI.get(detail, detail)}” đang bị chặn"
    elif kind == "override":
        why = f"Phụ huynh đã chặn riêng trang {detail}"
    elif kind == "app":
        why = f"Ứng dụng {event.subject} nằm trong danh sách chặn"
    elif kind == "quota":
        why = "Đã hết thời gian dùng máy của hôm nay"
    elif kind == "schedule":
        why = "Đang ngoài khung giờ được phép dùng máy"
    elif kind == "group_budget":
        why = f"Đã dùng hết thời gian dành cho nhóm “{cls.CATEGORY_LABELS_VI.get(detail, detail)}”"
    else:
        why = "Quy tắc của phụ huynh"
    return {"why": why, "rule_set_by": who["name"], "rule_set_at": who["at"], "policy_version": version}


def period_stats(db: Session, child_id: str, days: int = 7) -> dict:
    days = max(1, min(days, 90))
    today = datetime.now(VN_TZ).date()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days - 1, -1, -1)]
    since = utcnow() - timedelta(days=days + 1)
    daily = defaultdict(int)
    for r in db.execute(select(DailyUsage).where(DailyUsage.child_id == child_id,
                                                 DailyUsage.usage_date >= dates[0])).scalars():
        daily[r.usage_date] += r.used_seconds
    apps, domains, cats = Counter(), Counter(), Counter()
    blocks, counts = [], Counter()
    events = db.execute(select(Event).where(Event.child_id == child_id, Event.ts >= since)
                        .order_by(Event.ts.desc())).scalars().all()
    for e in events:
        if _vn_date(e.ts) < dates[0]:
            continue
        counts[e.type] += 1
        if e.type == "app_stop":
            apps[e.subject] += e.duration_sec
        elif e.type == "domain_query":
            domains[e.subject] += 1
            cats[cls.classify(e.subject)] += 1
        elif e.type in ("blocked_app", "blocked_domain"):
            blocks.append(e)
    top_blocked = Counter(b.subject for b in blocks)
    return {
        "days": [{"date": d, "used_seconds": daily.get(d, 0)} for d in dates],
        "top_apps": [{"name": k, "seconds": v} for k, v in apps.most_common(10)],
        "top_domains": [{"domain": k, "count": v} for k, v in domains.most_common(10)],
        "categories": [{"category": k, "label": cls.CATEGORY_LABELS_VI.get(k, k), "count": v} for k, v in cats.most_common()],
        "blocked_total": len(blocks), "blocked_top": [{"subject": k, "count": v} for k, v in top_blocked.most_common(10)],
        "blocks": [{"ts": b.ts.isoformat(), "type": b.type, "subject": b.subject, "policy_id": b.policy_id,
                    **explain_block(db, child_id, b)} for b in blocks[:50]],
        "event_counts": dict(counts),
        "requests": {s: n for s, n in Counter(
            r.status for r in db.execute(select(ChildRequest).where(ChildRequest.child_id == child_id,
                                                                    ChildRequest.created_at >= since)).scalars()).items()},
    }


def allowed_minutes_today(pol: ChildPolicy) -> int:
    wd = datetime.now(VN_TZ).weekday()
    return pol.weekend_limit_minutes if wd >= 5 else pol.weekday_limit_minutes


def today_summary(db: Session, child: Child) -> dict:
    pol = get_or_create_policy(db, child.id)
    today = local_date_str()
    rows = db.execute(select(DailyUsage).where(DailyUsage.child_id == child.id, DailyUsage.usage_date == today)).scalars().all()
    used = sum(r.used_seconds for r in rows)
    bonus = sum(r.bonus_seconds for r in rows)
    limit = allowed_minutes_today(pol) * 60 + bonus
    apps, sites, blocks = Counter(), Counter(), []
    for e in db.execute(select(Event).where(Event.child_id == child.id, Event.ts >= utcnow() - timedelta(days=2))
                        .order_by(Event.ts.desc())).scalars():
        if _vn_date(e.ts) != today:
            continue
        if e.type == "app_stop":
            apps[e.subject] += e.duration_sec
        elif e.type == "domain_query":
            sites[e.subject] += 1
        elif e.type in ("blocked_app", "blocked_domain") and len(blocks) < 20:
            blocks.append({"ts": e.ts.isoformat(), "subject": e.subject, **explain_block(db, child.id, e)})
    return {
        "child_name": child.name, "date": today, "used_minutes": used // 60, "limit_minutes": limit // 60,
        "remaining_minutes": max(0, (limit - used) // 60), "bonus_minutes": bonus // 60,
        "apps": [{"name": k, "minutes": max(1, v // 60)} for k, v in apps.most_common(10)],
        "sites": [{"domain": k, "count": v} for k, v in sites.most_common(10)],
        "blocks": blocks, "policy_version": pol.version,
        "rules": {"weekday_limit_minutes": pol.weekday_limit_minutes, "weekend_limit_minutes": pol.weekend_limit_minutes,
                  "safesearch": pol.safesearch,
                  "category_actions": {**cls.DEFAULT_ACTIONS_6_11, **pol.category_actions},
                  "safety_whitelist": cls.SAFETY_WHITELIST},
        "not_collected": ["nội dung tin nhắn/email/tài liệu", "địa chỉ trang đầy đủ", "tiêu đề cửa sổ",
                          "phím gõ", "ảnh chụp màn hình"],
    }


def rule_log(db: Session, child_id: str, limit: int = 100) -> list[dict]:
    out = []
    q = select(AuditLog).where(AuditLog.child_id == child_id, AuditLog.action.in_(POLICY_ACTIONS)).order_by(AuditLog.id.desc()).limit(limit)
    for r in db.execute(q).scalars():
        out.append({"id": r.id, "ts": r.ts.isoformat(), "action": r.action, "actor": r.actor_name or r.actor_type,
                    "ip": r.ip, "old": r.old_value, "new": r.new_value})
    return out
