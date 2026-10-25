"""Xóa dữ liệu, xuất dữ liệu, quản trị."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.audit import verify_chain, write_audit
from app.core.database import get_db
from app.core.deps import require_admin, require_parent, scoped_child
from app.core.ratelimit import client_ip
from app.models import Account, Child, ChildPolicy, ChildRequest, Command, DailyUsage, Device, Event
from app.policy_service import push_command

router = APIRouter(tags=["privacy"])


def erase_child_data(db: Session, child: Child, actor: Account, ip: str | None, delete_child: bool = False) -> dict:
    """Xóa dữ liệu sử dụng trên server và ra lệnh agent xóa cache cục bộ."""
    cid = child.id
    n_events = db.execute(delete(Event).where(Event.child_id == cid)).rowcount
    n_usage = db.execute(delete(DailyUsage).where(DailyUsage.child_id == cid)).rowcount
    n_req = db.execute(delete(ChildRequest).where(ChildRequest.child_id == cid)).rowcount
    devs = db.execute(select(Device).where(Device.child_id == cid, Device.status == "active")).scalars().all()
    if not delete_child:
        for d in devs:
            push_command(db, d, "purge_local_data", ttl_seconds=7 * 86400)
    write_audit(db, "data_erased", actor_type="parent", actor_id=actor.id, actor_name=actor.display_name,
                child_id=cid, ip=ip, new={"events": n_events, "usage_days": n_usage, "requests": n_req,
                                          "child_deleted": delete_child})
    if delete_child:
        # thiết bị/chính sách/lệnh bị xóa theo ràng buộc ON DELETE CASCADE; agent nhận 401 ở lần
        # heartbeat kế tiếp và tự gỡ cấu hình + xóa cache cục bộ.
        db.execute(delete(Account).where(Account.linked_child_id == cid))
        db.execute(delete(Child).where(Child.id == cid))
    return {"events": n_events, "usage_days": n_usage, "requests": n_req}


class EraseIn(BaseModel):
    confirm: str


@router.delete("/children/{child_id}/data")
def erase(child_id: str, body: EraseIn, request: Request, parent: Account = Depends(require_parent),
          db: Session = Depends(get_db)):
    """“Xóa toàn bộ dữ liệu của con tôi”. Cần gõ đúng cụm xác nhận."""
    if body.confirm != "XOA DU LIEU":
        raise HTTPException(422, "Gõ chính xác “XOA DU LIEU” để xác nhận")
    child = scoped_child(db, parent, child_id, write=True)
    res = erase_child_data(db, child, parent, client_ip(request))
    db.commit()
    return {"ok": True, "deleted": res, "agent_cache": "đã gửi lệnh xóa tới các thiết bị"}


@router.get("/children/{child_id}/export")
def export(child_id: str, parent: Account = Depends(require_parent), db: Session = Depends(get_db)):
    """Quyền truy cập/sao chép dữ liệu cá nhân: xuất toàn bộ dữ liệu về trẻ dạng JSON."""
    child = scoped_child(db, parent, child_id, write=True)
    from app.policy_service import get_or_create_policy, policy_to_dict
    evs = db.execute(select(Event).where(Event.child_id == child.id).order_by(Event.ts)).scalars().all()
    return {"child": {"id": child.id, "name": child.name, "age_group": child.age_group},
            "policy": policy_to_dict(get_or_create_policy(db, child.id)),
            "events": [{"ts": e.ts.isoformat(), "type": e.type, "subject": e.subject,
                        "duration_sec": e.duration_sec, "policy_id": e.policy_id} for e in evs]}


@router.get("/admin/audit/verify")
def audit_verify(admin: Account = Depends(require_admin), db: Session = Depends(get_db)):
    ok, bad = verify_chain(db)
    return {"ok": ok, "first_bad_id": bad}


@router.get("/admin/accounts")
def admin_accounts(admin: Account = Depends(require_admin), db: Session = Depends(get_db)):
    """Quản trị chỉ thấy tài khoản, KHÔNG thấy dữ liệu sử dụng của trẻ."""
    return [{"id": a.id, "email": a.email, "role": a.role, "created_at": a.created_at.isoformat()}
            for a in db.execute(select(Account)).scalars()]
