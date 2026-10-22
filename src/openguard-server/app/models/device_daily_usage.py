
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DeviceDailyUsage(Base):
    __tablename__ = "device_daily_usage"

    __table_args__ = (
        UniqueConstraint(
            "device_id",
            "usage_date",
            name="uq_device_daily_usage_device_date",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    device_id: Mapped[str] = mapped_column(
        ForeignKey("devices.id"),
        nullable=False,
        index=True,
    )

    usage_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    used_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
