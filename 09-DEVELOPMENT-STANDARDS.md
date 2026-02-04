# 09 - ESTÁNDARES DE DESARROLLO: CISO Digital

## 1. CONVENCIONES DE CÓDIGO

### 1.1 Python (Backend)

**Style Guide:** PEP 8 + Type Hints

```python
# ✅ CORRECTO

from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel

async def calculate_risk_score(
    vulnerabilities: List[Vulnerability],
    asset_criticality: str,
    context: Optional[Dict] = None
) -> float:
    """
    Calcula el score de riesgo basado en vulnerabilidades.
    
    Args:
        vulnerabilities: Lista de vulnerabilidades detectadas
        asset_criticality: Criticidad del asset (critical|high|medium|low)
        context: Contexto adicional opcional
        
    Returns:
        float: Risk score entre 0.0 y 10.0
        
    Raises:
        ValueError: Si asset_criticality es inválido
    """
    if not vulnerabilities:
        return 0.0
        
    base_score = sum(v.cvss_score for v in vulnerabilities) / len(vulnerabilities)
    
    # Ajustar por criticidad del asset
    criticality_multiplier = {
        "critical": 1.5,
        "high": 1.2,
        "medium": 1.0,
        "low": 0.8
    }
    
    multiplier = criticality_multiplier.get(asset_criticality)
    if multiplier is None:
        raise ValueError(f"Invalid criticality: {asset_criticality}")
        
    return min(base_score * multiplier, 10.0)


# ❌ INCORRECTO

def calcRiskScore(vulns, crit, ctx=None):  # No type hints, camelCase
    if len(vulns)==0: return 0  # No spacing, inline
    score=sum([v.score for v in vulns])/len(vulns)  # No spacing
    # No docstring, nombres poco descriptivos
    m={"critical":1.5,"high":1.2}[crit]  # Puede fallar sin try/except
    return score*m
```

**Reglas de Naming:**
```python
# Variables y funciones: snake_case
user_email = "user@example.com"
def get_user_by_id(user_id: str) -> User:
    pass

# Clases: PascalCase
class RiskAssessmentAgent:
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_RETRIES = 3
API_TIMEOUT_SECONDS = 30

# Private methods/attributes: _prefijo
class MyClass:
    def __init__(self):
        self._internal_state = {}
    
    def _private_method(self):
        pass

# Enums: PascalCase para clase, UPPER para valores
class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

**Type Hints Obligatorios:**
```python
# ✅ Siempre usar type hints
async def process_incident(
    incident_id: str,
    auto_respond: bool = False
) -> IncidentResponse:
    pass

# Para tipos complejos
from typing import List, Dict, Optional, Union

def aggregate_metrics(
    data: Dict[str, List[float]]
) -> Dict[str, float]:
    pass

# Para callbacks
from typing import Callable

def register_callback(
    event: str,
    callback: Callable[[Event], None]
) -> None:
    pass
```

**Async/Await:**
```python
# ✅ CORRECTO - Usar async para I/O operations

async def get_user(user_id: str) -> User:
    """Database query es I/O bound"""
    async with db.session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

async def call_llm(prompt: str) -> str:
    """API call es I/O bound"""
    response = await anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


# ❌ INCORRECTO - No usar async para CPU bound

async def calculate_hash(data: str) -> str:
    """Este es CPU bound, no necesita async"""
    import hashlib
    return hashlib.sha256(data.encode()).hexdigest()

# ✅ CORRECTO - Sin async
def calculate_hash(data: str) -> str:
    import hashlib
    return hashlib.sha256(data.encode()).hexdigest()
```

**Error Handling:**
```python
# ✅ CORRECTO

from typing import Optional
import logging

logger = logging.getLogger(__name__)

async def fetch_risk_data(risk_id: str) -> Optional[Risk]:
    """
    Fetch risk with proper error handling.
    
    Returns None if not found, raises for other errors.
    """
    try:
        risk = await db.get(Risk, risk_id)
        if risk is None:
            logger.warning(f"Risk {risk_id} not found")
            return None
        return risk
        
    except DatabaseConnectionError as e:
        logger.error(f"Database connection failed: {e}")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error fetching risk {risk_id}: {e}")
        raise


