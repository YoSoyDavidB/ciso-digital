# 01 - ARQUITECTURA TÉCNICA: CISO Digital con IA

## 1. VISIÓN ARQUITECTÓNICA

### 1.1 Principios de Arquitectura

1. **Modularidad**: Componentes desacoplados y reutilizables
2. **Escalabilidad**: Diseño horizontal-scalable desde el inicio
3. **Observabilidad**: Logging, métricas y tracing en todos los niveles
4. **Seguridad por Diseño**: Security-first en todas las decisiones
5. **Simplicidad**: Evitar sobre-ingeniería, usar soluciones probadas
6. **Open Source First**: Preferir tecnologías open-source cuando sea posible

### 1.2 Patrones Arquitectónicos

- **Event-Driven Architecture**: Para comunicación asíncrona
- **Microservices**: Agentes como servicios independientes
- **CQRS**: Separación de queries y commands donde sea beneficioso
- **Repository Pattern**: Abstracción de persistencia
- **Strategy Pattern**: Para diferentes estrategias de agentes'''''''''''''

## 2. ARQUITECTURA GENERAL DEL SISTEMA

### 2.1 Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CAPA DE PRESENTACIÓN                        │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   Web UI     │  │  Mobile App  │  │  CLI Tools   │            │
│  │   (React)    │  │   (Future)   │  │              │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│                           │                                         │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
                            │ HTTPS / WSS
                            │
┌───────────────────────────┼─────────────────────────────────────────┐
│                           │   CAPA DE API GATEWAY                    │
│                           ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │         Nginx / Traefik / Kong                            │      │
│  │  • Authentication                                         │      │
│  │  • Rate Limiting                                          │      │
│  │  • SSL Termination                                        │      │
│  │  • Load Balancing                                         │      │
│  └──────────────────────────────────────────────────────────┘      │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────────┐
│                           │  CAPA DE APLICACIÓN                      │
│                           ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              FastAPI Backend (Python)                      │    │
│  │                                                            │    │
│  │  ┌────────────────┐  ┌────────────────┐  ┌─────────────┐ │    │
│  │  │  REST API      │  │  WebSocket     │  │  GraphQL    │ │    │
│  │  │  Endpoints     │  │  Real-time     │  │  (Optional) │ │    │
│  │  └────────────────┘  └────────────────┘  └─────────────┘ │    │
│  │                                                            │    │
│  │  ┌────────────────────────────────────────────────────┐  │    │
│  │  │          CISO ORCHESTRATOR                        │  │    │
│  │  │  • Request routing                                 │  │    │
│  │  │  • Agent coordination                              │  │    │
│  │  │  • Context management                              │  │    │
│  │  └────────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────────┘    │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────────┐
│                  CAPA DE ORQUESTACIÓN Y WORKFLOWS                    │
│                           │                                          │
│  ┌────────────────────────▼──────────────────────────────────┐     │
│  │                     N8N Workflows                         │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │     │
│  │  │  Monitoring  │  │  Vuln Scan   │  │  Compliance  │   │     │
│  │  │  Workflow    │  │  Workflow    │  │  Workflow    │   │     │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │     │
│  └───────────────────────────────────────────────────────────┘     │
│                           │                                          │
│  ┌────────────────────────▼──────────────────────────────────┐     │
│  │              Task Scheduler (APScheduler)                  │     │
│  │  • Cron jobs                                              │     │
│  │  • Periodic tasks                                         │     │
│  │  • Event-based triggers                                   │     │
│  └───────────────────────────────────────────────────────────┘     │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────────┐
│                    CAPA DE INTELIGENCIA (AI)                         │
│                           ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                   SPECIALIZED AGENTS                       │    │
│  │                                                            │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │    │
│  │  │    Risk      │  │   Incident   │  │  Compliance  │   │    │
│  │  │  Assessment  │  │   Response   │  │    Agent     │   │    │
│  │  │    Agent     │  │    Agent     │  │              │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │    │
│  │                                                            │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │    │
│  │  │   Threat     │  │   Reporting  │  │  Proactive   │   │    │
│  │  │  Intelligence│  │    Agent     │  │    Review    │   │    │
│  │  │    Agent     │  │              │  │    Agent     │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │    │
│  └────────────────────────────────────────────────────────────┘    │
│                           │                                          │
│  ┌────────────────────────▼──────────────────────────────────┐     │
│  │         RAG SYSTEM (GitHub Copilot SDK Tools)              │     │
│  │                                                            │     │
│  │  ┌──────────────────┐         ┌──────────────────┐       │     │
│  │  │  Query Processor │────────▶│ Embedding Service│       │     │
│  │  └──────────────────┘         └──────────────────┘       │     │
│  │           │                             │                 │     │
│  │           ▼                             ▼                 │     │
│  │  ┌──────────────────┐         ┌──────────────────┐       │     │
│  │  │  Qdrant Vector   │◀────────│   Re-ranker      │       │     │
│  │  │     Search       │         │   (Optional)     │       │     │
│  │  └──────────────────┘         └──────────────────┘       │     │
│  │           │                                                │     │
│  │           ▼                                                │     │
│  │  ┌──────────────────┐         ┌──────────────────┐       │     │
│  │  │  Context Builder │────────▶│  Copilot Session │       │     │
│  │  │  & Prompt Eng    │         │ (Multi-modelo)   │       │     │
│  │  └──────────────────┘         └──────────────────┘       │     │
│  └────────────────────────────────────────────────────────────┘     │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────────┐
│                  CAPA DE DATOS Y PERSISTENCIA                        │
│                           │                                          │
│  ┌────────────────────────▼──────────────────────────────────┐     │
│  │                   PostgreSQL                               │     │
│  │  • Risks, Incidents, Assets                               │     │
│  │  • Vulnerabilities, Policies                              │     │
│  │  • Compliance, Metrics                                    │     │
│  │  • Conversations, Audit Logs                              │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │              Qdrant (Vector Database)                     │      │
│  │  • Security Knowledge Base                                │      │
│  │  • Incident Memory                                        │      │
│  │  • Conversational Context                                 │      │
│  │  • Document Embeddings                                    │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │                     Redis                                  │      │
│  │  • Session Management                                     │      │
│  │  • Query Cache                                            │      │
│  │  • Rate Limiting                                          │      │
│  │  • Task Queue (Celery Backend)                            │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │            TimescaleDB (Time-Series)                       │      │
│  │  • Security Events                                        │      │
│  │  • Metrics & KPIs                                         │      │
│  │  • Performance Monitoring                                 │      │
│  └──────────────────────────────────────────────────────────┘      │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────────┐
│                    CAPA DE INTEGRACIONES                             │
│                           │                                          │
│  ┌────────────────────────▼──────────────────────────────────┐     │
│  │                  Integration Layer                         │     │
│  │                                                            │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │     │
│  │  │   SIEM   │  │  Vuln    │  │  Cloud   │  │ Ticket  │  │     │
│  │  │  (Elastic│  │ Scanners │  │ Providers│  │ Systems │  │     │
│  │  │  /Splunk)│  │ (Nessus) │  │ (AWS/GCP)│  │ (Jira)  │  │     │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘  │     │
│  │                                                            │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │     │
│  │  │   Comm   │  │  Email   │  │   Git    │  │  Other  │  │     │
│  │  │ (Slack/  │  │  (SMTP)  │  │ (GitHub) │  │   APIs  │  │     │
│  │  │  Teams)  │  │          │  │          │  │         │  │     │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘  │     │
│  └────────────────────────────────────────────────────────────┘     │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────────┐
│               CAPA DE OBSERVABILIDAD Y MONITOREO                     │
│                           │                                          │
│  ┌────────────────────────▼──────────────────────────────────┐     │
│  │                 Logging (ELK Stack)                        │     │
│  │  Elasticsearch + Logstash + Kibana                         │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │            Metrics (Prometheus + Grafana)                  │      │
│  │  • System metrics                                         │      │
│  │  • Application metrics                                    │      │
│  │  • Business metrics                                       │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │              Tracing (Jaeger/Zipkin)                       │      │
│  │  Distributed request tracing                              │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │               Alerting (AlertManager)                      │      │
│  │  • PagerDuty                                              │      │
│  │  • Slack/Email notifications                              │      │
│  └──────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────┘
```

## 3. STACK TECNOLÓGICO DETALLADO

### 3.1 Backend Core

**Lenguaje y Framework:**
```yaml
Lenguaje: Python 3.11+
Framework: FastAPI 0.109+
  - Razón: 
    * Async nativo (alto performance)
    * Type hints y Pydantic (type safety)
    * Auto-generación de docs OpenAPI
    * Excelente ecosistema para IA/ML

