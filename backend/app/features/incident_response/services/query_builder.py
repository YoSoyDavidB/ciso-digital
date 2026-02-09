"""
Query Builder helpers for Incident Service.

Proporciona funciones helper para construir queries de SQLAlchemy
de manera consistente y reutilizable.
"""

from typing import Any, Dict, List
from sqlalchemy import Select, and_, select
from sqlalchemy.sql.expression import ColumnElement

from app.features.incident_response.models.incident import Incident
from app.shared.models.enums import IncidentSeverity, IncidentStatus, IncidentType


class IncidentQueryBuilder:
    """
    Builder para queries de incidentes.
    
    Facilita la construcción de queries complejas con filtros
    de manera consistente y type-safe.
    """
    
    def __init__(self):
        """Inicializa el builder con una query base."""
        self._query: Select = select(Incident)
        self._conditions: List[ColumnElement] = []
    
    def filter_by_severity(self, severity: IncidentSeverity) -> "IncidentQueryBuilder":
        """
        Filtra por severidad.
        
        Args:
            severity: Nivel de severidad
            
        Returns:
            Self para method chaining
        """
        self._conditions.append(Incident.severity == severity)
        return self
    
    def filter_by_status(self, status: IncidentStatus) -> "IncidentQueryBuilder":
        """
        Filtra por estado.
        
        Args:
            status: Estado del incidente
            
        Returns:
            Self para method chaining
        """
        self._conditions.append(Incident.status == status)
        return self
    
    def filter_by_type(self, incident_type: IncidentType) -> "IncidentQueryBuilder":
        """
        Filtra por tipo de incidente.
        
        Args:
            incident_type: Tipo de incidente
            
        Returns:
            Self para method chaining
        """
        self._conditions.append(Incident.incident_type == incident_type)
        return self
    
    def filter_by_assigned_to(self, assigned_to: str) -> "IncidentQueryBuilder":
        """
        Filtra por usuario asignado.
        
        Args:
            assigned_to: Email del usuario asignado
            
        Returns:
            Self para method chaining
        """
        self._conditions.append(Incident.assigned_to == assigned_to)
        return self
    
    def apply_filters(self, filters: Dict[str, Any]) -> "IncidentQueryBuilder":
        """
        Aplica múltiples filtros desde un diccionario.
        
        Args:
            filters: Diccionario de filtros soportados:
                - severity: IncidentSeverity
                - status: IncidentStatus
                - incident_type: IncidentType
                - assigned_to: str
                
        Returns:
            Self para method chaining
            
        Example:
            >>> builder = IncidentQueryBuilder()
            >>> builder.apply_filters({
            ...     "severity": IncidentSeverity.CRITICAL,
            ...     "status": IncidentStatus.INVESTIGATING
            ... })
        """
        if "severity" in filters:
            self.filter_by_severity(filters["severity"])
        
        if "status" in filters:
            self.filter_by_status(filters["status"])
        
        if "incident_type" in filters:
            self.filter_by_type(filters["incident_type"])
        
        if "assigned_to" in filters:
            self.filter_by_assigned_to(filters["assigned_to"])
        
        return self
    
    def order_by_detected_at(self, desc: bool = True) -> "IncidentQueryBuilder":
        """
        Ordena por fecha de detección.
        
        Args:
            desc: Si True, orden descendente (más recientes primero)
            
        Returns:
            Self para method chaining
        """
        if desc:
            self._query = self._query.order_by(Incident.detected_at.desc())
        else:
            self._query = self._query.order_by(Incident.detected_at.asc())
        return self
    
    def paginate(self, limit: int, offset: int) -> "IncidentQueryBuilder":
        """
        Aplica paginación.
        
        Args:
            limit: Número máximo de resultados
            offset: Número de resultados a saltar
            
        Returns:
            Self para method chaining
        """
        self._query = self._query.limit(limit).offset(offset)
        return self
    
    def build(self) -> Select:
        """
        Construye y retorna la query final.
        
        Returns:
            Select: Query de SQLAlchemy lista para ejecutar
        """
        if self._conditions:
            self._query = self._query.where(and_(*self._conditions))
        
        return self._query
    
    @staticmethod
    def create_base_query() -> Select:
        """
        Crea una query base simple.
        
        Returns:
            Select: Query base de Incident
        """
        return select(Incident)


def build_incident_list_query(
    filters: Dict[str, Any],
    limit: int = 20,
    offset: int = 0,
) -> Select:
    """
    Helper function para construir query de listado de incidentes.
    
    Args:
        filters: Diccionario de filtros
        limit: Límite de resultados
        offset: Offset para paginación
        
    Returns:
        Select: Query construida
        
    Example:
        >>> query = build_incident_list_query(
        ...     filters={"severity": IncidentSeverity.CRITICAL},
        ...     limit=10,
        ...     offset=0
        ... )
        >>> result = await session.execute(query)
    """
    return (
        IncidentQueryBuilder()
        .apply_filters(filters)
        .order_by_detected_at(desc=True)
        .paginate(limit, offset)
        .build()
    )
