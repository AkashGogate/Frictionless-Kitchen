"""Structured, timestamped, speaker-attributed call log (SQLite via SQLAlchemy async).

PROJECT_SPEC.md #4.3: every call logged, matched or not.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Boolean
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.models import MismatchResult


class Base(DeclarativeBase):
    pass


class CallLog(Base):
    __tablename__ = "call_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    raw_text: Mapped[str] = mapped_column(String)
    item: Mapped[str | None] = mapped_column(String, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer)
    station: Mapped[str | None] = mapped_column(String, nullable=True)
    speaker_turn: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_call: Mapped[bool] = mapped_column(Boolean)
    matched: Mapped[bool] = mapped_column(Boolean)
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
    ticket_id: Mapped[str | None] = mapped_column(String, nullable=True)


def make_session_factory(db_path: str = "sqlite+aiosqlite:///kitchen_copilot.db"):
    engine = create_async_engine(db_path)
    return engine, async_sessionmaker(engine, expire_on_commit=False)


async def init_db(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def write_result(session: AsyncSession, result: MismatchResult) -> CallLog:
    row = CallLog(
        raw_text=result.call.raw_text,
        item=result.call.item,
        quantity=result.call.quantity,
        station=result.call.station,
        speaker_turn=result.call.speaker_turn,
        timestamp=result.call.timestamp,
        is_call=result.call.is_call,
        matched=result.matched,
        reason=result.reason,
        ticket_id=result.ticket_id,
    )
    session.add(row)
    await session.commit()
    return row