Web Server: Uvicorn con Gunicorn
  - Workers: 4-8 (según CPU cores)
  - Timeout: 120s (para queries LLM largos)
```

**Librerías Principales:**
```python
# requirements.txt (core)
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0  # JWT
passlib[bcrypt]==1.7.4  # Password hashing
python-multipart==0.0.6  # File uploads
aiofiles==23.2.1  # Async file operations
httpx==0.26.0  # Async HTTP client
```

### 3.2 Inteligencia Artificial

**LLM Engine:**
```python
# AI/LLM Stack - GitHub Copilot SDK como motor principal
github-copilot-sdk==0.1.0  # Motor principal de agentes con multi-modelo
# Soporta: Claude Sonnet 4.5, GPT-4.5, o1, o1-mini via single SDK
# VENTAJA: $0 costo adicional (ya tenemos suscripción GitHub Copilot)
# AHORRO ESTIMADO: $6,000-12,000 USD/año vs Anthropic/OpenAI directo

# Azure OpenAI (fallback para redundancia)
azure-openai==1.12.0  # Fallback si GitHub Copilot no disponible
openai==1.12.0  # Client base para Azure OpenAI

# Embeddings
sentence-transformers==2.3.1  # Local embeddings (fallback)
cohere==4.47  # Cohere embeddings (option)

# NOTA: NO usar langchain - GitHub Copilot SDK es framework completo
# El SDK incluye:
# - Orquestación de agentes
# - Tool calling automático
# - Session management
# - Streaming responses
# - Context management
```

**RAG Stack:**
```python
# Vector DB
qdrant-client==1.7.3

# Text processing
pypdf==3.17.4  # PDF parsing
python-docx==1.1.0  # DOCX parsing
beautifulsoup4==4.12.3  # HTML parsing
markdown==3.5.2  # Markdown processing

