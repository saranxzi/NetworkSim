import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, ConfigDict
from app.deps import get_db, get_current_user, CurrentUser
from app.db_models import SimulationRun, BlueprintVersion, Blueprint, Workspace

logger = logging.getLogger(__name__)
router = APIRouter()

class RunCreate(BaseModel):
    blueprint_version_id: str
    triggered_by: str
    seed: int
    status: str
    total_ticks: int
    p99_latency_ms: Optional[float] = None
    total_dropped: int = 0
    invariant_violations: Optional[dict] = None
    summary_markdown: Optional[str] = None
    duration_seconds: Optional[float] = None

class RunResponse(BaseModel):
    id: str
    blueprint_version_id: str
    triggered_by: str
    seed: int
    status: str
    total_ticks: int
    p99_latency_ms: Optional[float]
    total_dropped: int
    invariant_violations: Optional[dict]
    summary_markdown: Optional[str]
    executed_at: datetime
    duration_seconds: Optional[float]

    model_config = ConfigDict(from_attributes=True)

@router.post("", response_model=RunResponse)
async def record_run(
    data: RunCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """Record a new simulation run."""
    # Verify the blueprint version exists
    stmt = (
        select(BlueprintVersion)
        .join(Blueprint)
        .join(Workspace)
        .where(
            BlueprintVersion.id == data.blueprint_version_id,
            Workspace.owner_id == user.id
        )
    )
    result = await db.execute(stmt)
    v = result.scalars().first()
    if not v:
        raise HTTPException(status_code=404, detail="Blueprint version not found")
        
    run = SimulationRun(**data.model_dump())
    db.add(run)
    await db.flush()
    return run

@router.get("", response_model=List[RunResponse])
async def list_runs(
    blueprint_id: str = Query(..., description="The blueprint ID to fetch runs for"),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """List simulation runs for a blueprint."""
    stmt = (
        select(SimulationRun)
        .join(BlueprintVersion)
        .join(Blueprint)
        .join(Workspace)
        .where(
            BlueprintVersion.blueprint_id == blueprint_id,
            Workspace.owner_id == user.id
        )
        .order_by(SimulationRun.executed_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{id}", response_model=RunResponse)
async def get_run(
    id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """Get details of a specific run."""
    stmt = (
        select(SimulationRun)
        .join(BlueprintVersion)
        .join(Blueprint)
        .join(Workspace)
        .where(
            SimulationRun.id == id,
            Workspace.owner_id == user.id
        )
    )
    result = await db.execute(stmt)
    run = result.scalars().first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
