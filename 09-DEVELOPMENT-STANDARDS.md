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
│   │   ├── copilot_client_service.py  # GitHub Copilot SDK wrapper
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

## 7. GITHUB COPILOT SDK BEST PRACTICES

### 7.1 Configuración y Cliente

**Inicialización del Cliente:**
```python
# ✅ CORRECTO - Copilot Client Service

from copilot import CopilotClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class CopilotClientService:
    """Service para manejar GitHub Copilot SDK con fallback a Azure"""
    
    def __init__(self):
        """
        Inicializa el cliente de Copilot.
        
        GitHub token se auto-detecta de:
        1. Variable de entorno GITHUB_TOKEN
        2. Configuración de git (~/.gitconfig)
        3. GitHub CLI (gh)
        """
        self.client = CopilotClient()
        self.primary_model = "claude-sonnet-4.5"
        self.fallback_model = "gpt-4"
        
    async def create_session(
        self,
        system_prompt: str,
        tools: list,
        temperature: float = 0.7,
        use_azure_fallback: bool = False
    ):
        """
        Crea una sesión de chat con Copilot SDK.
        
        Args:
            system_prompt: System prompt para el agente
            tools: Lista de tools definidas con @define_tool
            temperature: Temperatura para generación (0.0-1.0)
            use_azure_fallback: Si True, usa Azure OpenAI en lugar de Copilot
            
        Returns:
            Session object para interactuar con el modelo
        """
        try:
            if use_azure_fallback:
                logger.info("Using Azure OpenAI fallback")
                return await self._create_azure_session(
                    system_prompt, tools, temperature
                )
            
            logger.info(f"Creating Copilot session with {self.primary_model}")
            session = await self.client.create_session({
                "model": self.primary_model,
                "system": system_prompt,
                "tools": tools,
                "temperature": temperature,
                "max_tokens": 4096
            })
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to create Copilot session: {e}", exc_info=True)
            logger.warning("Falling back to Azure OpenAI")
            return await self._create_azure_session(
                system_prompt, tools, temperature
            )
    
    async def _create_azure_session(
        self,
        system_prompt: str,
        tools: list,
        temperature: float
    ):
        """Crea sesión con Azure OpenAI como fallback"""
        return await self.client.create_session({
            "model": self.fallback_model,
            "system": system_prompt,
            "tools": tools,
            "temperature": temperature,
            "provider": {
                "type": "azure",
                "base_url": settings.AZURE_OPENAI_ENDPOINT,
                "api_key": settings.AZURE_OPENAI_KEY
            }
        })

# ❌ INCORRECTO - Hardcoded API keys, no fallback

from anthropic import Anthropic

client = Anthropic(api_key="sk-ant-hardcoded-key")  # Never hardcode!
# No fallback, no error handling
```

### 7.2 Definición de Tools

