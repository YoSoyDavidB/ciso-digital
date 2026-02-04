"""
Core Module - Servicios Fundamentales
=====================================

Este módulo contiene los componentes fundamentales de la aplicación
que son necesarios para su funcionamiento básico.

Contenido:
- config.py       → Configuración de la aplicación (pydantic-settings)
- database.py     → Conexión y sesión de base de datos
- security.py     → JWT, hashing de passwords, autenticación
- dependencies.py → Dependencias de FastAPI (get_db, get_current_user, etc.)

Principios:
- Estos módulos NO deben depender de features específicas
- Deben ser estables y cambiar con poca frecuencia
- Son la base sobre la que se construye el resto de la aplicación
"""
