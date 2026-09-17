"""API endpoints for Canonical Environmental State management."""

import uuid
from typing import List, Optional, Dict
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy import select

from backend.app.db.session import get_db
from backend.app.models.environmental_state import EnvironmentalProfile
from backend.app.schemas.environmental_state import (
    EnvironmentalState,
    EnvironmentalStateCreate,
    EnvironmentalStateUpdate,
    EnvironmentalStateResponse,
)
from backend.app.core.logging import logger

router = APIRouter()

# In-memory store fallback used when database is disconnected/offline
_IN_MEMORY_PROFILES: Dict[str, dict] = {}


def _serialize_profile(
    profile_id: str,
    name: Optional[str],
    description: Optional[str],
    state: EnvironmentalState,
    created_at: datetime,
    updated_at: datetime,
) -> EnvironmentalStateResponse:
    return EnvironmentalStateResponse(
        id=profile_id,
        name=name,
        description=description,
        state=state,
        metrics_count=state.count_known_metrics(),
        created_at=created_at,
        updated_at=updated_at,
    )


@router.post(
    "",
    response_model=EnvironmentalStateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Environmental Profile",
    description="Initialize a new environmental profile with canonical validated environmental state.",
)
def create_environmental_state(
    payload: EnvironmentalStateCreate,
    db: Session = Depends(get_db),
) -> EnvironmentalStateResponse:
    profile_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    canonical_state = payload.state

    try:
        db_profile = EnvironmentalProfile(
            id=profile_id,
            name=payload.name,
            description=payload.description,
            created_at=now,
            updated_at=now,
        )
        db_profile.sync_spatial_and_metrics(canonical_state)
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)

        return _serialize_profile(
            profile_id=db_profile.id,
            name=db_profile.name,
            description=db_profile.description,
            state=db_profile.to_canonical_state(),
            created_at=db_profile.created_at,
            updated_at=db_profile.updated_at,
        )
    except (OperationalError, SQLAlchemyError) as exc:
        logger.warning(f"Database unavailable for create_environmental_state, using in-memory store: {exc}")
        db.rollback()
        # In-memory fallback
        _IN_MEMORY_PROFILES[profile_id] = {
            "id": profile_id,
            "name": payload.name,
            "description": payload.description,
            "state_data": canonical_state.model_dump(),
            "created_at": now,
            "updated_at": now,
        }
        return _serialize_profile(
            profile_id=profile_id,
            name=payload.name,
            description=payload.description,
            state=canonical_state,
            created_at=now,
            updated_at=now,
        )


@router.get(
    "/{profile_id}",
    response_model=EnvironmentalStateResponse,
    summary="Get Environmental Profile",
    description="Retrieve an existing environmental profile by ID.",
)
def get_environmental_state(
    profile_id: str,
    db: Session = Depends(get_db),
) -> EnvironmentalStateResponse:
    try:
        db_profile = db.get(EnvironmentalProfile, profile_id)
        if db_profile is not None:
            return _serialize_profile(
                profile_id=db_profile.id,
                name=db_profile.name,
                description=db_profile.description,
                state=db_profile.to_canonical_state(),
                created_at=db_profile.created_at,
                updated_at=db_profile.updated_at,
            )
    except (OperationalError, SQLAlchemyError) as exc:
        logger.warning(f"Database query failed, checking in-memory store: {exc}")

    # Check in-memory store fallback
    if profile_id in _IN_MEMORY_PROFILES:
        item = _IN_MEMORY_PROFILES[profile_id]
        state = EnvironmentalState.model_validate(item["state_data"])
        return _serialize_profile(
            profile_id=item["id"],
            name=item["name"],
            description=item["description"],
            state=state,
            created_at=item["created_at"],
            updated_at=item["updated_at"],
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Environmental profile with id '{profile_id}' not found.",
    )