**Usar Decorador `@define_tool`:**
```python
# ✅ CORRECTO - Tool definition con type hints y docstring

from copilot.tools import define_tool
from typing import List, Optional

@define_tool(description="Search security knowledge base for relevant information")
async def search_knowledge_base(
    query: str,
    collection: str = "security_knowledge",
    top_k: int = 5
) -> dict:
    """
    Busca información en la knowledge base usando búsqueda semántica.
    
    Args:
        query: Consulta de búsqueda en lenguaje natural
        collection: Colección de Qdrant a buscar (default: security_knowledge)
        top_k: Número máximo de resultados a retornar
        
    Returns:
        Dict con resultados encontrados y metadatos:
        {
            "results": [
                {"content": "...", "score": 0.95, "metadata": {...}},
                ...
            ],
            "total_found": 5
        }
    """
    logger.info(
        "searching_knowledge_base",
        query=query,
        collection=collection,
        top_k=top_k
    )
    
    try:
        results = await rag_service.search(
            query=query,
            collection=collection,
            limit=top_k
        )
        
        return {
            "results": [
                {
                    "content": r.payload.get("content"),
                    "score": r.score,
                    "metadata": r.payload.get("metadata", {})
                }
                for r in results
            ],
            "total_found": len(results)
        }
        
    except Exception as e:
        logger.error(f"Knowledge base search failed: {e}", exc_info=True)
        return {"results": [], "total_found": 0, "error": str(e)}


@define_tool(description="Calculate risk score based on vulnerabilities and asset criticality")
async def calculate_risk_score(
    cvss_scores: List[float],
    asset_criticality: str,
    existing_controls: Optional[List[str]] = None
) -> dict:
    """
    Calcula el risk score considerando vulnerabilidades, criticidad y controles.
    
    Args:
        cvss_scores: Lista de CVSS scores de vulnerabilidades (0.0-10.0)
        asset_criticality: Criticidad del asset (critical|high|medium|low)
        existing_controls: Controles de seguridad existentes (opcional)
        
    Returns:
        Dict con score calculado y detalles:
        {
            "risk_score": 8.5,
            "severity": "high",
            "factors": {...},
            "recommendations": [...]
        }
    """
    # Validación
    if not all(0.0 <= score <= 10.0 for score in cvss_scores):
        return {"error": "CVSS scores must be between 0.0 and 10.0"}
    
    valid_criticalities = ["critical", "high", "medium", "low"]
    if asset_criticality not in valid_criticalities:
        return {"error": f"Invalid criticality. Must be one of {valid_criticalities}"}
    
    # Cálculo
    avg_cvss = sum(cvss_scores) / len(cvss_scores) if cvss_scores else 0.0
    
    criticality_multiplier = {
        "critical": 1.5,
        "high": 1.2,
        "medium": 1.0,
        "low": 0.8
    }[asset_criticality]
    
    controls_reduction = len(existing_controls or []) * 0.1
    
    risk_score = min(
        avg_cvss * criticality_multiplier - controls_reduction,
        10.0
    )
    
    severity = (
        "critical" if risk_score >= 9.0 else
        "high" if risk_score >= 7.0 else
        "medium" if risk_score >= 4.0 else
        "low"
    )
    
    return {
        "risk_score": round(risk_score, 2),
        "severity": severity,
        "factors": {
            "avg_cvss": avg_cvss,
            "criticality_multiplier": criticality_multiplier,
            "controls_reduction": controls_reduction
        },
        "recommendations": _generate_recommendations(risk_score, asset_criticality)
    }


# ❌ INCORRECTO - Sin decorador, sin types, sin docstring

def search_kb(query):  # Sin type hints
    return rag.search(query)  # No async, no error handling, no logging
```

### 7.3 BaseAgent Pattern con Copilot SDK

