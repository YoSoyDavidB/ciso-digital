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
│  │              RAG SYSTEM (LangChain/LlamaIndex)             │     │
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
│  │  │  Context Builder │────────▶│   LLM Service    │       │     │
│  │  │  & Prompt Eng    │         │ (Claude/GPT-4)   │       │     │
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

**LLM Providers:**
```python
# AI/LLM Stack
anthropic==0.18.1  # Claude (primary)
openai==1.12.0  # GPT-4 (fallback/specialized tasks)
langchain==0.1.6  # Orchestration
langchain-anthropic==0.1.1
langchain-openai==0.0.5
langchain-community==0.0.20
llama-index==0.10.0  # Alternative RAG framework

# Embeddings
sentence-transformers==2.3.1  # Local embeddings (fallback)
cohere==4.47  # Cohere embeddings (option)
```

**RAG Stack:**
```python
# Vector DB & RAG
qdrant-client==1.7.3
langchain-qdrant==0.1.0

# Text processing
pypdf==3.17.4  # PDF parsing
python-docx==1.1.0  # DOCX parsing
beautifulsoup4==4.12.3  # HTML parsing
markdown==3.5.2  # Markdown processing
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
# Estructura de clases base

class BaseAgent(ABC):
    """Clase base para todos los agentes"""
    
    def __init__(
        self,
        llm_service: LLMService,
        rag_service: RAGService,
        db_session: AsyncSession
    ):
        self.llm = llm_service
        self.rag = rag_service
        self.db = db_session
        self.name = self.__class__.__name__
        
    @abstractmethod
    async def execute(self, task: Task) -> AgentResponse:
        """Método principal de ejecución"""
        pass
        
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
```

### 4.2 CISO Orchestrator

```python
class CISOOrchestrator:
    """
    Orquestador principal que:
    1. Analiza intención del usuario
    2. Selecciona agente(s) apropiado(s)
    3. Coordina ejecución
    4. Agrega resultados
    """
    
    def __init__(self):
        self.agents = {
            "risk": RiskAssessmentAgent(),
            "incident": IncidentResponseAgent(),
            "compliance": ComplianceAgent(),
            "threat_intel": ThreatIntelAgent(),
            "reporting": ReportingAgent(),
            "proactive": ProactiveReviewAgent()
        }
        
    async def process_request(
        self,
        user_query: str,
        context: ConversationContext
    ) -> Response:
        """
        Procesa request del usuario
        """
        # 1. Clasificar intención
        intent = await self.classify_intent(user_query)
        
        # 2. Seleccionar agentes
        agents_to_run = self.select_agents(intent)
        
        # 3. Ejecutar agentes (paralelo si es posible)
        results = await asyncio.gather(
            *[agent.execute(user_query, context) 
              for agent in agents_to_run]
        )
        
        # 4. Agregar resultados
        final_response = await self.aggregate_results(results)
        
        return final_response
```

### 4.3 Agentes Especializados

