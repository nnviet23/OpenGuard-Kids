from __future__ import annotations

import re
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import classification as cls
from app.core.audit import write_audit
from app.core.database import get_db, utcnow
from app.core.deps import AuthContext, get_auth, require_parent, scoped_child
from app.core.ratelimit import client_ip
from app.core.security import hash_password, validate_password
from app.models import Account, Child, ChildPolicy, Device
from app.policy_service import (add_bonus, get_or_create_policy, policy_to_dict, push_command,
                                push_to_child_devices)

router = APIRouter(tags=["children"])
DOMAIN_RE = re.compile(r"^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


class ChildIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age_group: str = Field(default="6-11", pattern=r"^(6-11|12-15|16-17)$")


def child_out(c: Child, db: Session) -> dict:
    devs = db.execute(select(Device).where(Device.child_id == c.id)).scalars().all()
    return {"id": c.id, "name": c.name, "age_group": c.age_group,
            "device_count": sum(1 for d in devs if d.status == "active")}


@router.get("/children")
def list_children(ctx: AuthContext = Depends(get_auth), db: Session = Depends(get_db)):
    a = ctx.account
    q = select(Child)
    if a.role == "parent":
        q = q.where(Child.parent_id == a.id)
    elif a.role == "child_view":
        q = q.where(Child.id == a.linked_child_id, Child.parent_id == a.owner_id)
    else:
        return []
    return [child_out(c, db) for c in db.execute(q.order_by(Child.created_at)).scalars()]


@router.post("/children", status_code=201)
def create_child(body: ChildIn, request: Request, parent: Account = Depends(require_parent),
                 db: Session = Depends(get_db)):
    c = Child(parent_id=parent.id, name=body.name.strip(), age_group=body.age_group)
    db.add(c)
    db.flush()
    pol = get_or_create_policy(db, c.id)
    pol.updated_by = parent.id
    write_audit(db, "child_created", actor_type="parent", actor_id=parent.id, actor_name=parent.display_name,
                child_id=c.id, ip=client_ip(request), new={"name": c.name, "age_group": c.age_group})
    db.commit()
    return child_out(c, db)


@router.get("/children/{child_id}")
def get_child(child_id: str, ctx: AuthContext = Depends(get_auth), db: Session = Depends(get_db)):
    return child_out(scoped_child(db, ctx.account, child_id), db)


@router.delete("/children/{child_id}")
def delete_child(child_id: str, request: Request, parent: Account = Depends(require_parent),
                 db: Session = Depends(get_db)):
    from app.routers.privacy import erase_child_data
    c = scoped_child(db, parent, child_id, write=True)
    erase_child_data(db, c, parent, client_ip(request), delete_child=True)
    db.commit()
    return {"ok": True}


@router.get("/children/{child_id}/policy")
def get_policy(child_id: str, ctx: AuthContext = Depends(get_auth), db: Session = Depends(get_db)):
    scoped_child(db, ctx.account, child_id)
    pol = get_or_create_policy(db, child_id)
    db.commit()
    return {**policy_to_dict(pol), "safety_whitelist": cls.SAFETY_WHITELIST}


class PolicyIn(BaseModel):
    expected_version: int | None = None
    enabled: bool | None = None
    weekday_limit_minutes: int | None = Field(default=None, ge=0, le=1440)
    weekend_limit_minutes: int | None = Field(default=None, ge=0, le=1440)
    schedule: list[list[bool]] | None = None
    group_budgets: dict[str, int] | None = None
    category_actions: dict[str, str] | None = None
    domain_overrides: dict[str, str] | None = None
    app_rules: list[dict] | None = None
    safesearch: bool | None = None


def _validate(body: PolicyIn) -> None:
    if body.schedule is not None and (len(body.schedule) != 7 or any(len(d) != 48 for d in body.schedule)):
        raise HTTPException(422, "Lịch phải gồm 7 ngày × 48 khung 30 phút")
    if body.group_budgets is not None:
        for k, v in body.group_budgets.items():
            if k not in cls.CATEGORIES or not 0 <= v <= 1440:
                raise HTTPException(422, f"Ngân sách nhóm không hợp lệ: {k}")
    if body.category_actions is not None:
        for k, v in body.category_actions.items():
            if k not in cls.CATEGORIES or v not in cls.ACTIONS:
                raise HTTPException(422, f"Hành động nhóm không hợp lệ: {k}={v}")
    if body.domain_overrides is not None:
        for d, a in body.domain_overrides.items():
            if not DOMAIN_RE.match(d) or a not in {"allow", "block"}:
                raise HTTPException(422, f"Tên miền/hành động không hợp lệ: {d}")
    if body.app_rules is not None:
        for r in body.app_rules:
            name, sha, act = r.get("name", ""), r.get("sha256"), r.get("action")
            if (not name or len(name) > 100 or "/" in name or "\\" in name
                    or act not in {"allow", "block", "limit"} or (sha and not SHA_RE.match(sha))):
                raise HTTPException(422, "Quy tắc ứng dụng không hợp lệ (name, sha256 64 hex, action)")


@router.put("/children/{child_id}/policy")
def update_policy(child_id: str, body: PolicyIn, request: Request, parent: Account = Depends(require_parent),
                  db: Session = Depends(get_db)):
    child = scoped_child(db, parent, child_id, write=True)
    _validate(body)
    pol = get_or_create_policy(db, child.id)
    if body.expected_version is not None and body.expected_version != pol.version:
        raise HTTPException(409, "Chính sách đã được thay đổi ở nơi khác, hãy tải lại")
    old = policy_to_dict(pol)
    changes = {k: v for k, v in body.model_dump(exclude_unset=True, exclude={"expected_version"}).items()
               if v is not None}
    if "domain_overrides" in changes:
        changes["domain_overrides"] = {k.lower(): v for k, v in changes["domain_overrides"].items()}
    for k, v in changes.items():
        setattr(pol, k, v)
    if not changes:
        return policy_to_dict(pol)
    pol.version += 1
    pol.updated_by, pol.updated_at = parent.id, utcnow()
    new = policy_to_dict(pol)
    diff_old = {k: old[k] for k in changes}
    diff_new = {k: new[k] for k in changes}
    write_audit(db, "policy_updated", actor_type="parent", actor_id=parent.id, actor_name=parent.display_name,
                child_id=child.id, ip=client_ip(request), old={"version": old["version"], **diff_old},
                new={"version": new["version"], **diff_new})
    push_to_child_devices(db, child.id, "refresh_policy")
    db.commit()
    return new


class LockIn(BaseModel):
    lock: bool
    minutes: int | None = Field(default=None, ge=1, le=1440)


@router.post("/children/{child_id}/lock")
def lock_now(child_id: str, body: LockIn, request: Request, parent: Account = Depends(require_parent),
             db: Session = Depends(get_db)):
    """Khóa/mở khóa khẩn: gửi qua WebSocket, agent hành động trong ≤5 giây."""
    child = scoped_child(db, parent, child_id, write=True)
    devs = db.execute(select(Device).where(Device.child_id == child.id, Device.status == "active")).scalars().all()
    for d in devs:
        d.forced_lock = body.lock
        push_command(db, d, "lock_now" if body.lock else "unlock", {"minutes": body.minutes})
    write_audit(db, "lock_now" if body.lock else "unlock_now", actor_type="parent", actor_id=parent.id,
                actor_name=parent.display_name, child_id=child.id, ip=client_ip(request), new={"minutes": body.minutes})
    db.commit()
    return {"ok": True, "devices": len(devs)}


class GrantIn(BaseModel):
    minutes: int = Field(ge=1, le=240)


@router.post("/children/{child_id}/grant-time")
def grant_time(child_id: str, body: GrantIn, request: Request, parent: Account = Depends(require_parent),
               db: Session = Depends(get_db)):
    child = scoped_child(db, parent, child_id, write=True)
    devs = db.execute(select(Device).where(Device.child_id == child.id, Device.status == "active")).scalars().all()
    for d in devs:
        add_bonus(db, d, body.minutes * 60)
        push_command(db, d, "refresh_policy")
    write_audit(db, "override_granted", actor_type="parent", actor_id=parent.id, actor_name=parent.display_name,
                child_id=child.id, ip=client_ip(request), new={"minutes": body.minutes})
    db.commit()
    return {"ok": True}


class ViewerIn(BaseModel):
    email: EmailStr
    password: str = Field(max_length=256)
    display_name: str = Field(default="", max_length=100)


@router.post("/children/{child_id}/viewer", status_code=201)
def create_viewer(child_id: str, body: ViewerIn, request: Request, parent: Account = Depends(require_parent),
                  db: Session = Depends(get_db)):
    """Tạo tài khoản chỉ-xem cho trẻ (NT5: hai chiều minh bạch)."""
    child = scoped_child(db, parent, child_id, write=True)
    errs = validate_password(body.password)
    if errs:
        raise HTTPException(422, "; ".join(errs))
    if db.execute(select(Account).where(Account.email == body.email.lower())).scalar_one_or_none():
        raise HTTPException(409, "Email đã tồn tại")
    v = Account(email=body.email.lower(), display_name=body.display_name or child.name,
                password_hash=hash_password(body.password), role="child_view",
                owner_id=parent.id, linked_child_id=child.id)
    db.add(v)
    write_audit(db, "viewer_created", actor_type="parent", actor_id=parent.id, actor_name=parent.display_name,
                child_id=child.id, ip=client_ip(request))
    db.commit()
    return {"id": v.id, "email": v.email}