**Implementación de BaseAgent:**
```python
# ✅ CORRECTO - BaseAgent con Copilot SDK

from abc import ABC, abstractmethod
from copilot import CopilotClient
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Clase base para todos los agentes del sistema.
    
    Todos los agentes deben heredar de esta clase e implementar:
    - get_system_prompt(): Retorna el system prompt del agente
    - get_tools(): Retorna lista de tools disponibles
    - process_request(): Lógica específica del agente
    """
    
    def __init__(
        self,
        copilot_client: CopilotClient,
        rag_service,
        db_session
    ):
        """
        Inicializa el agente base.
        
        Args:
            copilot_client: Cliente de GitHub Copilot SDK
            rag_service: Servicio de RAG para búsquedas
            db_session: Sesión de base de datos
        """
        self.client = copilot_client
        self.rag = rag_service
        self.db = db_session
        self.session = None
        self.conversation_history = []
        
    @abstractmethod
    async def get_system_prompt(self) -> str:
        """
        Retorna el system prompt específico del agente.
        
        Este método debe ser implementado por cada agente especializado.
        """
        pass
    
    @abstractmethod
    def get_tools(self) -> List:
        """
        Retorna lista de tools disponibles para este agente.
        
        Las tools deben estar definidas con @define_tool decorator.
        """
        pass
    
    async def initialize_session(self, temperature: float = 0.7):
        """
        Inicializa una sesión de Copilot para este agente.
        
        Args:
            temperature: Temperatura para generación (0.0 = determinística, 1.0 = creativa)
        """
        logger.info(
            "initializing_agent_session",
            agent=self.__class__.__name__,
            temperature=temperature
        )
        
        try:
            self.session = await self.client.create_session({
                "model": "claude-sonnet-4.5",
                "system": await self.get_system_prompt(),
                "tools": self.get_tools(),
                "temperature": temperature
            })
            
            logger.info("agent_session_initialized", agent=self.__class__.__name__)
            
        except Exception as e:
            logger.error(f"Failed to initialize session: {e}", exc_info=True)
            await self.fallback_to_azure()
    
    async def fallback_to_azure(self):
        """Fallback a Azure OpenAI si Copilot falla"""
        logger.warning("Falling back to Azure OpenAI")
        
        self.session = await self.client.create_session({
            "model": "gpt-4",
            "system": await self.get_system_prompt(),
            "tools": self.get_tools(),
            "provider": {
                "type": "azure",
                "base_url": settings.AZURE_OPENAI_ENDPOINT,
                "api_key": settings.AZURE_OPENAI_KEY
            }
        })
    
    async def chat(self, user_message: str) -> Dict[str, Any]:
        """
        Envía un mensaje al agente y retorna la respuesta.
        
        El SDK maneja automáticamente:
        - Tool calling y execution
        - Retry logic
        - Context management
        
        Args:
            user_message: Mensaje del usuario
            
        Returns:
            Dict con respuesta del agente y metadatos
        """
        if not self.session:
            await self.initialize_session()
        
        logger.info(
            "agent_processing_message",
            agent=self.__class__.__name__,
            message_length=len(user_message)
        )
        
        try:
            # Copilot SDK automáticamente ejecuta tools si es necesario
            response = await self.session.chat(user_message)
            
            # Guardar en historial
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })
            
            logger.info(
                "agent_response_generated",
                agent=self.__class__.__name__,
                tools_used=len(response.tool_calls or []),
                response_length=len(response.content)
            )
            
            return {
                "success": True,
                "response": response.content,
                "tool_calls": response.tool_calls,
                "model_used": response.model
            }
            
        except Exception as e:
            logger.error(f"Chat failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una request específica del agente.
        
        Este método debe ser implementado por cada agente especializado
        con su lógica de negocio específica.
        """
        pass


# ❌ INCORRECTO - Sin abstracción, hardcoded model, no fallback

class BadAgent:
    def __init__(self):
        self.client = Anthropic(api_key="hardcoded")  # Bad!
    
    def chat(self, msg):  # No async, no types, no error handling
        return self.client.messages.create(
            model="claude-3-opus",  # Hardcoded, no fallback
            messages=[{"role": "user", "content": msg}]
        )
```

### 7.4 Ejemplo de Agente Especializado

