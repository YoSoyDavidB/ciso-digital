# AGENTS.md - Guía para Agentes de Desarrollo IA

## 🎯 PROPÓSITO DE ESTE DOCUMENTO

Este archivo define los lineamientos, estándares y metodología de desarrollo para el proyecto **CISO Digital con IA**. Está diseñado para ser leído por agentes de IA (Claude Code CLI, Cursor, etc.) y desarrolladores humanos para asegurar consistencia, calidad y adherencia a las mejores prácticas.

**Si eres un agente de IA trabajando en este proyecto, LEE ESTE DOCUMENTO COMPLETO antes de escribir cualquier código.**

---

## 📋 TABLA DE CONTENIDOS

1. [Filosofía de Desarrollo](#filosofía-de-desarrollo)
2. [Metodología TDD (Red-Green-Refactor)](#metodología-tdd)
3. [Workflow de Desarrollo](#workflow-de-desarrollo)
4. [Estándares de Código](#estándares-de-código)
5. [Estructura del Proyecto](#estructura-del-proyecto)
6. [Testing](#testing)
7. [Git y Commits](#git-y-commits)
8. [Documentación](#documentación)
9. [Ejemplos Prácticos](#ejemplos-prácticos)
10. [Comandos Útiles](#comandos-útiles)

---

## 🎨 FILOSOFÍA DE DESARROLLO

### Principios Fundamentales

1. **Test-Driven Development (TDD)**: SIEMPRE escribir tests antes que el código de producción
2. **Simplicidad**: El código más simple que funcione es el mejor código
3. **Legibilidad**: El código se lee 10x más veces de las que se escribe
4. **Type Safety**: Python con type hints obligatorios, TypeScript strict mode
5. **Fail Fast**: Los errores deben ser evidentes y tempranos
6. **Documentación en Código**: El código debe ser auto-documentado, pero complementado con docstrings

### Valores del Proyecto

- **Calidad sobre Velocidad**: Mejor código robusto y testeado que rápido y frágil
- **Automatización**: Si lo haces 2+ veces, automatízalo
- **Seguridad por Diseño**: La seguridad no es opcional, es fundamental
- **Observabilidad**: El sistema debe poder explicar qué está haciendo

---

## 🔴🟢🔵 METODOLOGÍA TDD (Red-Green-Refactor)

### El Ciclo Sagrado del TDD

**REGLA DE ORO: No escribas código de producción sin un test que falle primero.**

```
┌─────────────────────────────────────────────┐
│                                             │
│  🔴 RED (Rojo)                              │
│  ├─ Escribir un test que FALLE              │
│  ├─ El test define el comportamiento        │
│  └─ Ejecutar: pytest - debe fallar          │
│                                             │
│  ↓                                          │
│                                             │
│  🟢 GREEN (Verde)                           │
│  ├─ Escribir el MÍNIMO código necesario    │
│  ├─ El código hace pasar el test            │
│  └─ Ejecutar: pytest - debe pasar           │
│                                             │
│  ↓                                          │
│                                             │
│  🔵 REFACTOR (Azul)                         │
│  ├─ Mejorar el código sin cambiar           │
│  │  comportamiento                          │
│  ├─ Eliminar duplicación                    │
│  ├─ Mejorar nombres, estructura             │
│  └─ Ejecutar: pytest - debe seguir pasando  │
│                                             │
│  ↓ (Repetir para la siguiente feature)     │
│                                             │
└─────────────────────────────────────────────┘
```

### Workflow TDD Paso a Paso

#### 1. 🔴 RED: Escribir Test que Falla

```bash
# SIEMPRE empezar aquí
git checkout -b feature/CISO-123-risk-calculator
```

```python
# tests/unit/test_risk_calculator.py

import pytest
from app.services.risk_calculator import RiskCalculator

def test_calculate_risk_score_with_no_vulnerabilities():
    """
    🔴 RED: Este test debe FALLAR porque RiskCalculator
    aún no existe.
    """
    # Arrange
    calculator = RiskCalculator()
    vulnerabilities = []
    asset_criticality = "high"
    
    # Act
    score = calculator.calculate_score(vulnerabilities, asset_criticality)
    
    # Assert
    assert score == 0.0
```

```bash
# Ejecutar test - DEBE FALLAR
pytest tests/unit/test_risk_calculator.py -v

# Salida esperada:
# FAILED - ModuleNotFoundError: No module named 'app.services.risk_calculator'
# ✅ Perfecto! El test falla como se esperaba.
```

#### 2. 🟢 GREEN: Hacer Pasar el Test

Ahora escribimos el **MÍNIMO** código necesario:

```python
# app/services/risk_calculator.py

from typing import List

class RiskCalculator:
    """Calcula scores de riesgo basado en vulnerabilidades."""
    
    def calculate_score(
        self,
        vulnerabilities: List,
        asset_criticality: str
    ) -> float:
        """
        🟢 GREEN: Implementación mínima para pasar el test.
        """
        if not vulnerabilities:
            return 0.0
        
        # Por ahora, solo retornamos 0.0 para lista vacía
        # Próximos tests nos obligarán a implementar más lógica
        return 0.0
```

```bash
# Ejecutar test - DEBE PASAR
pytest tests/unit/test_risk_calculator.py -v

# Salida esperada:
# PASSED - test_calculate_risk_score_with_no_vulnerabilities
# ✅ Verde! El test pasa.
```

#### 3. 🔵 REFACTOR: Mejorar sin Romper

En este caso, el código es tan simple que no necesita refactor todavía. Pero si hubiera duplicación o mejoras obvias:

```python
# Ejemplo de refactor (si fuera necesario)

# Antes del refactor
def calculate_score(self, vulns, crit):
    if len(vulns) == 0:
        return 0.0
    return 0.0

# Después del refactor
def calculate_score(
    self,
    vulnerabilities: List[Vulnerability],
    asset_criticality: str
) -> float:
    """Calcula el score de riesgo."""
    if not vulnerabilities:
        return 0.0
    return 0.0
```

```bash
# Ejecutar tests después de refactor - DEBEN SEGUIR PASANDO
pytest tests/unit/test_risk_calculator.py -v

# ✅ Siguen pasando! Refactor exitoso.
```

#### 4. Repetir para la Siguiente Feature

```python
# 🔴 RED: Siguiente test

def test_calculate_risk_score_with_single_vulnerability():
    """Test con una vulnerabilidad de CVSS 9.0"""
    calculator = RiskCalculator()
    vulnerabilities = [
        Vulnerability(cvss_score=9.0, cve_id="CVE-2025-1234")
    ]
    asset_criticality = "high"
    
    score = calculator.calculate_score(vulnerabilities, asset_criticality)
    
    # Para asset high con vuln 9.0, esperamos score ajustado
    assert score > 9.0  # Por criticality multiplier
    assert score <= 10.0  # Max score es 10.0
```

```bash
# Ejecutar - DEBE FALLAR
pytest tests/unit/test_risk_calculator.py::test_calculate_risk_score_with_single_vulnerability -v

# Falla porque retornamos 0.0 siempre
# ✅ Ahora escribimos código para pasar este test
```

### Reglas de TDD para Este Proyecto

1. ✅ **NUNCA** escribas código de producción sin un test que falle primero
2. ✅ **NUNCA** escribas más código del necesario para pasar el test
3. ✅ **SIEMPRE** refactoriza cuando veas duplicación o código mejorable
4. ✅ **SIEMPRE** ejecuta todos los tests antes de commit
5. ✅ Los tests deben ser independientes (orden de ejecución no importa)
6. ✅ Los tests deben ser rápidos (< 1 segundo cada uno idealmente)
7. ✅ Los tests deben ser determinísticos (mismo input = mismo output)

---

## 🔄 WORKFLOW DE DESARROLLO

### Proceso Completo para una Nueva Feature

```bash
# 1. Crear branch desde develop
git checkout develop
git pull origin develop
git checkout -b feature/CISO-123-descriptive-name

# 2. 🔴 RED: Escribir test(s) que fallan
# Editar: tests/unit/test_nueva_feature.py

# 3. Ejecutar tests - verificar que fallan
pytest tests/unit/test_nueva_feature.py -v

# 4. 🟢 GREEN: Escribir código mínimo
# Editar: app/services/nueva_feature.py

# 5. Ejecutar tests - verificar que pasan
pytest tests/unit/test_nueva_feature.py -v

# 6. 🔵 REFACTOR: Mejorar código
# Editar código para mejorar (sin cambiar comportamiento)

# 7. Ejecutar TODOS los tests
pytest

# 8. Linting y formatting
ruff check .
ruff format .
black .
mypy app/

# 9. Commit
git add .
git commit -m "feat(risk): add risk score calculator

- Implement RiskCalculator service
- Add support for CVSS-based scoring
- Include asset criticality multipliers

Tests: test_risk_calculator.py
Closes #123"

# 10. Push y crear PR
git push origin feature/CISO-123-descriptive-name
# Crear Pull Request en GitHub/GitLab
```

### Checklist Antes de Cada Commit

- [ ] Todos los tests pasan (`pytest`)
- [ ] Coverage > 80% (`pytest --cov=app`)
- [ ] No hay errores de linting (`ruff check .`)
- [ ] Código formateado (`black .` y `ruff format .`)
- [ ] Type checking pasa (`mypy app/`)
- [ ] Commit message sigue convención
- [ ] Código revisado por ti mismo (self-review)

---

## 📝 ESTÁNDARES DE CÓDIGO

### Python Backend

#### Imports

```python
# ✅ CORRECTO - Orden de imports

# 1. Standard library
import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict

# 2. Third-party
import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

# 3. Local
from app.config import settings
from app.database import get_db
from app.models.risk import Risk
from app.schemas.risk import RiskCreate, RiskResponse
from app.services.llm_service import LLMService
```

#### Type Hints

```python
# ✅ SIEMPRE usar type hints

from typing import List, Optional, Dict, Union, Literal

async def process_risks(
    risk_ids: List[str],
    severity_filter: Optional[Literal["critical", "high", "medium", "low"]] = None,
    limit: int = 100
) -> Dict[str, List[Risk]]:
    """
    Procesa riesgos con filtros opcionales.
    
    Args:
        risk_ids: Lista de IDs de riesgos a procesar
        severity_filter: Filtro opcional por severidad
        limit: Número máximo de resultados
        
    Returns:
        Diccionario con riesgos agrupados por status
    """
    ...
```

#### Async/Await

```python
# ✅ CORRECTO - Usar async para I/O

async def get_risk_from_db(risk_id: str) -> Optional[Risk]:
    """Database I/O - usar async"""
    async with db.session() as session:
        result = await session.execute(
            select(Risk).where(Risk.id == risk_id)
        )
        return result.scalar_one_or_none()

async def call_llm_api(prompt: str) -> str:
    """API call - usar async"""
    response = await anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

# ❌ INCORRECTO - No usar async para CPU-bound

async def calculate_hash(data: str) -> str:
    """CPU-bound - NO necesita async"""
    import hashlib
    return hashlib.sha256(data.encode()).hexdigest()

# ✅ CORRECTO
def calculate_hash(data: str) -> str:
    """CPU-bound operations son síncronos"""
    import hashlib
    return hashlib.sha256(data.encode()).hexdigest()
```

#### Error Handling

```python
# ✅ CORRECTO

import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def safe_get_risk(risk_id: str) -> Optional[Risk]:
    """
    Get risk with proper error handling.
    
    Returns None if not found, raises for other errors.
    """
    try:
        risk = await db.get(Risk, risk_id)
        
        if risk is None:
            logger.warning(f"Risk {risk_id} not found")
            return None
            
        return risk
        
    except DatabaseConnectionError as e:
        logger.error(f"Database connection failed: {e}", exc_info=True)
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise

# ❌ INCORRECTO

async def bad_get_risk(risk_id):
    try:
        return await db.get(Risk, risk_id)
    except:  # ❌ Never bare except
        print("Error")  # ❌ Don't use print
        return None  # ❌ Hiding all errors
```

#### Naming Conventions

```python
# Variables y funciones: snake_case
user_email = "user@example.com"
risk_score = 8.5

async def calculate_risk_score(vulnerabilities: List[Vulnerability]) -> float:
    pass

# Clases: PascalCase
class RiskAssessmentAgent:
    pass

class HTTPException:
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT_SECONDS = 30
API_BASE_URL = "https://api.example.com"

# Private methods/attributes: _prefijo
class DatabaseService:
    def __init__(self):
        self._connection_pool = None
        self._cache = {}
    
    def _internal_method(self):
        pass
    
    def public_method(self):
        return self._internal_method()

# Enums
from enum import Enum

class RiskSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

### TypeScript Frontend

```typescript
// ✅ CORRECTO

import { useState, useEffect, useCallback } from 'react';
import { Risk, RiskFilters } from '@/types';
import { fetchRisks } from '@/api/risks';
import { useAuth } from '@/hooks/useAuth';

interface RiskDashboardProps {
  initialFilters?: RiskFilters;
  onRiskSelect?: (risk: Risk) => void;
}

export const RiskDashboard: React.FC<RiskDashboardProps> = ({
  initialFilters,
  onRiskSelect,
}) => {
  const [risks, setRisks] = useState<Risk[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const { user } = useAuth();

  const loadRisks = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchRisks(initialFilters);
      setRisks(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [initialFilters]);

  useEffect(() => {
    loadRisks();
  }, [loadRisks]);

  // ... rest of component
};
```

---

## 🧪 TESTING

### Estructura de Tests

```
tests/
├── unit/                    # Tests unitarios (lógica aislada)
│   ├── test_agents/
│   │   ├── test_risk_agent.py
│   │   ├── test_incident_agent.py
│   │   └── test_orchestrator.py
│   ├── test_services/
│   │   ├── test_llm_service.py
│   │   ├── test_rag_service.py
│   │   └── test_cache_service.py
│   └── test_utils/
│       └── test_validators.py
│
├── integration/             # Tests de integración (múltiples componentes)
│   ├── test_api/
│   │   ├── test_risk_endpoints.py
│   │   ├── test_incident_endpoints.py
│   │   └── test_chat_endpoints.py
│   └── test_database/
│       └── test_models.py
│
├── e2e/                     # Tests end-to-end (flujos completos)
│   ├── test_risk_workflow.py
│   ├── test_incident_response.py
│   └── test_compliance_check.py
│
└── conftest.py              # Fixtures compartidos
```

### Escribir Buenos Tests

```python
# ✅ CORRECTO - Test completo y claro

import pytest
from unittest.mock import AsyncMock, Mock
from app.agents.risk_agent import RiskAssessmentAgent
from app.models import Asset, Vulnerability
from app.services.llm_service import LLMService

@pytest.fixture
async def mock_llm_service():
    """Mock del LLM service para tests aislados"""
    service = AsyncMock(spec=LLMService)
    service.generate.return_value = "Risk analysis: High severity..."
    return service

@pytest.fixture
async def risk_agent(mock_llm_service, db_session):
    """Fixture del RiskAssessmentAgent"""
    return RiskAssessmentAgent(
        llm_service=mock_llm_service,
        rag_service=Mock(),
        db_session=db_session
    )

@pytest.fixture
async def sample_asset(db_session):
    """Asset de prueba en base de datos"""
    asset = Asset(
        id="test-asset-1",
        name="Production Web Server",
        type="server",
        criticality="critical"
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)
    return asset

@pytest.mark.asyncio
async def test_assess_risk_calculates_correct_score(
    risk_agent,
    sample_asset,
    db_session
):
    """
    Test que el RiskAgent calcula correctamente el score
    
    Given: Un asset crítico con 2 vulnerabilidades altas
    When: Se ejecuta assess_risk
    Then: El score debe ser > 7.0 y severity debe ser 'high' o 'critical'
    """
    # Arrange (Given)
    vulnerabilities = [
        Vulnerability(
            cvss_score=9.8,
            cve_id="CVE-2025-1234",
            description="Critical RCE vulnerability"
        ),
        Vulnerability(
            cvss_score=8.5,
            cve_id="CVE-2025-5678",
            description="High privilege escalation"
        )
    ]
    
    # Act (When)
    result = await risk_agent.assess_risk(
        asset=sample_asset,
        vulnerabilities=vulnerabilities
    )
    
    # Assert (Then)
    assert result.risk_score > 7.0, "Score should be high for critical asset with severe vulns"
    assert result.severity in ["high", "critical"], f"Expected high/critical, got {result.severity}"
    assert len(result.recommendations) > 0, "Should provide recommendations"
    assert result.asset_id == sample_asset.id, "Should reference correct asset"
    
    # Verify mock interactions
    risk_agent.llm_service.generate.assert_called_once()

# ❌ INCORRECTO

def test_risk():  # ❌ Nombre no descriptivo
    agent = RiskAssessmentAgent()  # ❌ No usa fixtures
    result = agent.assess_risk(None, [])  # ❌ No async, no setup claro
    assert result  # ❌ Assertion vaga
```

### Convenciones de Tests

1. **Naming**: `test_<what>_<condition>_<expected_result>`
2. **Structure**: Arrange-Act-Assert (Given-When-Then)
3. **One assertion concept per test**: Test una cosa a la vez
4. **Use fixtures**: Reutilizar setup común
5. **Mock external dependencies**: Database, APIs, etc.
6. **Fast tests**: Unit tests < 1s cada uno

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Solo unit tests
pytest tests/unit/

# Test específico
pytest tests/unit/test_risk_agent.py::test_assess_risk_calculates_correct_score

# Con coverage
pytest --cov=app --cov-report=html --cov-report=term

# Verbose
pytest -v

# Stop on first failure
pytest -x

# Ver prints
pytest -s

# Parallel (más rápido)
pytest -n auto
```

---

## 🔀 GIT Y COMMITS

### Branch Naming

```bash
# Features
feature/CISO-123-add-risk-calculator
feature/CISO-124-proactive-review-agent

# Bug fixes
bugfix/CISO-125-fix-chat-session-timeout
bugfix/CISO-126-resolve-qdrant-connection

# Hotfixes (producción)
hotfix/CISO-127-critical-security-patch

# Refactors
refactor/CISO-128-improve-rag-performance

# Documentation
docs/CISO-129-update-api-docs
```

### Commit Messages

**Formato:** `type(scope): subject`

```bash
# ✅ CORRECTOS

feat(agents): implement ProactiveReviewAgent with documentation gap detection
fix(api): resolve race condition in chat endpoint session management
docs(readme): add installation instructions for new developers
refactor(rag): improve vector search performance by 40%
test(agents): add comprehensive unit tests for RiskAssessmentAgent
chore(deps): update dependencies to latest stable versions
style(api): format code with black and fix linting issues

# Con cuerpo (para commits complejos)
git commit -m "feat(compliance): add automated ISO 27001 compliance checks

- Implement automated verification for controls A.8.1-A.8.3
- Add evidence collection from multiple sources
- Generate comprehensive compliance reports
- Include gap analysis and remediation suggestions

Tests: test_compliance_agent.py
Docs: Updated COMPLIANCE.md
Closes #123"

# ❌ INCORRECTOS

git commit -m "Fixed bug"  # ❌ Vago, no sigue formato
git commit -m "WIP"  # ❌ Work in progress no debe commitearse
git commit -m "Updated files"  # ❌ Muy genérico
git commit -m "asdf"  # ❌ No descriptivo
```

### Pre-commit Checklist

Antes de cada commit, verificar:

```bash
# 1. Tests pasan
pytest

# 2. Coverage OK
pytest --cov=app --cov-report=term

# 3. Linting
ruff check .

# 4. Formatting
black .
ruff format .

# 5. Type checking
mypy app/

# 6. Self-review
git diff --cached
```

---

## 📚 DOCUMENTACIÓN

### Docstrings (Python)

```python
# ✅ CORRECTO - Estilo Google

async def calculate_risk_score(
    vulnerabilities: List[Vulnerability],
    asset_criticality: str,
    context: Optional[Dict[str, Any]] = None
) -> float:
    """
    Calcula el score de riesgo basado en vulnerabilidades y criticidad del asset.
    
    El cálculo toma en cuenta la severidad de las vulnerabilidades (CVSS scores),
    la criticidad del asset, y opcionalmente contexto adicional como amenazas
    recientes o exploits conocidos.
    
    Args:
        vulnerabilities: Lista de vulnerabilidades detectadas en el asset.
            Cada vulnerabilidad debe tener un cvss_score válido (0.0-10.0).
        asset_criticality: Nivel de criticidad del asset. Debe ser uno de:
            'critical', 'high', 'medium', 'low'.
        context: Contexto adicional opcional que puede influir en el cálculo.
            Puede incluir 'recent_exploits', 'threat_intel', etc.
    
    Returns:
        float: Score de riesgo entre 0.0 y 10.0, donde:
            - 0.0-2.9: Riesgo bajo
            - 3.0-5.9: Riesgo medio
            - 6.0-8.9: Riesgo alto
            - 9.0-10.0: Riesgo crítico
    
    Raises:
        ValueError: Si asset_criticality no es un valor válido.
        ValueError: Si alguna vulnerabilidad tiene cvss_score inválido.
    
    Example:
        >>> vulns = [Vulnerability(cvss_score=9.8, cve_id="CVE-2025-1234")]
        >>> score = await calculate_risk_score(vulns, "critical")
        >>> print(f"Risk score: {score}")
        Risk score: 10.0
    
    Note:
        Para assets críticos, el score se multiplica por 1.5 para reflejar
        el impacto potencial mayor en la organización.
    """
    # Implementación...
```

### JSDoc (TypeScript)

```typescript
/**
 * Fetches risks from the API with optional filtering and pagination.
 *
 * This function handles authentication automatically and includes retry logic
 * for transient failures. Results are cached for 60 seconds to reduce API load.
 *
 * @param filters - Optional filters to apply to the risk query
 * @param filters.severity - Filter by risk severity level
 * @param filters.status - Filter by risk status
 * @param filters.assignedTo - Filter by assigned user email
 * @param options - Additional options for the request
 * @param options.limit - Maximum number of results (default: 50)
 * @param options.offset - Pagination offset (default: 0)
 *
 * @returns Promise resolving to an array of Risk objects
 *
 * @throws {AuthError} If the user is not authenticated
 * @throws {ApiError} If the API request fails after retries
 *
 * @example
 * ```typescript
 * // Fetch all critical risks
 * const risks = await fetchRisks({ severity: 'critical' });
 *
 * // Fetch with pagination
 * const page2 = await fetchRisks({}, { limit: 20, offset: 20 });
 * ```
 */
export async function fetchRisks(
  filters?: RiskFilters,
  options?: FetchOptions
): Promise<Risk[]> {
  // Implementation...
}
```

---

## 💡 EJEMPLOS PRÁCTICOS

### Ejemplo Completo: Desarrollar Nueva Feature con TDD

**Feature:** Agregar función para calcular MTTR (Mean Time To Resolve) de incidentes

#### Paso 1: 🔴 RED - Escribir Test que Falla

```bash
git checkout -b feature/CISO-150-mttr-calculation
```

```python
# tests/unit/test_metrics_service.py

import pytest
from datetime import datetime, timedelta
from app.services.metrics_service import MetricsService
from app.models import Incident

@pytest.fixture
def sample_incidents(db_session):
    """Incidentes de prueba con tiempos de resolución conocidos"""
    incidents = [
        Incident(
            id="inc-1",
            title="Incident 1",
            severity="critical",
            detection_time=datetime(2026, 2, 1, 10, 0, 0),
            resolution_time=datetime(2026, 2, 1, 12, 0, 0),  # 2 horas
            status="resolved"
        ),
        Incident(
            id="inc-2",
            title="Incident 2",
            severity="high",
            detection_time=datetime(2026, 2, 2, 9, 0, 0),
            resolution_time=datetime(2026, 2, 2, 13, 0, 0),  # 4 horas
            status="resolved"
        ),
        Incident(
            id="inc-3",
            title="Incident 3",
            severity="medium",
            detection_time=datetime(2026, 2, 3, 8, 0, 0),
            resolution_time=datetime(2026, 2, 3, 14, 0, 0),  # 6 horas
            status="resolved"
        ),
    ]
    for incident in incidents:
        db_session.add(incident)
    await db_session.commit()
    return incidents

@pytest.mark.asyncio
async def test_calculate_mttr_returns_correct_average(
    sample_incidents,
    db_session
):
    """
    🔴 RED: Test que MetricsService.calculate_mttr retorna
    el promedio correcto de tiempo de resolución.
    
    Given: 3 incidentes con tiempos de resolución de 2h, 4h y 6h
    When: Se calcula MTTR
    Then: Debe retornar 4 horas (promedio)
    """
    # Arrange
    metrics_service = MetricsService(db_session)
    
    # Act
    mttr_hours = await metrics_service.calculate_mttr(
        start_date=datetime(2026, 2, 1),
        end_date=datetime(2026, 2, 4)
    )
    
    # Assert
    assert mttr_hours == 4.0, f"Expected 4.0 hours, got {mttr_hours}"

@pytest.mark.asyncio
async def test_calculate_mttr_excludes_unresolved_incidents(
    db_session
):
    """
    🔴 RED: MTTR solo debe incluir incidentes resueltos.
    
    Given: 2 incidentes resueltos y 1 sin resolver
    When: Se calcula MTTR
    Then: Solo debe considerar los 2 resueltos
    """
    # Arrange
    incidents = [
        Incident(
            detection_time=datetime(2026, 2, 1, 10, 0),
            resolution_time=datetime(2026, 2, 1, 12, 0),
            status="resolved"
        ),
        Incident(
            detection_time=datetime(2026, 2, 2, 10, 0),
            resolution_time=datetime(2026, 2, 2, 14, 0),
            status="resolved"
        ),
        Incident(
            detection_time=datetime(2026, 2, 3, 10, 0),
            resolution_time=None,  # No resuelto
            status="investigating"
        ),
    ]
    for inc in incidents:
        db_session.add(inc)
    await db_session.commit()
    
    metrics_service = MetricsService(db_session)
    
    # Act
    mttr = await metrics_service.calculate_mttr()
    
    # Assert
    assert mttr == 3.0, "Should average 2h and 4h, excluding unresolved"
```

```bash
# Ejecutar - DEBE FALLAR
pytest tests/unit/test_metrics_service.py -v

# Output esperado:
# FAILED - ModuleNotFoundError: No module named 'app.services.metrics_service'
# ✅ Perfecto, falla como esperado!
```

#### Paso 2: 🟢 GREEN - Implementar Código Mínimo

```python
# app/services/metrics_service.py

from datetime import datetime
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Incident


class MetricsService:
    """Servicio para calcular métricas de seguridad."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def calculate_mttr(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> float:
        """
        Calcula Mean Time To Resolve (MTTR) de incidentes.
        
        Args:
            start_date: Fecha de inicio opcional para filtrar
            end_date: Fecha de fin opcional para filtrar
        
        Returns:
            float: MTTR en horas
        """
        # Construir query
        conditions = [
            Incident.status == "resolved",
            Incident.resolution_time.isnot(None)
        ]
        
        if start_date:
            conditions.append(Incident.detection_time >= start_date)
        if end_date:
            conditions.append(Incident.detection_time <= end_date)
        
        # Obtener incidentes resueltos
        query = select(Incident).where(and_(*conditions))
        result = await self.db.execute(query)
        incidents = result.scalars().all()
        
        if not incidents:
            return 0.0
        
        # Calcular tiempos de resolución
        resolution_times = []
        for incident in incidents:
            time_diff = incident.resolution_time - incident.detection_time
            hours = time_diff.total_seconds() / 3600
            resolution_times.append(hours)
        
        # Retornar promedio
        return sum(resolution_times) / len(resolution_times)
```

```bash
# Ejecutar tests - DEBEN PASAR
pytest tests/unit/test_metrics_service.py -v

# Output:
# PASSED - test_calculate_mttr_returns_correct_average
# PASSED - test_calculate_mttr_excludes_unresolved_incidents
# ✅ Verde! Tests pasan.
```

#### Paso 3: 🔵 REFACTOR - Mejorar Código

```python
# app/services/metrics_service.py - Versión mejorada

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Incident


class MetricsService:
    """Servicio para calcular métricas de seguridad."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def calculate_mttr(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[str] = None
    ) -> float:
        """
        Calcula Mean Time To Resolve (MTTR) de incidentes.
        
        Args:
            start_date: Fecha de inicio opcional para filtrar
            end_date: Fecha de fin opcional para filtrar
            severity: Filtro opcional por severidad
        
        Returns:
            float: MTTR en horas. Retorna 0.0 si no hay incidentes.
        
        Example:
            >>> service = MetricsService(db_session)
            >>> mttr = await service.calculate_mttr(
            ...     start_date=datetime(2026, 2, 1),
            ...     end_date=datetime(2026, 2, 28),
            ...     severity="critical"
            ... )
            >>> print(f"MTTR for critical incidents: {mttr:.2f} hours")
        """
        incidents = await self._get_resolved_incidents(
            start_date, end_date, severity
        )
        
        if not incidents:
            return 0.0
        
        resolution_times = self._calculate_resolution_times(incidents)
        return self._calculate_average(resolution_times)
    
    async def _get_resolved_incidents(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        severity: Optional[str]
    ) -> List[Incident]:
        """Obtiene incidentes resueltos con filtros aplicados."""
        conditions = [
            Incident.status == "resolved",
            Incident.resolution_time.isnot(None)
        ]
        
        if start_date:
            conditions.append(Incident.detection_time >= start_date)
        if end_date:
            conditions.append(Incident.detection_time <= end_date)
        if severity:
            conditions.append(Incident.severity == severity)
        
        query = select(Incident).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalars().all()
    
    def _calculate_resolution_times(
        self, 
        incidents: List[Incident]
    ) -> List[float]:
        """Calcula tiempo de resolución en horas para cada incidente."""
        times = []
        for incident in incidents:
            time_diff = incident.resolution_time - incident.detection_time
            hours = time_diff.total_seconds() / 3600
            times.append(hours)
        return times
    
    def _calculate_average(self, values: List[float]) -> float:
        """Calcula promedio de una lista de valores."""
        return sum(values) / len(values) if values else 0.0
```

```bash
# Ejecutar tests después de refactor - DEBEN SEGUIR PASANDO
pytest tests/unit/test_metrics_service.py -v

# ✅ Siguen pasando! Refactor exitoso.

# Ejecutar TODOS los tests del proyecto
pytest

# Verificar coverage
pytest --cov=app --cov-report=term

# Linting y formatting
ruff check .
black .
mypy app/

# Commit
git add .
git commit -m "feat(metrics): add MTTR calculation service

- Implement MetricsService.calculate_mttr()
- Support filtering by date range and severity
- Exclude unresolved incidents from calculation
- Add comprehensive unit tests

Tests: test_metrics_service.py
Coverage: 100% for MetricsService
Closes #150"
```

---

## ⚡ COMANDOS ÚTILES

### Desarrollo

```bash
# Iniciar servidor de desarrollo
uvicorn app.main:app --reload --port 8000

# Iniciar con debugging
uvicorn app.main:app --reload --log-level debug

# Shell interactivo de Python
python -m asyncio

# IPython (mejor que python shell)
ipython
```

### Testing

```bash
# Todos los tests
pytest

# Solo unit tests
pytest tests/unit/

# Test específico
pytest tests/unit/test_risk_agent.py::test_assess_risk

# Con coverage
pytest --cov=app --cov-report=html

# Watch mode (re-run on file changes)
pytest-watch

# Parallel execution
pytest -n auto

# Stop on first failure
pytest -x

# Ver output completo
pytest -s -v
```

### Linting y Formatting

```bash
# Ruff check (linting)
ruff check .

# Ruff format (formatting)
ruff format .

# Black (formatting)
black .

# Mypy (type checking)
mypy app/

# Todo en uno
ruff check . && ruff format . && black . && mypy app/
```

### Database

```bash
# Crear nueva migration
alembic revision --autogenerate -m "add mttr calculation table"

# Aplicar migrations
alembic upgrade head

# Revert última migration
alembic downgrade -1

# Ver historial
alembic history

# Reset database (cuidado!)
alembic downgrade base
alembic upgrade head
```

### Docker

```bash
# Build y start todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Rebuild
docker-compose up -d --build

# Stop todo
docker-compose down

# Reset completo (borra volúmenes)
docker-compose down -v
```

---

## 🎯 CHECKLIST FINAL

### Antes de Push

- [ ] 🔴🟢🔵 Seguiste TDD (Red-Green-Refactor)
- [ ] ✅ Todos los tests pasan
- [ ] 📊 Coverage > 80%
- [ ] 🎨 Código formateado (black, ruff)
- [ ] 🔍 Sin errores de linting
- [ ] 🏷️ Type hints en todas las funciones
- [ ] 📝 Docstrings completos
- [ ] 💬 Commit message sigue convención
- [ ] 👀 Self-review del código
- [ ] 🔒 No hay secrets en el código
- [ ] 📚 Documentación actualizada (si aplica)

---

## 📖 REFERENCIAS

- **[09-DEVELOPMENT-STANDARDS.md](09-DEVELOPMENT-STANDARDS.md)**: Estándares detallados de código
- **[08-IMPLEMENTATION-ROADMAP.md](08-IMPLEMENTATION-ROADMAP.md)**: Plan de implementación
- **[01-TECHNICAL-ARCHITECTURE.md](01-TECHNICAL-ARCHITECTURE.md)**: Arquitectura del sistema
- **[00-PROJECT-CHARTER.md](00-PROJECT-CHARTER.md)**: Visión y objetivos del proyecto

---

## 🤖 NOTA PARA AGENTES DE IA

Si eres Claude Code CLI, Cursor, o cualquier agente de IA:

1. **LEE ESTE DOCUMENTO COMPLETO** antes de escribir código
2. **SIGUE TDD RELIGIOSAMENTE**: Red-Green-Refactor
3. **PREGUNTA SI TIENES DUDAS** sobre estándares o arquitectura
4. **REFERENCIA OTROS DOCUMENTOS** cuando sea necesario
5. **MANTÉN CONSISTENCIA** con el código existente
6. **PRIORIZA CALIDAD SOBRE VELOCIDAD**

**Recuerda:** Un buen test es más valioso que código rápido pero frágil.

---

**Versión:** 1.0  
**Última Actualización:** Febrero 2026  
**Mantenido por:** David Buitrago

¡Feliz desarrollo con TDD! 🚀
