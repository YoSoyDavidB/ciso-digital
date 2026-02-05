"""
Pydantic schemas for Risk entities.

Defines request/response models for Risk API endpoints with comprehensive
validation and OpenAPI documentation.
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# =============================================================================
# Base Schema
# =============================================================================


class RiskBase(BaseModel):
    """
    Base schema with common Risk fields.

    Used as foundation for other Risk schemas (Create, Update, Response).
    """

    title: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Risk title (5-255 characters)",
        examples=["SQL Injection in Authentication Endpoint"],
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Detailed risk description",
        examples=[
            "Critical SQL injection vulnerability in login form allowing unauthorized access"
        ],
    )
    severity: str = Field(
        ...,
        description="Risk severity level: critical, high, medium, low",
        examples=["critical"],
    )
    likelihood: str = Field(
        ...,
        description="Probability of risk occurrence: high, medium, low",
        examples=["high"],
    )
    impact_score: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="Impact score (0.0-10.0)",
        examples=[9.5],
    )
    category: str = Field(
        ...,
        description="Risk category: technical, operational, compliance",
        examples=["technical"],
    )

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        """Validate severity is a valid enum value."""
        valid_values = ["critical", "high", "medium", "low"]
        if v not in valid_values:
            raise ValueError(f"severity must be one of {valid_values}")
        return v

    @field_validator("likelihood")
    @classmethod
    def validate_likelihood(cls, v: str) -> str:
        """Validate likelihood is a valid enum value."""
        valid_values = ["high", "medium", "low"]
        if v not in valid_values:
            raise ValueError(f"likelihood must be one of {valid_values}")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category is a valid enum value."""
        valid_values = ["technical", "operational", "compliance"]
        if v not in valid_values:
            raise ValueError(f"category must be one of {valid_values}")
        return v


# =============================================================================
# Request Schemas
# =============================================================================


class RiskCreate(RiskBase):
    """
    Schema for creating a new Risk.

    Used for POST /api/v1/risks endpoint.
    risk_number is optional - will be auto-generated if not provided.
    """

    risk_number: str | None = Field(
        None,
        min_length=1,
        max_length=50,
        description="Optional risk identifier (auto-generated if omitted)",
        examples=["RISK-2026-001"],
    )
    status: str = Field(
        default="open",
        description="Risk status: open, in_progress, mitigated, accepted",
        examples=["open"],
    )
    assigned_to: EmailStr | None = Field(
        None,
        description="Email of assigned person",
        examples=["security@company.com"],
    )
    mitigation_plan: str | None = Field(
        None,
        description="Plan to mitigate the risk",
        examples=["1. Apply security patches\n2. Update firewall rules\n3. Monitor logs"],
    )
    deadline: date | None = Field(
        None,
        description="Deadline for risk mitigation (must be future date)",
        examples=["2026-12-31"],
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is a valid enum value."""
        valid_values = ["open", "in_progress", "mitigated", "accepted"]
        if v not in valid_values:
            raise ValueError(f"status must be one of {valid_values}")
        return v

    @field_validator("deadline")
    @classmethod
    def validate_deadline_future(cls, v: date | None) -> date | None:
        """Validate deadline is in the future."""
        if v is not None and v < date.today():
            raise ValueError("deadline must be a future date")
        return v


class RiskUpdate(BaseModel):
    """
    Schema for updating an existing Risk.

    All fields are optional (partial update).
    Used for PATCH /api/v1/risks/{id} endpoint.
    """

    title: str | None = Field(
        None,
        min_length=5,
        max_length=255,
        description="Risk title",
    )
    description: str | None = Field(
        None,
        min_length=1,
        description="Risk description",
    )
    severity: str | None = Field(
        None,
        description="Risk severity",
    )
    likelihood: str | None = Field(
        None,
        description="Risk likelihood",
    )
    impact_score: float | None = Field(
        None,
        ge=0.0,
        le=10.0,
        description="Impact score (0.0-10.0)",
    )
    status: str | None = Field(
        None,
        description="Risk status",
    )
    category: str | None = Field(
        None,
        description="Risk category",
    )
    assigned_to: EmailStr | None = Field(
        None,
        description="Assigned person email",
    )
    mitigation_plan: str | None = Field(
        None,
        description="Mitigation plan",
    )
    deadline: date | None = Field(
        None,
        description="Mitigation deadline",
    )

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str | None) -> str | None:
        """Validate severity if provided."""
        if v is not None:
            valid_values = ["critical", "high", "medium", "low"]
            if v not in valid_values:
                raise ValueError(f"severity must be one of {valid_values}")
        return v

    @field_validator("likelihood")
    @classmethod
    def validate_likelihood(cls, v: str | None) -> str | None:
        """Validate likelihood if provided."""
        if v is not None:
            valid_values = ["high", "medium", "low"]
            if v not in valid_values:
                raise ValueError(f"likelihood must be one of {valid_values}")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str | None) -> str | None:
        """Validate category if provided."""
        if v is not None:
            valid_values = ["technical", "operational", "compliance"]
            if v not in valid_values:
                raise ValueError(f"category must be one of {valid_values}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        """Validate status if provided."""
        if v is not None:
            valid_values = ["open", "in_progress", "mitigated", "accepted"]
            if v not in valid_values:
                raise ValueError(f"status must be one of {valid_values}")
        return v

    @field_validator("deadline")
    @classmethod
    def validate_deadline_future(cls, v: date | None) -> date | None:
        """Validate deadline is in the future if provided."""
        if v is not None and v < date.today():
            raise ValueError("deadline must be a future date")
        return v


# =============================================================================
# Response Schemas
# =============================================================================


class RiskResponse(RiskBase):
    """
    Schema for Risk response (full details).

    Used for GET /api/v1/risks/{id} and POST/PATCH responses.
    Includes all fields including DB-generated ones.
    """

    id: UUID = Field(..., description="Unique risk ID")
    risk_number: str = Field(..., description="Risk identifier")
    status: str = Field(..., description="Risk status")
    assigned_to: EmailStr | None = Field(None, description="Assigned person")
    mitigation_plan: str | None = Field(None, description="Mitigation plan")
    deadline: date | None = Field(None, description="Mitigation deadline")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {
        "from_attributes": True,  # Enable ORM mode for SQLAlchemy models
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "risk_number": "RISK-2026-001",
                "title": "SQL Injection in Login",
                "description": "Critical vulnerability in authentication endpoint",
                "severity": "critical",
                "likelihood": "high",
                "impact_score": 9.5,
                "status": "open",
                "category": "technical",
                "assigned_to": "security@company.com",
                "mitigation_plan": "Apply security patches immediately",
                "deadline": "2026-03-01",
                "created_at": "2026-02-05T10:00:00Z",
                "updated_at": "2026-02-05T10:00:00Z",
            }
        },
    }


class RiskSummary(BaseModel):
    """
    Schema for Risk summary (essential fields only).

    Used for GET /api/v1/risks (list) to reduce payload size.
    Contains only the most important fields for listing.
    """

    id: UUID = Field(..., description="Unique risk ID")
    risk_number: str = Field(..., description="Risk identifier")
    title: str = Field(..., description="Risk title")
    severity: str = Field(..., description="Risk severity")
    status: str = Field(..., description="Risk status")
    calculated_risk_score: float = Field(
        ...,
        description="Calculated risk score (likelihood * impact)",
        examples=[9.5],
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "risk_number": "RISK-2026-001",
                "title": "SQL Injection in Login",
                "severity": "critical",
                "status": "open",
                "calculated_risk_score": 9.5,
            }
        },
    }
