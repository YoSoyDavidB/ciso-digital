"""
API routes for Incident Response management.

Provides CRUD endpoints for Incident entities using feature-based architecture.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.incident_response.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentTimelineEvent,
    IncidentUpdate,
)
from app.features.incident_response.services import (
    IncidentNotFoundError,
    IncidentService,
)
from app.shared.models.enums import IncidentSeverity, IncidentStatus, IncidentType


logger = logging.getLogger(__name__)

# Create router with prefix
router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["Incidents"],
)


# =============================================================================
# Dependency Injection
# =============================================================================


def get_incident_service(db: AsyncSession = Depends(get_db)) -> IncidentService:
    """
    Dependency to get IncidentService instance.

    Args:
        db: Database session from dependency

    Returns:
        IncidentService: Initialized service instance
    """
    return IncidentService(db)


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new incident",
    description="Create a new security incident. Incident number is auto-generated.",
    responses={
        201: {"description": "Incident created successfully"},
        422: {"description": "Validation error"},
    },
)
async def create_incident(
    incident_data: IncidentCreate,
    service: IncidentService = Depends(get_incident_service),
) -> IncidentResponse:
    """
    Create a new security incident.

    Args:
        incident_data: Incident creation data
        service: IncidentService instance

    Returns:
        IncidentResponse: Created incident with all fields

    Raises:
        422 Unprocessable Entity: If validation fails
    """
    logger.info(f"Creating new incident: {incident_data.title}")
    try:
        incident = await service.create(
            incident_data=incident_data, created_by="api-user"  # TODO: Get from auth
        )
        logger.info(f"Incident created: {incident.incident_number}")
        return IncidentResponse.model_validate(incident)
    except ValueError as e:
        logger.warning(f"Validation error creating incident: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.get(
    "/statistics",
    response_model=Dict,
    summary="Get incident statistics",
    description="Get aggregated incident statistics including MTTR.",
    responses={
        200: {"description": "Statistics retrieved successfully"},
    },
)
async def get_incident_statistics(
    start_date: Optional[datetime] = Query(
        default=None, description="Start date for statistics"
    ),
    end_date: Optional[datetime] = Query(
        default=None, description="End date for statistics"
    ),
    service: IncidentService = Depends(get_incident_service),
) -> Dict:
    """
    Get incident statistics.

    Args:
        start_date: Optional start date filter
        end_date: Optional end date filter
        service: IncidentService instance

    Returns:
        Dict: Statistics including MTTR, total incidents, distributions
    """
    logger.info(f"Retrieving statistics (start={start_date}, end={end_date})")
    stats = await service.get_statistics(start_date=start_date, end_date=end_date)
    return stats


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
    summary="Get an incident by ID",
    description="Retrieve a single incident by its UUID with all details.",
    responses={
        200: {"description": "Incident retrieved successfully"},
        404: {"description": "Incident not found"},
    },
)
async def get_incident(
    incident_id: UUID,
    service: IncidentService = Depends(get_incident_service),
) -> IncidentResponse:
    """
    Get an incident by ID.

    Args:
        incident_id: UUID of the incident
        service: IncidentService instance

    Returns:
        IncidentResponse: Incident details

    Raises:
        404 Not Found: If incident doesn't exist
    """
    logger.info(f"Retrieving incident: {incident_id}")
    try:
        incident = await service.get_by_id(str(incident_id))
        if incident is None:
            raise IncidentNotFoundError(str(incident_id))
        return IncidentResponse.model_validate(incident)
    except IncidentNotFoundError as e:
        logger.warning(f"Incident not found: {incident_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "",
    response_model=List[IncidentResponse],
    summary="List incidents",
    description="List incidents with optional filtering and pagination.",
    responses={
        200: {"description": "Incidents retrieved successfully"},
    },
)
async def list_incidents(
    severity: Optional[IncidentSeverity] = Query(
        default=None, description="Filter by severity level"
    ),
    status: Optional[IncidentStatus] = Query(
        default=None, description="Filter by status"
    ),
    incident_type: Optional[IncidentType] = Query(
        default=None, description="Filter by incident type", alias="type"
    ),
    assigned_to: Optional[str] = Query(
        default=None, description="Filter by assigned user email"
    ),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    service: IncidentService = Depends(get_incident_service),
) -> List[IncidentResponse]:
    """
    List incidents with filtering and pagination.

    Args:
        severity: Optional severity filter
        status: Optional status filter
        incident_type: Optional type filter
        assigned_to: Optional assigned user filter
        limit: Maximum number of results
        offset: Pagination offset
        service: IncidentService instance

    Returns:
        List[IncidentResponse]: List of incidents
    """
    logger.info(
        f"Listing incidents (severity={severity}, status={status}, "
        f"type={incident_type}, limit={limit}, offset={offset})"
    )

    filters = {}
    if severity:
        filters["severity"] = severity
    if status:
        filters["status"] = status
    if incident_type:
        filters["incident_type"] = incident_type
    if assigned_to:
        filters["assigned_to"] = assigned_to

    incidents = await service.list(filters=filters, limit=limit, offset=offset)

    return [IncidentResponse.model_validate(incident) for incident in incidents]


@router.patch(
    "/{incident_id}",
    response_model=IncidentResponse,
    summary="Update an incident",
    description="Update incident fields partially.",
    responses={
        200: {"description": "Incident updated successfully"},
        404: {"description": "Incident not found"},
        422: {"description": "Validation error"},
    },
)
async def update_incident(
    incident_id: UUID,
    incident_data: IncidentUpdate,
    service: IncidentService = Depends(get_incident_service),
) -> IncidentResponse:
    """
    Update an incident partially.

    Args:
        incident_id: UUID of the incident
        incident_data: Fields to update
        service: IncidentService instance

    Returns:
        IncidentResponse: Updated incident

    Raises:
        404 Not Found: If incident doesn't exist
        422 Unprocessable Entity: If validation fails
    """
    logger.info(f"Updating incident: {incident_id}")
    try:
        incident = await service.update(
            incident_id=str(incident_id), incident_data=incident_data
        )
        logger.info(f"Incident updated: {incident.incident_number}")
        return IncidentResponse.model_validate(incident)
    except IncidentNotFoundError as e:
        logger.warning(f"Incident not found: {incident_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValueError as e:
        logger.warning(f"Validation error updating incident: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.put(
    "/{incident_id}/status",
    response_model=IncidentResponse,
    summary="Update incident status",
    description="Update incident status with automatic timestamp tracking.",
    responses={
        200: {"description": "Status updated successfully"},
        404: {"description": "Incident not found"},
        422: {"description": "Invalid status transition"},
    },
)
async def update_incident_status(
    incident_id: UUID,
    status_update: Dict[str, str],
    service: IncidentService = Depends(get_incident_service),
) -> IncidentResponse:
    """
    Update incident status.

    Args:
        incident_id: UUID of the incident
        status_update: Dictionary with 'status' and 'updated_by' keys
        service: IncidentService instance

    Returns:
        IncidentResponse: Updated incident

    Raises:
        404 Not Found: If incident doesn't exist
        422 Unprocessable Entity: If status is invalid
    """
    logger.info(f"Updating status for incident: {incident_id}")

    new_status = status_update.get("status")
    updated_by = status_update.get("updated_by", "api-user")

    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="'status' field is required",
        )

    try:
        # Validate status enum
        status_enum = IncidentStatus(new_status)

        incident = await service.update_status(
            incident_id=str(incident_id), new_status=status_enum, updated_by=updated_by
        )
        logger.info(f"Status updated to {new_status}: {incident.incident_number}")
        return IncidentResponse.model_validate(incident)
    except ValueError as e:
        logger.warning(f"Invalid status value: {new_status}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status: {new_status}. Valid values: {[s.value for s in IncidentStatus]}",
        )
    except IncidentNotFoundError as e:
        logger.warning(f"Incident not found: {incident_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/{incident_id}/actions",
    response_model=IncidentResponse,
    summary="Add action to incident",
    description="Add an action taken to the incident's action log.",
    responses={
        200: {"description": "Action added successfully"},
        404: {"description": "Incident not found"},
    },
)
async def add_action_taken(
    incident_id: UUID,
    action: Dict,
    service: IncidentService = Depends(get_incident_service),
) -> IncidentResponse:
    """
    Add an action taken to an incident.

    Args:
        incident_id: UUID of the incident
        action: Action details dictionary
        service: IncidentService instance

    Returns:
        IncidentResponse: Updated incident with new action

    Raises:
        404 Not Found: If incident doesn't exist
    """
    logger.info(f"Adding action to incident: {incident_id}")
    try:
        incident = await service.add_action_taken(
            incident_id=str(incident_id), action=action
        )
        logger.info(f"Action added to incident: {incident.incident_number}")
        return IncidentResponse.model_validate(incident)
    except IncidentNotFoundError as e:
        logger.warning(f"Incident not found: {incident_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/{incident_id}/timeline",
    response_model=List[IncidentTimelineEvent],
    summary="Get incident timeline",
    description="Get chronological timeline of incident events.",
    responses={
        200: {"description": "Timeline retrieved successfully"},
        404: {"description": "Incident not found"},
    },
)
async def get_incident_timeline(
    incident_id: UUID,
    service: IncidentService = Depends(get_incident_service),
) -> List[IncidentTimelineEvent]:
    """
    Get incident timeline.

    Args:
        incident_id: UUID of the incident
        service: IncidentService instance

    Returns:
        List[IncidentTimelineEvent]: Chronologically ordered timeline

    Raises:
        404 Not Found: If incident doesn't exist
    """
    logger.info(f"Retrieving timeline for incident: {incident_id}")
    try:
        timeline = await service.get_timeline(incident_id=str(incident_id))
        return [IncidentTimelineEvent(**event) for event in timeline]
    except IncidentNotFoundError as e:
        logger.warning(f"Incident not found: {incident_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
