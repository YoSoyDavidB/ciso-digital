"""
Integration Tests
=================

Tests de integración que prueban múltiples componentes juntos.

Características:
- Más lentos que unit tests
- Usan base de datos real (SQLite en memoria para tests)
- Pueden llamar a APIs reales (con precaución)
- Prueban flujos entre componentes

Estructura:
- test_api/       → Tests de endpoints de API
- test_database/  → Tests de modelos y queries
- test_services/  → Tests de servicios con DB real
"""
