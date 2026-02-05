"""
Services Module - Servicios de Infraestructura
==============================================

Servicios que proveen funcionalidad de infraestructura
y conexión con sistemas externos.

⚡ ARQUITECTURA ACTUALIZADA CON GITHUB COPILOT SDK 0.1.21 ⚡

Servicios Actuales:
-------------------
✅ cache_service.py         → Caching con Redis (@cached decorator)
✅ vector_store.py          → Qdrant vector store client
✅ risk_calculator.py       → Risk score calculation (usado como tool)

🆕 NUEVOS con Copilot SDK:
---------------------------
📦 copilot_client_service.py → GitHub Copilot SDK wrapper (PRÓXIMO)
                                Cliente singleton para Copilot CLI
                                Multi-modelo: GPT-4/5, Claude Sonnet 4.5
                                Auto-detecta GITHUB_TOKEN
                                
📦 embedding_service.py      → Embeddings via Copilot SDK (PRÓXIMO)
📦 rag_service.py            → RAG service actualizado (FUTURO)

⚠️ DEPRECADOS:
--------------
❌ llm_service.py            → REEMPLAZADO por copilot_client_service.py
                               Eliminar después de migración completa

Arquitectura de Servicios con Copilot SDK:
-------------------------------------------

┌─────────────────────────────────────────────────────┐
│         GitHub Copilot SDK (Motor Principal)        │
│  ┌───────────────────────────────────────────────┐  │
│  │  CopilotClient (Singleton)                    │  │
│  │  • Multi-modelo (GPT-4/5, Claude Sonnet)      │  │
│  │  • Session management                         │  │
│  │  • Infinite context (auto-compaction)         │  │
│  │  • Streaming responses                        │  │
│  │  • Custom tools integration                   │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│              Infrastructure Services                 │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────┐ │
│  │ RAG Service  │  │ Cache Service │  │ Vector   │ │
│  │ (Qdrant)     │  │ (Redis)       │  │ Store    │ │
│  └──────────────┘  └───────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│          Custom Tools (@define_tool)                 │
│  • assess_risk()                                     │
│  • list_risks()                                      │
│  • search_documents() (RAG)                          │
│  • calculate_compliance_score()                      │
└─────────────────────────────────────────────────────┘

Principios:
-----------
- Cada servicio es una clase con métodos async
- Usan inyección de dependencias
- Son independientes entre sí (bajo acoplamiento)
- Tienen interfaces claras y documentadas
- Son fácilmente testeables con mocks
- Copilot SDK como única interfaz para LLMs

Ejemplo de uso (NUEVO):
------------------------
# Obtener cliente Copilot
from app.services.copilot_client_service import CopilotManager

async def example():
    client = await CopilotManager.get_client()
    
    session = await client.create_session({
        "model": "claude-sonnet-4.5",
        "tools": [assess_risk, list_risks],
        "streaming": True
    })
    
    await session.send({"prompt": "Evalúa riesgos del servidor PROD-001"})

# Cache decorator (SIN CAMBIOS)
from app.services.cache_service import cached

@cached(ttl=300)
async def expensive_operation():
    return await db.query(...)
"""

__all__ = [
    "cache_service",
    "vector_store",
    "risk_calculator",
    # Nuevos servicios Copilot SDK (agregar cuando estén implementados)
    # "copilot_client_service",
    # "embedding_service",
    # "rag_service",
]
