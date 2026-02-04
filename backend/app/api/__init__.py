"""
API Module - Endpoints REST
===========================

Módulo que contiene todos los endpoints de la API REST
y middleware de la aplicación.

Subcarpetas:
- routes/     → Routers de FastAPI organizados por dominio
- middleware/ → Middleware personalizado (auth, logging, etc.)

Contenido de routes/:
- health.py  → Health check y readiness
- auth.py    → Autenticación (login, logout, refresh)
- users.py   → Gestión de usuarios
- chat.py    → Chat con agentes de IA
- risks.py   → Gestión de riesgos
- incidents.py → Gestión de incidentes

Principios:
- Routers delgados: solo validación y llamada a services
- Documentación OpenAPI completa
- Manejo consistente de errores
- Respuestas estandarizadas
"""