# NOTA: RAG se integra directamente con GitHub Copilot SDK via tools
# No necesitamos langchain-qdrant
```

### 3.3 Bases de Datos

**PostgreSQL:**
```yaml
Version: PostgreSQL 16
Driver: psycopg[binary]==3.1.18 (async support)
ORM: SQLAlchemy 2.0+ (async)
Migrations: Alembic 1.13+

Connection Pool:
  - Min: 5
  - Max: 20
  - Overflow: 10
  - Timeout: 30s
```

**Qdrant:**
```yaml
Version: Qdrant 1.7+
Client: qdrant-client 1.7.3
Deployment: Docker container
Configuration:
  - Storage: /qdrant/storage (persistent)
  - Collection optimization: HNSW index
  - Distance metric: Cosine similarity
```

**Redis:**
```yaml
Version: Redis 7.2+
Client: redis[hiredis]==5.0.1 (fast C parser)
Use cases:
  - Session store
  - Cache layer
  - Rate limiting
  - Task queue backend (Celery)
  - Pub/Sub for real-time events
```

**TimescaleDB:**
```yaml
Version: TimescaleDB 2.13+ (PostgreSQL extension)
Use case: Time-series metrics
Retention: 
  - Raw data: 90 days
  - Aggregated: 5 years
Compression: Automatic
```

### 3.4 Orquestación y Workflows

**N8N:**
```yaml
Version: n8n latest
Deployment: Docker container
Database: PostgreSQL (shared with main app)
Workflows:
  - Monitoring continuous
  - Vulnerability scanning
  - Compliance checks
  - Report generation
  - Notifications
Integration with Backend:
  - Webhooks
  - REST API calls
  - Database writes
```

**Task Scheduler:**
```python
# APScheduler para tareas periódicas
apscheduler==3.10.4

# Celery para tareas distribuidas (heavy workloads)
celery[redis]==5.3.6
flower==2.0.1  # Celery monitoring
```

### 3.5 Frontend

**Web Application:**
```yaml
Framework: React 18+ with TypeScript
Build Tool: Vite 5+
State Management: Zustand / React Query
UI Library: 
  - shadcn/ui (Tailwind-based components)
  - Radix UI (headless components)
Styling: Tailwind CSS 3+
Charts: Recharts / Chart.js
Real-time: Socket.IO client

Dependencies:
  - react: ^18.2.0
  - typescript: ^5.3.0
  - @tanstack/react-query: ^5.17.0
  - axios: ^1.6.5
  - socket.io-client: ^4.6.1
  - recharts: ^2.10.0
  - tailwindcss: ^3.4.0
```

### 3.6 Infrastructure & DevOps

**Containerization:**
```yaml
Container Runtime: Docker 24+
Orchestration: Docker Compose (dev/small prod)
              Kubernetes (large scale)

Docker Images:
  - Backend: python:3.11-slim
  - Frontend: node:20-alpine + nginx:alpine
  - N8N: n8nio/n8n:latest
  - PostgreSQL: postgres:16-alpine
  - Qdrant: qdrant/qdrant:latest
  - Redis: redis:7-alpine
```

**CI/CD:**
```yaml
VCS: Git + GitHub/GitLab
CI/CD: GitHub Actions / GitLab CI
Pipeline stages:
  1. Lint & Format (black, ruff, prettier)
  2. Type checking (mypy, tsc)
  3. Unit tests (pytest, jest)
  4. Integration tests
  5. Build Docker images
  6. Security scan (Trivy)
  7. Deploy to staging
  8. Deploy to production (manual approval)
```

**Monitoring & Observability:**
```yaml
Logging: 
  - ELK Stack (Elasticsearch, Logstash, Kibana)
  - Alternative: Loki + Grafana

Metrics:
  - Prometheus (scraping)
  - Grafana (visualization)
  - Node Exporter (system metrics)

Tracing:
  - Jaeger (distributed tracing)
  - OpenTelemetry (instrumentation)

Alerting:
  - AlertManager (Prometheus alerts)
  - PagerDuty / Slack webhooks
```

## 4. ARQUITECTURA DE AGENTES IA

### 4.1 Diseño Multi-Agente

```python
# Estructura de clases base usando GitHub Copilot SDK

from copilot import CopilotClient
from copilot.tools import define_tool
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

