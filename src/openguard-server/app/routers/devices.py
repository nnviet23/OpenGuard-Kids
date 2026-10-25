"""Ghép cặp thiết bị (enrollment) và quản lý thiết bị phía phụ huynh."""
from __future__ import annotations

import base64
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.audit import write_audit
from app.core.config import settings
from app.core.database import get_db, utcnow
from app.core.deps import require_parent, scoped_child, scoped_device
from app.core.ratelimit import client_ip, login_rate_limit
from app.core.security import (create_device_access_token, device_signing_key, new_enroll_code, new_token,
                               token_hash)
from app.models import Account, Device, EnrollmentCode
from app.policy_service import push_command

CONSENT_VERSION = "2026-01"
router = APIRouter(tags=["devices"])


class EnrollCodeIn(BaseModel):
    parent_consent: bool
    child_informed: bool


@router.post("/children/{child_id}/enroll-code", status_code=201)
def create_enroll_code(child_id: str, body: EnrollCodeIn, request: Request,
                       parent: Account = Depends(require_parent), db: Session = Depends(get_db)):
    """Mã 8 ký tự, hiệu lực 10 phút. Việc phụ huynh nhập mã = bằng chứng đồng ý lắp đặt."""
    child = scoped_child(db, parent, child_id, write=True)
    if not (body.parent_consent and body.child_informed):
        raise HTTPException(422, "Cần xác nhận phụ huynh đồng ý và đã thông báo cho trẻ")
    code = new_enroll_code()
    ip = client_ip(request)
    db.add(EnrollmentCode(code_hash=token_hash(code), parent_id=parent.id, child_id=child.id,
                          expires_at=utcnow() + timedelta(seconds=settings.ENROLL_CODE_TTL_SECONDS),
                          consent_version=CONSENT_VERSION, consent_ip=ip, child_informed=True))
    write_audit(db, "enroll_code_created", actor_type="parent", actor_id=parent.id, actor_name=parent.display_name,
                child_id=child.id, ip=ip, new={"consent_version": CONSENT_VERSION})
    db.commit()
    return {"code": code, "expires_in": settings.ENROLL_CODE_TTL_SECONDS}


class EnrollIn(BaseModel):
    code: str = Field(min_length=8, max_length=8)
    device_name: str = Field(default="Máy tính", max_length=100)
    fingerprint: str = Field(default="", max_length=128)
    agent_version: str = Field(default="", max_length=32)


@router.post("/agent/enroll", dependencies=[Depends(login_rate_limit)])
def enroll(body: EnrollIn, request: Request, db: Session = Depends(get_db)):
    code = body.code.strip().upper()
    ip = client_ip(request)
    # đánh dấu đã dùng bằng UPDATE có điều kiện => mỗi mã chỉ dùng được một lần (kể cả khi đua)
    res = db.execute(update(EnrollmentCode).where(
        EnrollmentCode.code_hash == token_hash(code), EnrollmentCode.used_at.is_(None),
        EnrollmentCode.expires_at > utcnow()).values(used_at=utcnow()))
    if res.rowcount != 1:
        db.rollback()
        raise HTTPException(400, "Mã không hợp lệ, đã hết hạn hoặc đã được sử dụng")
    ec = db.get(EnrollmentCode, token_hash(code))
    refresh = new_token()
    dev = Device(parent_id=ec.parent_id, child_id=ec.child_id, name=body.device_name.strip() or "Máy tính",
                 fingerprint_hash=token_hash(body.fingerprint) if body.fingerprint else None,
                 refresh_hash=token_hash(refresh), agent_version=body.agent_version, last_seen_at=utcnow())
    db.add(dev)
    db.flush()
    access, ttl = create_device_access_token(dev.id, dev.child_id)
    write_audit(db, "device_enrolled", actor_type="device", actor_id=dev.id, child_id=dev.child_id,
                device_id=dev.id, ip=ip, new={"name": dev.name, "consent_version": ec.consent_version})
    db.commit()
    return {"device_id": dev.id, "child_id": dev.child_id, "access_token": access, "expires_in": ttl,
            "refresh_token": refresh, "signing_key": base64.b64encode(device_signing_key(dev.id)).decode(),
            "heartbeat_interval": settings.HEARTBEAT_INTERVAL_SECONDS}


class RefreshIn(BaseModel):
    device_id: str = Field(max_length=32)
    refresh_token: str = Field(max_length=128)


@router.post("/agent/token/refresh", dependencies=[Depends(login_rate_limit)])
def refresh(body: RefreshIn, db: Session = Depends(get_db)):
    dev = db.get(Device, body.device_id)
    if not dev or dev.status != "active" or not dev.refresh_hash or dev.refresh_hash != token_hash(body.refresh_token):
        raise HTTPException(401, "Refresh token không hợp lệ")
    new_refresh = new_token()  # xoay vòng refresh token
    dev.refresh_hash = token_hash(new_refresh)
    access, ttl = create_device_access_token(dev.id, dev.child_id)
    db.commit()
    return {"access_token": access, "expires_in": ttl, "refresh_token": new_refresh}


@router.get("/devices")
def list_devices(parent: Account = Depends(require_parent), db: Session = Depends(get_db)):
    now = utcnow()
    out = []
    for d in db.execute(select(Device).where(Device.parent_id == parent.id).order_by(Device.enrolled_at)).scalars():
        online = bool(d.last_seen_at and (now - d.last_seen_at).total_seconds() < 3 * settings.HEARTBEAT_INTERVAL_SECONDS)
        out.append({"id": d.id, "child_id": d.child_id, "name": d.name, "status": d.status, "online": online,
                    "agent_version": d.agent_version, "enrolled_at": d.enrolled_at.isoformat(),
                    "last_seen_at": d.last_seen_at.isoformat() if d.last_seen_at else None,
                    "forced_lock": d.forced_lock})
    return out


@router.delete("/devices/{device_id}")
def revoke_device(device_id: str, request: Request, parent: Account = Depends(require_parent),
                  db: Session = Depends(get_db)):
    dev = scoped_device(db, parent, device_id)
    if dev.status != "revoked":
        push_command(db, dev, "unenroll")  # agent tự gỡ cấu hình + trả lại DNS (không có chống gỡ)
        dev.status, dev.refresh_hash = "revoked", None
        write_audit(db, "device_revoked", actor_type="parent", actor_id=parent.id, actor_name=parent.display_name,
                    child_id=dev.child_id, device_id=dev.id, ip=client_ip(request))
    db.commit()
    return {"ok": True}