**RiskAssessmentAgent con Copilot SDK:**
```python
# ✅ CORRECTO - Agente especializado completo

from app.agents.base_agent import BaseAgent
from copilot.tools import define_tool
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class RiskAssessmentAgent(BaseAgent):
    """
    Agente especializado en evaluación de riesgos de seguridad.
    
    Capacidades:
    - Análisis de vulnerabilidades
    - Cálculo de risk scores
    - Generación de recomendaciones
    - Priorización de mitigaciones
    """
    
    async def get_system_prompt(self) -> str:
        """System prompt para RiskAssessmentAgent"""
        return """Eres un agente experto en evaluación de riesgos de ciberseguridad.

Tu rol es:
1. Analizar vulnerabilidades y amenazas
2. Calcular risk scores considerando CVSS, criticidad de assets y controles existentes
3. Generar recomendaciones de mitigación priorizadas
4. Buscar información en la knowledge base cuando sea necesario

Principios:
- Sé preciso con los cálculos de riesgo
- Prioriza riesgos críticos (score >= 9.0)
- Considera el contexto del negocio
- Recomienda mitigaciones prácticas y accionables

Usa las tools disponibles para:
- search_vulnerabilities: Buscar vulnerabilidades en assets
- calculate_risk_score: Calcular scores de riesgo
- get_mitigation_recommendations: Obtener recomendaciones específicas
"""
    
    def get_tools(self) -> List:
        """Tools disponibles para este agente"""
        return [
            self._search_vulnerabilities,
            self._calculate_risk_score,
            self._get_mitigation_recommendations
        ]
    
    @define_tool(description="Search for vulnerabilities in a specific asset")
    async def _search_vulnerabilities(
        self,
        asset_id: str,
        severity_filter: str = None
    ) -> dict:
        """Busca vulnerabilidades en un asset específico"""
        logger.info("searching_vulnerabilities", asset_id=asset_id)
        
        query = f"vulnerabilities asset:{asset_id}"
        if severity_filter:
            query += f" severity:{severity_filter}"
        
        results = await self.rag.search(
            query=query,
            collection="vulnerabilities",
            limit=10
        )
        
        return {
            "asset_id": asset_id,
            "vulnerabilities_found": len(results),
            "results": [
                {
                    "cve_id": r.payload.get("cve_id"),
                    "cvss_score": r.payload.get("cvss_score"),
                    "description": r.payload.get("description"),
                    "severity": r.payload.get("severity")
                }
                for r in results
            ]
        }
    
    @define_tool(description="Calculate risk score for given parameters")
    async def _calculate_risk_score(
        self,
        threat_level: float,
        asset_criticality: str,
        existing_controls: List[str] = None
    ) -> dict:
        """Calcula risk score"""
        # Implementación similar al ejemplo anterior
        pass
    
    @define_tool(description="Get mitigation recommendations for vulnerability type")
    async def _get_mitigation_recommendations(
        self,
        vulnerability_type: str,
        asset_type: str
    ) -> dict:
        """Obtiene recomendaciones de mitigación"""
        logger.info(
            "getting_recommendations",
            vuln_type=vulnerability_type,
            asset_type=asset_type
        )
        
        query = f"mitigation recommendations {vulnerability_type} {asset_type}"
        results = await self.rag.search(
            query=query,
            collection="security_knowledge",
            limit=5
        )
        
        return {
            "recommendations": [
                {
                    "title": r.payload.get("title"),
                    "description": r.payload.get("description"),
                    "priority": r.payload.get("priority"),
                    "estimated_effort": r.payload.get("effort")
                }
                for r in results
            ]
        }
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una request de evaluación de riesgo.
        
        Args:
            request: Dict con:
                - asset_id: ID del asset a evaluar
                - include_recommendations: Si incluir recomendaciones
                
        Returns:
            Dict con evaluación completa de riesgo
        """
        asset_id = request.get("asset_id")
        include_recommendations = request.get("include_recommendations", True)
        
        logger.info("processing_risk_assessment", asset_id=asset_id)
        
        # Construir mensaje para el agente
        message = f"""Evalúa el riesgo del asset {asset_id}.

Pasos:
1. Busca vulnerabilidades usando search_vulnerabilities
2. Calcula el risk score usando calculate_risk_score
3. {"Genera recomendaciones usando get_mitigation_recommendations" if include_recommendations else ""}

Proporciona un análisis completo y priorizado."""
        
        # El SDK automáticamente ejecuta las tools necesarias
        response = await self.chat(message)
        
        return response
```

### 7.5 Session Management y Context

**Manejo de Contexto:**
```python
# ✅ CORRECTO - Mantener contexto entre llamadas

class ConversationManager:
    """Maneja sesiones de conversación con contexto"""
    
    def __init__(self, copilot_client: CopilotClient):
        self.client = copilot_client
        self.active_sessions: Dict[str, Any] = {}
    
    async def get_or_create_session(
        self,
        user_id: str,
        agent_type: str
    ):
        """Obtiene sesión existente o crea una nueva"""
        session_key = f"{user_id}:{agent_type}"
        
        if session_key not in self.active_sessions:
            logger.info("creating_new_session", user_id=user_id, agent=agent_type)
            
            agent = self._get_agent_instance(agent_type)
            await agent.initialize_session()
            
            self.active_sessions[session_key] = {
                "agent": agent,
                "created_at": datetime.now(),
                "message_count": 0
            }
        
        return self.active_sessions[session_key]["agent"]
    
    async def clear_session(self, user_id: str, agent_type: str):
        """Limpia una sesión específica"""
        session_key = f"{user_id}:{agent_type}"
        if session_key in self.active_sessions:
            logger.info("clearing_session", session_key=session_key)
            del self.active_sessions[session_key]
    
    async def cleanup_old_sessions(self, max_age_minutes: int = 30):
        """Limpia sesiones inactivas"""
        now = datetime.now()
        to_remove = []
        
        for key, session in self.active_sessions.items():
            age = (now - session["created_at"]).total_seconds() / 60
            if age > max_age_minutes:
                to_remove.append(key)
        
        for key in to_remove:
            logger.info("removing_inactive_session", session_key=key)
            del self.active_sessions[key]
```