class BaseAgent(ABC):
    """Clase base para todos los agentes usando GitHub Copilot SDK"""
    
    def __init__(
        self,
        copilot_client: CopilotClient,
        rag_service: RAGService,
        db_session: AsyncSession
    ):
        self.client = copilot_client
        self.rag = rag_service
        self.db = db_session
        self.name = self.__class__.__name__
        self.session = None  # Copilot session
        
    @abstractmethod
    async def get_system_prompt(self) -> str:
        """Retorna el system prompt específico del agente"""
        pass
    
    @abstractmethod
    def get_tools(self) -> List:
        """Retorna las tools específicas del agente"""
        pass
        
    async def initialize_session(self):
        """Inicializa sesión de Copilot con model y tools"""
        self.session = await self.client.create_session({
            "model": "claude-sonnet-4.5",  # Primary model
            "system": await self.get_system_prompt(),
            "tools": self.get_tools()
        })
        
    @abstractmethod
    async def execute(self, task: Dict) -> Dict:
        """Método principal de ejecución"""
        pass
        
    async def chat(self, message: str) -> str:
        """Envía mensaje al agente y obtiene respuesta"""
        if not self.session:
            await self.initialize_session()
        
        response = await self.session.chat(message)
        return response.text
        
    async def gather_context(self, query: str) -> List[Document]:
        """Recopila contexto relevante de RAG"""
        return await self.rag.search(
            query=query,
            collection=self.collection_name,
            top_k=5
        )
        
    async def log_action(self, action: str, metadata: dict):
        """Registra acciones del agente"""
        await AuditLog.create(
            agent=self.name,
            action=action,
            metadata=metadata
        )
        
    async def fallback_to_azure(self):
        """Fallback a Azure OpenAI si Copilot falla"""
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
```

### 4.2 CISO Orchestrator

```python
class CISOOrchestrator:
    """
    Orquestador principal usando GitHub Copilot SDK:
    1. Analiza intención del usuario
    2. Selecciona agente(s) apropiado(s)
    3. Coordina ejecución
    4. Agrega resultados
    """
    
    def __init__(self, copilot_client: CopilotClient):
        self.client = copilot_client
        self.agents = {
            "risk": RiskAssessmentAgent(copilot_client, rag_service, db),
            "incident": IncidentResponseAgent(copilot_client, rag_service, db),
            "compliance": ComplianceAgent(copilot_client, rag_service, db),
            "threat_intel": ThreatIntelAgent(copilot_client, rag_service, db),
            "reporting": ReportingAgent(copilot_client, rag_service, db),
            "proactive": ProactiveReviewAgent(copilot_client, rag_service, db)
        }
        self.classifier_session = None
        
    async def initialize(self):
        """Inicializa session del clasificador de intención"""
        self.classifier_session = await self.client.create_session({
            "model": "claude-sonnet-4.5",
            "system": """Eres un clasificador de intenciones para un CISO Digital.
            Analiza el mensaje del usuario y determina qué agente(s) debe manejar la solicitud.
            
            Agentes disponibles:
            - risk: Evaluación de riesgos
            - incident: Respuesta a incidentes
            - compliance: Cumplimiento normativo
            - threat_intel: Inteligencia de amenazas
            - reporting: Generación de reportes
            - proactive: Revisiones proactivas
            
            Retorna JSON con: {"agents": ["agent1", "agent2"], "priority": "high|medium|low"}
            """
        })
        
    async def process_request(
        self,
        user_query: str,
        context: Dict
    ) -> Dict:
        """
        Procesa request del usuario
        """
        if not self.classifier_session:
            await self.initialize()
        
        # 1. Clasificar intención usando Copilot
        classification_response = await self.classifier_session.chat(
            f"Usuario: {user_query}\nContexto: {context}"
        )
        classification = json.loads(classification_response.text)
        
        # 2. Seleccionar agentes
        agents_to_run = [
            self.agents[agent_name] 
            for agent_name in classification["agents"]
        ]
        
        # 3. Ejecutar agentes (paralelo si es posible)
        results = await asyncio.gather(
            *[agent.execute({"query": user_query, "context": context}) 
              for agent in agents_to_run]
        )
        
        # 4. Agregar resultados usando Copilot
        aggregation_prompt = f"""
        Query del usuario: {user_query}
        
        Resultados de agentes:
        {json.dumps(results, indent=2)}
        
        Genera una respuesta consolidada y coherente.
        """
        
        aggregator_session = await self.client.create_session({
            "model": "claude-sonnet-4.5",
            "system": "Agrega y sintetiza respuestas de múltiples agentes especializados."
        })
        
        final_response = await aggregator_session.chat(aggregation_prompt)
        
        return {
            "response": final_response.text,
            "agents_used": classification["agents"],
            "raw_results": results
        }
```

### 4.3 Agentes Especializados

**1. Risk Assessment Agent:**
```python
from copilot.tools import define_tool

