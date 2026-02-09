# CISO Orchestrator - Technical Documentation

**Version:** 1.0  
**Last Updated:** 2026-02-06  
**Status:** Production Ready  

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Intent Classification](#intent-classification)
4. [Agent Selection](#agent-selection)
5. [Result Aggregation](#result-aggregation)
6. [Query Routing Examples](#query-routing-examples)
7. [Configuration](#configuration)
8. [API Reference](#api-reference)
9. [Best Practices](#best-practices)

---

## 🎯 Overview

The **CISO Orchestrator** is the central coordination layer for the CISO Digital AI assistant. It acts as an intelligent router that:

1. **Classifies** user intents from natural language queries
2. **Selects** the appropriate specialized agent(s) to handle the query
3. **Executes** the agent(s) with relevant context
4. **Aggregates** results when multiple agents are involved
5. **Manages** conversation memory and context

### Key Capabilities

- ✅ Multi-agent orchestration
- ✅ Intent-based routing
- ✅ Context-aware processing
- ✅ Conversation memory management
- ✅ Multi-turn dialogue support
- ✅ Confidence-based clarification
- ✅ Parallel agent execution
- ✅ Result aggregation and synthesis

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                          │
│                  (Chat, API, Dashboard)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   CISO Orchestrator                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Conversation Memory Service                      │  │
│  │     └─ Fetch conversation history                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  2. Intent Classifier                                │  │
│  │     ├─ Analyze query + context                       │  │
│  │     ├─ Extract entities                              │  │
│  │     └─ Return intent + confidence                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  3. Agent Selection                                  │  │
│  │     ├─ Map intent → agent(s)                         │  │
│  │     ├─ Check confidence threshold                    │  │
│  │     └─ Prepare execution plan                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  4. Agent Execution                                  │  │
│  │     ├─ Single agent: Direct execution                │  │
│  │     ├─ Multiple agents: Parallel execution           │  │
│  │     └─ Pass context and history                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  5. Result Aggregation                               │  │
│  │     ├─ Combine multiple agent responses              │  │
│  │     ├─ Synthesize unified answer                     │  │
│  │     └─ Add metadata (sources, confidence)            │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  6. Save to Memory                                   │  │
│  │     ├─ Store user query                              │  │
│  │     ├─ Store assistant response                      │  │
│  │     └─ Create embeddings for semantic search         │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Specialized Agents                         │
│  ┌────────────┬────────────┬────────────┬────────────┐     │
│  │   Risk     │  Incident  │ Compliance │   Threat   │     │
│  │ Assessment │  Response  │   Check    │   Intel    │     │
│  │   Agent    │   Agent    │   Agent    │   Agent    │     │
│  └────────────┴────────────┴────────────┴────────────┘     │
│  ┌────────────┬────────────┐                               │
│  │ Reporting  │  General   │                               │
│  │   Agent    │   Query    │                               │
│  └────────────┴────────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Input | Output |
|-----------|---------------|-------|--------|
| **Conversation Memory** | Fetch conversation history | `session_id` | List of messages |
| **Intent Classifier** | Classify user intent | `query`, `history` | `Intent` + confidence |
| **Agent Selector** | Choose appropriate agent(s) | `Intent` | Agent instance(s) |
| **Agent Executor** | Run agent with context | `query`, `context` | Agent response |
| **Result Aggregator** | Combine multi-agent results | Multiple responses | Unified response |
| **Memory Saver** | Persist conversation | User/Assistant messages | Success/Failure |

---

## 🎯 Intent Classification

The **IntentClassifier** analyzes user queries to determine their intent using LLM-based classification.

### Supported Intent Types

```python
from app.services.intent_classifier import IntentType

class IntentType(Enum):
    RISK_ASSESSMENT = "risk_assessment"        # Risk analysis queries
    INCIDENT_RESPONSE = "incident_response"    # Security incident handling
    COMPLIANCE_CHECK = "compliance_check"      # Compliance/audit queries
    THREAT_INTELLIGENCE = "threat_intelligence" # Threat intel queries
    REPORTING = "reporting"                    # Report generation
    PROACTIVE_REVIEW = "proactive_review"      # Proactive security reviews
    GENERAL_QUERY = "general_query"            # General questions
```

### Classification Process

```python
from app.services.intent_classifier import IntentClassifier

# Initialize classifier
classifier = IntentClassifier(llm_service)

# Classify a query
intent = await classifier.classify_intent(
    query="¿Cuáles son los riesgos críticos en el servidor web?",
    conversation_history=[
        {"role": "user", "content": "Hola"},
        {"role": "assistant", "content": "Hola, ¿en qué puedo ayudarte?"}
    ]
)

# Result
print(f"Intent: {intent.intent_type}")          # IntentType.RISK_ASSESSMENT
print(f"Confidence: {intent.confidence}")       # 0.95
print(f"Entities: {intent.entities}")           # ["servidor web"]
print(f"Reasoning: {intent.reasoning}")         # "User is asking about risks..."
```

### Classification Examples

| Query | Intent | Confidence | Reasoning |
|-------|--------|------------|-----------|
| "¿Cuáles son los riesgos críticos?" | `RISK_ASSESSMENT` | 0.95 | Direct risk inquiry |
| "Detectamos ransomware" | `INCIDENT_RESPONSE` | 0.98 | Active security incident |
| "¿Cumplimos con ISO 27001?" | `COMPLIANCE_CHECK` | 0.92 | Compliance inquiry |
| "Últimas amenazas de APT28" | `THREAT_INTELLIGENCE` | 0.90 | Threat actor query |
| "Dame reporte mensual" | `REPORTING` | 0.88 | Report request |
| "Revisa configs de AWS" | `PROACTIVE_REVIEW` | 0.85 | Proactive check |
| "¿Qué es un firewall?" | `GENERAL_QUERY` | 0.80 | General question |

### Confidence Thresholds

```python
# Orchestrator thresholds
CLARIFICATION_THRESHOLD = 0.7   # Ask for clarification if below
HIGH_CONFIDENCE = 0.85          # Direct routing
MEDIUM_CONFIDENCE = 0.70        # Route with caution
LOW_CONFIDENCE = 0.50           # Require clarification
```

**Behavior:**
- `confidence >= 0.85`: Execute agent directly
- `0.70 <= confidence < 0.85`: Execute with clarification option
- `confidence < 0.70`: Ask user to clarify intent

---

## 🤖 Agent Selection

The orchestrator maintains a mapping of intents to specialized agents.

### Agent Mapping

```python
INTENT_TO_AGENT_MAP = {
    IntentType.RISK_ASSESSMENT: "risk_agent",
    IntentType.INCIDENT_RESPONSE: "incident_agent",
    IntentType.COMPLIANCE_CHECK: "compliance_agent",
    IntentType.THREAT_INTELLIGENCE: "threat_agent",
    IntentType.REPORTING: "reporting_agent",
    IntentType.PROACTIVE_REVIEW: "proactive_agent",
    IntentType.GENERAL_QUERY: None,  # Handled directly by orchestrator
}
```

### Single Agent Selection

```python
# Simple case: one intent → one agent
async def select_agent(self, intent: Intent) -> Agent:
    """Select single agent based on intent."""
    agent_name = INTENT_TO_AGENT_MAP.get(intent.intent_type)
    
    if not agent_name:
        # Handle directly with LLM
        return None
    
    agent = self.agents.get(intent.intent_type)
    
    if not agent:
        raise ValueError(f"Agent {agent_name} not initialized")
    
    return agent
```

### Multi-Agent Selection

When confidence is below threshold or query requires multiple perspectives:

```python
async def select_agents(self, intent: Intent) -> List[Agent]:
    """Select multiple agents for complex queries."""
    agents = []
    
    # Primary agent
    primary_agent = self.agents.get(intent.intent_type)
    if primary_agent:
        agents.append(primary_agent)
    
    # Secondary agents based on entities
    if "compliance" in intent.entities:
        agents.append(self.agents[IntentType.COMPLIANCE_CHECK])
    
    if "threat" in intent.entities:
        agents.append(self.agents[IntentType.THREAT_INTELLIGENCE])
    
    return agents
```

### Agent Initialization

```python
from app.agents.orchestrator import CISOOrchestrator
from app.agents.risk_agent import RiskAssessmentAgent
from app.agents.incident_agent import IncidentResponseAgent

# Initialize agents
agents = {
    IntentType.RISK_ASSESSMENT: RiskAssessmentAgent(
        llm_service=llm_service,
        rag_service=rag_service,
        db_session=db_session
    ),
    IntentType.INCIDENT_RESPONSE: IncidentResponseAgent(
        llm_service=llm_service,
        playbook_service=playbook_service,
        db_session=db_session
    ),
    # ... more agents
}

# Initialize orchestrator
orchestrator = CISOOrchestrator(
    intent_classifier=intent_classifier,
    agents=agents,
    conversation_memory=conversation_memory,
    llm_service=llm_service
)
```

---

## 🔄 Result Aggregation

When multiple agents are executed, their results need to be synthesized.

### Aggregation Strategies

#### 1. Sequential Aggregation
Execute agents in order, passing results to next agent:

```python
async def aggregate_sequential(
    self,
    agents: List[Agent],
    query: str,
    context: Dict[str, Any]
) -> AgentResponse:
    """Execute agents sequentially, building on previous results."""
    responses = []
    
    for agent in agents:
        # Add previous responses to context
        agent_context = {
            **context,
            "previous_responses": responses
        }
        
        response = await agent.process(query, agent_context)
        responses.append(response)
    
    # Synthesize final response
    return await self._synthesize_responses(responses)
```

#### 2. Parallel Aggregation
Execute agents in parallel, then combine:

```python
async def aggregate_parallel(
    self,
    agents: List[Agent],
    query: str,
    context: Dict[str, Any]
) -> AgentResponse:
    """Execute agents in parallel and combine results."""
    # Execute all agents concurrently
    tasks = [
        agent.process(query, context)
        for agent in agents
    ]
    
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out errors
    valid_responses = [
        r for r in responses 
        if not isinstance(r, Exception)
    ]
    
    # Synthesize final response
    return await self._synthesize_responses(valid_responses)
```

#### 3. Response Synthesis

```python
async def _synthesize_responses(
    self,
    responses: List[AgentResponse]
) -> AgentResponse:
    """Synthesize multiple agent responses into one."""
    
    # Combine response texts
    combined_text = "\n\n".join([
        f"**{r.agent_name}:**\n{r.response}"
        for r in responses
    ])
    
    # Aggregate metadata
    all_sources = []
    for r in responses:
        all_sources.extend(r.sources or [])
    
    # Use LLM to create cohesive summary
    synthesis_prompt = f"""
    Synthesize these agent responses into a cohesive answer:
    
    {combined_text}
    
    Create a unified response that:
    1. Addresses the user's query comprehensively
    2. Highlights key insights from each agent
    3. Avoids redundancy
    4. Maintains professional tone
    """
    
    final_response = await self.llm_service.generate(synthesis_prompt)
    
    return AgentResponse(
        response=final_response,
        agent_name="orchestrator",
        sources=list(set(all_sources)),
        metadata={
            "agents_used": [r.agent_name for r in responses],
            "aggregation_method": "synthesis"
        }
    )
```

---

## 📚 Query Routing Examples

### Example 1: Risk Assessment Query

```python
# User query
query = "¿Cuáles son los riesgos críticos en nuestro servidor web de producción?"

# 1. Intent Classification
intent = await classifier.classify_intent(query)
# → IntentType.RISK_ASSESSMENT (confidence: 0.95)

# 2. Agent Selection
agent = agents[IntentType.RISK_ASSESSMENT]
# → RiskAssessmentAgent

# 3. Agent Execution
response = await agent.process(query, context={
    "session_id": session_id,
    "user_id": user_id
})

# 4. Response
# → "Identifiqué 3 riesgos críticos en production-web-01:
#    1. CVE-2025-1234 (CVSS 9.8) - RCE en Apache Struts
#    2. Configuración SSH expuesta (puerto 22 público)
#    3. Credenciales débiles en base de datos..."
```

### Example 2: Incident Response Query

```python
# User query
query = "Detectamos ransomware en el servidor de archivos. Los archivos tienen extensión .locked"

# 1. Intent Classification
intent = await classifier.classify_intent(query)
# → IntentType.INCIDENT_RESPONSE (confidence: 0.98)

# 2. Agent Selection
agent = agents[IntentType.INCIDENT_RESPONSE]
# → IncidentResponseAgent

# 3. Agent Execution
response = await agent.process(query, context={})

# 4. Response includes:
# - Incident classification (type: ransomware, severity: CRITICAL)
# - Response plan with 6+ steps
# - Immediate actions (0-15 min)
# - Containment steps (15 min - 4 hrs)
# - Incident number (INC-2026-042)
# - Stakeholder notifications
```

### Example 3: Multi-Turn Conversation

```python
# Turn 1
query1 = "¿Cuáles son los riesgos críticos?"
response1 = await orchestrator.process_request(query1, session_id, user_id)
# → Lists 3 critical risks

# Turn 2 (with context)
query2 = "Dame más detalles del primer riesgo"
response2 = await orchestrator.process_request(query2, session_id, user_id)
# → Orchestrator retrieves conversation history
# → Understands "primer riesgo" refers to CVE-2025-1234 from Turn 1
# → Returns detailed analysis of that specific CVE
```

### Example 4: Complex Multi-Agent Query

```python
# Query requiring multiple agents
query = "Evalúa el riesgo del servidor web y verifica cumplimiento con ISO 27001"

# 1. Intent Classification
# → Primary: RISK_ASSESSMENT (0.85)
# → Secondary: COMPLIANCE_CHECK (detected in entities)

# 2. Multi-Agent Selection
agents_to_use = [
    agents[IntentType.RISK_ASSESSMENT],
    agents[IntentType.COMPLIANCE_CHECK]
]

# 3. Parallel Execution
responses = await asyncio.gather(
    agents[0].process(query, context),
    agents[1].process(query, context)
)

# 4. Synthesis
final_response = await orchestrator._synthesize_responses(responses)
# → "Análisis de Riesgo:
#    - 2 vulnerabilidades críticas encontradas...
#    
#    Cumplimiento ISO 27001:
#    - Control A.8.1: ✅ Compliant
#    - Control A.12.6: ❌ Gap encontrado..."
```

---

## ⚙️ Configuration

### Orchestrator Configuration

```python
# app/core/config.py

class Settings(BaseSettings):
    # Orchestrator settings
    ORCHESTRATOR_CLARIFICATION_THRESHOLD: float = 0.7
    ORCHESTRATOR_HIGH_CONFIDENCE: float = 0.85
    ORCHESTRATOR_MULTI_AGENT_THRESHOLD: float = 0.7
    ORCHESTRATOR_MAX_AGENTS: int = 3
    ORCHESTRATOR_TIMEOUT_SECONDS: int = 30
    
    # Memory settings
    CONVERSATION_WINDOW_SIZE: int = 10
    CONVERSATION_MAX_TOKENS: int = 4000
    
    # Agent-specific settings
    RISK_AGENT_ENABLED: bool = True
    INCIDENT_AGENT_ENABLED: bool = True
    COMPLIANCE_AGENT_ENABLED: bool = True
    THREAT_AGENT_ENABLED: bool = True
```

### Environment Variables

```bash
# .env
ORCHESTRATOR_CLARIFICATION_THRESHOLD=0.7
ORCHESTRATOR_HIGH_CONFIDENCE=0.85
CONVERSATION_WINDOW_SIZE=10
RISK_AGENT_ENABLED=true
INCIDENT_AGENT_ENABLED=true
```

---

## 🔌 API Reference

### Process Request

```python
async def process_request(
    user_query: str,
    session_id: str,
    user_id: str
) -> OrchestratorResponse:
    """
    Main entry point for processing user requests.
    
    Args:
        user_query: Natural language query from user
        session_id: Conversation session identifier
        user_id: User identifier
    
    Returns:
        OrchestratorResponse with:
        - response: Final answer
        - intent: Classified intent
        - confidence: Classification confidence
        - agent_used: Agent that processed query
        - sources: Information sources used
        - metadata: Additional info (timing, etc.)
    """
```

### HTTP Endpoint

```http
POST /api/v1/chat/message
Content-Type: application/json
Authorization: Bearer <token>

{
  "message": "¿Cuáles son los riesgos críticos?",
  "session_id": "sess-123-abc",
  "user_id": "user-456"
}

Response 200:
{
  "response": "Actualmente tenemos 3 riesgos críticos...",
  "intent": "risk_assessment",
  "confidence": 0.95,
  "agent_used": "RiskAssessmentAgent",
  "sources": ["knowledge_base", "recent_scans"],
  "processing_time_ms": 1234,
  "metadata": {
    "context_used": true,
    "clarification_needed": false
  }
}
```

---

## ✅ Best Practices

### 1. Intent Classification

**DO:**
- ✅ Provide conversation history for better context
- ✅ Use entities to enhance classification
- ✅ Set appropriate confidence thresholds
- ✅ Handle low-confidence cases with clarification

**DON'T:**
- ❌ Classify without context
- ❌ Ignore confidence scores
- ❌ Hardcode intent mappings
- ❌ Skip entity extraction

### 2. Agent Selection

**DO:**
- ✅ Initialize all agents at startup
- ✅ Handle agent failures gracefully
- ✅ Use circuit breakers for agent calls
- ✅ Log agent selection decisions

**DON'T:**
- ❌ Create agents per request
- ❌ Fail entire request if one agent fails
- ❌ Ignore agent timeouts
- ❌ Skip error handling

### 3. Result Aggregation

**DO:**
- ✅ Use parallel execution when possible
- ✅ Synthesize responses coherently
- ✅ Preserve source attribution
- ✅ Handle partial failures

**DON'T:**
- ❌ Concatenate responses naively
- ❌ Lose agent-specific insights
- ❌ Ignore response order
- ❌ Skip error responses

### 4. Performance

**DO:**
- ✅ Cache frequently used data
- ✅ Use connection pooling
- ✅ Implement timeouts
- ✅ Monitor latency metrics

**DON'T:**
- ❌ Make sequential calls when parallel is possible
- ❌ Ignore memory leaks
- ❌ Skip request cancellation
- ❌ Forget to profile hot paths

---

## 📊 Monitoring & Metrics

### Key Metrics to Track

```python
# Metrics to monitor
metrics = {
    "orchestrator.requests_total": Counter,
    "orchestrator.request_duration_seconds": Histogram,
    "orchestrator.intent_classification_accuracy": Gauge,
    "orchestrator.agent_selection_duration": Histogram,
    "orchestrator.multi_agent_requests": Counter,
    "orchestrator.clarifications_requested": Counter,
    "orchestrator.errors_total": Counter,
}
```

### Logging

```python
import structlog

logger = structlog.get_logger(__name__)

# Log orchestrator decisions
logger.info(
    "request_processed",
    session_id=session_id,
    intent=intent.intent_type.value,
    confidence=intent.confidence,
    agent_used=agent.name,
    processing_time_ms=processing_time,
    multi_agent=len(agents) > 1
)
```

---

## 🔗 Related Documentation

- [Incident Response](./INCIDENT-RESPONSE.md)
- [Conversation Memory](./CONVERSATION-MEMORY.md)
- [API Documentation](./API.md)
- [Agent Development Guide](./AGENT-DEVELOPMENT.md)

---

**Maintained by:** CISO Digital Development Team  
**Last Review:** 2026-02-06  
**Next Review:** 2026-03-06
