"""
RiskService - CRUD operations for Risk entities.

Business logic layer for managing security risks using the new feature-based
schema architecture.
"""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.risk_assessment.schemas.risk import (
    RiskCreate,
    RiskResponse,
    RiskSummary,
    RiskUpdate,
)
from app.shared.models.enums import RiskCategory, RiskLikelihood, RiskSeverity, RiskStatus
from app.shared.models.risk import Risk


logger = logging.getLogger(__name__)


class RiskService:
    """
    Service for Risk CRUD operations.

    Handles business logic for creating, reading, updating, and deleting
    security risks. Converts between SQLAlchemy models and Pydantic schemas.

    Attributes:
        db: Async database session
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initialize RiskService.

        Args:
            db_session: AsyncSession for database operations
        """
        self.db = db_session

    # =========================================================================
    # CREATE
    # =========================================================================

    async def create_risk(self, data: RiskCreate) -> RiskResponse:
        """
        Create a new risk.

        Args:
            data: RiskCreate schema with risk data

        Returns:
            RiskResponse: Created risk with all fields

        Example:
            >>> service = RiskService(db_session)
            >>> risk_data = RiskCreate(
            ...     title="SQL Injection",
            ...     description="Critical vulnerability",
            ...     severity="critical",
            ...     likelihood="high",
            ...     impact_score=9.5,
            ...     category="technical"
            ... )
            >>> risk = await service.create_risk(risk_data)
            >>> print(risk.risk_number)
            RISK-2026-001
        """
        logger.info(f"Creating new risk: {data.title}")

        # Convert string enums to SQLAlchemy enums
        severity_enum = RiskSeverity(data.severity)
        likelihood_enum = RiskLikelihood(data.likelihood)
        status_enum = RiskStatus(data.status)
        category_enum = RiskCategory(data.category)

        # Create risk using Risk.create() classmethod (handles commit internally)
        try:
            risk = await Risk.create(
                db=self.db,
                risk_number=data.risk_number,  # Optional, auto-generated if None
                title=data.title,
                description=data.description,
                severity=severity_enum,
                likelihood=likelihood_enum,
                impact_score=data.impact_score,
                status=status_enum,
                category=category_enum,
                assigned_to=data.assigned_to,
                mitigation_plan=data.mitigation_plan,
                deadline=data.deadline,
            )
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Integrity error creating risk: {e}")
            raise ValueError(f"Risk with number '{data.risk_number}' already exists") from e

        logger.info(f"Risk created successfully: {risk.risk_number} (ID: {risk.id})")

        # Convert to response schema
        return self._to_response(risk)

    # =========================================================================
    # READ
    # =========================================================================

    async def get_risk_by_id(self, risk_id: UUID) -> RiskResponse | None:
        """
        Get risk by ID.

        Args:
            risk_id: UUID of the risk

        Returns:
            RiskResponse if found, None otherwise

        Example:
            >>> risk = await service.get_risk_by_id(uuid4())
            >>> if risk:
            ...     print(risk.title)
        """
        logger.debug(f"Fetching risk by ID: {risk_id}")

        query = select(Risk).where(Risk.id == risk_id)
        result = await self.db.execute(query)
        risk = result.scalar_one_or_none()

        if risk is None:
            logger.warning(f"Risk not found: {risk_id}")
            return None

        logger.debug(f"Risk found: {risk.risk_number}")
        return self._to_response(risk)

    async def list_risks(
        self,
        severity: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[RiskSummary]:
        """
        List risks with optional filters and pagination.

        Args:
            severity: Filter by severity (critical, high, medium, low)
            status: Filter by status (open, in_progress, mitigated, accepted)
            limit: Maximum number of results (default: 100)
            offset: Number of results to skip (default: 0)

        Returns:
            List of RiskSummary objects

        Example:
            >>> risks = await service.list_risks(
            ...     severity="critical",
            ...     status="open",
            ...     limit=10
            ... )
            >>> print(f"Found {len(risks)} critical open risks")
        """
        logger.debug(
            f"Listing risks: severity={severity}, status={status}, "
            f"limit={limit}, offset={offset}"
        )

        # Build query
        query = select(Risk)

        # Apply filters
        if severity:
            severity_enum = RiskSeverity(severity)
            query = query.where(Risk.severity == severity_enum)

        if status:
            status_enum = RiskStatus(status)
            query = query.where(Risk.status == status_enum)

        # Order by created_at descending (newest first)
        query = query.order_by(Risk.created_at.desc())

        # Apply pagination
        query = query.limit(limit).offset(offset)

        # Execute query
        result = await self.db.execute(query)
        risks = result.scalars().all()

        logger.info(f"Found {len(risks)} risks matching criteria")

        # Convert to summary schemas
        return [self._to_summary(risk) for risk in risks]

    # =========================================================================
    # UPDATE
    # =========================================================================

    async def update_risk(self, risk_id: UUID, data: RiskUpdate) -> RiskResponse | None:
        """
        Update an existing risk.

        Args:
            risk_id: UUID of the risk to update
            data: RiskUpdate schema with fields to update

        Returns:
            RiskResponse if updated, None if not found

        Example:
            >>> update_data = RiskUpdate(
            ...     status="mitigated",
            ...     mitigation_plan="Patch applied"
            ... )
            >>> risk = await service.update_risk(risk_id, update_data)
        """
        logger.info(f"Updating risk: {risk_id}")

        # Get existing risk
        query = select(Risk).where(Risk.id == risk_id)
        result = await self.db.execute(query)
        risk = result.scalar_one_or_none()

        if risk is None:
            logger.warning(f"Cannot update - risk not found: {risk_id}")
            return None

        # Build update dict with only provided fields
        update_data = {}

        if data.title is not None:
            update_data["title"] = data.title

        if data.description is not None:
            update_data["description"] = data.description

        if data.severity is not None:
            update_data["severity"] = RiskSeverity(data.severity)

        if data.likelihood is not None:
            update_data["likelihood"] = RiskLikelihood(data.likelihood)

        if data.impact_score is not None:
            update_data["impact_score"] = data.impact_score

        if data.status is not None:
            update_data["status"] = RiskStatus(data.status)

        if data.category is not None:
            update_data["category"] = RiskCategory(data.category)

        if data.assigned_to is not None:
            update_data["assigned_to"] = data.assigned_to

        if data.mitigation_plan is not None:
            update_data["mitigation_plan"] = data.mitigation_plan

        if data.deadline is not None:
            update_data["deadline"] = data.deadline

        # Apply updates
        for key, value in update_data.items():
            setattr(risk, key, value)

        await self.db.commit()
        await self.db.refresh(risk)

        logger.info(f"Risk updated successfully: {risk.risk_number}")

        return self._to_response(risk)

    # =========================================================================
    # DELETE
    # =========================================================================

    async def delete_risk(self, risk_id: UUID) -> bool:
        """
        Delete a risk.

        Args:
            risk_id: UUID of the risk to delete

        Returns:
            True if deleted, False if not found

        Example:
            >>> success = await service.delete_risk(risk_id)
            >>> if success:
            ...     print("Risk deleted")
        """
        logger.info(f"Deleting risk: {risk_id}")

        # Check if risk exists
        query = select(Risk).where(Risk.id == risk_id)
        result = await self.db.execute(query)
        risk = result.scalar_one_or_none()

        if risk is None:
            logger.warning(f"Cannot delete - risk not found: {risk_id}")
            return False

        # Delete
        await self.db.delete(risk)
        await self.db.commit()

        logger.info(f"Risk deleted successfully: {risk.risk_number}")
        return True

    # =========================================================================
    # Private Helper Methods
    # =========================================================================

    def _to_response(self, risk: Risk) -> RiskResponse:
        """
        Convert Risk model to RiskResponse schema.

        Args:
            risk: SQLAlchemy Risk model

        Returns:
            RiskResponse: Pydantic schema for API response
        """
        return RiskResponse(
            id=risk.id,
            risk_number=risk.risk_number,
            title=risk.title,
            description=risk.description,
            severity=risk.severity.value,
            likelihood=risk.likelihood.value,
            impact_score=risk.impact_score,
            status=risk.status.value,
            category=risk.category.value,
            assigned_to=risk.assigned_to,
            mitigation_plan=risk.mitigation_plan,
            deadline=risk.deadline,
            created_at=risk.created_at,
            updated_at=risk.updated_at,
        )

    def _to_summary(self, risk: Risk) -> RiskSummary:
        """
        Convert Risk model to RiskSummary schema.

        Args:
            risk: SQLAlchemy Risk model

        Returns:
            RiskSummary: Lightweight schema for list endpoints
        """
        return RiskSummary(
            id=risk.id,
            risk_number=risk.risk_number,
            title=risk.title,
            severity=risk.severity.value,
            status=risk.status.value,
            calculated_risk_score=risk.calculated_risk_score,
        )
