"""Dựng gói chính sách đã ký cho agent; lệnh khẩn; tiện ích ngày giờ."""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import classification as cls
from app.core.config import settings
from app.core.database import utcnow
from app.core.security import device_signing_key, sign_payload
from app.models import Child, ChildPolicy, Command, DailyUsage, Device

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def local_date_str(dt: datetime | None = None) -> str:
    return (dt or utcnow()).astimezone(VN_TZ).strftime("%Y-%m-%d")


def get_or_create_policy(db: Session, child_id: str) -> ChildPolicy:
    pol = db.get(ChildPolicy, child_id)
    if not pol:
        pol = ChildPolicy(child_id=child_id, category_actions=dict(cls.DEFAULT_ACTIONS_6_11))
        db.add(pol)
        db.flush()
    return pol


def policy_to_dict(pol: ChildPolicy) -> dict:
    return {"version": pol.version, "enabled": pol.enabled,
            "weekday_limit_minutes": pol.weekday_limit_minutes,
            "weekend_limit_minutes": pol.weekend_limit_minutes, "schedule": pol.schedule,
            "group_budgets": pol.group_budgets, "category_actions": pol.category_actions,
            "domain_overrides": pol.domain_overrides, "app_rules": pol.app_rules,
            "safesearch": pol.safesearch, "updated_by": pol.updated_by,
            "updated_at": pol.updated_at.isoformat() if pol.updated_at else None}


def today_usage(db: Session, device_id: str) -> DailyUsage | None:
    return db.execute(select(DailyUsage).where(DailyUsage.device_id == device_id,
                                               DailyUsage.usage_date == local_date_str())).scalar_one_or_none()


def build_bundle(db: Session, device: Device) -> dict:
    """Gói chính sách + chữ ký HMAC (khóa riêng của thiết bị, dẫn xuất từ master key)."""
    pol = get_or_create_policy(db, device.child_id)
    child = db.get(Child, device.child_id)
    use = today_usage(db, device.id)
    now = utcnow()
    from app.report_service import rule_setter
    who = rule_setter(db, device.child_id, pol.version)
    body = {
        "device_id": device.id, "child_id": device.child_id, "child_name": child.name if child else "",
        "policy_id": f"v{pol.version}", "policy_version": pol.version,
        "rule_set_by": who["name"], "rule_set_at": who["at"],
        "issued_at": now.isoformat(), "valid_until": (now + timedelta(days=settings.POLICY_VALID_DAYS)).isoformat(),
        "server_time": now.isoformat(), "enabled": pol.enabled,
        "weekday_limit_minutes": pol.weekday_limit_minutes, "weekend_limit_minutes": pol.weekend_limit_minutes,
        "schedule": pol.schedule, "group_budgets": pol.group_budgets,
        "category_actions": {**cls.DEFAULT_ACTIONS_6_11, **pol.category_actions},
        "domain_overrides": pol.domain_overrides, "app_rules": pol.app_rules,
        "domain_categories": cls.load_table(), "safety_whitelist": cls.SAFETY_WHITELIST,
        "doh_providers": cls.DOH_PROVIDERS, "safesearch": pol.safesearch,
        "safesearch_map": cls.SAFESEARCH_CNAME if pol.safesearch else {},
        "paused_until": device.paused_until.isoformat() if device.paused_until else None,
        "forced_lock": device.forced_lock,
        "used_seconds_today": use.used_seconds if use else 0,
        "group_seconds_today": use.group_seconds if use else {},
        "bonus_seconds_today": use.bonus_seconds if use else 0,
        "heartbeat_interval": settings.HEARTBEAT_INTERVAL_SECONDS,
        "offline_fail_mode": settings.OFFLINE_FAIL_MODE, "offline_fail_days": settings.OFFLINE_FAIL_DAYS,
    }
    return {"policy": body, "signature": sign_payload(body, device_signing_key(device.id))}


def add_bonus(db: Session, device: Device, seconds: int) -> None:
    d = local_date_str()
    row = today_usage(db, device.id)
    if not row:
        row = DailyUsage(device_id=device.id, child_id=device.child_id, usage_date=d, used_seconds=0,
                         group_seconds={}, bonus_seconds=0)
        db.add(row)
    row.bonus_seconds += seconds


def push_command(db: Session, device: Device, command: str, payload: dict | None = None,
                 ttl_seconds: int = 600) -> Command:
    from app.realtime import hub
    cmd = Command(device_id=device.id, command=command, payload=payload or {},
                  expires_at=utcnow() + timedelta(seconds=ttl_seconds))
    db.add(cmd)
    db.flush()
    hub.notify(device.id, {"id": cmd.id, "command": cmd.command, "payload": cmd.payload})
    return cmd


def push_to_child_devices(db: Session, child_id: str, command: str, payload: dict | None = None) -> int:
    devs = db.execute(select(Device).where(Device.child_id == child_id, Device.status == "active")).scalars().all()
    for d in devs:
        push_command(db, d, command, payload)
    return len(devs)
