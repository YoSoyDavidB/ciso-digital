"""
Shared Module - Global Scope
============================

Este módulo contiene código compartido que puede ser usado
por cualquier parte de la aplicación.

Subcarpetas:
- models/      → SQLAlchemy base models y mixins
- schemas/     → Pydantic schemas compartidos (pagination, responses, etc.)
- utils/       → Funciones de utilidad generales
- exceptions/  → Excepciones personalizadas de la aplicación

Impacto de GitHub Copilot SDK:
------------------------------
✅ Este módulo NO cambia con la adopción de Copilot SDK
✅ Todos los modelos, schemas y utils permanecen iguales
✅ Puede ser usado por features/, agents/ y services/

Contenido Típico:

models/ (Base Models y Mixins)
------------------------------
- base.py           → Base class para todos los modelos
- mixins.py         → Timestamp, SoftDelete, etc.
- audit_mixin.py    → created_by, updated_by tracking

Ejemplo:
    class TimestampMixin:
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            server_default=func.now()
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now()
        )

schemas/ (Shared Schemas)
------------------------
- pagination.py     → PaginationParams, PaginatedResponse
- responses.py      → StandardResponse, ErrorResponse
- filters.py        → Common filter schemas

Ejemplo:
    class PaginatedResponse(BaseModel, Generic[T]):
        items: List[T]
        total: int
        page: int
        page_size: int
        total_pages: int

utils/ (Utility Functions)
--------------------------
- validators.py     → Custom validation functions
- formatters.py     → Date, string formatting
- crypto.py         → Encryption, hashing utilities
- json_utils.py     → JSON serialization helpers

Ejemplo:
    def validate_email(email: str) -> bool:
        pattern = r'^[\\w.\\-]+@[\\w.\\-]+\\.\\w+$'
        return re.match(pattern, email) is not None

exceptions/ (Custom Exceptions)
-------------------------------
- base.py           → BaseAppException
- not_found.py      → ResourceNotFoundError
- validation.py     → ValidationError
- auth.py           → AuthenticationError, AuthorizationError

Ejemplo:
    class ResourceNotFoundError(BaseAppException):
        def __init__(self, resource_type: str, resource_id: str):
            self.message = f"{resource_type} with ID {resource_id} not found"
            super().__init__(self.message)

Uso desde Agents (via Tools):
-----------------------------
Los agents pueden usar shared/ indirectamente:

    # En app/agents/tools/risk_tools.py
    from app.shared.exceptions import ResourceNotFoundError
    from app.shared.schemas.pagination import PaginationParams
    
    @define_tool
    async def get_paginated_risks(input: GetRisksInput) -> str:
        try:
            params = PaginationParams(
                page=input.page,
                page_size=input.page_size
            )
            risks = await risk_service.get_paginated(params)
            return json.dumps(risks.model_dump())
        except ResourceNotFoundError as e:
            return json.dumps({"error": str(e)})

Reglas:
------
✅ El código aquí NO debe importar de features/
✅ El código aquí NO debe importar de agents/
✅ El código aquí NO debe importar de api/
✅ Debe ser código genérico y reutilizable
✅ Cambios aquí pueden afectar a toda la aplicación
✅ Solo dependencias en: core/ y third-party packages

Dependency Graph:
----------------
    shared/          (nivel más bajo, sin deps internas)
      ↑
      ├── core/      (config, database)
      ↑
      ├── services/  (business logic helpers)
      ↑
      ├── features/  (domain logic)
      ↑
      ├── agents/    (AI agents y tools)
      ↑
      └── api/       (endpoints)

Testing:
-------
- Unit tests en tests/unit/shared/
- Debe tener alta cobertura (>90%)
- NO necesita mocks complejos (lógica simple)

Ejemplo de Test:
    def test_validate_email_with_valid_email():
        assert validate_email("user@example.com") is True
    
    def test_validate_email_with_invalid_email():
        assert validate_email("invalid-email") is False

Referencias:
-----------
- SQLAlchemy mixins: https://docs.sqlalchemy.org/en/20/orm/declarative_mixins.html
- Pydantic schemas: https://docs.pydantic.dev/
"""
