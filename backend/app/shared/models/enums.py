"""
Risk-related Enums for the CISO Digital platform.

Este módulo define los Enums utilizados en el modelo Risk y otros
componentes relacionados con gestión de riesgos.
"""

from enum import Enum


class RiskSeverity(str, Enum):
    """
    Severidad del riesgo basada en su impacto potencial.

    Attributes:
        CRITICAL: Riesgo crítico que requiere atención inmediata
        HIGH: Riesgo alto que debe abordarse pronto
        MEDIUM: Riesgo medio que necesita planificación
        LOW: Riesgo bajo que puede monitorearse
    """

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskLikelihood(str, Enum):
    """
    Probabilidad de que el riesgo se materialice.

    Attributes:
        HIGH: Alta probabilidad de ocurrencia
        MEDIUM: Probabilidad media de ocurrencia
        LOW: Baja probabilidad de ocurrencia
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskStatus(str, Enum):
    """
    Estado del ciclo de vida del riesgo.

    Attributes:
        OPEN: Riesgo identificado pero no atendido
        IN_PROGRESS: Riesgo en proceso de mitigación
        MITIGATED: Riesgo mitigado exitosamente
        ACCEPTED: Riesgo aceptado por la organización
    """

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    MITIGATED = "mitigated"
    ACCEPTED = "accepted"


class RiskCategory(str, Enum):
    """
    Categoría del riesgo según su naturaleza.

    Attributes:
        TECHNICAL: Riesgos relacionados con tecnología
        OPERATIONAL: Riesgos operacionales del negocio
        COMPLIANCE: Riesgos de cumplimiento regulatorio
    """

    TECHNICAL = "technical"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
