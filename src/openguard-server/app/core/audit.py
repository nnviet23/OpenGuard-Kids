"""Nhật ký kiểm toán có chuỗi băm (hash chain) – phát hiện sửa/xóa bản ghi cũ."""
from __future__ import annotations

import hashlib
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import utcnow


def _digest(prev: str, d: dict) -> str:
    return hashlib.sha256((prev + json.dumps(d, sort_keys=True, ensure_ascii=False, default=str)).encode()).hexdigest()


def _fields(e) -> dict:
    return {"ts": e.ts.isoformat(), "actor_type": e.actor_type, "actor_id": e.actor_id,
            "actor_name": e.actor_name, "action": e.action, "child_id": e.child_id,
            "device_id": e.device_id, "ip": e.ip, "old": e.old_value, "new": e.new_value}


def write_audit(db: Session, action: str, *, actor_type: str, actor_id: str | None = None,
                actor_name: str | None = None, child_id: str | None = None, device_id: str | None = None,
                ip: str | None = None, old=None, new=None):
    from app.models import AuditLog
    last = db.execute(select(AuditLog).order_by(AuditLog.id.desc()).limit(1)).scalar_one_or_none()
    e = AuditLog(ts=utcnow(), actor_type=actor_type, actor_id=actor_id, actor_name=actor_name,
                 action=action, child_id=child_id, device_id=device_id, ip=ip,
                 old_value=json.dumps(old, ensure_ascii=False, sort_keys=True) if old is not None else None,
                 new_value=json.dumps(new, ensure_ascii=False, sort_keys=True) if new is not None else None,
                 prev_hash=last.entry_hash if last else "0" * 64, entry_hash="")
    e.entry_hash = _digest(e.prev_hash, _fields(e))
    db.add(e)
    db.flush()
    return e


def verify_chain(db: Session) -> tuple[bool, int | None]:
    from app.models import AuditLog
    prev = "0" * 64
    for e in db.execute(select(AuditLog).order_by(AuditLog.id)).scalars():
        if e.prev_hash != prev or e.entry_hash != _digest(prev, _fields(e)):
            return False, e.id
        prev = e.entry_hash
    return True, None
