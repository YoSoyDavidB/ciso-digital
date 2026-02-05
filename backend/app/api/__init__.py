"""
API Module - Endpoints REST
===========================

Módulo que contiene todos los endpoints de la API REST
y middleware de la aplicación.

Subcarpetas:
- routes/     → Routers de FastAPI organizados por dominio
- middleware/ → Middleware personalizado (auth, logging, etc.)

Contenido de routes/:
✅ health.py    → Health check y readiness (IMPLEMENTADO)
✅ risks.py     → Gestión de riesgos (IMPLEMENTADO - 139 tests passing)
🆕 auth.py      → Autenticación (login, logout, refresh)
🆕 users.py     → Gestión de usuarios
🆕 chat.py      → Chat con agentes de IA (GitHub Copilot SDK)
🆕 incidents.py → Gestión de incidentes
🆕 compliance.py → Gestión de compliance

GitHub Copilot SDK Integration:
-------------------------------
El nuevo endpoint chat.py integra los agentes de IA:

Endpoints de Chat:
- POST /api/v1/chat              → Mensaje simple al orchestrator
- POST /api/v1/chat/stream       → Streaming de respuesta
- GET /api/v1/chat/sessions      → Lista sesiones del usuario
- GET /api/v1/chat/sessions/{id} → Historial de una sesión
- DELETE /api/v1/chat/sessions/{id} → Eliminar sesión

Ejemplo de implementación:
    # app/api/routes/chat.py
    from fastapi import APIRouter, Depends
    from app.services.copilot_client_service import get_copilot_client
    from app.agents.orchestrator import Orchestrator
    
    router = APIRouter(prefix="/chat", tags=["chat"])
    
    @router.post("/")
    async def chat(
        message: ChatMessage,
        copilot_client = Depends(get_copilot_client)
    ):
        orchestrator = Orchestrator(copilot_client)
        response = await orchestrator.process_query(
            query=message.content,
            session_id=message.session_id
        )
        return {"response": response}

Flujo de Request:
----------------
1. User → POST /api/v1/chat {"message": "¿Riesgos críticos?"}
2. Router → Valida request (Pydantic)
3. Router → Obtiene CopilotClient (Depends)
4. Router → Llama Orchestrator.process_query()
5. Orchestrator → Decide usar RiskAgent
6. RiskAgent → Usa tool get_critical_risks
7. Tool → Llama RiskService.get_risks()
8. Response → JSON al usuario

Streaming Response:
------------------
    from fastapi.responses import StreamingResponse
    
    @router.post("/stream")
    async def chat_stream(message: ChatMessage):
        async def generate():
            async for chunk in orchestrator.stream_response(message):
                yield f"data: {chunk}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")

Integración con Features:
-------------------------
Los endpoints REST tradicionales (risks.py, incidents.py) NO cambian:

✅ /api/v1/risks/       → Sigue funcionando igual (RiskService directo)
✅ /api/v1/incidents/   → Lógica de negocio directa
🆕 /api/v1/chat         → Nueva funcionalidad (IA agents)

Ambos tipos de endpoints coexisten:
- REST tradicional: CRUD directo (para UIs, scripts, integraciones)
- Chat: Interacción conversacional con IA (para usuarios finales)

Principios:
----------
✅ Routers delgados: solo validación y llamada a services
✅ Documentación OpenAPI completa
✅ Manejo consistente de errores
✅ Respuestas estandarizadas
✅ Dependency injection para services
✅ Autenticación y autorización en middleware

Ejemplo de Router Delgado (NO cambia con Copilot SDK):
------------------------------------------------------
    @router.post("/risks/", response_model=RiskResponse)
    async def create_risk(
        risk_data: RiskCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        '''Crea un nuevo riesgo (endpoint REST tradicional).'''
        risk_service = RiskService(db)
        risk = await risk_service.create_risk(risk_data, current_user.id)
        return risk

Error Handling:
--------------
    from fastapi import HTTPException
    
    try:
        result = await service.do_something()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Resource not found")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

Testing:
-------
- Integration tests en tests/integration/test_api/
- Ejemplo: tests/integration/test_api/test_risk_endpoints.py
- Mock de dependencies (CopilotClient, Database, etc.)

Referencias:
-----------
- FastAPI docs: https://fastapi.tiangolo.com/
- Análisis Copilot SDK: docs/COPILOT_SDK_ANALYSIS.md
"""
