"""
API Routes - FastAPI Routers
============================

Routers de FastAPI organizados por dominio funcional.

Cada archivo define un APIRouter que se monta en la app principal.

Convenciones:
- Prefijo de ruta en el router: /api/v1/{dominio}
- Tags para documentación OpenAPI
- Responses documentados con status codes
- Dependencias de autenticación donde aplique

Ejemplo de router:
    from fastapi import APIRouter, Depends
    from app.core.dependencies import get_current_user

    router = APIRouter(
        prefix="/api/v1/risks",
        tags=["risks"],
        dependencies=[Depends(get_current_user)]
    )

    @router.get("/")
    async def list_risks():
        ...
"""
