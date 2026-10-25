from __future__ import annotations

import csv
import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import AuthContext, get_auth, scoped_child
from app.models import Event
from app.report_service import period_stats, rule_log, today_summary

router = APIRouter(tags=["reports"])


@router.get("/children/{child_id}/report")
def report(child_id: str, days: int = Query(7, ge=1, le=90), ctx: AuthContext = Depends(get_auth),
           db: Session = Depends(get_db)):
    scoped_child(db, ctx.account, child_id)
    return period_stats(db, child_id, days)


@router.get("/children/{child_id}/today")
def today(child_id: str, ctx: AuthContext = Depends(get_auth), db: Session = Depends(get_db)):
    """Màn hình “Hôm nay em đã dùng gì” – trẻ và phụ huynh thấy cùng một nội dung (NT5)."""
    child = scoped_child(db, ctx.account, child_id)
    return today_summary(db, child)


@router.get("/children/{child_id}/rule-log")
def rules(child_id: str, ctx: AuthContext = Depends(get_auth), db: Session = Depends(get_db)):
    scoped_child(db, ctx.account, child_id)
    return rule_log(db, child_id)


@router.get("/children/{child_id}/events")
def events(child_id: str, type: str | None = None, limit: int = Query(100, ge=1, le=1000),
           ctx: AuthContext = Depends(get_auth), db: Session = Depends(get_db)):
    scoped_child(db, ctx.account, child_id)
    q = select(Event).where(Event.child_id == child_id)
    if type:
        q = q.where(Event.type == type)
    return [{"event_id": e.event_id, "ts": e.ts.isoformat(), "device_id": e.device_id, "child_id": e.child_id,
             "type": e.type, "subject": e.subject, "duration_sec": e.duration_sec, "policy_id": e.policy_id}
            for e in db.execute(q.order_by(Event.ts.desc()).limit(limit)).scalars()]


@router.get("/children/{child_id}/events.csv")
def events_csv(child_id: str, ctx: AuthContext = Depends(get_auth), db: Session = Depends(get_db)):
    scoped_child(db, ctx.account, child_id)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["ts", "device_id", "child_id", "type", "subject", "duration_sec", "policy_id"])
    for e in db.execute(select(Event).where(Event.child_id == child_id).order_by(Event.ts)).scalars():
        w.writerow([e.ts.isoformat(), e.device_id, e.child_id, e.type, e.subject, e.duration_sec, e.policy_id])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": f'attachment; filename="events-{child_id[:8]}.csv"'})
