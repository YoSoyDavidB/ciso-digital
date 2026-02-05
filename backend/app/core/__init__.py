"""
Core Module - Servicios Fundamentales
=====================================

Este módulo contiene los componentes fundamentales de la aplicación
que son necesarios para su funcionamiento básico.

Contenido:
- config.py       → Configuración de la aplicación (pydantic-settings)
                    Variables: DATABASE_URL, REDIS_URL, QDRANT_URL, 
                    GITHUB_TOKEN (para Copilot SDK, auto-detectado),
                    AZURE_* (fallback opcional), SECRET_KEY
- database.py     → Conexión async PostgreSQL con SQLAlchemy
- security.py     → JWT, hashing de passwords, autenticación (TODO)
- dependencies.py → Dependencias de FastAPI (get_db, get_current_user, etc.) (TODO)

Principios:
- Estos módulos NO deben depender de features específicas
- Deben ser estables y cambiar con poca frecuencia
- Son la base sobre la que se construye el resto de la aplicación
- GitHub Copilot SDK se inicializa aquí como servicio core
"""

__all__ = ["config", "database"]
