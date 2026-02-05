"""
API routes for Risk management.

Provides CRUD endpoints for Risk entities using feature-based architecture.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.risk_assessment.schemas.risk import (
    RiskCreate,
    RiskResponse,
    RiskSummary,
    RiskUpdate,
)
from app.features.risk_assessment.services.risk_service import RiskService


logger = logging.getLogger(__name__)

# Create router with prefix
router = APIRouter(
    prefix="/api/v1/risks",
    tags=["Risks"],
)


# =============================================================================
# Dependency Injection
# =============================================================================


def get_risk_service(db: AsyncSession = Depends(get_db)) -> RiskService:
    """
    Dependency to get RiskService instance.

    Args:
        db: Database session from dependency

    Returns:
        RiskService: Initialized service instance
    """
    return RiskService(db)


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "",
    response_model=RiskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new risk",
    description="Create a new risk with the provided data. Risk number is auto-generated if not provided.",
    responses={
        201: {"description": "Risk created successfully"},
        422: {"description": "Validation error"},
    },
)
async def create_risk(
    risk_data: RiskCreate,
    service: RiskService = Depends(get_risk_service),
) -> RiskResponse:
    """
    Create a new risk.

    Args:
        risk_data: Risk creation data
        service: RiskService instance

    Returns:
        RiskResponse: Created risk with all fields

    Raises:
        422 Unprocessable Entity: If validation fails (e.g., invalid email, past deadline)
    """
    logger.info(f"Creating new risk: {risk_data.title}")
    try:
        risk = await service.create_risk(risk_data)
        logger.info(f"Risk created: {risk.risk_number}")
        return risk
    except ValueError as e:
        logger.warning(f"Duplicate risk_number: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get(
    "/{risk_id}",
    response_model=RiskResponse,
    summary="Get a risk by ID",
    description="Retrieve a single risk by its UUID with all details.",
    responses={
        200: {"description": "Risk found"},
        404: {"description": "Risk not found"},
    },
)
async def get_risk(
    risk_id: UUID,
    service: RiskService = Depends(get_risk_service),
) -> RiskResponse:
    """
    Get a risk by its ID.

    Args:
        risk_id: UUID of the risk
        service: RiskService instance

    Returns:
        RiskResponse: Complete risk data

    Raises:
        404 Not Found: If risk doesn't exist
    """
    logger.debug(f"Fetching risk: {risk_id}")
    risk = await service.get_risk_by_id(risk_id)

    if not risk:
        logger.warning(f"Risk not found: {risk_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Risk with ID {risk_id} not found",
        )

    return risk


@router.get(
    "",
    response_model=list[RiskSummary],
    summary="List risks",
    description="Get a list of risks with optional filters. Returns lightweight summary objects.",
    responses={
        200: {"description": "List of risks (may be empty)"},
    },
)
async def list_risks(
    offset: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    severity: str | None = Query(
        None,
        description="Filter by severity",
        pattern="^(critical|high|medium|low)$",
    ),
    status: str | None = Query(
        None,
        description="Filter by status",
        pattern="^(open|in_progress|mitigated|accepted)$",
    ),
    service: RiskService = Depends(get_risk_service),
) -> list[RiskSummary]:
    """
    Get a list of risks with optional filters.

    Args:
        offset: Number of records to skip (pagination)
        limit: Maximum number of records to return
        severity: Optional severity filter (critical, high, medium, low)
        status: Optional status filter (open, in_progress, mitigated, accepted)
        service: RiskService instance

    Returns:
        list[RiskSummary]: List of risk summaries (lightweight objects)

    Note:
        - Uses RiskSummary for reduced payload size
        - Results ordered by created_at descending (newest first)
        - Empty list returned if no risks match criteria
    """
    logger.debug(
        f"Listing risks: offset={offset}, limit={limit}, " f"severity={severity}, status={status}"
    )

    risks = await service.list_risks(
        severity=severity,
        status=status,
        limit=limit,
        offset=offset,
    )

    logger.info(f"Found {len(risks)} risks matching criteria")
    return risks


@router.patch(
    "/{risk_id}",
    response_model=RiskResponse,
    summary="Update a risk",
    description="Update an existing risk. Only provided fields will be updated (partial update).",
    responses={
        200: {"description": "Risk updated successfully"},
        404: {"description": "Risk not found"},
        422: {"description": "Validation error"},
    },
)
async def update_risk(
    risk_id: UUID,
    risk_update: RiskUpdate,
    service: RiskService = Depends(get_risk_service),
) -> RiskResponse:
    """
    Update an existing risk (partial update).

    Args:
        risk_id: UUID of the risk to update
        risk_update: Fields to update (all optional)
        service: RiskService instance

    Returns:
        RiskResponse: Updated risk with all fields

    Raises:
        404 Not Found: If risk doesn't exist
        422 Unprocessable Entity: If validation fails

    Note:
        - Only fields provided in the request body will be updated
        - Empty request body is valid (no-op)
        - Validators still apply to provided fields
    """
    logger.info(f"Updating risk: {risk_id}")
    risk = await service.update_risk(risk_id, risk_update)

    if not risk:
        logger.warning(f"Cannot update - risk not found: {risk_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Risk with ID {risk_id} not found",
        )

    logger.info(f"Risk updated: {risk.risk_number}")
    return risk


@router.delete(
    "/{risk_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a risk",
    description="Permanently delete a risk from the database.",
    responses={
        204: {"description": "Risk deleted successfully"},
        404: {"description": "Risk not found"},
    },
)
async def delete_risk(
    risk_id: UUID,
    service: RiskService = Depends(get_risk_service),
) -> None:
    """
    Delete a risk permanently.

    Args:
        risk_id: UUID of the risk to delete
        service: RiskService instance

    Raises:
        404 Not Found: If risk doesn't exist

    Warning:
        This operation is permanent and cannot be undone.
    """
    logger.info(f"Deleting risk: {risk_id}")
    deleted = await service.delete_risk(risk_id)

    if not deleted:
        logger.warning(f"Cannot delete - risk not found: {risk_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Risk with ID {risk_id} not found",
        )

    logger.info(f"Risk deleted successfully: {risk_id}")
