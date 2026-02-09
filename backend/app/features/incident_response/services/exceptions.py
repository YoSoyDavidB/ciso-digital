"""
Custom exceptions for Incident Response service.

Define excepciones específicas para el servicio de incidentes,
facilitando el manejo de errores y debugging.
"""


class IncidentServiceError(Exception):
    """Base exception para errores del servicio de incidentes."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class IncidentNotFoundError(IncidentServiceError):
    """Excepción cuando un incidente no se encuentra."""

    def __init__(self, incident_id: str):
        super().__init__(
            f"Incident not found: {incident_id}",
            {"incident_id": incident_id}
        )


class InvalidIncidentDataError(IncidentServiceError):
    """Excepción cuando los datos del incidente son inválidos."""

    def __init__(self, message: str, field: str = None):
        details = {"field": field} if field else {}
        super().__init__(message, details)


class IncidentStateError(IncidentServiceError):
    """Excepción cuando hay un error en transición de estado."""

    def __init__(self, current_status: str, target_status: str, reason: str):
        super().__init__(
            f"Cannot transition from {current_status} to {target_status}: {reason}",
            {
                "current_status": current_status,
                "target_status": target_status,
                "reason": reason
            }
        )


class DatabaseOperationError(IncidentServiceError):
    """Excepción para errores de operaciones de base de datos."""

    def __init__(self, operation: str, original_error: Exception = None):
        super().__init__(
            f"Database operation failed: {operation}",
            {
                "operation": operation,
                "original_error": str(original_error) if original_error else None
            }
        )
        self.original_error = original_error
