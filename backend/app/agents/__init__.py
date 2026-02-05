"""
Agents Module - Agentes de IA Especializados (GitHub Copilot SDK)
=================================================================

Agentes de IA que realizan tareas específicas de seguridad usando
GitHub Copilot SDK (v0.1.21) como motor de IA principal.

AI Engine: github-copilot-sdk==0.1.21
Default Model: claude-sonnet-4.5 (multi-model support)

Contenido:
- base_agent.py      → Clase base abstracta para todos los agentes
- orchestrator.py    → Orquestador que coordina múltiples agentes
- risk_agent.py      → Agente de evaluación de riesgos
- incident_agent.py  → Agente de respuesta a incidentes
- compliance_agent.py → Agente de compliance y auditoría
- threat_agent.py    → Agente de inteligencia de amenazas
- tools/             → Herramientas (@define_tool) usadas por agentes

Arquitectura GitHub Copilot SDK:
--------------------------------
1. CopilotClient (Singleton en services/copilot_client_service.py)
   - Inicializado una vez con configuración global
   - Maneja autenticación (GITHUB_TOKEN auto-detectado)
   - Soporta múltiples modelos (GPT-4/5, Claude Sonnet 4.5)

2. Agent Sessions (Instancias por conversación)
   - Cada agente crea una sesión con create_agent()
   - Sesiones persistentes con auto-compactación de contexto
   - System prompts específicos por agente

3. Tools (@define_tool decorator)
   - Herramientas definidas en tools/ subdirectorio
   - Type-safe con Pydantic models
   - Registradas en agentes con session.add_tools()

4. Orchestrator (Multi-agent coordination)
   - Decide qué agente(s) usar según la query
   - Coordina múltiples agentes para tareas complejas
   - Mantiene contexto entre agentes

Tools Directory Structure:
-------------------------
tools/
├── __init__.py           → Exports y documentación
├── risk_tools.py         → @define_tool para riesgos
│   ├── get_critical_risks()
│   ├── calculate_risk_score()
│   └── search_similar_risks()
├── incident_tools.py     → @define_tool para incidentes
├── compliance_tools.py   → @define_tool para compliance
└── shared_tools.py       → Herramientas compartidas

Ejemplo de Tool Definition:
---------------------------
    from github_copilot_sdk import define_tool
    from pydantic import BaseModel, Field
    
    class GetCriticalRisksInput(BaseModel):
        limit: int = Field(default=10, description="Número máximo de riesgos")
        severity: str = Field(default="critical", description="Severidad mínima")
    
    @define_tool
    async def get_critical_risks(input: GetCriticalRisksInput) -> str:
        '''Obtiene los riesgos críticos del sistema.
        
        Retorna lista de riesgos con severidad >= especificada.
        Ordenados por score descendente.
        '''
        # Implementation...
        return json.dumps(risks)

Ejemplo de Agent Creation:
--------------------------
    from github_copilot_sdk import CopilotClient
    from app.agents.tools.risk_tools import (
        get_critical_risks,
        calculate_risk_score,
        search_similar_risks
    )
    
    class RiskAgent:
        def __init__(self, copilot_client: CopilotClient):
            self.session = copilot_client.create_agent(
                model="claude-sonnet-4.5",
                system_prompt='''Eres un experto en evaluación de riesgos...''',
                tools=[
                    get_critical_risks,
                    calculate_risk_score,
                    search_similar_risks
                ]
            )
        
        async def assess_risk(self, query: str) -> str:
            response = await self.session.send(query)
            return response.content

Ejemplo de uso del Orchestrator:
--------------------------------
    from app.agents.orchestrator import Orchestrator
    from app.services.copilot_client_service import get_copilot_client
    
    copilot_client = get_copilot_client()
    orchestrator = Orchestrator(copilot_client)
    
    response = await orchestrator.process_query(
        query="¿Cuáles son los riesgos críticos y cómo los mitigamos?",
        session_id="user-123-session-456"
    )

Ventajas de GitHub Copilot SDK:
-------------------------------
✅ Multi-model support (GPT-4/5, Claude, custom)
✅ Type-safe tools con Pydantic
✅ Infinite context (auto-compactación)
✅ Streaming responses
✅ Session persistence
✅ Mantenido por GitHub
✅ 80% del código backend existente NO cambia

Migración desde LLM directo:
----------------------------
❌ DEPRECATED: app/services/llm_service.py (remover)
✅ NUEVO: app/services/copilot_client_service.py (singleton)
✅ NUEVO: app/agents/tools/* (herramientas con @define_tool)
✅ MANTENER: Todos los services existentes (cache, vector_store, risk_calculator)
✅ MANTENER: Toda la API de riesgos (/api/v1/risks/*)

Referencias:
-----------
- GitHub Copilot SDK: https://github.com/github/copilot-sdk-python
- Documentación completa: docs/COPILOT_SDK_ANALYSIS.md
- Guía de desarrollo: AGENTS.md
"""
