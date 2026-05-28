from datetime import datetime, timezone
from sqlalchemy import Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class VesselSnapshot(Base):
    __tablename__ = "vessel_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mmsi: Mapped[int] = mapped_column(Integer, index=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    sog: Mapped[float | None] = mapped_column(Float, nullable=True)
    cog: Mapped[float | None] = mapped_column(Float, nullable=True)
    heading: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nav_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class PortCallSnapshot(Base):
    __tablename__ = "port_call_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    port_call_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    vessel_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    mmsi: Mapped[int | None] = mapped_column(Integer, nullable=True)
    port_to_visit: Mapped[str | None] = mapped_column(String(10), nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AtonFaultSnapshot(Base):
    __tablename__ = "aton_fault_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fault_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    aton_id: Mapped[int] = mapped_column(Integer, index=True)
    aton_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    fault_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(20))
    fixed: Mapped[bool] = mapped_column(Boolean, default=False)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class RiskScoreLog(Base):
    __tablename__ = "risk_score_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    score: Mapped[float] = mapped_column(Float)
    level: Mapped[str] = mapped_column(String(20))
    vessel_density_score: Mapped[float] = mapped_column(Float)
    port_congestion_score: Mapped[float] = mapped_column(Float)
    sea_state_score: Mapped[float] = mapped_column(Float)
    aton_fault_score: Mapped[float] = mapped_column(Float)
    winter_navigation_score: Mapped[float] = mapped_column(Float)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