class RiskAssessmentAgent(BaseAgent):
    """
    Responsabilidades:
    - Evaluar riesgos de assets
    - Calcular scores de riesgo
    - Priorizar remediaciones
    - Identificar tendencias
    """
    
    collection_name = "security_knowledge"
    
    async def get_system_prompt(self) -> str:
        return """Eres un experto en evaluación de riesgos de seguridad.
        Analizas vulnerabilidades, criticidad de assets, y contexto de amenazas
        para calcular risk scores precisos y recomendar remediaciones priorizadas.
        
        Usa las tools disponibles para:
        - Buscar información en la base de conocimientos
        - Consultar vulnerabilidades conocidas
        - Calcular risk scores
        """
    
    def get_tools(self) -> List:
        """Define tools específicas para risk assessment"""
        
        @define_tool(description="Busca información de riesgos en knowledge base")
        async def search_risk_knowledge(query: str) -> dict:
            results = await self.rag.search(query, self.collection_name)
            return {"results": [doc.content for doc in results]}
        
        @define_tool(description="Obtiene vulnerabilidades de un asset")
        async def get_asset_vulnerabilities(asset_id: str) -> dict:
            vulns = await self.db.execute(
                select(Vulnerability).where(Vulnerability.asset_id == asset_id)
            )
            return {"vulnerabilities": [v.to_dict() for v in vulns.scalars()]}
        
        @define_tool(description="Calcula risk score basado en parámetros")
        async def calculate_risk_score(
            cvss_scores: List[float],
            asset_criticality: str,
            exploitability: str
        ) -> dict:
            # Lógica de cálculo
            base_score = max(cvss_scores) if cvss_scores else 0
            multiplier = {"critical": 1.5, "high": 1.3, "medium": 1.0, "low": 0.8}
            final_score = min(10.0, base_score * multiplier.get(asset_criticality, 1.0))
            return {"risk_score": final_score}
        
        return [search_risk_knowledge, get_asset_vulnerabilities, calculate_risk_score]
    
    async def execute(self, task: Dict) -> Dict:
        """Ejecuta evaluación de riesgo"""
        asset_id = task.get("asset_id")
        
        # Inicializar session si no existe
        if not self.session:
            await self.initialize_session()
        
        # El agente usará las tools automáticamente según necesite
        prompt = f"""
        Evalúa el riesgo del asset ID: {asset_id}
        
        Pasos:
        1. Obtén las vulnerabilidades del asset
        2. Busca contexto sobre riesgos similares
        3. Calcula el risk score
        4. Genera recomendaciones priorizadas
        
        Retorna JSON con:
        {{
            "risk_score": float,
            "severity": "critical|high|medium|low",
            "vulnerabilities_count": int,
            "recommendations": [...]
        }}
        """
        
        try:
            response = await self.session.chat(prompt)
            result = json.loads(response.text)
            
            # Guardar en DB
            await Risk.create(
                asset_id=asset_id,
                score=result["risk_score"],
                severity=result["severity"],
                analysis=response.text,
                status="open"
            )
            
            await self.log_action("risk_assessment", {
                "asset_id": asset_id,
                "score": result["risk_score"]
            })
            
            return result
            
        except Exception as e:
            # Fallback a Azure si GitHub Copilot falla
            logger.warning(f"Copilot failed, using Azure fallback: {e}")
            await self.fallback_to_azure()
            response = await self.session.chat(prompt)
            return json.loads(response.text)
```

**2. Incident Response Agent:**
```python
class IncidentResponseAgent(BaseAgent):
    """
    Responsabilidades:
    - Detectar incidentes
    - Clasificar severidad
    - Ejecutar playbooks
    - Documentar respuesta
    """
    
    async def get_system_prompt(self) -> str:
        return """Eres un experto en respuesta a incidentes de seguridad.
        Clasifica incidentes, ejecutas playbooks apropiados, y coordinas
        las acciones de respuesta según las mejores prácticas.
        """
    
    def get_tools(self) -> List:
        @define_tool(description="Busca playbooks para tipo de incidente")
        async def get_playbook(incident_type: str) -> dict:
            playbook = await self.db.execute(
                select(Playbook).where(Playbook.incident_type == incident_type)
            )
            return {"playbook": playbook.scalar_one_or_none().to_dict()}
        
        @define_tool(description="Busca incidentes similares previos")
        async def search_similar_incidents(description: str) -> dict:
            results = await self.rag.search(description, "incident_memory")
            return {"similar_incidents": [doc.content for doc in results]}
        
        @define_tool(description="Ejecuta acción de respuesta")
        async def execute_response_action(action: str, params: dict) -> dict:
            # Ejecutar acción (ej: aislar host, bloquear IP, etc.)
            result = await action_executor.execute(action, params)
            return {"action_result": result}
        
        return [get_playbook, search_similar_incidents, execute_response_action]
    
    async def execute(self, task: Dict) -> Dict:
        event = task.get("event")
        
        if not self.session:
            await self.initialize_session()
        
        prompt = f"""
        Incidente detectado:
        - Tipo: {event.get("type")}
        - Descripción: {event.get("description")}
        - Fuente: {event.get("source")}
        
        Acciones:
        1. Clasifica la severidad (critical/high/medium/low)
        2. Busca playbook apropiado
        3. Revisa incidentes similares para aprender
        4. Determina acciones de respuesta
        5. Ejecuta acciones automatizadas si es seguro
        
        Retorna JSON con plan de respuesta completo.
        """
        
        response = await self.session.chat(prompt)
        result = json.loads(response.text)
        
        # Crear incident record
        incident = await Incident.create(
            title=event.get("title"),
            severity=result["severity"],
            actions_taken=result.get("actions_taken", []),
            status="investigating"
        )
        
        # Notificar si es crítico
        if result["severity"] == "critical":
            await self.notify_stakeholders(incident)
        
        return {
            "incident_id": incident.id,
            "severity": result["severity"],
            "response_plan": result
        }