# ❌ INCORRECTO

async def fetch_risk_data(risk_id):
    try:
        return await db.get(Risk, risk_id)
    except:  # Never use bare except
        print("Error")  # Don't use print, use logger
        return None  # Don't hide all errors
```

### 1.2 TypeScript (Frontend)

**Style Guide:** Airbnb + Prettier

```typescript
// ✅ CORRECTO

import { useState, useEffect } from 'react';
import { Risk } from '@/types';
import { fetchRisks } from '@/api';

interface RiskListProps {
  severity?: 'critical' | 'high' | 'medium' | 'low';
  onRiskSelect?: (risk: Risk) => void;
}

export const RiskList: React.FC<RiskListProps> = ({ 
  severity, 
  onRiskSelect 
}) => {
  const [risks, setRisks] = useState<Risk[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const loadRisks = async () => {
      try {
        setLoading(true);
        const data = await fetchRisks({ severity });
        setRisks(data);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    loadRisks();
  }, [severity]);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div className="risk-list">
      {risks.map((risk) => (
        <RiskCard 
          key={risk.id} 
          risk={risk}
          onClick={() => onRiskSelect?.(risk)}
        />
      ))}
    </div>
  );
};

// ❌ INCORRECTO

export const RiskList = (props) => {  // No types
  const [risks, setRisks] = useState([]);  // No generic type
  
  useEffect(() => {
    fetchRisks().then(data => setRisks(data));  // No error handling
  });  // Missing dependency array
  
  return (
    <div>
      {risks.map(r => <RiskCard risk={r} />)}  // No key
    </div>
  );
}
```

### 1.3 SQL

```sql
-- ✅ CORRECTO

-- Keywords en mayúsculas
-- Nombres de tablas/columnas en snake_case
-- Comentarios descriptivos

-- Get all critical risks created in last 7 days
SELECT 
    r.id,
    r.risk_number,
    r.title,
    r.severity,
    r.created_at,
    a.name AS asset_name
FROM risks r
INNER JOIN assets a ON r.asset_id = a.id
WHERE 
    r.severity = 'critical'
    AND r.created_at >= NOW() - INTERVAL '7 days'
    AND r.status IN ('open', 'in_progress')
ORDER BY r.created_at DESC
LIMIT 100;

-- ❌ INCORRECTO

-- sin comentarios, keywords mezclados, mal formateado
select * from risks where severity='critical' and created_at>now()-interval '7 days'
```

## 2. ESTRUCTURA DE PROYECTO

### 2.1 Backend (Python)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry
│   ├── config.py              # Settings con pydantic-settings
│   ├── database.py            # DB connection & session
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py    # Shared dependencies
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   ├── risks.py
│   │   │   ├── incidents.py
│   │   │   └── compliance.py
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── logging.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── orchestrator.py
│   │   ├── risk_agent.py
│   │   ├── incident_agent.py
│   │   └── ...
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py            # SQLAlchemy Base
│   │   ├── user.py
│   │   ├── risk.py
│   │   ├── incident.py
│   │   └── ...
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py            # Pydantic schemas
│   │   ├── risk.py
│   │   └── ...
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py
│   │   ├── rag_service.py
│   │   ├── embedding_service.py
│   │   ├── vector_store.py
│   │   ├── cache_service.py
│   │   └── notification_service.py
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   ├── scheduler.py
│   │   └── background_jobs.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py
│       ├── validators.py
│       └── exceptions.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── unit/
│   │   ├── test_agents.py
│   │   └── test_services.py
│   ├── integration/
│   │   └── test_api.py
│   └── e2e/
│       └── test_flows.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── scripts/
│   ├── seed_db.py
│   └── ingest_documents.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt       # Dev dependencies
├── pytest.ini
├── mypy.ini
├── Dockerfile
└── docker-compose.yml
```