**1. Risk Assessment Agent:**
```python
class RiskAssessmentAgent(BaseAgent):
    """
    Responsabilidades:
    - Evaluar riesgos de assets
    - Calcular scores de riesgo
    - Priorizar remediaciones
    - Identificar tendencias
    """
    
    collection_name = "security_knowledge"
    
    async def execute(self, task: RiskAssessmentTask) -> RiskReport:
        # Obtener información del asset
        asset = await self.db.get(Asset, task.asset_id)
        
        # Buscar vulnerabilidades conocidas
        vulns = await self.get_vulnerabilities(asset)
        
        # Contexto de RAG sobre riesgos similares
        context = await self.gather_context(
            f"riesgos de {asset.type} con {vulns}"
        )
        
        # LLM evalúa riesgo
        risk_analysis = await self.llm.analyze(
            prompt=self.build_risk_prompt(asset, vulns, context),
            temperature=0.3  # Más determinístico
        )
        
        # Calcular risk score
        risk_score = self.calculate_risk_score(
            vulns, 
            asset.criticality,
            risk_analysis
        )
        
        # Guardar en DB
        risk = await Risk.create(
            asset_id=asset.id,
            score=risk_score,
            analysis=risk_analysis,
            status="open"
        )
        
        return RiskReport(risk=risk, recommendations=[...])
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
    
    async def execute(self, event: SecurityEvent) -> IncidentResponse:
        # Clasificar tipo de incidente
        incident_type = await self.classify_incident(event)
        
        # Buscar playbook apropiado
        playbook = await self.get_playbook(incident_type)
        
        # Contexto de incidentes similares
        similar_incidents = await self.rag.search(
            query=f"{incident_type} incident",
            collection="incident_memory",
            top_k=3
        )
        
        # LLM determina acciones
        response_plan = await self.llm.generate(
            prompt=self.build_response_prompt(
                event, playbook, similar_incidents
            )
        )
        
        # Ejecutar acciones automatizadas
        actions_taken = await self.execute_actions(response_plan)
        
        # Crear incident record
        incident = await Incident.create(
            title=event.title,
            severity=response_plan.severity,
            actions=actions_taken,
            status="investigating"
        )
        
        # Notificar stakeholders si es crítico
        if incident.severity == "critical":
            await self.notify_stakeholders(incident)
        
        return IncidentResponse(
            incident=incident,
            actions=actions_taken,
            next_steps=response_plan.next_steps
        )
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
    
    async def execute(
        self,
        task: ComplianceCheckTask
    ) -> ComplianceReport:
        
        framework = task.framework  # ISO27001, NIST, etc.
        
        # Obtener controles del framework
        controls = await self.get_framework_controls(framework)
        
        # Verificar cada control
        results = []
        for control in controls:
            # Buscar evidencias en RAG
            evidence = await self.rag.search(
                query=f"{framework} {control.id} evidence",
                collection="security_knowledge"
            )
            
            # LLM evalúa cumplimiento
            assessment = await self.llm.assess(
                prompt=self.build_compliance_prompt(
                    control, evidence
                )
            )
            
            results.append(
                ControlAssessment(
                    control=control,
                    status=assessment.status,
                    evidence=evidence,
                    gaps=assessment.gaps
                )
            )
        
        # Generar reporte
        report = ComplianceReport(
            framework=framework,
            controls=results,
            compliance_rate=self.calculate_rate(results),
            recommendations=await self.generate_recommendations(results)
        )
        
        return report
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
    
    async def execute(
        self, 
        task: ProactiveReviewTask
    ) -> ProactiveReport:
        
        # 1. Inventario de documentación actual
        current_docs = await self.inventory_documents()
        
        # 2. Obtener frameworks aplicables
        frameworks = await self.get_applicable_frameworks()
        
        # 3. Para cada framework, identificar gaps
        gaps = []
        for framework in frameworks:
            required_docs = await self.get_required_documents(framework)
            
            for req_doc in required_docs:
                if not self.document_exists(req_doc, current_docs):
                    gaps.append(
                        DocumentGap(
                            framework=framework,
                            missing_document=req_doc,
                            priority=req_doc.priority,
                            deadline=self.calculate_deadline(req_doc)
                        )
                    )
        
        # 4. Revisar documentos existentes
        outdated_docs = []
        for doc in current_docs:
            is_outdated = await self.check_if_outdated(doc)
            if is_outdated:
                outdated_docs.append(doc)
        
        # 5. LLM genera recomendaciones proactivas
        recommendations = await self.llm.generate(
            prompt=self.build_proactive_prompt(
                gaps, outdated_docs, current_docs
            )
        )
        
        # 6. Crear action plan
        action_plan = await self.create_action_plan(
            gaps, outdated_docs, recommendations
        )
        
        # 7. Guardar en DB para seguimiento
        await self.save_proactive_review(
            gaps, outdated_docs, action_plan
        )
        
        return ProactiveReport(
            gaps=gaps,
            outdated_documents=outdated_docs,
            recommendations=recommendations,
            action_plan=action_plan
        )
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
    """
    
    def __init__(
        self,
        qdrant_client: QdrantClient,
        embedding_service: EmbeddingService,
        llm_service: LLMService
    ):
        self.qdrant = qdrant_client
        self.embedder = embedding_service
        self.llm = llm_service
        
    async def search(
        self,
        query: str,
        collection: str,
        top_k: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Document]:
        """
        Búsqueda semántica con RAG
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
        reranked = await self.rerank(query, search_results)
        
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
        
    async def rerank(
        self,
        query: str,
        results: List[ScoredPoint]
    ) -> List[ScoredPoint]:
        """
        Re-ranking usando LLM para mejor relevancia
        """
        # Usar LLM para evaluar relevancia
        prompt = f"""
        Query: {query}
        
        Evalúa la relevancia de cada documento (1-10):
        {self.format_results_for_reranking(results)}
        
        Retorna scores en orden.
        """
        
        scores = await self.llm.get_relevance_scores(prompt, results)
        
        # Combinar scores originales con LLM scores
        for result, llm_score in zip(results, scores):
            result.score = (result.score + llm_score / 10) / 2
        
        # Re-ordenar
        return sorted(results, key=lambda x: x.score, reverse=True)
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
