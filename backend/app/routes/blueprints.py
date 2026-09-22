import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, ConfigDict
from app.deps import get_db, get_current_user, CurrentUser
from app.db_models import Workspace, Blueprint, BlueprintVersion

logger = logging.getLogger(__name__)
router = APIRouter()

class BlueprintCreate(BaseModel):
    name: str
    description: Optional[str] = None

class BlueprintVersionCreate(BaseModel):
    graph_schema: dict
    invariants: Optional[dict] = None

class BlueprintVersionResponse(BaseModel):
    id: str
    blueprint_id: str
    version_number: int
    graph_schema: dict
    invariants: Optional[dict]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class BlueprintResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class BlueprintWithLatestVersion(BlueprintResponse):
    latest_version: Optional[BlueprintVersionResponse] = None

async def _get_default_workspace(db: AsyncSession, user: CurrentUser) -> str:
    stmt = select(Workspace).where(Workspace.owner_id == user.id)
    result = await db.execute(stmt)
    workspace = result.scalars().first()
    
    if not workspace:
        from app.db_models import User
        # Ensure user exists for FK
        user_stmt = select(User).where(User.id == user.id)
        user_res = await db.execute(user_stmt)
        if not user_res.scalars().first():
            db_user = User(id=user.id, email=user.email, display_name=user.display_name, auth_provider=user.auth_provider, auth_provider_id=user.id)
            db.add(db_user)
            await db.flush()

        workspace = Workspace(name="Default Workspace", owner_id=user.id)
        db.add(workspace)
        await db.flush()
    return workspace.id

@router.post("", response_model=BlueprintResponse)
async def create_blueprint(
    data: BlueprintCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """Create a new blueprint."""
    workspace_id = await _get_default_workspace(db, user)
    blueprint = Blueprint(
        workspace_id=workspace_id,
        name=data.name,
        description=data.description
    )
    db.add(blueprint)
    await db.flush()
    return blueprint

@router.get("", response_model=List[BlueprintResponse])
async def list_blueprints(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """List blueprints for user."""
    workspace_id = await _get_default_workspace(db, user)
    stmt = select(Blueprint).where(Blueprint.workspace_id == workspace_id)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{id}", response_model=BlueprintWithLatestVersion)
async def get_blueprint(
    id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """Get blueprint and latest version."""
    workspace_id = await _get_default_workspace(db, user)
    stmt = select(Blueprint).where(Blueprint.id == id, Blueprint.workspace_id == workspace_id)
    result = await db.execute(stmt)
    bp = result.scalars().first()
    if not bp:
        raise HTTPException(status_code=404, detail="Blueprint not found")
        
    v_stmt = select(BlueprintVersion).where(BlueprintVersion.blueprint_id == id).order_by(BlueprintVersion.version_number.desc()).limit(1)
    v_res = await db.execute(v_stmt)
    latest_v = v_res.scalars().first()
    
    resp = BlueprintWithLatestVersion.model_validate(bp)
    if latest_v:
        resp.latest_version = BlueprintVersionResponse.model_validate(latest_v)
    return resp

@router.post("/{id}/versions", response_model=BlueprintVersionResponse)
async def save_version(
    id: str,
    data: BlueprintVersionCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """Save a new blueprint version."""
    workspace_id = await _get_default_workspace(db, user)
    stmt = select(Blueprint).where(Blueprint.id == id, Blueprint.workspace_id == workspace_id).with_for_update()
    result = await db.execute(stmt)
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Blueprint not found")
        
    v_stmt = select(BlueprintVersion.version_number).where(BlueprintVersion.blueprint_id == id).order_by(BlueprintVersion.version_number.desc()).limit(1)
    v_res = await db.execute(v_stmt)
    latest_num = v_res.scalars().first() or 0
    
    new_ver = BlueprintVersion(
        blueprint_id=id,
        version_number=latest_num + 1,
        graph_schema=data.graph_schema,
        invariants=data.invariants or {},
        created_by=user.id
    )
    db.add(new_ver)
    await db.flush()
    return new_ver

@router.get("/{id}/versions", response_model=List[BlueprintVersionResponse])
async def list_versions(
    id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """List all versions of a blueprint."""
    workspace_id = await _get_default_workspace(db, user)
    stmt = select(Blueprint).where(Blueprint.id == id, Blueprint.workspace_id == workspace_id)
    result = await db.execute(stmt)
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Blueprint not found")
        
    v_stmt = select(BlueprintVersion).where(BlueprintVersion.blueprint_id == id).order_by(BlueprintVersion.version_number.desc())
    v_res = await db.execute(v_stmt)
    return v_res.scalars().all()

@router.get("/{id}/versions/{ver}", response_model=BlueprintVersionResponse)
async def get_version(
    id: str,
    ver: int,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """Get a specific blueprint version."""
    workspace_id = await _get_default_workspace(db, user)
    stmt = select(Blueprint).where(Blueprint.id == id, Blueprint.workspace_id == workspace_id)
    result = await db.execute(stmt)
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Blueprint not found")
        
    v_stmt = select(BlueprintVersion).where(BlueprintVersion.blueprint_id == id, BlueprintVersion.version_number == ver)
    v_res = await db.execute(v_stmt)
    v = v_res.scalars().first()
    if not v:
        raise HTTPException(status_code=404, detail="Version not found")
    return v

@router.delete("/{id}")
async def delete_blueprint(
    id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """Delete a blueprint."""
    workspace_id = await _get_default_workspace(db, user)
    stmt = select(Blueprint).where(Blueprint.id == id, Blueprint.workspace_id == workspace_id)
    result = await db.execute(stmt)
    bp = result.scalars().first()
    if not bp:
        raise HTTPException(status_code=404, detail="Blueprint not found")
        
    await db.delete(bp)
    return {"status": "deleted"}
