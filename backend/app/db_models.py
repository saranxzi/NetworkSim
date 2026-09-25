import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Float, BigInteger, ForeignKey, JSON, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    auth_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    auth_provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    
    workspaces: Mapped[list["Workspace"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("auth_provider", "auth_provider_id", name="uq_auth_provider_id"),
    )

class Workspace(Base):
    __tablename__ = "workspaces"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    
    owner: Mapped["User"] = relationship(back_populates="workspaces")
    members: Mapped[list["WorkspaceMember"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
    blueprints: Mapped[list["Blueprint"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_workspace_owner", "owner_id"),
    )

class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="editor")
    
    workspace: Mapped["Workspace"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()

    __table_args__ = (
        Index("idx_member_user", "user_id"),
    )

class Blueprint(Base):
    __tablename__ = "blueprints"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
    
    workspace: Mapped["Workspace"] = relationship(back_populates="blueprints")
    versions: Mapped[list["BlueprintVersion"]] = relationship(back_populates="blueprint", cascade="all, delete-orphan", order_by="BlueprintVersion.version_number.desc()")
    
    __table_args__ = (
        Index("idx_bp_workspace", "workspace_id"),
    )

class BlueprintVersion(Base):
    __tablename__ = "blueprint_versions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    blueprint_id: Mapped[str] = mapped_column(ForeignKey("blueprints.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    graph_schema: Mapped[dict] = mapped_column(JSON, nullable=False)
    invariants: Mapped[list | None] = mapped_column(JSON, default=list)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    
    blueprint: Mapped["Blueprint"] = relationship(back_populates="versions")
    runs: Mapped[list["SimulationRun"]] = relationship(back_populates="blueprint_version", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("blueprint_id", "version_number", name="uq_bp_version"),
        Index("idx_bpv_blueprint", "blueprint_id"),
    )

class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    blueprint_version_id: Mapped[str] = mapped_column(ForeignKey("blueprint_versions.id", ondelete="CASCADE"), nullable=False)
    triggered_by: Mapped[str] = mapped_column(String(100), nullable=False)  # 'web_ui', 'cli', 'github_action'
    seed: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # 'passed', 'failed', 'error', 'running'
    total_ticks: Mapped[int] = mapped_column(Integer, nullable=False)
    p99_latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_dropped: Mapped[int] = mapped_column(BigInteger, default=0)
    invariant_violations: Mapped[dict | None] = mapped_column(JSON, default=dict)
    summary_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    executed_at: Mapped[datetime] = mapped_column(default=utcnow)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    blueprint_version: Mapped["BlueprintVersion"] = relationship(back_populates="runs")
    
    __table_args__ = (
        Index("idx_runs_bpv", "blueprint_version_id"),
        Index("idx_runs_status", "status"),
        Index("idx_runs_executed_at", "executed_at"),
    )

class CloudPricing(Base):
    __tablename__ = "cloud_pricing"
    provider: Mapped[str] = mapped_column(String(50), primary_key=True)
    resource_type: Mapped[str] = mapped_column(String(100), primary_key=True)
    region: Mapped[str] = mapped_column(String(50), primary_key=True)
    hourly_cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    capacity_rps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    egress_cost_per_gb: Mapped[float] = mapped_column(Float, default=0.0)
    last_synced_at: Mapped[datetime] = mapped_column(default=utcnow)
