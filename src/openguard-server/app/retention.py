"""Lưu trữ tối đa 90 ngày và tự xóa (F3)."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.audit import write_audit
from app.core.config import settings
from app.core.database import SessionLocal, utcnow
from app.models import ChildRequest, Command, DailyUsage, EnrollmentCode, Event, WebSession
from app.policy_service import VN_TZ

log = logging.getLogger("ogk.retention")


def purge_expired(db: Session, days: int | None = None) -> dict:
    days = days or settings.RETENTION_DAYS
    cutoff = utcnow() - timedelta(days=days)
    cutoff_date = cutoff.astimezone(VN_TZ).strftime("%Y-%m-%d")
    res = {
        "events": db.execute(delete(Event).where(Event.ts < cutoff)).rowcount,
        "daily_usage": db.execute(delete(DailyUsage).where(DailyUsage.usage_date < cutoff_date)).rowcount,
        "requests": db.execute(delete(ChildRequest).where(ChildRequest.created_at < cutoff,
                                                          ChildRequest.status != "pending")).rowcount,
        "commands": db.execute(delete(Command).where(Command.expires_at < utcnow() - timedelta(days=7))).rowcount,
        "sessions": db.execute(delete(WebSession).where(WebSession.expires_at < utcnow())).rowcount,
        "enroll_codes": db.execute(delete(EnrollmentCode).where(EnrollmentCode.expires_at < utcnow() - timedelta(days=1))).rowcount,
    }
    if res["events"] or res["daily_usage"]:
        write_audit(db, "retention_purge", actor_type="system", new=res)
    db.commit()
    return res


async def retention_loop() -> None:
    while True:
        try:
            with SessionLocal() as db:
                r = purge_expired(db)
                log.info("retention purge: %s", r)
        except Exception:  # không để job chết
            log.exception("retention failed")
        await asyncio.sleep(settings.RETENTION_SWEEP_SECONDS)