### 2.2 Frontend (React)

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Modal.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   └── features/
│   │       ├── RiskList.tsx
│   │       ├── RiskCard.tsx
│   │       └── ChatInterface.tsx
│   │
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Risks.tsx
│   │   ├── Incidents.tsx
│   │   └── Compliance.tsx
│   │
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── websocket.ts
│   │
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useRisks.ts
│   │   └── useWebSocket.ts
│   │
│   ├── store/
│   │   ├── authStore.ts
│   │   └── riskStore.ts
│   │
│   ├── types/
│   │   ├── risk.ts
│   │   ├── incident.ts
│   │   └── api.ts
│   │
│   ├── utils/
│   │   ├── formatters.ts
│   │   └── validators.ts
│   │
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
│
├── public/
├── .env.example
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## 3. GIT WORKFLOW

### 3.1 Branch Strategy

```
main (production)
  ↑
develop (staging)
  ↑
feature/CISO-123-risk-assessment
feature/CISO-124-compliance-check
bugfix/CISO-125-chat-error
hotfix/CISO-126-security-patch
```

**Convenciones:**
- `feature/*` - Nuevas features
- `bugfix/*` - Bugs no críticos
- `hotfix/*` - Bugs críticos en producción
- `refactor/*` - Refactorings sin cambio de funcionalidad
- `docs/*` - Solo documentación

### 3.2 Commit Messages

**Formato:** `type(scope): subject`

```bash
# ✅ CORRECTO

feat(agents): add ProactiveReviewAgent
fix(api): resolve race condition in chat endpoint
docs(readme): update installation instructions
refactor(rag): improve vector search performance
test(agents): add unit tests for RiskAgent
chore(deps): update dependencies to latest

# Con cuerpo del mensaje
feat(compliance): add automated ISO 27001 checks

- Implement check for control A.8.1
- Add evidence collection
- Generate compliance report

Closes #123

# ❌ INCORRECTO

Added feature  # Vago, no sigue formato
Fix bug  # No especifica qué bug
WIP  # Work in progress no debe commitearse
Updated files  # Muy genérico
```

**Types:**
- `feat` - Nueva feature
- `fix` - Bug fix
- `docs` - Documentación
- `style` - Formateo, no cambia código
- `refactor` - Refactoring sin cambio de funcionalidad
- `test` - Agregar o modificar tests
- `chore` - Mantenimiento, deps, config

### 3.3 Pull Requests

**Template:**
```markdown
## Descripción
Breve descripción del cambio

## Tipo de cambio
- [ ] Bug fix
- [ ] Nueva feature
- [ ] Breaking change
- [ ] Refactor
- [ ] Documentación

## ¿Cómo se ha probado?
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Checklist
- [ ] Mi código sigue los estándares del proyecto
- [ ] He agregado tests
- [ ] He actualizado la documentación
- [ ] Los tests pasan localmente
- [ ] He hecho self-review del código

## Screenshots (si aplica)

## Issues relacionados
Closes #123
```

**Review Process:**
1. Self-review antes de crear PR
2. Automated checks (CI) deben pasar
3. Al menos 1 approval requerido (en equipo futuro)
4. Squash and merge a develop

## 4. TESTING

### 4.1 Pytest (Backend)

```python
# tests/unit/test_risk_agent.py

import pytest
from app.agents.risk_agent import RiskAssessmentAgent
from app.models import Risk, Asset, Vulnerability

@pytest.fixture
async def risk_agent(db_session):
    """Fixture para RiskAssessmentAgent"""
    return RiskAssessmentAgent(
        llm_service=mock_llm_service(),
        rag_service=mock_rag_service(),
        db_session=db_session
    )

@pytest.fixture
async def sample_asset(db_session):
    """Asset de prueba"""
    asset = Asset(
        name="Test Server",
        type="server",
        criticality="high"
    )
    db_session.add(asset)
    await db_session.commit()
    return asset

@pytest.mark.asyncio
async def test_risk_assessment_with_vulnerabilities(
    risk_agent,
    sample_asset
):
    """Test evaluación de riesgo con vulnerabilidades"""
    # Arrange
    vulnerabilities = [
        Vulnerability(cvss_score=9.8, cve_id="CVE-2025-1234"),
        Vulnerability(cvss_score=7.5, cve_id="CVE-2025-5678")
    ]
    
    # Act
    result = await risk_agent.assess_risk(
        asset=sample_asset,
        vulnerabilities=vulnerabilities
    )
    
    # Assert
    assert result.risk_score > 7.0
    assert result.severity == "high"
    assert len(result.recommendations) > 0

@pytest.mark.asyncio
async def test_risk_assessment_no_vulnerabilities(
    risk_agent,
    sample_asset
):
    """Test con asset sin vulnerabilidades"""
    # Act
    result = await risk_agent.assess_risk(
        asset=sample_asset,
        vulnerabilities=[]
    )
    
    # Assert
    assert result.risk_score == 0.0
    assert result.severity == "low"
```

