"""
Incident Response CRUD Service.

Este servicio proporciona operaciones CRUD y lógica de negocio para
gestión de incidentes de seguridad.

Responsabilidades:
- CRUD básico (Create, Read, Update, Delete)
- Generación automática de incident_number
- Actualización de estados con timestamps automáticos
- Gestión de acciones ejecutadas (JSON)
- Generación de timeline de eventos
- Cálculo de estadísticas y métricas (MTTR, etc.)
"""

import structlog
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import attributes

from app.features.incident_response.models.incident import Incident
from app.features.incident_response.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
)
from app.features.incident_response.services.exceptions import (
    DatabaseOperationError,
    IncidentNotFoundError,
    InvalidIncidentDataError,
)
from app.features.incident_response.services.query_builder import (
    build_incident_list_query,
)
from app.shared.models.enums import IncidentSeverity, IncidentStatus, IncidentType

logger = structlog.get_logger(__name__)


class IncidentService:
    """
    Servicio CRUD para gestión de incidentes de seguridad.

    Proporciona métodos para crear, leer, actualizar y eliminar incidentes,
    así como operaciones especializadas como actualización de estado,
    registro de acciones, generación de timeline y cálculo de estadísticas.

    Attributes:
        db: SQLAlchemy AsyncSession para operaciones de base de datos

    Example:
        >>> async with get_async_session_local()() as session:
        ...     service = IncidentService(session)
        ...     incident = await service.create(incident_data, "user@example.com")
    """

    def __init__(self, db: AsyncSession):
        """
        Inicializa el servicio con una sesión de base de datos.

        Args:
            db: SQLAlchemy AsyncSession
        """
        self.db = db

    @asynccontextmanager
    async def _transaction(self):
        """
        Context manager para transacciones con rollback automático.

        Yields:
            AsyncSession: Sesión de base de datos

        Raises:
            DatabaseOperationError: Si la operación falla
        """
        try:
            yield self.db
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error("database_transaction_failed", error=str(e))
            raise DatabaseOperationError("Transaction failed", e)
        except Exception as e:
            await self.db.rollback()
            logger.error("unexpected_error_in_transaction", error=str(e))
            raise

    async def _commit_and_refresh(self, instance: Incident) -> Incident:
        """
        Helper para commit y refresh de una instancia.

        Args:
            instance: Instancia de Incident

        Returns:
            Incident: Instancia refreshed

        Raises:
            DatabaseOperationError: Si falla el commit
        """
        try:
            await self.db.commit()
            await self.db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error("commit_failed", error=str(e))
            raise DatabaseOperationError("Commit operation failed", e)

    async def create(
        self,
        incident_data: IncidentCreate,
        created_by: str,
    ) -> Incident:
        """
        Crea un nuevo incidente en la base de datos.

        El incident_number se genera automáticamente si no se proporciona.
        El estado inicial es DETECTED.

        Args:
            incident_data: Datos del incidente validados por Pydantic
            created_by: Email del usuario que crea el incidente

        Returns:
            Incident: Incidente creado con ID y timestamps generados

        Raises:
            DatabaseOperationError: Si falla la creación
            InvalidIncidentDataError: Si los datos son inválidos

        Example:
            >>> incident_data = IncidentCreate(
            ...     title="Ransomware Attack",
            ...     description="...",
            ...     incident_type=IncidentType.RANSOMWARE,
            ...     severity=IncidentSeverity.CRITICAL,
            ...     detected_at=datetime.now(timezone.utc)
            ... )
            >>> incident = await service.create(incident_data, "admin@example.com")
            >>> print(incident.incident_number)  # INC-2026-...
        """
        try:
            # Convertir schema a dict
            incident_dict = incident_data.model_dump()

            # Crear modelo SQLAlchemy
            incident = Incident(**incident_dict)

            # El incident_number se genera automáticamente via database event
            # (ver incident.py: @event.listens_for(Incident, "before_insert"))

            # Agregar a sesión y commit
            self.db.add(incident)
            incident = await self._commit_and_refresh(incident)

            logger.info(
                "incident_created",
                incident_id=str(incident.id),
                incident_number=incident.incident_number,
                severity=incident.severity.value,
                created_by=created_by,
            )

            return incident

        except DatabaseOperationError:
            raise
        except ValueError as e:
            logger.warning("invalid_incident_data", error=str(e))
            raise InvalidIncidentDataError(str(e))
        except Exception as e:
            logger.error("incident_creation_failed", error=str(e))
            raise DatabaseOperationError("Failed to create incident", e)

    async def get_by_id(self, incident_id: str) -> Optional[Incident]:
        """
        Obtiene un incidente por su UUID.

        Args:
            incident_id: UUID del incidente como string

        Returns:
            Optional[Incident]: Incidente si existe, None en caso contrario

        Raises:
            InvalidIncidentDataError: Si el UUID es inválido

        Example:
            >>> incident = await service.get_by_id("550e8400-e29b-41d4-a716-446655440000")
            >>> if incident:
            ...     print(f"Found: {incident.title}")
        """
        try:
            incident_uuid = UUID(incident_id)
        except (ValueError, AttributeError) as e:
            logger.warning("invalid_incident_uuid", incident_id=incident_id, error=str(e))
            raise InvalidIncidentDataError(
                f"Invalid incident ID format: {incident_id}",
                field="incident_id"
            )

        try:
            result = await self.db.execute(
                select(Incident).where(Incident.id == incident_uuid)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error("database_query_failed", error=str(e))
            raise DatabaseOperationError("Failed to fetch incident", e)

    async def get_by_incident_number(
        self, incident_number: str
    ) -> Optional[Incident]:
        """
        Obtiene un incidente por su número único.

        Args:
            incident_number: Número de incidente (e.g., "INC-2026-001")

        Returns:
            Optional[Incident]: Incidente si existe, None en caso contrario

        Example:
            >>> incident = await service.get_by_incident_number("INC-2026-001")
        """
        result = await self.db.execute(
            select(Incident).where(Incident.incident_number == incident_number)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        filters: Dict[str, Any],
        limit: int = 20,
        offset: int = 0,
    ) -> List[Incident]:
        """
        Lista incidentes con filtros opcionales.

        Args:
            filters: Diccionario de filtros. Soporta:
                - severity: IncidentSeverity (e.g., IncidentSeverity.CRITICAL)
                - status: IncidentStatus (e.g., IncidentStatus.INVESTIGATING)
                - incident_type: IncidentType
                - assigned_to: str (email)
            limit: Número máximo de resultados (default: 20)
            offset: Número de resultados a saltar (default: 0)

        Returns:
            List[Incident]: Lista de incidentes ordenados por detected_at DESC

        Raises:
            DatabaseOperationError: Si falla la query

        Example:
            >>> incidents = await service.list(
            ...     filters={"severity": IncidentSeverity.CRITICAL},
            ...     limit=10,
            ...     offset=0
            ... )
        """
        try:
            # Usar query builder para construir query
            query = build_incident_list_query(filters, limit, offset)

            # Ejecutar query
            result = await self.db.execute(query)
            return list(result.scalars().all())

        except SQLAlchemyError as e:
            logger.error("incident_list_query_failed", error=str(e), filters=filters)
            raise DatabaseOperationError("Failed to list incidents", e)

    async def update(
        self,
        incident_id: str,
        incident_data: IncidentUpdate,
    ) -> Optional[Incident]:
        """
        Actualiza un incidente existente.

        Solo actualiza los campos proporcionados (actualización parcial).

        Args:
            incident_id: UUID del incidente
            incident_data: Datos a actualizar (campos opcionales)

        Returns:
            Optional[Incident]: Incidente actualizado, None si no existe

        Raises:
            IncidentNotFoundError: Si el incidente no existe
            DatabaseOperationError: Si falla la actualización

        Example:
            >>> update_data = IncidentUpdate(
            ...     status=IncidentStatus.CONTAINED,
            ...     contained_at=datetime.now(timezone.utc)
            ... )
            >>> incident = await service.update(incident_id, update_data)
        """
        try:
            incident = await self.get_by_id(incident_id)
            if not incident:
                raise IncidentNotFoundError(incident_id)

            # Actualizar solo campos no-None
            update_dict = incident_data.model_dump(exclude_unset=True)

            for field, value in update_dict.items():
                setattr(incident, field, value)
            
            # Manually update updated_at for SQLite compatibility
            from datetime import datetime, timezone
            incident.updated_at = datetime.now(timezone.utc)

            incident = await self._commit_and_refresh(incident)

            logger.info(
                "incident_updated",
                incident_id=incident_id,
                incident_number=incident.incident_number,
                updated_fields=list(update_dict.keys()),
            )

            return incident

        except (IncidentNotFoundError, DatabaseOperationError):
            raise
        except Exception as e:
            logger.error("incident_update_failed", incident_id=incident_id, error=str(e))
            raise DatabaseOperationError("Failed to update incident", e)

    async def update_status(
        self,
        incident_id: str,
        new_status: IncidentStatus,
        updated_by: str,
    ) -> Optional[Incident]:
        """
        Actualiza el estado de un incidente y establece timestamps automáticamente.

        Si el nuevo estado es CONTAINED, establece contained_at.
        Si el nuevo estado es CLOSED, establece resolved_at.

        Args:
            incident_id: UUID del incidente
            new_status: Nuevo estado del incidente
            updated_by: Email del usuario que actualiza

        Returns:
            Optional[Incident]: Incidente actualizado, None si no existe

        Raises:
            IncidentNotFoundError: Si el incidente no existe
            DatabaseOperationError: Si falla la actualización

        Example:
            >>> incident = await service.update_status(
            ...     incident_id,
            ...     IncidentStatus.CONTAINED,
            ...     "responder@example.com"
            ... )
        """
        try:
            incident = await self.get_by_id(incident_id)
            if not incident:
                raise IncidentNotFoundError(incident_id)

            old_status = incident.status
            incident.status = new_status

            # Establecer timestamps automáticamente según el estado
            now = datetime.now(timezone.utc)

            if new_status == IncidentStatus.CONTAINED and not incident.contained_at:
                incident.contained_at = now

            if new_status == IncidentStatus.CLOSED and not incident.resolved_at:
                incident.resolved_at = now

            incident = await self._commit_and_refresh(incident)

            logger.info(
                "incident_status_updated",
                incident_id=incident_id,
                incident_number=incident.incident_number,
                old_status=old_status.value,
                new_status=new_status.value,
                updated_by=updated_by,
            )

            return incident

        except (IncidentNotFoundError, DatabaseOperationError):
            raise
        except Exception as e:
            logger.error("status_update_failed", incident_id=incident_id, error=str(e))
            raise DatabaseOperationError("Failed to update incident status", e)

    async def add_action_taken(
        self,
        incident_id: str,
        action: Dict[str, Any],
    ) -> Optional[Incident]:
        """
        Agrega una acción ejecutada al incidente.

        Las acciones se almacenan en el campo JSON actions_taken.
        La nueva acción se AGREGA (append) a las existentes.

        Args:
            incident_id: UUID del incidente
            action: Diccionario con datos de la acción:
                - timestamp: ISO datetime
                - action: Nombre de la acción
                - description: Descripción
                - status: Estado (completed, failed, etc.)
                - performed_by: Quién ejecutó la acción

        Returns:
            Optional[Incident]: Incidente actualizado, None si no existe

        Raises:
            IncidentNotFoundError: Si el incidente no existe
            DatabaseOperationError: Si falla la actualización

        Example:
            >>> action = {
            ...     "timestamp": datetime.now(timezone.utc).isoformat(),
            ...     "action": "isolated_system",
            ...     "description": "Isolated compromised server",
            ...     "status": "completed",
            ...     "performed_by": "security-team@example.com"
            ... }
            >>> incident = await service.add_action_taken(incident_id, action)
        """
        try:
            incident = await self.get_by_id(incident_id)
            if not incident:
                raise IncidentNotFoundError(incident_id)

            # Inicializar actions_taken si es None
            if incident.actions_taken is None:
                incident.actions_taken = []

            # Agregar nueva acción
            incident.actions_taken.append(action)

            # IMPORTANTE: Marcar el atributo como modificado para que SQLAlchemy
            # detecte el cambio en el campo JSON
            attributes.flag_modified(incident, "actions_taken")

            incident = await self._commit_and_refresh(incident)

            logger.info(
                "action_added_to_incident",
                incident_id=incident_id,
                incident_number=incident.incident_number,
                action=action.get("action"),
                performed_by=action.get("performed_by"),
            )

            return incident

        except (IncidentNotFoundError, DatabaseOperationError):
            raise
        except Exception as e:
            logger.error("add_action_failed", incident_id=incident_id, error=str(e))
            raise DatabaseOperationError("Failed to add action to incident", e)

    async def get_timeline(self, incident_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene la línea de tiempo completa del incidente.

        Genera una lista ordenada cronológicamente de todos los eventos
        importantes: detección, reporte, contención, resolución, y acciones ejecutadas.

        Args:
            incident_id: UUID del incidente

        Returns:
            List[Dict[str, Any]]: Lista de eventos ordenados por timestamp ASC
                Cada evento contiene: timestamp, event, status, description

        Raises:
            IncidentNotFoundError: Si el incidente no existe
            DatabaseOperationError: Si falla la query

        Example:
            >>> timeline = await service.get_timeline(incident_id)
            >>> for event in timeline:
            ...     print(f"{event['timestamp']}: {event['event']}")
        """
        try:
            incident = await self.get_by_id(incident_id)
            if not incident:
                raise IncidentNotFoundError(incident_id)

            # Usar el método del modelo para generar timeline
            timeline = incident.get_timeline()

            return timeline

        except (IncidentNotFoundError, DatabaseOperationError):
            raise
        except Exception as e:
            logger.error("get_timeline_failed", incident_id=incident_id, error=str(e))
            raise DatabaseOperationError("Failed to get incident timeline", e)

    async def get_statistics(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """
        Calcula estadísticas de incidentes en un rango de fechas.

        Incluye:
        - total_incidents: Total de incidentes detectados
        - resolved_incidents: Incidentes resueltos (status = CLOSED)
        - mttr_hours: Mean Time To Resolve en horas
        - by_severity: Distribución por severidad
        - by_type: Distribución por tipo

        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango

        Returns:
            Dict[str, Any]: Diccionario con estadísticas

        Raises:
            DatabaseOperationError: Si falla la query

        Example:
            >>> stats = await service.get_statistics(
            ...     start_date=datetime.now(timezone.utc) - timedelta(days=30),
            ...     end_date=datetime.now(timezone.utc)
            ... )
            >>> print(f"MTTR: {stats['mttr_hours']:.2f} hours")
        """
        try:
            # Query base: incidentes en el rango de fechas
            conditions = []
            if start_date is not None:
                conditions.append(Incident.detected_at >= start_date)
            if end_date is not None:
                conditions.append(Incident.detected_at <= end_date)
            
            if conditions:
                base_query = select(Incident).where(and_(*conditions))
            else:
                base_query = select(Incident)

            # Total de incidentes
            result = await self.db.execute(base_query)
            all_incidents = list(result.scalars().all())
            total_incidents = len(all_incidents)

            # Incidentes resueltos
            resolved_incidents = [
                inc for inc in all_incidents if inc.status == IncidentStatus.CLOSED
            ]
            resolved_count = len(resolved_incidents)

            # Calcular MTTR (Mean Time To Resolve) en horas
            mttr_hours = self._calculate_mttr(resolved_incidents)

            # Distribución por severidad
            by_severity = self._calculate_severity_distribution(all_incidents)

            # Distribución por tipo
            by_type = self._calculate_type_distribution(all_incidents)

            return {
                "total_incidents": total_incidents,
                "resolved_incidents": resolved_count,
                "mttr_hours": mttr_hours,
                "by_severity": by_severity,
                "by_type": by_type,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            }

        except SQLAlchemyError as e:
            logger.error("statistics_query_failed", error=str(e))
            raise DatabaseOperationError("Failed to get incident statistics", e)

    def _calculate_mttr(self, resolved_incidents: List[Incident]) -> float:
        """
        Calcula Mean Time To Resolve en horas.

        Args:
            resolved_incidents: Lista de incidentes resueltos

        Returns:
            float: MTTR en horas, 0.0 si no hay incidentes
        """
        if not resolved_incidents:
            return 0.0

        resolution_times = []
        for incident in resolved_incidents:
            res_time = incident.calculate_resolution_time()
            if res_time:
                resolution_times.append(res_time.total_seconds() / 3600)

        return sum(resolution_times) / len(resolution_times) if resolution_times else 0.0

    def _calculate_severity_distribution(
        self, incidents: List[Incident]
    ) -> Dict[str, int]:
        """
        Calcula distribución de incidentes por severidad.

        Args:
            incidents: Lista de incidentes

        Returns:
            Dict[str, int]: Diccionario con conteo por severidad
        """
        distribution = {}
        for severity in IncidentSeverity:
            count = len([inc for inc in incidents if inc.severity == severity])
            distribution[severity.value] = count

        return distribution

    def _calculate_type_distribution(
        self, incidents: List[Incident]
    ) -> Dict[str, int]:
        """
        Calcula distribución de incidentes por tipo.

        Args:
            incidents: Lista de incidentes

        Returns:
            Dict[str, int]: Diccionario con conteo por tipo
        """
        distribution = {}
        for inc_type in IncidentType:
            count = len([inc for inc in incidents if inc.incident_type == inc_type])
            distribution[inc_type.value] = count

        return distribution
