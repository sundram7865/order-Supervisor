import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from .database import Base


class Supervisor(Base):
    __tablename__ = "supervisors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    base_instruction = Column(Text, nullable=False)
    available_actions = Column(ARRAY(Text), nullable=False, default=[])
    wake_aggressiveness = Column(String(50), nullable=False, default="normal")
    model_config = Column(JSONB, nullable=False, default={})
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    runs = relationship("Run", back_populates="supervisor")


class Run(Base):
    __tablename__ = "runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supervisor_id = Column(UUID(as_uuid=True), ForeignKey("supervisors.id"), nullable=False)
    order_id = Column(String(255), nullable=False)
    workflow_id = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), nullable=False, default="active")
    memory_summary = Column(Text, nullable=False, default="")
    next_wake_at = Column(DateTime, nullable=True)
    order_context = Column(JSONB, nullable=False, default={})
    extra_instructions = Column(ARRAY(Text), nullable=False, default=[])
    final_summary = Column(JSONB, nullable=True)
    event_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    supervisor = relationship("Supervisor", back_populates="runs")
    activities = relationship("ActivityLog", back_populates="run", order_by="ActivityLog.created_at")


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id"), nullable=False)
    kind = Column(String(50), nullable=False)
    payload = Column(JSONB, nullable=False)
    importance = Column(String(50), nullable=False, default="normal")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    run = relationship("Run", back_populates="activities")