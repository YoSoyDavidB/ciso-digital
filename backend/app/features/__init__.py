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
    ├── services.py    → Lógica de negocio (SIN cambios con Copilot SDK)
    ├── repository.py  → Acceso a datos (SIN cambios)
    └── routes.py      → Endpoints específicos (opcional)

Features implementadas:
✅ risk_assessment/     → Evaluación y gestión de riesgos (COMPLETADO)
   - RiskService: Lógica de negocio de riesgos
   - RiskRepository: Acceso a datos
   - Schemas: RiskCreate, RiskUpdate, RiskResponse
   - Models: Risk (SQLAlchemy)
   - API: /api/v1/risks/* (139 tests, 86% coverage)

Features planeadas:
🆕 incident_response/   → Respuesta a incidentes de seguridad
   - IncidentService, IncidentRepository
   - Models: Incident, IncidentTimeline
   - API: /api/v1/incidents/*

🆕 compliance/          → Gestión de compliance (ISO 27001, etc.)
   - ComplianceService, AuditService
   - Models: ComplianceCheck, Evidence
   - API: /api/v1/compliance/*

🆕 vulnerability_mgmt/  → Gestión de vulnerabilidades
   - VulnerabilityService, ScanService
   - Models: Vulnerability, Scan
   - API: /api/v1/vulnerabilities/*

🆕 threat_intelligence/ → Inteligencia de amenazas
   - ThreatIntelService
   - Models: Threat, ThreatIndicator
   - API: /api/v1/threats/*

🆕 asset_management/    → Inventario de activos
   - AssetService
   - Models: Asset, AssetRelationship
   - API: /api/v1/assets/*

Integración con GitHub Copilot SDK:
-----------------------------------
✅ Features NO cambian con la adopción de Copilot SDK
✅ La lógica de negocio en services.py permanece igual
✅ Los modelos y schemas no se modifican
✅ Los endpoints REST siguen funcionando igual

Los agentes de IA (app/agents/) USAN los features mediante:
- Llamadas a services (RiskService, IncidentService, etc.)
- Tools (@define_tool) que wrappean los services
- Ejemplo: get_critical_risks tool → llama a RiskService.get_risks()

Flujo de Interacción:
--------------------
User → Chat API (/api/v1/chat)
  → Orchestrator (decide qué agente usar)
    → RiskAgent (usa risk_tools)
      → get_critical_risks tool
        → RiskService.get_risks()
          → RiskRepository.find_by_criteria()
            → Database (PostgreSQL)

Principios:
----------
✅ Cada feature puede depender de shared/ y core/
✅ Features NO deben depender entre sí directamente
✅ Comunicación entre features via services/ o eventos
✅ Features NO conocen la existencia de agents/
✅ Agents sí conocen y usan features (one-way dependency)

Ejemplo de uso desde Agent Tool:
--------------------------------
    # En app/agents/tools/risk_tools.py
    from app.features.risk_assessment.services import RiskService
    from github_copilot_sdk import define_tool
    
    @define_tool
    async def get_critical_risks(input: GetCriticalRisksInput) -> str:
        '''Obtiene riesgos críticos del sistema.'''
        risk_service = RiskService(db_session)
        risks = await risk_service.get_risks(
            severity=input.severity,
            limit=input.limit
        )
        return json.dumps([risk.model_dump() for risk in risks])

Testing:
-------
- Features se testean de forma aislada (unit tests)
- No necesitan conocer los agentes de IA
- Tests existentes NO cambian con Copilot SDK
- Ejemplo: tests/unit/test_services/test_risk_service_new.py (✅ 139 passing)

Referencias:
-----------
- Arquitectura completa: docs/01-TECHNICAL-ARCHITECTURE.md
- Análisis Copilot SDK: docs/COPILOT_SDK_ANALYSIS.md
"""
