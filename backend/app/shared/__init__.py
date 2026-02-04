"""
Shared Module - Global Scope
============================

Este módulo contiene código compartido que puede ser usado
por cualquier parte de la aplicación.

Subcarpetas:
- models/      → SQLAlchemy base models y mixins
- schemas/     → Pydantic schemas compartidos (pagination, responses, etc.)
- utils/       → Funciones de utilidad generales
- exceptions/  → Excepciones personalizadas de la aplicación

Reglas:
- El código aquí NO debe importar de features/
- Debe ser código genérico y reutilizable
- Cambios aquí pueden afectar a toda la aplicación
"""