### 7.6 Error Handling y Fallback

**Manejo Robusto de Errores:**
```python
# ✅ CORRECTO - Error handling con fallback automático

async def safe_agent_call(
    agent: BaseAgent,
    message: str,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Llama a un agente con retry logic y fallback.
    
    Args:
        agent: Instancia del agente
        message: Mensaje a enviar
        max_retries: Número máximo de reintentos
        
    Returns:
        Respuesta del agente o error detallado
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            logger.info(
                "agent_call_attempt",
                agent=agent.__class__.__name__,
                attempt=attempt + 1
            )
            
            response = await agent.chat(message)
            
            if response["success"]:
                return response
            
            # Si falla, intentar con Azure fallback
            if attempt == 0:
                logger.warning("Primary failed, trying Azure fallback")
                await agent.fallback_to_azure()
                continue
            
        except RateLimitError as e:
            logger.warning(f"Rate limit hit, waiting before retry: {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            last_error = e
            
        except Exception as e:
            logger.error(f"Agent call failed: {e}", exc_info=True)
            last_error = e
            
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
    
    # Todos los reintentos fallaron
    logger.error(
        "all_agent_retries_failed",
        agent=agent.__class__.__name__,
        retries=max_retries
    )
    
    return {
        "success": False,
        "error": f"Failed after {max_retries} attempts: {str(last_error)}",
        "last_error_type": type(last_error).__name__
    }
```

### 7.7 Testing de Agentes con Copilot SDK

**Unit Tests para Agentes:**
```python
# ✅ CORRECTO - Test de agente con mocks

import pytest
from unittest.mock import AsyncMock, Mock, patch
from app.agents.risk_agent import RiskAssessmentAgent

@pytest.fixture
async def mock_copilot_client():
    """Mock del CopilotClient"""
    client = AsyncMock()
    
    # Mock de session
    session = AsyncMock()
    session.chat = AsyncMock(return_value=Mock(
        content="Risk score calculado: 8.5",
        tool_calls=[],
        model="claude-sonnet-4.5"
    ))
    
    client.create_session = AsyncMock(return_value=session)
    
    return client

@pytest.fixture
async def risk_agent(mock_copilot_client, db_session, rag_service):
    """Fixture del RiskAssessmentAgent"""
    return RiskAssessmentAgent(
        copilot_client=mock_copilot_client,
        rag_service=rag_service,
        db_session=db_session
    )

@pytest.mark.asyncio
async def test_risk_agent_initializes_session(risk_agent, mock_copilot_client):
    """Test que el agente inicializa sesión correctamente"""
    # Act
    await risk_agent.initialize_session()
    
    # Assert
    mock_copilot_client.create_session.assert_called_once()
    call_args = mock_copilot_client.create_session.call_args[0][0]
    
    assert call_args["model"] == "claude-sonnet-4.5"
    assert "tools" in call_args
    assert len(call_args["tools"]) == 3  # 3 tools del RiskAgent

@pytest.mark.asyncio
async def test_risk_agent_processes_request(risk_agent):
    """Test que el agente procesa request correctamente"""
    # Arrange
    request = {
        "asset_id": "asset-123",
        "include_recommendations": True
    }
    
    # Act
    response = await risk_agent.process_request(request)
    
    # Assert
    assert response["success"] is True
    assert "Risk score calculado" in response["response"]

@pytest.mark.asyncio
async def test_risk_agent_falls_back_to_azure_on_error(
    risk_agent,
    mock_copilot_client
):
    """Test que el agente hace fallback a Azure en caso de error"""
    # Arrange - Hacer que primary falle
    mock_copilot_client.create_session.side_effect = [
        Exception("Copilot unavailable"),
        AsyncMock()  # Azure session exitosa
    ]
    
    # Act
    await risk_agent.initialize_session()
    
    # Assert
    assert mock_copilot_client.create_session.call_count == 2
    # Segunda llamada debe incluir provider Azure
    second_call_args = mock_copilot_client.create_session.call_args_list[1][0][0]
    assert "provider" in second_call_args
    assert second_call_args["provider"]["type"] == "azure"
```

### 7.8 Monitoring y Observabilidad

