"""
CISO Digital Backend Application
================================

Aplicación principal del backend para el sistema CISO Digital con IA.

Estructura del proyecto (Scope Rule):
- core/      → Servicios fundamentales (config, db, security, dependencies)
- shared/    → Código compartido globalmente (models, schemas, utils, exceptions)
- services/  → Servicios de infraestructura (Copilot SDK, RAG, Cache, Embeddings)
- agents/    → Agentes de IA especializados (Risk, Incident, Compliance)
  - tools/   → Custom tools para GitHub Copilot SDK (@define_tool decorators)
- api/       → Endpoints REST (health, auth, chat, risks) y middleware
- features/  → Funcionalidades específicas del dominio (risk_assessment, etc.)

Motor AI: GitHub Copilot SDK 0.1.21 (multi-modelo: GPT-4/5, Claude Sonnet 4.5)
"""

__version__ = "0.1.0"
__ai_engine__ = "github-copilot-sdk==0.1.21"
