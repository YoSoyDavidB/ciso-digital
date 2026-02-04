"""
Services Module - Servicios de Infraestructura
==============================================

Servicios que proveen funcionalidad de infraestructura
y conexión con sistemas externos.

Contenido:
- llm_service.py       → Cliente para Claude/OpenAI API
- rag_service.py       → Servicio RAG con Qdrant
- embedding_service.py → Generación de embeddings
- cache_service.py     → Caching con Redis

Principios:
- Cada servicio es una clase con métodos async
- Usan inyección de dependencias
- Son independientes entre sí
- Tienen interfaces claras y documentadas
- Son fácilmente testeables con mocks

Ejemplo de uso:
    from app.services.llm_service import LLMService

    class RiskAgent:
        def __init__(self, llm_service: LLMService):
            self.llm = llm_service

        async def analyze(self, data: str) -> str:
            return await self.llm.generate(prompt=data)
"""