**Coverage Target:** >80%

```bash
# Run tests con coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run solo unit tests
pytest tests/unit/

# Run con verbose
pytest -v

# Run tests específicos
pytest tests/unit/test_agents.py::test_risk_assessment
```

### 4.2 Jest (Frontend)

```typescript
// src/components/RiskCard.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import { RiskCard } from './RiskCard';
import { Risk } from '@/types';

const mockRisk: Risk = {
  id: '123',
  title: 'Critical Vulnerability',
  severity: 'critical',
  status: 'open',
  created_at: '2026-02-04T08:00:00Z'
};

describe('RiskCard', () => {
  it('renders risk information correctly', () => {
    render(<RiskCard risk={mockRisk} />);
    
    expect(screen.getByText('Critical Vulnerability')).toBeInTheDocument();
    expect(screen.getByText('CRITICAL')).toBeInTheDocument();
    expect(screen.getByText('Open')).toBeInTheDocument();
  });

  it('calls onClick when card is clicked', () => {
    const handleClick = jest.fn();
    render(<RiskCard risk={mockRisk} onClick={handleClick} />);
    
    fireEvent.click(screen.getByRole('article'));
    
    expect(handleClick).toHaveBeenCalledWith(mockRisk);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies correct severity color', () => {
    const { container } = render(<RiskCard risk={mockRisk} />);
    
    const badge = container.querySelector('.severity-badge');
    expect(badge).toHaveClass('bg-red-500');
  });
});
```

## 5. LINTING Y FORMATTING

### 5.1 Python

**Tools:**
- **Black** - Code formatter (opinionated)
- **Ruff** - Fast linter (replaces flake8, isort)
- **mypy** - Type checker

```toml
# pyproject.toml

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'

[tool.ruff]
line-length = 100
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = ["E501"]  # Line too long (handled by black)

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**Pre-commit Hook:**
```yaml
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.15
    hooks:
      - id: ruff

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

### 5.2 TypeScript

**Tools:**
- **Prettier** - Code formatter
- **ESLint** - Linter

```json
// .eslintrc.json

{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "prettier"
  ],
  "rules": {
    "react/react-in-jsx-scope": "off",
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "@typescript-eslint/no-explicit-any": "error"
  }
}
```

```json
// .prettierrc

{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

## 6. DOCUMENTACIÓN

### 6.1 Code Documentation

**Python - Docstrings (Google Style):**
```python
def complex_function(
    param1: str,
    param2: int,
    param3: Optional[Dict] = None
) -> List[Result]:
    """
    Brief description of what the function does.
    
    More detailed explanation if needed. Can span multiple lines.
    Explain the logic, important considerations, edge cases.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        param3: Optional description of param3. Defaults to None.
        
    Returns:
        List of Result objects containing...
        
    Raises:
        ValueError: If param2 is negative
        DatabaseError: If database connection fails
        
    Example:
        >>> results = complex_function("test", 42)
        >>> len(results)
        5
    """
    pass
```

**TypeScript - JSDoc:**
```typescript
/**
 * Fetches risks from the API with optional filters.
 *
 * @param filters - Optional filters to apply
 * @param filters.severity - Filter by severity level
 * @param filters.status - Filter by status
 * @returns Promise resolving to array of Risk objects
 * @throws {ApiError} If the API request fails
 *
 * @example
 * ```ts
 * const risks = await fetchRisks({ severity: 'critical' });
 * console.log(risks.length);
 * ```
 */
