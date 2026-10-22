
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def default_schedule():
    # 7 ngày, mỗi ngày 48 khung giờ.
    # Mặc định chặn toàn bộ cho đến khi phụ huynh cấu hình.
    return [[False for _ in range(48)] for _ in range(7)]


class DeviceSchedule(Base):
    __tablename__ = "device_schedules"

    device_id = Column(
        String(64),
        ForeignKey("devices.id", ondelete="CASCADE"),
        primary_key=True,
    )

    schedule = Column(
        JSON,
        nullable=False,
        default=default_schedule,
    )

    version = Column(Integer, nullable=False, default=1)

    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    device = relationship("Device", back_populates="schedule")
