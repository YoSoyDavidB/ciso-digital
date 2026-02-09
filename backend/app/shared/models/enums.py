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


# ============================================================================
# INCIDENT RESPONSE ENUMS
# ============================================================================

class IncidentType(str, Enum):
    """
    Tipos de incidentes de seguridad siguiendo categorías NIST CSF.

    Attributes:
        MALWARE: Infección por software malicioso
        PHISHING: Intento de phishing o ingeniería social
        DATA_BREACH: Filtración o acceso no autorizado a datos
        DDOS: Ataque de denegación de servicio distribuido
        UNAUTHORIZED_ACCESS: Acceso no autorizado a sistemas
        INSIDER_THREAT: Amenaza interna por empleado o contratista
        RANSOMWARE: Ataque de ransomware o cifrado de datos
        UNKNOWN: Tipo de incidente aún no clasificado
        OTHER: Otro tipo de incidente no categorizado
    """

    MALWARE = "malware"
    PHISHING = "phishing"
    DATA_BREACH = "data_breach"
    DDOS = "ddos"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    INSIDER_THREAT = "insider_threat"
    RANSOMWARE = "ransomware"
    UNKNOWN = "unknown"
    OTHER = "other"


class IncidentSeverity(str, Enum):
    """
    Niveles de severidad para incidentes de seguridad.

    Attributes:
        CRITICAL: Amenaza inmediata a operaciones críticas, requiere respuesta inmediata
        HIGH: Impacto significativo, sistemas productivos afectados
        MEDIUM: Impacto limitado, sistemas no críticos, amenaza contenida
        LOW: Impacto mínimo, actividad sospechosa, potencial falso positivo
    """

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentStatus(str, Enum):
    """
    Estados del ciclo de vida de un incidente siguiendo NIST SP 800-61.

    El flujo típico es:
    DETECTED → INVESTIGATING → CONTAINED → ERADICATED → RECOVERED → CLOSED

    Attributes:
        DETECTED: Incidente detectado inicialmente
        INVESTIGATING: Bajo investigación para determinar alcance
        CONTAINED: Amenaza contenida, daño limitado
        ERADICATED: Amenaza erradicada del entorno
        RECOVERED: Sistemas restaurados a operación normal
        CLOSED: Incidente cerrado con análisis post-mortem completo
    """

    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    ERADICATED = "eradicated"
    RECOVERED = "recovered"
    CLOSED = "closed"
