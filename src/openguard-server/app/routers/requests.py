from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import write_audit
from app.core.database import get_db, utcnow
from app.core.deps import AuthContext, get_auth, require_parent, scoped_child
from app.core.ratelimit import client_ip
from app.models import Account, Child, ChildPolicy, ChildRequest, Device
from app.policy_service import add_bonus, get_or_create_policy, push_command
from app.routers.agent import HOST_RE

router = APIRouter(tags=["requests"])


def req_out(r: ChildRequest) -> dict:
    return {"id": r.id, "child_id": r.child_id, "kind": r.kind, "subject": r.subject, "minutes": r.minutes,
            "message": r.message, "status": r.status, "response_note": r.response_note,
            "created_at": r.created_at.isoformat(), "decided_at": r.decided_at.isoformat() if r.decided_at else None}


@router.get("/requests")
def list_requests(child_id: str | None = None, status: str | None = None,
                  ctx: AuthContext = Depends(get_auth), db: Session = Depends(get_db)):
    a = ctx.account
    q = select(ChildRequest).join(Child, Child.id == ChildRequest.child_id)
    if a.role == "parent":
        q = q.where(Child.parent_id == a.id)
    elif a.role == "child_view":
        q = q.where(Child.id == a.linked_child_id, Child.parent_id == a.owner_id)
    else:
        raise HTTPException(403, "Không có quyền")
    if child_id:
        q = q.where(ChildRequest.child_id == child_id)
    if status:
        q = q.where(ChildRequest.status == status)
    return [req_out(r) for r in db.execute(q.order_by(ChildRequest.created_at.desc()).limit(200)).scalars()]


class NewRequest(BaseModel):
    child_id: str
    kind: str = Field(pattern=r"^(more_time|unblock)$")
    subject: str = Field(default="", max_length=255)
    minutes: int = Field(default=0, ge=0, le=240)
    message: str = Field(default="", max_length=500)


@router.post("/requests", status_code=201)
def create_request(body: NewRequest, ctx: AuthContext = Depends(get_auth), db: Session = Depends(get_db)):
    """Trẻ (tài khoản child_view) gửi yêu cầu từ trang web."""
    child = scoped_child(db, ctx.account, body.child_id)  # IDOR: chỉ trẻ được liên kết
    if body.kind == "unblock":
        s = body.subject.strip().lower()
        if not HOST_RE.match(s):
            raise HTTPException(422, "Chỉ nhập tên miền")
        body.subject = s
    r = ChildRequest(child_id=child.id, kind=body.kind, subject=body.subject, message=body.message,
                     minutes=body.minutes if body.kind == "more_time" else 0)
    db.add(r)
    db.commit()
    return req_out(r)


class Decision(BaseModel):
    approve: bool
    note: str = Field(default="", max_length=500)
    minutes: int | None = Field(default=None, ge=1, le=240)


@router.post("/requests/{request_id}/decide")
def decide(request_id: str, body: Decision, request: Request, parent: Account = Depends(require_parent),
           db: Session = Depends(get_db)):
    r = db.execute(select(ChildRequest).join(Child, Child.id == ChildRequest.child_id)
                   .where(ChildRequest.id == request_id, Child.parent_id == parent.id)).scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Không tìm thấy")
    if r.status != "pending":
        raise HTTPException(409, "Yêu cầu đã được xử lý")
    ip = client_ip(request)
    r.status, r.response_note, r.decided_at = ("approved" if body.approve else "denied"), body.note, utcnow()
    detail = {"request": r.id, "kind": r.kind, "subject": r.subject, "approved": body.approve}
    devs = db.execute(select(Device).where(Device.child_id == r.child_id, Device.status == "active")).scalars().all()
    if body.approve and r.kind == "more_time":
        minutes = body.minutes or r.minutes or 15
        detail["minutes"] = minutes
        for d in devs:
            add_bonus(db, d, minutes * 60)
            push_command(db, d, "refresh_policy")
    elif body.approve and r.kind == "unblock":
        pol = get_or_create_policy(db, r.child_id)
        old = dict(pol.domain_overrides or {})
        pol.domain_overrides = {**old, r.subject: "allow"}
        pol.version += 1
        pol.updated_by, pol.updated_at = parent.id, utcnow()
        write_audit(db, "policy_updated", actor_type="parent", actor_id=parent.id, actor_name=parent.display_name,
                    child_id=r.child_id, ip=ip, old={"version": pol.version - 1, "domain_overrides": old},
                    new={"version": pol.version, "domain_overrides": pol.domain_overrides})
        for d in devs:
            push_command(db, d, "refresh_policy")
    write_audit(db, "request_decided", actor_type="parent", actor_id=parent.id, actor_name=parent.display_name,
                child_id=r.child_id, ip=ip, new=detail)
    db.commit()
    return req_out(r)
