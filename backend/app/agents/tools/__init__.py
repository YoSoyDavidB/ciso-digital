"""
Agent Tools - Herramientas para Agentes de IA
=============================================

Herramientas (tools) que los agentes pueden usar para interactuar
con el sistema. Definidas usando el decorator @define_tool del
GitHub Copilot SDK.

Arquitectura de Tools:
----------------------
1. Cada tool es una función async decorada con @define_tool
2. Input: Pydantic model (type-safe parameters)
3. Output: string (JSON serializado para el LLM)
4. Docstring: Describe qué hace la tool (usado por el LLM)

Estructura de Tool:
------------------
    from github_copilot_sdk import define_tool
    from pydantic import BaseModel, Field
    
    class ToolNameInput(BaseModel):
        param1: str = Field(..., description="Descripción del parámetro")
        param2: int = Field(default=10, description="Parámetro opcional")
    
    @define_tool
    async def tool_name(input: ToolNameInput) -> str:
        '''Descripción corta de lo que hace la tool.
        
        Descripción detallada opcional.
        El LLM usa esto para decidir cuándo llamar la tool.
        '''
        # Implementation
        result = await some_service.do_something(input.param1, input.param2)
        return json.dumps(result)

Módulos de Tools:
----------------

risk_tools.py - Herramientas de Gestión de Riesgos
--------------------------------------------------
✅ get_critical_risks(limit, severity)
   - Obtiene riesgos críticos del sistema
   - Usa: app.features.risk_assessment.services.RiskService
   
✅ calculate_risk_score(vulnerabilities, asset_criticality)
   - Calcula score de riesgo basado en vulnerabilidades
   - Usa: app.services.risk_calculator.RiskCalculator
   
✅ search_similar_risks(risk_description)
   - Busca riesgos similares usando RAG
   - Usa: app.services.vector_store.VectorStoreService
   
✅ get_risk_by_id(risk_id)
   - Obtiene detalles completos de un riesgo específico
   
✅ create_risk(title, description, severity, affected_assets)
   - Crea un nuevo riesgo en el sistema
   
✅ update_risk_status(risk_id, new_status, notes)
   - Actualiza el estado de un riesgo existente

incident_tools.py - Herramientas de Incidentes
----------------------------------------------
🆕 get_active_incidents(severity, limit)
   - Obtiene incidentes activos
   
🆕 create_incident(title, severity, description, affected_systems)
   - Registra un nuevo incidente de seguridad
   
🆕 escalate_incident(incident_id, escalation_level, reason)
   - Escala un incidente a nivel superior
   
🆕 get_incident_timeline(incident_id)
   - Obtiene línea de tiempo de un incidente
   
🆕 add_incident_note(incident_id, note, author)
   - Añade nota a un incidente
   
🆕 close_incident(incident_id, resolution, lessons_learned)
   - Cierra un incidente con resolución

compliance_tools.py - Herramientas de Compliance
------------------------------------------------
🆕 check_iso27001_compliance(control_id)
   - Verifica cumplimiento de control ISO 27001
   
🆕 generate_compliance_report(framework, date_range)
   - Genera reporte de compliance
   
🆕 get_compliance_gaps(framework)
   - Identifica brechas de cumplimiento
   
🆕 get_evidence_for_control(control_id)
   - Obtiene evidencia para un control específico
   
🆕 schedule_audit(framework, date, auditor)
   - Programa una auditoría de compliance

shared_tools.py - Herramientas Compartidas
------------------------------------------
✅ search_documentation(query)
   - Busca en la documentación usando RAG
   - Usa: app.services.rag_service.RAGService
   
✅ get_asset_info(asset_id)
   - Obtiene información de un asset
   
✅ send_notification(recipient, message, priority)
   - Envía notificación al usuario
   
🆕 get_user_permissions(user_id)
   - Obtiene permisos de un usuario
   
🆕 log_security_event(event_type, description, severity)
   - Registra evento de seguridad en el sistema

Mejores Prácticas:
-----------------
✅ SIEMPRE usar async def (I/O operations)
✅ SIEMPRE retornar string (JSON.dumps() si es objeto/lista)
✅ SIEMPRE añadir docstring descriptivo
✅ SIEMPRE validar inputs con Pydantic
✅ SIEMPRE manejar excepciones y retornar mensajes claros
✅ NUNCA retornar objetos Python directamente (solo strings)
✅ NUNCA hacer operaciones bloqueantes sin async
✅ NUNCA exponer información sensible en los outputs

Ejemplo de Uso en Agent:
------------------------
    from github_copilot_sdk import CopilotClient
    from app.agents.tools.risk_tools import (
        get_critical_risks,
        calculate_risk_score
    )
    
    class RiskAgent:
        def __init__(self, copilot_client: CopilotClient):
            self.session = copilot_client.create_agent(
                model="claude-sonnet-4.5",
                system_prompt="Eres un experto en riesgos...",
                tools=[get_critical_risks, calculate_risk_score]
            )
        
        async def process(self, query: str):
            response = await self.session.send(query)
            return response.content

Manejo de Errores en Tools:
---------------------------
    @define_tool
    async def example_tool(input: ExampleInput) -> str:
        '''Tool de ejemplo con manejo de errores.'''
        try:
            result = await some_service.process(input.param)
            return json.dumps({"success": True, "data": result})
        
        except ValidationError as e:
            return json.dumps({
                "success": False,
                "error": "Invalid input",
                "details": str(e)
            })
        
        except Exception as e:
            logger.error(f"Error in example_tool: {e}", exc_info=True)
            return json.dumps({
                "success": False,
                "error": "Internal error",
                "message": "Please contact support"
            })

Testing Tools:
-------------
Tools deben tener tests unitarios en tests/unit/agents/tools/:

    @pytest.mark.asyncio
    async def test_get_critical_risks_returns_data(mock_risk_service):
        input_data = GetCriticalRisksInput(limit=5, severity="critical")
        result = await get_critical_risks(input_data)
        
        data = json.loads(result)
        assert data["success"] is True
        assert len(data["risks"]) <= 5
        assert all(r["severity"] == "critical" for r in data["risks"])

Implementación por Fases:
-------------------------
Phase 1 (MVP - 3-5h):
  ✅ risk_tools.py (3 tools básicas)
  ✅ shared_tools.py (search_documentation)

Phase 2 (Specialized Agents - 4-5h):
  🆕 incident_tools.py (completo)
  🆕 compliance_tools.py (básico)
  ✅ Expandir risk_tools.py

Phase 3 (Production Ready - 3-4h):
  🆕 compliance_tools.py (completo)
  🆕 threat_intel_tools.py
  🆕 asset_tools.py

Referencias:
-----------
- GitHub Copilot SDK Tools: https://github.com/github/copilot-sdk-python#tools
- Pydantic Validation: https://docs.pydantic.dev/
- Guía completa: docs/COPILOT_SDK_ANALYSIS.md
"""
