"""Mô hình dữ liệu. Quan hệ: 1 phụ huynh : n trẻ : m thiết bị."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, UTCDateTime, utcnow

DEFAULT_START_SLOT, DEFAULT_END_SLOT = 12, 42  # 06:00 – 21:00


def uid() -> str:
    return uuid.uuid4().hex


def default_schedule() -> list[list[bool]]:
    return [[DEFAULT_START_SLOT <= s < DEFAULT_END_SLOT for s in range(48)] for _ in range(7)]


class Account(Base):
    """Tài khoản web. role: parent | child_view | admin."""
    __tablename__ = "accounts"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100), default="")
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="parent")
    owner_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=True)
    linked_child_id: Mapped[str | None] = mapped_column(String(32), nullable=True)  # cho child_view
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    totp_secret_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    totp_last_counter: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class WebSession(Base):
    __tablename__ = "web_sessions"
    id_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    csrf_token: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class Child(Base):
    __tablename__ = "children"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    parent_id: Mapped[str] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    age_group: Mapped[str] = mapped_column(String(10), default="6-11")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class ChildPolicy(Base):
    __tablename__ = "child_policies"
    child_id: Mapped[str] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    weekday_limit_minutes: Mapped[int] = mapped_column(Integer, default=120)
    weekend_limit_minutes: Mapped[int] = mapped_column(Integer, default=180)
    schedule: Mapped[list] = mapped_column(JSON, default=default_schedule)
    group_budgets: Mapped[dict] = mapped_column(JSON, default=dict)      # {"games": 60} phút/ngày
    category_actions: Mapped[dict] = mapped_column(JSON, default=dict)   # {"games":"limit"}
    domain_overrides: Mapped[dict] = mapped_column(JSON, default=dict)   # {"example.com":"block"|"allow"}
    app_rules: Mapped[list] = mapped_column(JSON, default=list)          # [{name,sha256,action,group}]
    safesearch: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_by: Mapped[str | None] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class Device(Base):
    __tablename__ = "devices"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    parent_id: Mapped[str] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    child_id: Mapped[str] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100), default="Máy tính")
    fingerprint_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active | revoked
    refresh_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    agent_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    enrolled_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    last_seen_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    paused_until: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    forced_lock: Mapped[bool] = mapped_column(Boolean, default=False)


class EnrollmentCode(Base):
    """Mã ghép cặp 8 ký tự, hiệu lực 10 phút = bằng chứng phụ huynh đồng ý lắp đặt."""
    __tablename__ = "enrollment_codes"
    code_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    parent_id: Mapped[str] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    child_id: Mapped[str] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"))
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime)
    used_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    consent_version: Mapped[str] = mapped_column(String(20))
    consent_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    consent_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    child_informed: Mapped[bool] = mapped_column(Boolean, default=False)


class DailyUsage(Base):
    __tablename__ = "daily_usage"
    __table_args__ = (UniqueConstraint("device_id", "usage_date"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    child_id: Mapped[str] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    usage_date: Mapped[str] = mapped_column(String(10))  # YYYY-MM-DD giờ VN
    used_seconds: Mapped[int] = mapped_column(Integer, default=0)
    group_seconds: Mapped[dict] = mapped_column(JSON, default=dict)
    bonus_seconds: Mapped[int] = mapped_column(Integer, default=0)


class Event(Base):
    """Lược đồ sự kiện đúng đặc tả F3 – không có URL đầy đủ/tiêu đề/phím gõ."""
    __tablename__ = "events"
    __table_args__ = (Index("ix_events_child_ts", "child_id", "ts"),)
    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)  # khóa idempotency
    ts: Mapped[datetime] = mapped_column(UTCDateTime)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    child_id: Mapped[str] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(24))
    subject: Mapped[str] = mapped_column(String(255), default="")
    duration_sec: Mapped[int] = mapped_column(Integer, default=0)
    policy_id: Mapped[str] = mapped_column(String(64), default="")


class ChildRequest(Base):
    __tablename__ = "child_requests"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    child_id: Mapped[str] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    device_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    kind: Mapped[str] = mapped_column(String(20))  # more_time | unblock
    subject: Mapped[str] = mapped_column(String(255), default="")
    minutes: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[str] = mapped_column(String(12), default="pending")  # pending|approved|denied
    response_note: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    decided_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)


class Command(Base):
    """Lệnh khẩn gửi tới agent: lock_now, unlock, extend_time, purge_local_data, refresh_policy."""
    __tablename__ = "commands"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    command: Mapped[str] = mapped_column(String(32))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(10), default="pending")  # pending|acked|expired
    issued_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime)
    acked_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, index=True)
    actor_type: Mapped[str] = mapped_column(String(12))  # parent|child_view|device|system
    actor_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    actor_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    action: Mapped[str] = mapped_column(String(48))
    child_id: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    device_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    prev_hash: Mapped[str] = mapped_column(String(64))
    entry_hash: Mapped[str] = mapped_column(String(64))
