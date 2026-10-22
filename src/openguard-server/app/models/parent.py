
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Parent(Base):
    __tablename__ = "parents"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    devices = relationship(
        "Device",
        back_populates="parent",
    )
