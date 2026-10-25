"""API cho agent: heartbeat, đồng bộ chính sách, sự kiện, lệnh, yêu cầu của trẻ, WebSocket."""
from __future__ import annotations

import asyncio
import re
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.audit import write_audit
from app.core.config import settings
from app.core.database import SessionLocal, get_db, utcnow
from app.core.deps import get_device
from app.core.security import decode_device_access_token
from app.models import ChildRequest, Command, DailyUsage, Device, Event
from app.policy_service import build_bundle, local_date_str, today_usage
from app.realtime import hub
from app.report_service import rule_log, today_summary

router = APIRouter(prefix="/agent", tags=["agent"])

EVENT_TYPES = {"app_start", "app_stop", "domain_query", "blocked_app", "blocked_domain", "quota_warning",
               "locked", "unlock_request", "override_granted"}
HOST_RE = re.compile(r"^(?=.{1,253}$)([a-z0-9_]([a-z0-9_-]{0,61}[a-z0-9_])?\.)+[a-z0-9-]{2,63}$")
APP_RE = re.compile(r"^[^/\\:*?\"<>|]{1,100}$")
SAFE_TEXT_RE = re.compile(r"^[\w .:\-–()]{0,100}$", re.UNICODE)


class EventIn(BaseModel):
    event_id: str = Field(min_length=8, max_length=64)  # khóa idempotency do agent sinh
    ts: datetime
    type: str
    subject: str = Field(default="", max_length=255)
    duration_sec: int = Field(default=0, ge=0, le=86400)
    policy_id: str = Field(default="", max_length=64)


def _validate_event(e: EventIn) -> str | None:
    """Tối thiểu hóa dữ liệu: từ chối mọi thứ trông như URL đầy đủ/tiêu đề/nội dung."""
    if e.type not in EVENT_TYPES:
        return "type không hợp lệ"
    s = e.subject.strip().lower() if e.type in ("domain_query", "blocked_domain") else e.subject.strip()
    if e.type in ("domain_query", "blocked_domain"):
        if not HOST_RE.match(s):
            return "subject phải là tên miền (không URL/đường dẫn)"
    elif e.type in ("app_start", "app_stop", "blocked_app"):
        if not APP_RE.match(s):
            return "subject phải là tên ứng dụng (không đường dẫn)"
    elif not SAFE_TEXT_RE.match(s):
        return "subject không hợp lệ"
    now = utcnow()
    ts = e.ts if e.ts.tzinfo else e.ts.replace(tzinfo=timezone.utc)
    if ts > now + timedelta(minutes=5) or ts < now - timedelta(days=settings.RETENTION_DAYS):
        return "ts ngoài khoảng cho phép"
    e.subject = s
    return None


class EventsIn(BaseModel):
    events: list[EventIn] = Field(max_length=500)


@router.post("/events")
def ingest_events(body: EventsIn, dev: Device = Depends(get_device), db: Session = Depends(get_db)):
    accepted = dup = 0
    rejected: list[dict] = []
    for e in body.events:
        err = _validate_event(e)
        if err:
            rejected.append({"event_id": e.event_id, "reason": err})
            continue
        if db.get(Event, e.event_id):
            dup += 1  # gửi lại do offline/retry -> bỏ qua, vẫn báo thành công (idempotent)
            continue
        db.add(Event(event_id=e.event_id, ts=e.ts, device_id=dev.id, child_id=dev.child_id, type=e.type,
                     subject=e.subject, duration_sec=e.duration_sec, policy_id=e.policy_id))
        try:
            db.flush()
            accepted += 1
        except IntegrityError:
            db.rollback()
            dup += 1
    dev.last_seen_at = utcnow()
    db.commit()
    return {"accepted": accepted, "duplicates": dup, "rejected": rejected}


class HeartbeatIn(BaseModel):
    used_seconds_today: int = Field(default=0, ge=0, le=86400)
    group_seconds_today: dict[str, int] = {}
    agent_date: str | None = Field(default=None, max_length=10)
    agent_version: str = Field(default="", max_length=32)
    policy_version: int = 0
    locked: bool = False
    dns_ok: bool = True
    clock_tamper_count: int = Field(default=0, ge=0, le=100000)
    clock_skew_seconds: int = Field(default=0, ge=-10**7, le=10**7)


@router.post("/heartbeat")
def heartbeat(body: HeartbeatIn, dev: Device = Depends(get_device), db: Session = Depends(get_db)):
    now = utcnow()
    dev.last_seen_at, dev.agent_version = now, body.agent_version or dev.agent_version
    if not body.agent_date or body.agent_date == local_date_str():
        row = today_usage(db, dev.id)
        if not row:
            row = DailyUsage(device_id=dev.id, child_id=dev.child_id, usage_date=local_date_str(),
                             used_seconds=0, group_seconds={}, bonus_seconds=0)
            db.add(row)
        # chỉ tăng, không giảm: chống agent gửi số nhỏ hơn / gửi lại gói cũ
        row.used_seconds = max(row.used_seconds, body.used_seconds_today)
        merged = dict(row.group_seconds or {})
        for k, v in body.group_seconds_today.items():
            merged[k] = max(merged.get(k, 0), v)
        row.group_seconds = merged
    if body.clock_tamper_count > 0 and abs(body.clock_skew_seconds) > 120:
        write_audit(db, "clock_tamper_detected", actor_type="device", actor_id=dev.id, child_id=dev.child_id,
                    device_id=dev.id, new={"skew_seconds": body.clock_skew_seconds, "count": body.clock_tamper_count})
    cmds = db.execute(select(Command).where(Command.device_id == dev.id, Command.status == "pending",
                                            Command.expires_at > now).order_by(Command.issued_at).limit(20)).scalars().all()
    db.flush()  # autoflush tắt: cần ghi trước khi dựng gói để số liệu hôm nay không bị cũ
    out = build_bundle(db, dev)
    db.commit()
    return {**out, "commands": [{"id": c.id, "command": c.command, "payload": c.payload} for c in cmds],
            "server_time": now.isoformat()}


