
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String

class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    parent_id: Mapped[str] = mapped_column(
        ForeignKey("parents.id"),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    policy_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    used_screen_time_sec: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    parent = relationship(
        "Parent",
        back_populates="devices",
    )

    policy = relationship(
        "DevicePolicy",
        back_populates="device",
        uselist=False,
    )
#Added 17/10/2026
    schedule = relationship(
        "DeviceSchedule",
        back_populates="device",
        uselist=False,
    )
    
    # Session Agent gần nhất gửi heartbeat
    agent_session_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
    )

    # Bộ đếm cuối cùng nhận được trong session hiện tại
    agent_last_reported_usage_sec: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

