"""
Agents Module - Agentes de IA Especializados
============================================

Agentes de IA que realizan tareas específicas de seguridad.
Cada agente es un experto en su dominio.

Contenido:
- base_agent.py      → Clase base abstracta para todos los agentes
- orchestrator.py    → Orquestador que coordina múltiples agentes
- risk_agent.py      → Agente de evaluación de riesgos
- incident_agent.py  → Agente de respuesta a incidentes
- compliance_agent.py → Agente de compliance y auditoría
- threat_agent.py    → Agente de inteligencia de amenazas

Arquitectura:
- Todos los agentes heredan de BaseAgent
- El Orchestrator decide qué agente(s) usar
- Los agentes usan services/ para LLM, RAG, etc.
- Cada agente tiene su propio system prompt y tools

Ejemplo de uso:
    from app.agents.orchestrator import Orchestrator

    orchestrator = Orchestrator(llm_service, rag_service)
    response = await orchestrator.process_query(
        query="¿Cuáles son los riesgos críticos?",
        context=user_context
    )
"""