@router.get("/policy")
def get_policy(dev: Device = Depends(get_device), db: Session = Depends(get_db)):
    out = build_bundle(db, dev)
    db.commit()
    return out


@router.post("/commands/{command_id}/ack")
def ack_command(command_id: str, dev: Device = Depends(get_device), db: Session = Depends(get_db)):
    cmd = db.execute(select(Command).where(Command.id == command_id, Command.device_id == dev.id)).scalar_one_or_none()
    if not cmd:
        raise HTTPException(404, "Không tìm thấy")
    cmd.status, cmd.acked_at = "acked", utcnow()
    db.commit()
    return {"ok": True}


class AgentRequestIn(BaseModel):
    kind: str = Field(pattern=r"^(more_time|unblock)$")
    subject: str = Field(default="", max_length=255)
    minutes: int = Field(default=0, ge=0, le=240)
    message: str = Field(default="", max_length=500)


@router.post("/requests", status_code=201)
def create_request(body: AgentRequestIn, dev: Device = Depends(get_device), db: Session = Depends(get_db)):
    """Trẻ xin thêm giờ hoặc báo chặn nhầm ngay từ khay hệ thống (NT3)."""
    if body.kind == "unblock":
        s = body.subject.strip().lower()
        if not HOST_RE.match(s):
            raise HTTPException(422, "Chỉ nhập tên miền, ví dụ example.com")
        body.subject = s
    r = ChildRequest(child_id=dev.child_id, device_id=dev.id, kind=body.kind, subject=body.subject,
                     minutes=body.minutes if body.kind == "more_time" else 0, message=body.message)
    db.add(r)
    db.add(Event(event_id=f"req-{uuid.uuid4().hex}",
                 ts=utcnow(), device_id=dev.id, child_id=dev.child_id, type="unlock_request",
                 subject=(body.subject or "more_time")[:100], duration_sec=body.minutes * 60, policy_id=""))
    db.flush()
    db.commit()
    return {"id": r.id, "status": r.status}


@router.get("/requests")
def my_requests(dev: Device = Depends(get_device), db: Session = Depends(get_db)):
    rows = db.execute(select(ChildRequest).where(ChildRequest.child_id == dev.child_id)
                      .order_by(ChildRequest.created_at.desc()).limit(20)).scalars()
    return [{"id": r.id, "kind": r.kind, "subject": r.subject, "minutes": r.minutes, "status": r.status,
             "response_note": r.response_note, "created_at": r.created_at.isoformat()} for r in rows]


@router.get("/transparency")
def transparency(dev: Device = Depends(get_device), db: Session = Depends(get_db)):
    """Dữ liệu cho màn hình “Hôm nay em đã dùng gì” trên khay hệ thống."""
    from app.models import Child
    child = db.get(Child, dev.child_id)
    return {"today": today_summary(db, child), "rule_log": rule_log(db, dev.child_id, 30)}


class UninstallIn(BaseModel):
    reason: str = Field(default="", max_length=100)


@router.post("/uninstall-notice")
def uninstall_notice(body: UninstallIn, dev: Device = Depends(get_device), db: Session = Depends(get_db)):
    """Agent báo gỡ cài đặt hợp lệ (không có cơ chế chống gỡ)."""
    write_audit(db, "agent_uninstalled", actor_type="device", actor_id=dev.id, child_id=dev.child_id,
                device_id=dev.id, new={"reason": body.reason})
    dev.status, dev.refresh_hash = "revoked", None
    db.commit()
    return {"ok": True}


@router.websocket("/ws")
async def agent_ws(ws: WebSocket):
    """Kênh lệnh khẩn. Tin đầu tiên phải là {"token": <access token>} (không đặt token trên URL)."""
    await ws.accept()
    try:
        first = await asyncio.wait_for(ws.receive_json(), timeout=5)
    except Exception:
        await ws.close(code=4401)
        return
    data = decode_device_access_token(str(first.get("token", "")))
    if not data:
        await ws.close(code=4401)
        return
    device_id = data["sub"]
    with SessionLocal() as db:
        dev = db.get(Device, device_id)
        if not dev or dev.status != "active":
            await ws.close(code=4403)
            return
        pending = db.execute(select(Command).where(Command.device_id == device_id, Command.status == "pending",
                                                   Command.expires_at > utcnow())).scalars().all()
        backlog = [{"id": c.id, "command": c.command, "payload": c.payload} for c in pending]
    hub.register(device_id, ws)
    try:
        await ws.send_json({"type": "hello", "pending": len(backlog)})
        for m in backlog:
            await ws.send_json({"type": "command", **m})
        while True:
            msg = await ws.receive_json()
            if msg.get("ack"):
                with SessionLocal() as db:
                    c = db.execute(select(Command).where(Command.id == str(msg["ack"]), Command.device_id == device_id)).scalar_one_or_none()
                    if c:
                        c.status, c.acked_at = "acked", utcnow()
                        db.commit()
            elif msg.get("ping"):
                await ws.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        hub.unregister(device_id, ws)
