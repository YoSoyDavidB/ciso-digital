"""
CISO Digital Backend Application
================================

Aplicación principal del backend para el sistema CISO Digital con IA.

Estructura del proyecto (Scope Rule):
- core/      → Servicios fundamentales (config, db, security)
- shared/    → Código compartido globalmente (models, schemas, utils)
- services/  → Servicios de infraestructura (LLM, RAG, cache)
- agents/    → Agentes de IA especializados
- api/       → Endpoints REST y middleware
- features/  → Funcionalidades específicas del dominio
"""

__version__ = "0.1.0"
