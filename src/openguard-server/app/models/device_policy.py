
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DevicePolicy(Base):
    __tablename__ = "device_policies"

    device_id: Mapped[str] = mapped_column(
        ForeignKey("devices.id"),
        primary_key=True,
    )

    weekday_limit_minutes: Mapped[int] = mapped_column(
        Integer,
        default=90,
        nullable=False,
    )

    weekend_limit_minutes: Mapped[int] = mapped_column(
        Integer,
        default=120,
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    device = relationship(
        "Device",
        back_populates="policy",
    )
