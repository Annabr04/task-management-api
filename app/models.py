from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class UTCDateTime(TypeDecorator):
    """DateTime that is always stored and loaded as timezone-aware UTC.

    SQLite has no native timezone type and will otherwise drop tzinfo on read,
    which made API timestamps look naive (no Z / offset) even though values
    were produced with datetime.now(timezone.utc).
    """

    impl = DateTime
    cache_ok = True

    def __init__(self, *args, **kwargs):
        kwargs["timezone"] = True
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


def utc_now():
    return datetime.now(timezone.utc)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utc_now, onupdate=utc_now
    )
