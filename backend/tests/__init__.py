"""
Tests Package
=============

Organización de tests siguiendo estructura paralela a app/.

Estructura:
- conftest.py     → Fixtures compartidos
- unit/           → Tests unitarios (rápidos, aislados)
- integration/    → Tests de integración (DB, APIs externas)
- e2e/            → Tests end-to-end (flujos completos)

Convenciones:
- Nombres: test_{module}_{function}_{scenario}
- Markers: @pytest.mark.unit, @pytest.mark.integration, @pytest.mark.e2e
- Fixtures en conftest.py para reutilización
- Mocks para dependencias externas en unit tests

Comandos:
- pytest                     → Todos los tests
- pytest -m unit             → Solo unit tests
- pytest -m integration      → Solo integration tests
- pytest --cov=app           → Con coverage
"""