```

**3. Compliance Agent:**
```python
class ComplianceAgent(BaseAgent):
    """
    Responsabilidades:
    - Verificar cumplimiento de controles
    - Generar evidencias
    - Identificar gaps
    - Producir reportes de compliance
    """
    
    async def get_system_prompt(self) -> str:
        return """Eres un auditor de cumplimiento de seguridad experto en 
        frameworks como ISO 27001, NIST CSF, SOC 2, GDPR, etc.
        Evalúas controles, recopilas evidencias, y generas reportes de compliance.
        """
    
    def get_tools(self) -> List:
        @define_tool(description="Obtiene controles de un framework")
        async def get_framework_controls(framework: str) -> dict:
            controls = await self.db.execute(
                select(Control).where(Control.framework == framework)
            )
            return {"controls": [c.to_dict() for c in controls.scalars()]}
        
        @define_tool(description="Busca evidencias de cumplimiento")
        async def search_compliance_evidence(control_id: str) -> dict:
            results = await self.rag.search(
                f"evidence for control {control_id}",
                "security_knowledge"
            )
            return {"evidence": [doc.content for doc in results]}
        
        @define_tool(description="Evalúa estado de un control")
        async def assess_control_status(
            control_id: str,
            evidence: List[str]
        ) -> dict:
            # Lógica de evaluación
            status = "compliant" if len(evidence) >= 3 else "non_compliant"
            return {"status": status, "evidence_count": len(evidence)}
        
        return [get_framework_controls, search_compliance_evidence, assess_control_status]
    
    async def execute(self, task: Dict) -> Dict:
        framework = task.get("framework")  # ISO27001, NIST, etc.
        
        if not self.session:
            await self.initialize_session()
        
        prompt = f"""
        Ejecuta auditoría de cumplimiento para: {framework}
        
        Proceso:
        1. Obtén todos los controles del framework
        2. Para cada control, busca evidencias
        3. Evalúa el estado de cumplimiento
        4. Identifica gaps y recomendaciones
        5. Calcula compliance rate global
        
        Retorna reporte completo en JSON.
        """
        
        response = await self.session.chat(prompt)
        result = json.loads(response.text)
        
        # Guardar reporte
        await ComplianceReport.create(
            framework=framework,
            compliance_rate=result["compliance_rate"],
            controls_assessed=result["controls_count"],
            gaps=result["gaps"],
            report_data=result
        )
        
        return result
```

**4. Proactive Review Agent:** (⭐ CLAVE)
```python
class ProactiveReviewAgent(BaseAgent):
    """
    Responsabilidades:
    - Revisar documentación existente periódicamente
    - Identificar documentación faltante
    - Detectar políticas desactualizadas
    - Proponer planes de acción
    - Sugerir mejoras proactivas
    """
    
    async def get_system_prompt(self) -> str:
        return """Eres un CISO proactivo que revisa constantemente la postura
        de seguridad de la organización. Identificas gaps en documentación,
        políticas desactualizadas, controles faltantes, y propones mejoras
        antes de que se conviertan en problemas.
        
        Tu objetivo es mantener la seguridad al día y adelantarte a problemas.
        """
    
    def get_tools(self) -> List:
        @define_tool(description="Obtiene inventario de documentación actual")
        async def get_current_documents() -> dict:
            docs = await self.db.execute(select(Document))
            return {
                "documents": [
                    {
                        "id": d.id,
                        "title": d.title,
                        "type": d.type,
                        "last_updated": str(d.updated_at),
                        "framework": d.framework
                    }
                    for d in docs.scalars()
                ]
            }
        
        @define_tool(description="Obtiene frameworks aplicables")
        async def get_applicable_frameworks() -> dict:
            frameworks = await self.db.execute(
                select(ComplianceFramework).where(
                    ComplianceFramework.applicable == True
                )
            )
            return {"frameworks": [f.name for f in frameworks.scalars()]}
        
        @define_tool(description="Verifica si documento está desactualizado")
        async def check_document_freshness(doc_id: str, max_age_days: int = 365) -> dict:
            doc = await self.db.get(Document, doc_id)
            age_days = (datetime.utcnow() - doc.updated_at).days
            is_outdated = age_days > max_age_days
            return {
                "document_id": doc_id,
                "age_days": age_days,
                "is_outdated": is_outdated,
                "last_updated": str(doc.updated_at)
            }
        
        @define_tool(description="Busca documentos requeridos por framework")
        async def get_required_documents(framework: str) -> dict:
            results = await self.rag.search(
                f"{framework} required documentation policies procedures",
                "compliance_requirements"
            )
            return {"required_docs": [doc.content for doc in results]}
        
        return [
            get_current_documents,
            get_applicable_frameworks,
            check_document_freshness,
            get_required_documents
        ]
    
    async def execute(self, task: Dict) -> Dict:
        """Ejecuta revisión proactiva completa"""
        
        if not self.session:
            await self.initialize_session()
        
        prompt = """
        Ejecuta revisión proactiva de la postura de seguridad:
        
        1. INVENTARIO:
           - Obtén documentación actual
           - Obtén frameworks aplicables
        
        2. GAP ANALYSIS:
           - Para cada framework, identifica documentos requeridos
           - Compara con inventario actual
           - Lista documentos faltantes con prioridad
        
        3. FRESHNESS CHECK:
           - Revisa edad de cada documento existente
           - Identifica documentos desactualizados (>365 días)
           - Prioriza actualizaciones necesarias
        
        4. RECOMMENDATIONS:
           - Genera plan de acción priorizado
           - Estima esfuerzo para cada tarea
           - Define deadlines sugeridos
           - Identifica riesgos de no actuar
        
        Retorna JSON completo con:
        {
            "missing_documents": [...],
            "outdated_documents": [...],
            "action_plan": [...],
            "priority_score": float,
            "estimated_effort_hours": int
        }
        """
        
        response = await self.session.chat(prompt)
        result = json.loads(response.text)
        
        # Guardar resultados para seguimiento
        await ProactiveReview.create(
            review_type="full_assessment",
            gaps_found=len(result["missing_documents"]),
            outdated_found=len(result["outdated_documents"]),
            priority_score=result["priority_score"],
            action_plan=result["action_plan"],
            review_data=result
        )
        
        # Crear tasks automáticamente para items críticos
        for item in result["action_plan"]:
            if item.get("priority") == "critical":
                await Task.create(
                    title=item["title"],
                    description=item["description"],
                    priority="critical",
                    due_date=item["deadline"],
                    assigned_to="security_team",
                    source="proactive_review"
                )
        
        return result
