"""
Features Module - Funcionalidades del Dominio
=============================================

Módulo que contiene las funcionalidades específicas del dominio
de seguridad (CISO). Cada feature es autocontenida.

Estructura de cada feature:
    feature_name/
    ├── __init__.py
    ├── models.py      → SQLAlchemy models específicos
    ├── schemas.py     → Pydantic schemas específicos
    ├── services.py    → Lógica de negocio
    ├── repository.py  → Acceso a datos
    └── routes.py      → Endpoints específicos (opcional)

Features planeadas:
- risk_assessment/     → Evaluación y gestión de riesgos
- incident_response/   → Respuesta a incidentes de seguridad
- compliance/          → Gestión de compliance (ISO 27001, etc.)
- vulnerability_mgmt/  → Gestión de vulnerabilidades
- threat_intelligence/ → Inteligencia de amenazas
- asset_management/    → Inventario de activos

Principios:
- Cada feature puede depender de shared/ y core/
- Features NO deben depender entre sí directamente
- Comunicación entre features via services/ o eventos
"""