@router.patch(
    "/{profile_id}",
    response_model=EnvironmentalStateResponse,
    summary="Update Environmental Profile State",
    description=(
        "Update an existing environmental profile. Supports partial input. "
        "Rule: Latest explicit user values override older values. "
        "Missing/null values in update do NOT erase previously known values."
    ),
)
def update_environmental_state(
    profile_id: str,
    payload: EnvironmentalStateUpdate,
    db: Session = Depends(get_db),
) -> EnvironmentalStateResponse:
    now = datetime.now(timezone.utc)

    # Extract non-null update fields from payload
    update_dict: dict = {}
    for section in ["soil", "land", "biodiversity", "climate", "human_impact", "spatial_context"]:
        section_val = getattr(payload, section)
        if section_val is not None:
            # exclude_none=True ensures we only take explicitly supplied values
            sub_dict = section_val.model_dump(exclude_none=True)
            if sub_dict:
                update_dict[section] = sub_dict

    try:
        db_profile = db.get(EnvironmentalProfile, profile_id)
        if db_profile is not None:
            current_state = db_profile.to_canonical_state()
            merged_state = current_state.merge_update(update_dict)

            if payload.name is not None:
                db_profile.name = payload.name
            if payload.description is not None:
                db_profile.description = payload.description

            db_profile.updated_at = now
            db_profile.sync_spatial_and_metrics(merged_state)

            db.commit()
            db.refresh(db_profile)

            return _serialize_profile(
                profile_id=db_profile.id,
                name=db_profile.name,
                description=db_profile.description,
                state=db_profile.to_canonical_state(),
                created_at=db_profile.created_at,
                updated_at=db_profile.updated_at,
            )
    except (OperationalError, SQLAlchemyError) as exc:
        logger.warning(f"Database update failed, updating in-memory store: {exc}")
        db.rollback()

    # Fallback to in-memory store
    if profile_id in _IN_MEMORY_PROFILES:
        item = _IN_MEMORY_PROFILES[profile_id]
        current_state = EnvironmentalState.model_validate(item["state_data"])
        merged_state = current_state.merge_update(update_dict)

        if payload.name is not None:
            item["name"] = payload.name
        if payload.description is not None:
            item["description"] = payload.description

        item["state_data"] = merged_state.model_dump()
        item["updated_at"] = now

        return _serialize_profile(
            profile_id=item["id"],
            name=item["name"],
            description=item["description"],
            state=merged_state,
            created_at=item["created_at"],
            updated_at=item["updated_at"],
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Environmental profile with id '{profile_id}' not found.",
    )


@router.get(
    "",
    response_model=List[EnvironmentalStateResponse],
    summary="List Environmental Profiles",
    description="Retrieve recent environmental profiles with optional pagination.",
)
def list_environmental_states(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> List[EnvironmentalStateResponse]:
    results: List[EnvironmentalStateResponse] = []

    try:
        stmt = select(EnvironmentalProfile).order_by(EnvironmentalProfile.updated_at.desc()).limit(limit).offset(offset)
        profiles = db.scalars(stmt).all()
        for p in profiles:
            results.append(
                _serialize_profile(
                    profile_id=p.id,
                    name=p.name,
                    description=p.description,
                    state=p.to_canonical_state(),
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                )
            )
        return results
    except (OperationalError, SQLAlchemyError) as exc:
        logger.warning(f"Database list failed, returning in-memory profiles: {exc}")

    # Fallback to in-memory store
    for item in list(_IN_MEMORY_PROFILES.values())[offset:offset + limit]:
        state = EnvironmentalState.model_validate(item["state_data"])
        results.append(
            _serialize_profile(
                profile_id=item["id"],
                name=item["name"],
                description=item["description"],
                state=state,
                created_at=item["created_at"],
                updated_at=item["updated_at"],
            )
        )
    return results


@router.post(
    "/validate",
    summary="Validate Environmental State Payload",
    description="Pure validation endpoint to test any environmental state payload without persistence.",
)
def validate_environmental_state(payload: EnvironmentalState) -> dict:
    return {
        "valid": True,
        "metrics_count": payload.count_known_metrics(),
        "is_empty": payload.is_empty(),
        "state": payload.model_dump(),
    }