```

## 5. SISTEMA RAG (Retrieval Augmented Generation)

### 5.1 Pipeline de RAG

```python
class RAGService:
    """
    Servicio principal de RAG que coordina:
    1. Query processing
    2. Embedding generation
    3. Vector search
    4. Re-ranking
    5. Context building
    
    Se integra con GitHub Copilot SDK via tools (@define_tool)
    """
    
    def __init__(
        self,
        qdrant_client: QdrantClient,
        embedding_service: EmbeddingService
    ):
        self.qdrant = qdrant_client
        self.embedder = embedding_service
        
    async def search(
        self,
        query: str,
        collection: str,
        top_k: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Document]:
        """
        Búsqueda semántica con RAG
        Esta función se expone como tool para los agentes de Copilot
        """
        # 1. Generar embedding del query
        query_vector = await self.embedder.embed(query)
        
        # 2. Búsqueda en Qdrant
        search_results = await self.qdrant.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k * 2,  # Obtenemos más para re-ranking
            query_filter=self.build_filter(filters)
        )
        
        # 3. Re-ranking (opcional pero recomendado)
        reranked = await self.rerank_with_copilot(query, search_results)
        
        # 4. Tomar top_k después de re-ranking
        final_results = reranked[:top_k]
        
        # 5. Construir documentos
        documents = [
            Document(
                content=result.payload['content'],
                metadata=result.payload,
                score=result.score
            )
            for result in final_results
        ]
        
        return documents
    
    async def rerank_with_copilot(
        self,
        query: str,
        results: List[ScoredPoint]
    ) -> List[ScoredPoint]:
        """
        Re-ranking usando GitHub Copilot SDK para mejor relevancia
        """
        # Crear sesión temporal de Copilot para re-ranking
        client = CopilotClient()
        session = await client.create_session({
            "model": "claude-sonnet-4.5",
            "system": """Eres un experto en evaluar relevancia de documentos.
            Asigna scores de relevancia (1-10) basado en qué tan bien 
            responde cada documento a la query del usuario."""
        })
        
        # Formatear resultados para evaluación
        docs_text = "\n\n".join([
            f"[Doc {i+1}]: {r.payload.get('content', '')[:500]}"
            for i, r in enumerate(results)
        ])
        
        prompt = f"""
        Query: "{query}"
        
        Documentos:
        {docs_text}
        
        Evalúa relevancia de cada documento (1-10).
        Retorna JSON: {{"scores": [9, 7, 8, 5, ...]}}
        """
        
        response = await session.chat(prompt)
        scores_data = json.loads(response.text)
        llm_scores = scores_data["scores"]
        
        # Combinar scores originales con LLM scores
        for result, llm_score in zip(results, llm_scores):
            # Normalizar LLM score a 0-1
            normalized_llm = llm_score / 10.0
            # Promedio ponderado (60% original, 40% LLM)
            result.score = (result.score * 0.6) + (normalized_llm * 0.4)
        
        # Re-ordenar
        return sorted(results, key=lambda x: x.score, reverse=True)
    
    def as_copilot_tool(self):
        """
        Convierte RAG search en tool para Copilot agents
        """
        from copilot.tools import define_tool
        
        @define_tool(description="Busca información en knowledge base usando RAG")
        async def search_knowledge_base(
            query: str,
            collection: str = "security_knowledge",
            top_k: int = 5
        ) -> dict:
            results = await self.search(query, collection, top_k)
            return {
                "results": [
                    {
                        "content": doc.content,
                        "score": doc.score,
                        "metadata": doc.metadata
                    }
                    for doc in results
                ]
            }
        
        return search_knowledge_base
```

### 5.2 Embedding Strategy

```python
class EmbeddingService:
    """
    Servicio de embeddings con fallback strategy
    """
    
    def __init__(self):
        # Primary: OpenAI embeddings (mejor calidad)
        self.primary_embedder = OpenAIEmbeddings(
            model="text-embedding-3-large",
            dimensions=1536
        )
        
        # Fallback: Sentence Transformers (local, gratis)
        self.fallback_embedder = SentenceTransformer(
            'sentence-transformers/all-mpnet-base-v2'
        )
        
    async def embed(
        self,
        text: str,
        use_fallback: bool = False
    ) -> List[float]:
        """
        Genera embedding con fallback automático
        """
        try:
            if not use_fallback:
                return await self.primary_embedder.aembed_query(text)
        except Exception as e:
            logger.warning(f"Primary embedder failed: {e}, using fallback")
            
        # Fallback a modelo local
        return self.fallback_embedder.encode(text).tolist()
