"""
API Middleware - Middleware Personalizado
=========================================

Middleware de FastAPI para funcionalidad transversal.

Contenido esperado:
- logging.py     → Logging de requests/responses
- auth.py        → Verificación de autenticación
- rate_limit.py  → Rate limiting
- cors.py        → Configuración CORS
- error_handler.py → Manejo global de errores

Ejemplo de middleware:
    from starlette.middleware.base import BaseHTTPMiddleware

    class RequestLoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            start_time = time.time()
            response = await call_next(request)
            duration = time.time() - start_time
            logger.info(f"{request.method} {request.url.path} - {duration:.3f}s")
            return response
"""
