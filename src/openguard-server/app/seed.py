"""Dữ liệu mẫu cho demo (chỉ tên miền/ứng dụng công khai, trung lập). Chỉ chạy khi CSDL trống."""
from __future__ import annotations

import random
import uuid
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import write_audit
from app.core.config import settings
from app.core.database import utcnow
from app.core.security import hash_password
from app.models import Account, Child, ChildRequest, DailyUsage, Device, Event
from app.policy_service import VN_TZ, get_or_create_policy

VIEWER_EMAIL, VIEWER_PASSWORD = "beminh@example.com", "BeMinh@2026"


def seed_demo(db: Session) -> bool:
    if db.execute(select(Account).limit(1)).first():
        return False
    parent = Account(email=settings.DEMO_EMAIL, display_name="Phụ huynh Demo",
                     password_hash=hash_password(settings.DEMO_PASSWORD), role="parent")
    admin = Account(email="admin@example.com", display_name="Quản trị Demo",
                    password_hash=hash_password(settings.DEMO_PASSWORD), role="admin")
    db.add_all([parent, admin])
    db.flush()
    child = Child(parent_id=parent.id, name="Bé Minh", age_group="6-11")
    db.add(child)
    db.flush()
    pol = get_or_create_policy(db, child.id)
    pol.updated_by = parent.id
    db.add(Account(email=VIEWER_EMAIL, display_name="Bé Minh", password_hash=hash_password(VIEWER_PASSWORD),
                   role="child_view", owner_id=parent.id, linked_child_id=child.id))
    dev = Device(parent_id=parent.id, child_id=child.id, name="Máy học (dữ liệu mẫu)", status="active",
                 last_seen_at=utcnow() - timedelta(hours=1), agent_version="demo")
    db.add(dev)
    db.flush()
    write_audit(db, "child_created", actor_type="parent", actor_id=parent.id, actor_name=parent.display_name,
                child_id=child.id, new={"name": child.name, "seed": True})
    write_audit(db, "policy_updated", actor_type="parent", actor_id=parent.id, actor_name=parent.display_name,
                child_id=child.id, ip="127.0.0.1", old={"version": 0}, new={"version": 1, "seed": True})
    rnd = random.Random(42)
    apps = [("chrome.exe", 0.5), ("scratch.exe", 0.15), ("minecraft.exe", 0.2), ("winword.exe", 0.15)]
    sites = ["khanacademy.org", "vi.wikipedia.org", "youtube.com", "olm.vn", "scratch.mit.edu", "hocmai.vn"]
    now = utcnow()
    for back in range(14, -1, -1):
        day = now - timedelta(days=back)
        base = day.astimezone(VN_TZ).replace(hour=19, minute=0, second=0, microsecond=0)
        total = 0
        for name, share in apps:
            dur = int(rnd.randint(40, 110) * 60 * share * 2)
            total += dur
            ts = base + timedelta(minutes=rnd.randint(0, 90))
            db.add(Event(event_id=f"seed-{uuid.uuid4().hex}", ts=ts, device_id=dev.id, child_id=child.id,
                         type="app_stop", subject=name, duration_sec=dur, policy_id="v1"))
        for _ in range(rnd.randint(6, 14)):
            db.add(Event(event_id=f"seed-{uuid.uuid4().hex}", ts=base + timedelta(minutes=rnd.randint(0, 120)),
                         device_id=dev.id, child_id=child.id, type="domain_query",
                         subject=rnd.choice(sites), duration_sec=0, policy_id="v1"))
        if rnd.random() < 0.6:
            db.add(Event(event_id=f"seed-{uuid.uuid4().hex}", ts=base + timedelta(minutes=30), device_id=dev.id,
                         child_id=child.id, type="blocked_domain", subject=rnd.choice(["roblox.com", "tiktok.com", "discord.com"]),
                         duration_sec=0, policy_id="v1:category:" + rnd.choice(["games", "social"])))
        db.add(DailyUsage(device_id=dev.id, child_id=child.id, usage_date=day.astimezone(VN_TZ).strftime("%Y-%m-%d"),
                          used_seconds=total, group_seconds={}, bonus_seconds=0))
    db.add(ChildRequest(child_id=child.id, kind="more_time", minutes=15, message="Con muốn làm nốt bài Scratch ạ"))
    db.commit()
    return True
