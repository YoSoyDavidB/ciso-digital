"""
Risk Model - Modelo de riesgos de seguridad.

Este módulo define el modelo Risk para gestión de riesgos identificados
en la organización con el nuevo schema optimizado.
"""

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, Float, String, Text, func, select
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.shared.models.base import Base, TimestampMixin, UUIDMixin
from app.shared.models.enums import (
    RiskCategory,
    RiskLikelihood,
    RiskSeverity,
    RiskStatus,
)


class Risk(Base, UUIDMixin, TimestampMixin):
    """
    Modelo de Riesgo de Seguridad.

    Representa un riesgo identificado en la organización con su evaluación,
    estado y plan de mitigación.

    Attributes:
        id: UUID único del riesgo (heredado de UUIDMixin)
        risk_number: Número único identificador (ej: RISK-2026-001)
        title: Título descriptivo del riesgo (max 255 caracteres)
        description: Descripción detallada del riesgo
        severity: Severidad del riesgo (critical, high, medium, low)
        likelihood: Probabilidad de ocurrencia (high, medium, low)
        impact_score: Score de impacto en escala 0.0-10.0
        status: Estado actual del riesgo (open, in_progress, mitigated, accepted)
        category: Categoría del riesgo (technical, operational, compliance)
        assigned_to: Email del responsable asignado (opcional)
        mitigation_plan: Plan de mitigación detallado (opcional)
        deadline: Fecha límite para mitigación (opcional)
        created_at: Timestamp de creación (heredado de TimestampMixin)
        updated_at: Timestamp de última actualización (heredado de TimestampMixin)

    Example:
        >>> risk = Risk(
        ...     risk_number="RISK-2026-001",
        ...     title="SQL Injection Vulnerability",
        ...     description="Critical SQL injection in login endpoint",
        ...     severity=RiskSeverity.CRITICAL,
        ...     likelihood=RiskLikelihood.HIGH,
        ...     impact_score=9.5,
        ...     status=RiskStatus.OPEN,
        ...     category=RiskCategory.TECHNICAL,
        ...     assigned_to="security@company.com",
        ...     deadline=date(2026, 3, 1),
        ... )
        >>> print(risk.risk_number)
        RISK-2026-001
    """

    __tablename__ = "risks"

    # =========================================================================
    # Identificación
    # =========================================================================

    risk_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Identificador único del riesgo (ej: RISK-2026-001)",
    )

    # =========================================================================
    # Información Básica
    # =========================================================================

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Título descriptivo del riesgo",
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Descripción detallada del riesgo",
    )

    # =========================================================================
    # Evaluación de Riesgo
    # =========================================================================

    severity: Mapped[RiskSeverity] = mapped_column(
        SQLAlchemyEnum(
            RiskSeverity,
            name="riskseverity",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        index=True,
        comment="Severidad del riesgo: critical, high, medium, low",
    )

    likelihood: Mapped[RiskLikelihood] = mapped_column(
        SQLAlchemyEnum(
            RiskLikelihood,
            name="risklikelihood",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        index=True,
        comment="Probabilidad de ocurrencia: high, medium, low",
    )

    impact_score: Mapped[float] = mapped_column(
        Float,
        CheckConstraint("impact_score >= 0.0 AND impact_score <= 10.0"),
        nullable=False,
        comment="Score de impacto en escala 0.0-10.0",
    )

    # =========================================================================
    # Estado y Categorización
    # =========================================================================

    status: Mapped[RiskStatus] = mapped_column(
        SQLAlchemyEnum(
            RiskStatus,
            name="riskstatus",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=RiskStatus.OPEN,
        server_default="open",
        index=True,
        comment="Estado actual: open, in_progress, mitigated, accepted",
    )

    category: Mapped[RiskCategory] = mapped_column(
        SQLAlchemyEnum(
            RiskCategory,
            name="riskcategory",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        index=True,
        comment="Categoría: technical, operational, compliance",
    )

    # =========================================================================
    # Asignación y Mitigación (Campos Opcionales)
    # =========================================================================

    assigned_to: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="Email del responsable asignado",
    )

    mitigation_plan: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Plan detallado de mitigación",
    )

    deadline: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        index=True,
        comment="Fecha límite para mitigación",
    )

    # =========================================================================
    # Métodos
    # =========================================================================

    def __repr__(self) -> str:
        """Representación string del modelo para debugging."""
        return (
            f"<Risk {self.risk_number}: {self.title} [{self.severity.value}/{self.status.value}]>"
        )

    def __str__(self) -> str:
        """Representación string user-friendly."""
        return f"{self.risk_number} - {self.title}"

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        risk_number: str | None = None,
        **kwargs,
    ) -> "Risk":
        """
        Crea un nuevo Risk con risk_number auto-generado si no se proporciona.

        Este método de clase simplifica la creación de riesgos al generar
        automáticamente un risk_number único si no se proporciona uno.

        Args:
            db: Sesión de base de datos async
            risk_number: Número de riesgo opcional. Si no se proporciona,
                se genera automáticamente con formato RISK-YYYY-NNN
            **kwargs: Campos del modelo Risk (title, description, severity, etc.)

        Returns:
            Risk: Instancia de Risk creada y guardada en la base de datos

        Raises:
            ValueError: Si faltan campos requeridos
            IntegrityError: Si el risk_number generado ya existe

        Example:
            >>> risk = await Risk.create(
            ...     db_session,
            ...     title="SQL Injection",
            ...     description="Critical vulnerability",
            ...     severity="critical",
            ...     likelihood="high",
            ...     impact_score=9.5,
            ...     category="technical"
            ... )
            >>> print(risk.risk_number)
            RISK-2026-001
        """
        # Si no se proporciona risk_number, generar uno automáticamente
        if risk_number is None:
            risk_number = await cls._generate_risk_number(db)

        # Establecer valores predeterminados si no se proporcionan
        if "status" not in kwargs:
            kwargs["status"] = RiskStatus.OPEN

        # Crear instancia del Risk
        risk = cls(risk_number=risk_number, **kwargs)

        # Guardar en base de datos
        db.add(risk)
        await db.commit()
        await db.refresh(risk)

        return risk

    @classmethod
    async def _generate_risk_number(cls, db: AsyncSession) -> str:
        """
        Genera un risk_number único con formato RISK-YYYY-NNN.

        Args:
            db: Sesión de base de datos async

        Returns:
            str: Risk number generado (ej: RISK-2026-001)

        Example:
            >>> number = await Risk._generate_risk_number(db_session)
            >>> print(number)
            RISK-2026-001
        """
        current_year = datetime.now().year

        # Obtener el último número secuencial del año actual
        result = await db.execute(
            select(func.max(cls.risk_number)).where(cls.risk_number.like(f"RISK-{current_year}-%"))
        )
        last_risk_number = result.scalar()

        if last_risk_number:
            # Extraer el número secuencial y incrementar
            last_sequence = int(last_risk_number.split("-")[2])
            next_sequence = last_sequence + 1
        else:
            # Primer riesgo del año
            next_sequence = 1

        # Formatear con padding de 3 dígitos
        return f"RISK-{current_year}-{next_sequence:03d}"

    @property
    def calculated_risk_score(self) -> float:
        """
        Calcula el risk score combinando likelihood e impact_score.

        Fórmula: likelihood_weight * impact_score

        Pesos de likelihood:
        - HIGH: 1.0 (100% probabilidad)
        - MEDIUM: 0.6 (60% probabilidad)
        - LOW: 0.3 (30% probabilidad)

        Returns:
            float: Risk score calculado (0.0-10.0)

        Example:
            >>> risk = Risk(
            ...     likelihood=RiskLikelihood.HIGH,
            ...     impact_score=10.0,
            ...     ...
            ... )
            >>> risk.calculated_risk_score
            10.0  # 1.0 * 10.0

            >>> risk.likelihood = RiskLikelihood.MEDIUM
            >>> risk.calculated_risk_score
            6.0  # 0.6 * 10.0
        """
        # Mapeo de likelihood a peso numérico
        likelihood_weights = {
            RiskLikelihood.HIGH: 1.0,
            RiskLikelihood.MEDIUM: 0.6,
            RiskLikelihood.LOW: 0.3,
        }

        weight = likelihood_weights.get(self.likelihood, 0.6)
        return round(weight * self.impact_score, 2)

    def is_overdue(self) -> bool:
        """
        Verifica si el riesgo está atrasado (deadline pasó).

        Un riesgo se considera atrasado si:
        1. Tiene un deadline definido
        2. El deadline ya pasó (< hoy)
        3. El status NO es 'mitigated' ni 'accepted'

        Returns:
            bool: True si está atrasado, False en caso contrario

        Example:
            >>> risk = Risk(
            ...     deadline=date(2020, 1, 1),  # Pasado
            ...     status=RiskStatus.OPEN,
            ...     ...
            ... )
            >>> risk.is_overdue()
            True

            >>> risk.status = RiskStatus.MITIGATED
            >>> risk.is_overdue()
            False  # Ya mitigado, no cuenta como atrasado
        """
        # Sin deadline, no puede estar atrasado
        if self.deadline is None:
            return False

        # Si ya fue mitigado o aceptado, no está atrasado
        if self.status in (RiskStatus.MITIGATED, RiskStatus.ACCEPTED):
            return False

        # Verificar si el deadline ya pasó
        today = date.today()
        return self.deadline < today

    # =========================================================================
    # Validadores
    # =========================================================================

    @validates("severity")
    def validate_severity(self, key: str, value: str | RiskSeverity) -> RiskSeverity:
        """
        Valida que severity sea un valor válido del enum.

        Args:
            key: Nombre del campo ('severity')
            value: Valor a validar

        Returns:
            RiskSeverity: Enum validado

        Raises:
            ValueError: Si el valor no es válido
        """
        if isinstance(value, RiskSeverity):
            return value

        try:
            return RiskSeverity(value)
        except ValueError:
            valid_values = [e.value for e in RiskSeverity]
            raise ValueError(
                f"Invalid severity '{value}'. Must be one of: {', '.join(valid_values)}"
            )

    @validates("likelihood")
    def validate_likelihood(self, key: str, value: str | RiskLikelihood) -> RiskLikelihood:
        """
        Valida que likelihood sea un valor válido del enum.

        Args:
            key: Nombre del campo ('likelihood')
            value: Valor a validar

        Returns:
            RiskLikelihood: Enum validado

        Raises:
            ValueError: Si el valor no es válido
        """
        if isinstance(value, RiskLikelihood):
            return value

        try:
            return RiskLikelihood(value)
        except ValueError:
            valid_values = [e.value for e in RiskLikelihood]
            raise ValueError(
                f"Invalid likelihood '{value}'. Must be one of: {', '.join(valid_values)}"
            )

    @validates("status")
    def validate_status(self, key: str, value: str | RiskStatus) -> RiskStatus:
        """
        Valida que status sea un valor válido del enum.

        Args:
            key: Nombre del campo ('status')
            value: Valor a validar

        Returns:
            RiskStatus: Enum validado

        Raises:
            ValueError: Si el valor no es válido
        """
        if isinstance(value, RiskStatus):
            return value

        try:
            return RiskStatus(value)
        except ValueError:
            valid_values = [e.value for e in RiskStatus]
            raise ValueError(f"Invalid status '{value}'. Must be one of: {', '.join(valid_values)}")

    @validates("category")
    def validate_category(self, key: str, value: str | RiskCategory) -> RiskCategory:
        """
        Valida que category sea un valor válido del enum.

        Args:
            key: Nombre del campo ('category')
            value: Valor a validar

        Returns:
            RiskCategory: Enum validado

        Raises:
            ValueError: Si el valor no es válido
        """
        if isinstance(value, RiskCategory):
            return value

        try:
            return RiskCategory(value)
        except ValueError:
            valid_values = [e.value for e in RiskCategory]
            raise ValueError(
                f"Invalid category '{value}'. Must be one of: {', '.join(valid_values)}"
            )