**Logging de Copilot SDK:**
```python
# ✅ CORRECTO - Logging detallado para debugging

import structlog

logger = structlog.get_logger(__name__)

class ObservableAgent(BaseAgent):
    """Agente con observabilidad completa"""
    
    async def chat(self, user_message: str) -> Dict[str, Any]:
        """Chat con logging detallado"""
        start_time = time.time()
        
        logger.info(
            "agent_chat_started",
            agent=self.__class__.__name__,
            message_preview=user_message[:100],
            session_active=self.session is not None
        )
        
        try:
            response = await self.session.chat(user_message)
            
            duration_ms = (time.time() - start_time) * 1000
            
            logger.info(
                "agent_chat_completed",
                agent=self.__class__.__name__,
                duration_ms=duration_ms,
                model_used=response.model,
                tools_called=len(response.tool_calls or []),
                response_length=len(response.content),
                success=True
            )
            
            # Métricas para Prometheus (opcional)
            metrics.agent_response_time.labels(
                agent=self.__class__.__name__,
                model=response.model
            ).observe(duration_ms / 1000)
            
            return {
                "success": True,
                "response": response.content,
                "metadata": {
                    "duration_ms": duration_ms,
                    "model": response.model,
                    "tools_used": response.tool_calls
                }
            }
            
        except Exception as e:
            logger.error(
                "agent_chat_failed",
                agent=self.__class__.__name__,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            
            metrics.agent_errors.labels(
                agent=self.__class__.__name__,
                error_type=type(e).__name__
            ).inc()
            
            return {"success": False, "error": str(e)}
```

### 7.9 Optimización de Costos

**Estrategias para Reducir Costos:**
```python
# ✅ CORRECTO - Caching y optimización

from functools import lru_cache
import hashlib

class CostOptimizedAgent(BaseAgent):
    """Agente optimizado para minimizar costos"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = {}  # Cache de respuestas
    
    def _get_cache_key(self, message: str) -> str:
        """Genera cache key para un mensaje"""
        return hashlib.sha256(message.encode()).hexdigest()
    
    async def chat(self, user_message: str) -> Dict[str, Any]:
        """Chat con caching para reducir llamadas"""
        # Check cache
        cache_key = self._get_cache_key(user_message)
        
        if cache_key in self.cache:
            logger.info("cache_hit", agent=self.__class__.__name__)
            return self.cache[cache_key]
        
        logger.info("cache_miss", agent=self.__class__.__name__)
        
        # Llamada normal
        response = await super().chat(user_message)
        
        # Cache respuesta (solo si fue exitosa)
        if response["success"]:
            self.cache[cache_key] = response
            
            # Limitar tamaño de cache
            if len(self.cache) > 100:
                # Eliminar entrada más antigua (FIFO simple)
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
        
        return response
    
    async def chat_streaming(self, user_message: str):
        """
        Chat con streaming para respuestas largas.
        Reduce latencia percibida sin costo adicional.
        """
        if not self.session:
            await self.initialize_session()
        
        async for chunk in self.session.chat_stream(user_message):
            yield chunk
```

---

## 8. LOGGING

### 8.1 Structured Logging

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

### 8.2 Log Levels

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

## 9. SEGURIDAD

### 9.1 Secrets Management

```python
# ✅ CORRECTO

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuration from environment variables"""
    
    database_url: str
    redis_url: str
    github_token: str  # For Copilot SDK (auto-detected if not set)
    azure_openai_key: str  # Fallback only
    azure_openai_endpoint: str  # Fallback only
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
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/ciso_db
REDIS_URL=redis://localhost:6379

# GitHub Copilot SDK (Primary LLM Engine)
# Usually auto-detected from git config, but can be set explicitly
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx

# Azure OpenAI (Fallback only, used in case Copilot fails)
AZURE_OPENAI_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com

# Security
SECRET_KEY=generate-with-secrets-token-urlsafe-32

# Qdrant
QDRANT_URL=http://localhost:6333

# Optional: Copilot SDK specific settings
COPILOT_TIMEOUT_SECONDS=30
COPILOT_MAX_RETRIES=3
```

**Never commit:**
- `.env` → Add to `.gitignore`
- API keys (GitHub tokens, Azure keys)
- Passwords
- Private keys
- Any credentials or secrets

### 9.2 Input Validation

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