```

### 5.3 Context Building

```python
class ContextBuilder:
    """
    Construye contexto optimizado para el LLM
    """
    
    async def build_context(
        self,
        query: str,
        documents: List[Document],
        max_tokens: int = 8000
    ) -> str:
        """
        Construye contexto respetando límites de tokens
        """
        context_parts = []
        current_tokens = 0
        
        for doc in documents:
            # Estimar tokens (aprox 4 chars = 1 token)
            doc_tokens = len(doc.content) // 4
            
            if current_tokens + doc_tokens > max_tokens:
                # Truncar si es necesario
                remaining_tokens = max_tokens - current_tokens
                truncated_content = doc.content[:remaining_tokens * 4]
                context_parts.append(truncated_content)
                break
            
            context_parts.append(doc.content)
            current_tokens += doc_tokens
        
        # Formatear contexto
        formatted_context = "\n\n---\n\n".join([
            f"[Documento {i+1}]\n{content}"
            for i, content in enumerate(context_parts)
        ])
        
        return formatted_context
```

## 6. SEGURIDAD

### 6.1 Authentication & Authorization

```python
# OAuth2 with JWT tokens

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# Configuration
SECRET_KEY = settings.SECRET_KEY  # From environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuthService:
    async def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    async def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(401, "Invalid token")

# Dependency
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = await auth_service.verify_token(token)
    user = await User.get(id=payload["sub"])
    if not user:
        raise HTTPException(401, "User not found")
    return user

# Role-based access control
def require_role(role: str):
    async def role_checker(user: User = Depends(get_current_user)):
        if role not in user.roles:
            raise HTTPException(403, f"Role {role} required")
        return user
    return role_checker

# Usage in endpoint
@router.get("/admin/users")
async def get_users(user: User = Depends(require_role("admin"))):
    ...
```

### 6.2 Data Encryption

```python
# Encryption at rest

from cryptography.fernet import Fernet

class EncryptionService:
    def __init__(self):
        # Key from environment variable
        key = settings.ENCRYPTION_KEY.encode()
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# Usage in models
class SensitiveData(BaseModel):
    _encryption_service = EncryptionService()
    
    @validator('api_key', pre=True)
    def encrypt_api_key(cls, v):
        if v and not v.startswith('gAAAAA'):  # Not already encrypted
            return cls._encryption_service.encrypt(v)
        return v
    
    def get_api_key_decrypted(self):
        return self._encryption_service.decrypt(self.api_key)
```

### 6.3 Rate Limiting

```python
# Rate limiting middleware

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Global rate limit
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Check if user is authenticated
    token = request.headers.get("Authorization")
    if token:
        # Authenticated users get higher limits
        limit = "100/minute"
    else:
        # Anonymous users get lower limits
        limit = "10/minute"
    
    # Apply rate limit
    # (actual implementation using Redis)
    ...
    
    response = await call_next(request)
    return response

# Per-endpoint rate limiting
@router.post("/chat")
@limiter.limit("30/minute")
async def chat_endpoint(request: Request, ...):
    ...
```

## 7. PERFORMANCE & SCALING

### 7.1 Caching Strategy

```python
# Multi-level caching

from functools import wraps
import hashlib
import json

class CacheService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.local_cache = {}  # In-memory cache
        
    async def get(self, key: str) -> Optional[Any]:
        # Level 1: In-memory cache
        if key in self.local_cache:
            return self.local_cache[key]
        
        # Level 2: Redis cache
        value = await self.redis.get(key)
        if value:
            deserialized = json.loads(value)
            self.local_cache[key] = deserialized  # Populate L1
            return deserialized
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300
    ):
        serialized = json.dumps(value)
        
        # Set in both caches
        self.local_cache[key] = value
        await self.redis.setex(key, ttl, serialized)

def cached(ttl: int = 300):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_data = f"{func.__name__}:{args}:{kwargs}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Usage
@cached(ttl=600)
async def get_risk_assessment(asset_id: str) -> RiskReport:
    # Expensive operation
    ...
```

### 7.2 Database Connection Pooling

```python
# SQLAlchemy async engine configuration

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,  # Connections to maintain
    max_overflow=10,  # Additional connections under load
    pool_timeout=30,  # Seconds to wait for connection
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connections before use
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 7.3 Asynchronous Processing

```python
# Background tasks with Celery

from celery import Celery

celery_app = Celery(
    "ciso_digital",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery_app.task(name="vulnerability_scan")
def run_vulnerability_scan(asset_id: str):
    """
    Long-running task - runs in background
    """
    # Execute scan
    results = scan_vulnerabilities(asset_id)
    
    # Store results
    store_scan_results(results)
    
    # Notify completion
    send_notification(f"Scan completed for {asset_id}")
    
    return results

# Trigger from API
@router.post("/scans/{asset_id}")
async def start_scan(asset_id: str):
    # Queue task
    task = run_vulnerability_scan.delay(asset_id)
    
    return {"task_id": task.id, "status": "queued"}
```

## 8. DEPLOYMENT

### 8.1 Docker Compose (Development/Small Production)

```yaml
# docker-compose.yml

version: '3.9'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/ciso_db
      - REDIS_URL=redis://redis:6379
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - postgres
      - redis
      - qdrant
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=ciso_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=user
      - DB_POSTGRESDB_PASSWORD=pass
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
  n8n_data:
  prometheus_data:
  grafana_data:
```

---

**Versión:** 1.0  
**Última Actualización:** Febrero 2026  
**Próximo Documento:** [02-DATABASE-DESIGN.md](02-DATABASE-DESIGN.md)
