"""
Shared Schemas - Pydantic Schemas Compartidos
=============================================

Schemas de Pydantic que son usados en múltiples partes de la aplicación.

Contenido esperado:
- PaginationParams  → Parámetros de paginación (page, limit)
- PaginatedResponse → Response genérico paginado
- HealthResponse    → Response de health check
- ErrorResponse     → Response de error estandarizado
- MessageResponse   → Response simple con mensaje

Ejemplo de uso:
    from app.shared.schemas import PaginatedResponse, ErrorResponse

    @router.get("/items", response_model=PaginatedResponse[ItemSchema])
    async def list_items(pagination: PaginationParams = Depends()):
        ...
"""