export async function fetchRisks(
  filters?: RiskFilters
): Promise<Risk[]> {
  // ...
}
```

### 6.2 API Documentation

**OpenAPI/Swagger** - Auto-generado por FastAPI

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title="CISO Digital API",
    description="API para CISO Digital con IA",
    version="1.0.0"
)

class RiskCreate(BaseModel):
    """Schema para crear un nuevo riesgo"""
    
    title: str = Field(..., description="Título del riesgo", min_length=5, max_length=255)
    description: str = Field(..., description="Descripción detallada")
    severity: str = Field(..., description="Severidad", regex="^(critical|high|medium|low)$")

@app.post(
    "/risks",
    response_model=Risk,
    status_code=201,
    summary="Crear nuevo riesgo",
    description="Crea un nuevo riesgo de seguridad en el sistema",
    tags=["Risks"]
)
async def create_risk(
    risk: RiskCreate,
    user: User = Depends(get_current_user)
):
    """
    Endpoint para crear un nuevo riesgo.
    
    - **title**: Título descriptivo del riesgo
    - **description**: Descripción detallada
    - **severity**: Nivel de severidad (critical, high, medium, low)
    """
    # Implementation
    pass
```

## 7. LOGGING

### 7.1 Structured Logging

```python
import logging
import structlog

# Configurar structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger(__name__)

# ✅ CORRECTO - Structured logging

logger.info(
    "risk_assessed",
    risk_id="RISK-2026-001",
    risk_score=8.5,
    asset_id="asset-123",
    agent="risk_assessment",
    duration_ms=450
)

logger.error(
    "api_call_failed",
    provider="anthropic",
    endpoint="/v1/messages",
    status_code=429,
    retry_count=3,
    exc_info=True
)

# ❌ INCORRECTO

logger.info("Risk assessed")  # No context
print(f"Error: {e}")  # Never use print
```

### 7.2 Log Levels

```python
# CRITICAL - System is unusable
logger.critical("database_unavailable", error=str(e))

# ERROR - Error that needs attention
logger.error("api_call_failed", provider="openai", error=str(e))

# WARNING - Something unexpected but handled
logger.warning("rate_limit_approaching", current_rate=95, limit=100)

# INFO - Normal but significant events
logger.info("risk_created", risk_id=risk.id, severity=risk.severity)

# DEBUG - Detailed information for debugging
logger.debug("query_executed", query=query, duration_ms=45)
```

## 8. SEGURIDAD

### 8.1 Secrets Management

```python
# ✅ CORRECTO

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuration from environment variables"""
    
    database_url: str
    redis_url: str
    anthropic_api_key: str
    openai_api_key: str
    secret_key: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# ❌ INCORRECTO

API_KEY = "sk-ant-1234..."  # Hardcoded secret
DATABASE_URL = "postgresql://user:password@localhost/db"  # In code
```

**`.env` example:**
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/ciso_db
REDIS_URL=redis://localhost:6379
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
SECRET_KEY=generate-with-secrets-token-urlsafe-32
```

**Never commit:**
- `.env` → Add to `.gitignore`
- API keys
- Passwords
- Private keys

### 8.2 Input Validation

```python
# ✅ CORRECTO - Pydantic validation

from pydantic import BaseModel, validator, Field
from typing import Literal

class RiskCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    severity: Literal["critical", "high", "medium", "low"]
    
    @validator('title')
    def title_must_not_be_sql_injection(cls, v):
        dangerous = ["DROP", "DELETE", "INSERT", "UPDATE", "--"]
        if any(word in v.upper() for word in dangerous):
            raise ValueError("Potential SQL injection detected")
        return v

# SQL queries - Always use parametrized
async def get_risk(risk_id: str):
    # ✅ CORRECTO
    query = "SELECT * FROM risks WHERE id = $1"
    result = await db.execute(query, risk_id)
    
    # ❌ INCORRECTO - SQL Injection
    query = f"SELECT * FROM risks WHERE id = '{risk_id}'"
    result = await db.execute(query)
```

---

**Versión:** 1.0  
**Última Actualización:** Febrero 2026  
**Finalizado:** ¡Stack completo definido! 🎉
