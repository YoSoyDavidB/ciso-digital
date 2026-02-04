# Agentes de IA - CISO Digital

## 1. Arquitectura Multi-Agente

### 1.1 Filosofía de Diseño

El CISO Digital utiliza una **arquitectura multi-agente** donde cada agente es un especialista en su dominio. Esta aproximación ofrece:

**Ventajas**:
- Prompts más focalizados = respuestas de mayor calidad
- Especialización permite optimización independiente
- Escalabilidad horizontal (agregar nuevos agentes fácilmente)
- Mantenimiento más simple
- Posibilidad de usar diferentes LLMs por agente según necesidad

**Principio clave**: Un agente maestro (Orchestrator) coordina a agentes especializados

### 1.2 Tipos de Agentes

```
CISO Orchestrator (Coordinador Principal)
    ├── Risk Assessment Agent (Evaluación de Riesgos)
    ├── Incident Response Agent (Respuesta a Incidentes)
    ├── Compliance Agent (Cumplimiento Normativo)
    ├── Threat Intelligence Agent (Inteligencia de Amenazas)
    ├── Reporting Agent (Generación de Reportes)
    └── Proactive Planning Agent (Planificación Proactiva) ⭐ Nuevo
```

---

## 2. CISO Orchestrator - Agente Principal

### 2.1 Responsabilidades

El Orchestrator es el punto de entrada y coordinador principal:

1. **Análisis de intención**: Determinar qué quiere el usuario
2. **Routing**: Decidir qué agente(s) activar
3. **Context management**: Mantener el contexto conversacional
4. **Coordinación multi-agente**: Cuando múltiples agentes son necesarios
5. **Consolidación de respuestas**: Unificar outputs de múltiples agentes
6. **Escalamiento**: Decidir cuando elevar criticidad

### 2.2 System Prompt

```python
ORCHESTRATOR_SYSTEM_PROMPT = """
Eres el CISO Digital, un Chief Information Security Officer con IA avanzada para una organización.

TU ROL:
- Eres el punto de contacto principal para todas las consultas de seguridad
- Coordinas equipos especializados (agentes) para resolver problemas complejos
- Mantienes una visión holística de la postura de seguridad organizacional
- Tomas decisiones estratégicas basadas en riesgo y impacto al negocio

TU EXPERTISE:
- Gestión de riesgos de seguridad de la información
- Respuesta y manejo de incidentes
- Cumplimiento normativo (ISO 27001, NIST, GDPR, etc.)
- Arquitectura de seguridad
- Gobernanza de seguridad
- Inteligencia de amenazas

AGENTES ESPECIALIZADOS A TU DISPOSICIÓN:
1. Risk Assessment Agent: Evaluación y gestión de riesgos
2. Incident Response Agent: Manejo de incidentes de seguridad
3. Compliance Agent: Verificación de cumplimiento normativo
4. Threat Intelligence Agent: Análisis de amenazas y TTPs
5. Reporting Agent: Generación de reportes y métricas
6. Proactive Planning Agent: Identificación de gaps y propuestas proactivas

PROCESO DE TOMA DE DECISIONES:
1. Analiza la consulta del usuario cuidadosamente
2. Determina qué información necesitas (búsqueda RAG)
3. Decide qué agente(s) especializado(s) activar
4. Si múltiples agentes son necesarios, coordínalos en secuencia lógica
5. Consolida respuestas en una respuesta coherente y accionable
6. Si detectas situaciones críticas, escala apropiadamente

COMUNICACIÓN:
- Sé claro, conciso y profesional
- Prioriza acciones concretas sobre teoría
- Cuando des recomendaciones, incluye justificación basada en riesgo
- Si algo es crítico, hazlo explícito
- Usa terminología técnica apropiada pero explica cuando sea necesario

CONTEXTO ACTUAL:
{context}

MEMORIA CONVERSACIONAL:
{conversation_history}

DOCUMENTOS RELEVANTES (RAG):
{rag_documents}
"""
```

### 2.3 Flujo de Procesamiento

```python
class CISOOrchestrator:
    def __init__(self, llm, rag_system, agents_registry):
        self.llm = llm
        self.rag = rag_system
        self.agents = agents_registry
        self.conversation_memory = ConversationMemory()
    
    async def process_query(self, user_query: str, session_id: str) -> Response:
        # 1. Cargar contexto conversacional
        context = await self.conversation_memory.load(session_id)
        
        # 2. Búsqueda RAG - obtener documentos relevantes
        rag_docs = await self.rag.search(
            query=user_query,
            top_k=5,
            filters={
                "status": "active"
            }
        )
        
        # 3. Analizar intención y determinar ruta
        intent_analysis = await self._analyze_intent(
            query=user_query,
            context=context,
            rag_docs=rag_docs
        )
        
        # 4. Routing a agentes especializados
        if intent_analysis.requires_multiple_agents:
            response = await self._multi_agent_execution(
                query=user_query,
                agents_needed=intent_analysis.agents_needed,
                context=context,
                rag_docs=rag_docs
            )
        else:
            agent = self.agents[intent_analysis.primary_agent]
            response = await agent.execute(
                query=user_query,
                context=context,
                rag_docs=rag_docs
            )
        
        # 5. Post-processing y validación
        validated_response = await self._validate_response(response)
        
        # 6. Guardar en memoria
        await self.conversation_memory.save(
            session_id=session_id,
            user_query=user_query,
            response=validated_response,
            metadata={
                "intent": intent_analysis.intent,
                "agents_used": intent_analysis.agents_needed,
                "rag_docs_count": len(rag_docs)
            }
        )
        
        return validated_response
    
    async def _analyze_intent(self, query, context, rag_docs):
        """Analiza la intención del usuario y determina routing"""
        
        analysis_prompt = f"""
        Analiza la siguiente consulta y determina:
        1. Intención principal (risk_assessment, incident_response, compliance_check, etc.)
        2. Entidades mencionadas (risk IDs, asset IDs, frameworks, etc.)
        3. Qué agente(s) especializado(s) se necesitan
        4. Prioridad/urgencia
        
        Consulta: {query}
        Contexto conversacional: {context}
        
        Responde en JSON:
        {{
            "intent": "string",
            "entities": {{}},
            "primary_agent": "string",
            "agents_needed": ["string"],
            "urgency": "low|medium|high|critical",
            "reasoning": "string"
        }}
        """
        
        analysis = await self.llm.generate(analysis_prompt, response_format="json")
        return IntentAnalysis(**analysis)
    
    async def _multi_agent_execution(self, query, agents_needed, context, rag_docs):
        """Ejecuta múltiples agentes en secuencia o paralelo según necesidad"""
        
        results = []
        
        # Determinar si ejecutar en secuencia o paralelo
        if self._requires_sequential_execution(agents_needed):
            # Secuencial: output de un agente puede ser input del siguiente
            for agent_name in agents_needed:
                agent = self.agents[agent_name]
                result = await agent.execute(
                    query=query,
                    context=context,
                    rag_docs=rag_docs,
                    previous_results=results
                )
                results.append(result)
        else:
            # Paralelo: agentes independientes
            tasks = [
                self.agents[agent_name].execute(
                    query=query,
                    context=context,
                    rag_docs=rag_docs
                )
                for agent_name in agents_needed
            ]
            results = await asyncio.gather(*tasks)
        
        # Consolidar resultados
        consolidated = await self._consolidate_results(results)
        return consolidated
```

---

## 3. Risk Assessment Agent

### 3.1 Especialización

Experto en evaluación, análisis y gestión de riesgos de seguridad.

**Capacidades**:
- Identificar y evaluar nuevos riesgos
- Calcular scores de riesgo (likelihood × impact)
- Priorizar riesgos según criticidad
- Recomendar mitigaciones
- Analizar riesgos residuales
- Generar matrices de riesgo

### 3.2 System Prompt

```python
RISK_AGENT_SYSTEM_PROMPT = """
Eres el Risk Assessment Agent del CISO Digital, especialista en gestión de riesgos de seguridad.

TU EXPERTISE:
- Metodologías de evaluación de riesgos (NIST SP 800-30, ISO 27005, FAIR)
- Análisis cuantitativo y cualitativo de riesgos
- Matrices de riesgo y heat maps
- Análisis de impacto al negocio
- Cálculo de riesgo residual
- Frameworks de control (ISO 27001, NIST CSF, CIS Controls)

PROCESO DE EVALUACIÓN DE RIESGOS:
1. IDENTIFICACIÓN:
   - Analiza el contexto proporcionado
   - Identifica amenazas, vulnerabilidades y activos afectados
   - Considera el entorno de negocio

2. ANÁLISIS:
   - Likelihood (probabilidad): rare, unlikely, possible, likely, certain
   - Impact (impacto): negligible, minor, moderate, major, severe
   - Risk Score = Likelihood (1-5) × Impact (1-5)
   
3. EVALUACIÓN:
   - Risk Score 1-5: Low
   - Risk Score 6-11: Medium
   - Risk Score 12-19: High
   - Risk Score 20-25: Critical

4. MITIGACIÓN:
   - Proponer controles aplicables
   - Considerar costo vs beneficio
   - Calcular riesgo residual esperado

CONSIDERACIONES IMPORTANTES:
- Siempre contextualizar el riesgo al negocio
- Priorizar riesgos que afecten operaciones críticas
- Considerar riesgos emergentes y tendencias
- Recomendar tratamiento: mitigar, transferir, aceptar, o evitar
- Mapear controles a frameworks relevantes

FORMATO DE OUTPUT:
Cuando evalúes un riesgo, estructura así:
1. Resumen ejecutivo (2-3 líneas)
2. Análisis detallado:
   - Amenaza identificada
   - Vulnerabilidad explotada
   - Activos afectados
   - Likelihood score y justificación
   - Impact score y justificación
   - Risk score total
3. Recomendaciones de mitigación (priorizadas)
4. Riesgo residual estimado post-mitigación
5. Acciones inmediatas (si es high/critical)

HERRAMIENTAS DISPONIBLES:
{tools}

CONTEXTO ORGANIZACIONAL:
{org_context}

DOCUMENTOS RELEVANTES:
{rag_documents}
"""
```

### 3.3 Herramientas (Tools)

```python
risk_agent_tools = [
    {
        "name": "get_asset_info",
        "description": "Obtiene información detallada de un activo por ID",
        "parameters": {
            "asset_id": "UUID del activo",
            "include_vulnerabilities": "bool - incluir vulnerabilidades conocidas"
        }
    },
    {
        "name": "get_vulnerabilities_by_asset",
        "description": "Lista vulnerabilidades de un activo específico",
        "parameters": {
            "asset_id": "UUID del activo",
            "severity_filter": "optional - filtrar por severidad"
        }
    },
    {
        "name": "calculate_risk_score",
        "description": "Calcula risk score basado en likelihood e impact",
        "parameters": {
            "likelihood": "int 1-5",
            "impact": "int 1-5"
        }
    },
    {
        "name": "get_similar_risks",
        "description": "Busca riesgos similares en el historial",
        "parameters": {
            "risk_description": "string",
            "top_k": "int - número de resultados"
        }
    },
    {
        "name": "create_risk",
        "description": "Crea un nuevo registro de riesgo en la base de datos",
        "parameters": {
            "title": "string",
            "description": "string",
            "category": "string",
            "severity": "critical|high|medium|low",
            "likelihood_score": "int 1-5",
            "impact_score": "int 1-5",
            "mitigation_plan": "string",
            "assigned_to": "string",
            "target_closure_date": "date"
        }
    },
    {
        "name": "get_control_recommendations",
        "description": "Obtiene recomendaciones de controles para un tipo de riesgo",
        "parameters": {
            "risk_type": "string",
            "framework": "ISO27001|NIST_CSF|CIS"
        }
    }
]
```

### 3.4 Ejemplo de Ejecución

```python
# Query: "Evalúa el riesgo de un servidor web expuesto sin WAF"

# 1. RAG busca documentación relevante sobre web security
rag_docs = [
    "Best practices for web server hardening...",
    "ISO 27001 A.13.1.3 - Protection of network services..."
]

# 2. Agent usa herramientas
asset_info = get_asset_info(asset_id="web-server-001")
vulnerabilities = get_vulnerabilities_by_asset(asset_id="web-server-001")

# 3. Agent analiza con LLM
analysis = """
RESUMEN EJECUTIVO:
Servidor web de producción expuesto sin WAF representa un riesgo HIGH 
(score 16/25) de explotación de vulnerabilidades web y ataques DDoS.

ANÁLISIS DETALLADO:
- Amenaza: Atacantes externos buscando explotar vulnerabilidades web
- Vulnerabilidad: Ausencia de Web Application Firewall (WAF)
- Activos afectados: web-server-001 (criticidad: HIGH, datos: confidencial)
- Servicios expuestos: HTTPS (443), HTTP (80)
- Vulnerabilidades conocidas: 
  * SQL Injection (CVE-2024-1234, CVSS 8.5)
  * XSS persistente (CVSS 7.2)

SCORING:
- Likelihood: 4/5 (Likely)
  Justificación: Servidor público, scans automáticos constantes, 
  exploits disponibles para CVEs detectados
  
- Impact: 4/5 (Major)
  Justificación: Servidor maneja datos confidenciales de clientes,
  compromiso podría resultar en data breach (multas GDPR), 
  downtime afecta operaciones críticas

- Risk Score: 16/25 (HIGH)

RECOMENDACIONES DE MITIGACIÓN:
1. [INMEDIATO] Desplegar WAF (AWS WAF, Cloudflare, ModSecurity)
   - Tiempo: 1-2 días
   - Costo: $200/mes
   - Reducción de riesgo: HIGH → MEDIUM (score 8)
   
2. [URGENTE] Parchear vulnerabilidades conocidas
   - Aplicar updates para CVE-2024-1234
   - Implementar input validation
   
3. [CORTO PLAZO] Rate limiting y DDoS protection
   - Cloudflare Pro o similar
   
4. [MEDIO PLAZO] Implementar security headers
   - CSP, HSTS, X-Frame-Options

RIESGO RESIDUAL:
Con todas las mitigaciones: MEDIUM (score 6-8)
- Likelihood: 2/5 (Unlikely) - WAF bloquea la mayoría de ataques
- Impact: 4/5 (Major) - Impacto permanece si WAF es bypasseado

ACCIONES INMEDIATAS:
☐ Crear ticket para despliegue de WAF (URGENTE)
☐ Notificar a CTO sobre riesgo HIGH
☐ Programar emergency patch deployment
☐ Activar monitoring adicional en servidor
"""

# 4. Agent crea el riesgo en BD
create_risk(
    title="Servidor web expuesto sin WAF",
    severity="high",
    risk_score=16,
    mitigation_plan=analysis.mitigations,
    assigned_to="security_team"
)
```

---

## 4. Incident Response Agent

### 4.1 Especialización

Experto en detección, análisis y respuesta a incidentes de seguridad.

**Capacidades**:
- Clasificar incidentes por severidad
- Ejecutar playbooks de respuesta
- Coordinar acciones de contención
- Análisis forense básico
- Generación de post-mortems
- Lecciones aprendidas

### 4.2 System Prompt

```python
INCIDENT_AGENT_SYSTEM_PROMPT = """
Eres el Incident Response Agent, especialista en manejo de incidentes de seguridad.

TU EXPERTISE:
- Metodología NIST SP 800-61 (Incident Response Lifecycle)
- Fases: Detection, Analysis, Containment, Eradication, Recovery, Post-Incident
- Análisis de IOCs (Indicators of Compromise)
- MITRE ATT&CK Framework
- Forensics digital básico
- Gestión de crisis

PROCESO DE RESPUESTA:

1. DETECCIÓN Y ANÁLISIS (Detection & Analysis):
   - Verificar el incidente es real (descartar falsos positivos)
   - Clasificar tipo: malware, phishing, data breach, DDoS, unauthorized access
   - Determinar severidad basado en:
     * Confidentiality Impact
     * Integrity Impact  
     * Availability Impact
   - Identificar scope: sistemas afectados, datos comprometidos
   
2. CLASIFICACIÓN DE SEVERIDAD:
   - P1 (Critical): Impacto severo en operaciones críticas, data breach activo
   - P2 (High): Impacto significativo, potencial de escalamiento
   - P3 (Medium): Impacto limitado, sistemas no críticos
   - P4 (Low): Impacto mínimo, principalmente molestia

3. CONTENCIÓN (Containment):
   - Short-term: Acciones inmediatas para limitar daño
     * Aislar sistemas comprometidos
     * Bloquear IPs/dominios maliciosos
     * Deshabilitar cuentas comprometidas
   - Long-term: Soluciones temporales mientras se prepara remediación
   
4. ERRADICACIÓN (Eradication):
   - Eliminar causa raíz
   - Remover malware
   - Cerrar vectores de ataque
   - Parchear vulnerabilidades
   
5. RECUPERACIÓN (Recovery):
   - Restaurar sistemas a operación normal
   - Verificar que amenaza fue eliminada
   - Monitoreo incrementado post-recovery

6. POST-INCIDENT:
   - Documentar el incidente completamente
   - Lecciones aprendidas
   - Actualizar playbooks si es necesario
   - Métricas: Time to Detect, Time to Respond, Time to Resolve

PLAYBOOKS DISPONIBLES:
- Malware Response
- Phishing Response
- Data Breach Response
- DDoS Mitigation
- Ransomware Response
- Unauthorized Access Response
- Insider Threat Response

COMUNICACIÓN DURANTE INCIDENTES:
- P1/P2: Notificación inmediata a stakeholders
- Actualizaciones regulares (cada 30-60 min para P1)
- Post-mortem completo para P1/P2

HERRAMIENTAS DISPONIBLES:
{tools}

PLAYBOOK ACTIVO:
{active_playbook}

DOCUMENTOS RELEVANTES:
{rag_documents}
"""
```

### 4.3 Herramientas

```python
incident_agent_tools = [
    {
        "name": "create_incident",
        "description": "Crea un registro de incidente",
        "parameters": {
            "title": "string",
            "description": "string",
            "incident_type": "malware|phishing|data_breach|dos|unauthorized_access",
            "severity": "critical|high|medium|low",
            "affected_assets": "list of asset IDs",
            "detection_time": "timestamp"
        }
    },
    {
        "name": "execute_playbook_step",
        "description": "Ejecuta un paso específico de un playbook",
        "parameters": {
            "playbook_name": "string",
            "step_number": "int",
            "incident_id": "UUID"
        }
    },
    {
        "name": "isolate_asset",
        "description": "Aísla un activo de la red (contención)",
        "parameters": {
            "asset_id": "UUID",
            "isolation_type": "network|quarantine|shutdown"
        }
    },
    {
        "name": "block_ioc",
        "description": "Bloquea un IOC en sistemas de seguridad",
        "parameters": {
            "ioc_type": "ip|domain|hash|url",
            "ioc_value": "string",
            "systems": "list - firewall, waf, edr, email_gateway"
        }
    },
    {
        "name": "disable_user_account",
        "description": "Deshabilita una cuenta de usuario comprometida",
        "parameters": {
            "user_id": "string",
            "reason": "string"
        }
    },
    {
        "name": "send_alert",
        "description": "Envía alerta a stakeholders",
        "parameters": {
            "severity": "critical|high|medium|low",
            "recipients": "list",
            "channel": "slack|email|pagerduty",
            "message": "string"
        }
    },
    {
        "name": "search_similar_incidents",
        "description": "Busca incidentes similares en el historial",
        "parameters": {
            "incident_description": "string",
            "incident_type": "optional - filtro por tipo",
            "top_k": "int"
        }
    },
    {
        "name": "generate_incident_report",
        "description": "Genera reporte de incidente",
        "parameters": {
            "incident_id": "UUID",
            "report_type": "preliminary|final|post_mortem"
        }
    }
]
```

### 4.4 Playbook Example: Phishing Response

```python
PHISHING_RESPONSE_PLAYBOOK = {
    "name": "Phishing Response",
    "version": "2.0",
    "steps": [
        {
            "phase": "Detection & Analysis",
            "step": 1,
            "action": "Verify the phishing report",
            "details": [
                "Review reported email headers",
                "Analyze sender domain and SPF/DKIM",
                "Identify phishing indicators",
                "Determine if legitimate or false positive"
            ],
            "automated": False,
            "escalation_if_fails": "P2"
        },
        {
            "phase": "Detection & Analysis",
            "step": 2,
            "action": "Assess scope",
            "details": [
                "Check email gateway logs for delivery count",
                "Identify all recipients",
                "Determine if any users clicked links/opened attachments",
                "Check for credential submission to phishing site"
            ],
            "automated": True,
            "tools": ["email_gateway_api", "edr_query"]
        },
        {
            "phase": "Containment",
            "step": 3,
            "action": "Block malicious indicators",
            "details": [
                "Add sender domain/IP to email blocklist",
                "Block phishing URLs at web proxy/firewall",
                "Quarantine related emails in user mailboxes"
            ],
            "automated": True,
            "tools": ["email_gateway", "firewall", "web_proxy"]
        },
        {
            "phase": "Containment",
            "step": 4,
            "action": "User account protection",
            "details": [
                "If credentials compromised: Force password reset",
                "Enable MFA if not already enabled",
                "Review account activity for suspicious actions",
                "Revoke active sessions"
            ],
            "automated": True,
            "tools": ["identity_provider"],
            "conditional": "if credentials_compromised"
        },
        {
            "phase": "Eradication",
            "step": 5,
            "action": "Remove malicious artifacts",
            "details": [
                "Delete phishing emails from all mailboxes",
                "Remove any downloaded malware",
                "Clear browser cache on affected systems"
            ],
            "automated": True,
            "tools": ["email_gateway", "edr"]
        },
        {
            "phase": "Recovery",
            "step": 6,
            "action": "User communication and training",
            "details": [
                "Notify affected users",
                "Provide security awareness guidance",
                "Conduct mini phishing training if multiple users fell for it"
            ],
            "automated": False
        },
        {
            "phase": "Post-Incident",
            "step": 7,
            "action": "Documentation and lessons learned",
            "details": [
                "Document incident timeline",
                "Analyze why email filters didn't catch it",
                "Update email filtering rules if needed",
                "Generate metrics: detection time, response time"
            ],
            "automated": True,
            "tools": ["incident_management"]
        }
    ]
}
```

---

## 5. Compliance Agent

### 5.1 Especialización

Experto en verificación de cumplimiento normativo y frameworks de seguridad.

**Capacidades**:
- Verificar cumplimiento con frameworks (ISO 27001, NIST, PCI-DSS, GDPR)
- Mapear controles a requisitos
- Identificar gaps de cumplimiento
- Generar evidencias
- Recomendar remediaciones

### 5.2 System Prompt

```python
COMPLIANCE_AGENT_SYSTEM_PROMPT = """
Eres el Compliance Agent, especialista en cumplimiento normativo y frameworks de seguridad.

TU EXPERTISE:
- ISO/IEC 27001:2022 (Information Security Management)
- NIST Cybersecurity Framework (CSF) 2.0
- CIS Controls v8
- GDPR (General Data Protection Regulation)
- PCI-DSS v4.0
- HIPAA Security Rule
- SOC 2 Type II
- SOX (Sarbanes-Oxley) IT Controls

PROCESO DE VERIFICACIÓN DE CUMPLIMIENTO:

1. IDENTIFICACIÓN DE REQUISITOS:
   - Mapear control específico del framework
   - Entender el requisito exacto
   - Identificar evidencias necesarias

2. ASSESSMENT:
   - Revisar implementación actual
   - Comparar contra el estándar
   - Clasificar estado:
     * Compliant: Control totalmente implementado
     * Partially Compliant: Control parcialmente implementado
     * Non-Compliant: Control no implementado o insuficiente
     * Not Applicable: Control no aplica al contexto

3. GAP ANALYSIS:
   - Identificar diferencias entre estado actual y requerido
   - Cuantificar impacto del gap
   - Priorizar por riesgo y esfuerzo

4. RECOMENDACIONES:
   - Pasos concretos para cerrar gaps
   - Timeline realista
   - Recursos necesarios
   - Quick wins vs proyectos largos

5. EVIDENCIA:
   - Documentar evidencias de cumplimiento
   - Screenshots, logs, configuraciones, políticas
   - Tracking para auditorías

MAPEO DE CONTROLES:
Conoces el mapeo entre frameworks:
- ISO 27001 ↔ NIST CSF
- ISO 27001 ↔ CIS Controls
- NIST CSF ↔ CIS Controls
- GDPR Articles ↔ ISO 27001 Controls

SCORING:
- Compliance Score = (Controles Cumplidos / Controles Totales) × 100
- Por dominio/categoría
- Trend over time

HERRAMIENTAS DISPONIBLES:
{tools}

FRAMEWORKS ACTIVOS:
{active_frameworks}

DOCUMENTOS RELEVANTES:
{rag_documents}
"""
```

### 5.3 Ejemplo de Control Mapping

```python
# ISO 27001 A.9.1.2: Access to networks and network services
CONTROL_MAPPING = {
    "iso27001": {
        "control_id": "A.9.1.2",
        "control_name": "Access to networks and network services",
        "description": "Users should only be provided with access to the network and network services that they have been specifically authorized to use.",
        "requirement": "Implement authentication and authorization for network access"
    },
    "mapped_to": {
        "nist_csf": ["PR.AC-1", "PR.AC-3", "PR.AC-5"],
        "cis_controls": ["4.1", "4.2", "4.3", "5.3"],
        "pci_dss": ["8.1", "8.2", "8.3"]
    },
    "implementation_guidance": [
        "Implement network access control (NAC)",
        "Use 802.1X for wired/wireless authentication",
        "Deploy VPN with MFA for remote access",
        "Segment network by role/function",
        "Monitor and log all network access attempts"
    ],
    "evidence_types": [
        "Network access control policies",
        "NAC system configuration",
        "VPN authentication logs",
        "Network diagram showing segmentation",
        "User access reviews"
    ],
    "common_gaps": [
        "No formal authorization process for network access",
        "Guest network not properly isolated",
        "VPN without MFA",
        "No regular access reviews"
    ]
}
```

---

## 6. Proactive Planning Agent ⭐

### 6.1 Especialización

Este es el agente clave para el aspecto proactivo del CISO Digital.

**Capacidades**:
- Analizar documentación existente
- Detectar gaps (políticas faltantes, procedimientos incompletos)
- Proponer planes de trabajo
- Priorizar iniciativas
- Generar templates y guías
- Programar reviews periódicos

### 6.2 System Prompt

```python
PROACTIVE_PLANNING_AGENT_SYSTEM_PROMPT = """
Eres el Proactive Planning Agent, responsable de mantener la postura de seguridad 
de la organización mediante identificación proactiva de gaps y propuestas de mejora.

TU MISIÓN:
Garantizar que la organización tenga TODA la documentación, procesos y controles 
necesarios para una gestión de seguridad madura, identificando proactivamente 
lo que falta y proponiendo soluciones.

TU EXPERTISE:
- Análisis de madurez de programas de seguridad
- Frameworks de seguridad (ISO 27001, NIST CSF, CIS)
- Best practices de documentación de seguridad
- Project management y planificación
- Gestión del cambio organizacional

PROCESO DE ANÁLISIS PROACTIVO:

1. ANÁLISIS DE ESTADO ACTUAL:
   - Revisar documentación existente en knowledge base
   - Inventario de políticas, procedimientos, estándares
   - Estado de cumplimiento con frameworks
   - Riesgos abiertos y su tracking
   - Incidentes recurrentes

2. DETECCIÓN DE GAPS:
   
   A. DOCUMENTACIÓN:
   - ¿Qué políticas obligatorias faltan?
     * Según ISO 27001: Necesitamos 93+ políticas/procedimientos
     * Según framework de la org: ¿cuáles son mandatorios?
   - ¿Políticas desactualizadas? (> 1 año sin review)
   - ¿Procedimientos sin documentar?
   
   B. PROCESOS:
   - ¿Existen procesos definidos para todas las actividades críticas?
   - ¿Los procesos tienen owners asignados?
   - ¿Hay métricas para medir efectividad de procesos?
   
   C. CONTROLES:
   - ¿Controles de seguridad faltantes?
   - ¿Controles implementados pero no documentados?
   - ¿Controles que requieren mejora?
   
   D. CAPACITACIÓN:
   - ¿Personal con training requerido?
   - ¿Security awareness actualizado?
   
   E. TECNOLOGÍA:
   - ¿Herramientas de seguridad necesarias pero ausentes?
   - ¿Activos sin las protecciones adecuadas?

3. PRIORIZACIÓN:
   Clasifica gaps por:
   - Criticidad: ¿Qué impacto tiene la ausencia?
     * P1: Crítico - Riesgo inmediato o requisito legal
     * P2: High - Riesgo significativo
     * P3: Medium - Mejora importante
     * P4: Low - Nice to have
   
   - Esfuerzo: ¿Cuánto trabajo requiere?
     * Quick Win: <1 semana
     * Short-term: 1-4 semanas
     * Medium-term: 1-3 meses
     * Long-term: >3 meses
   
   - Dependencias: ¿Qué necesita hacerse primero?

4. GENERACIÓN DE PROPUESTAS:
   
   Para cada gap, generar:
   - Descripción clara del problema
   - Impacto de no resolverlo
   - Propuesta de solución
   - Plan de trabajo detallado con:
     * Actividades específicas
     * Recursos necesarios
     * Timeline estimado
     * Owner sugerido
     * Criterios de éxito
   - Si es documentación: Ofrecer template o outline

5. SEGUIMIENTO:
   - Crear tareas programadas para review
   - Alertar cuando deadlines se acercan
   - Reportar progreso mensualmente

TIPOS DE PROPUESTAS:

A. POLÍTICA FALTANTE:
"Detecté que falta la Política de [X]. Esta política es requerida por [framework] 
y su ausencia representa un gap de cumplimiento.

PROPUESTA:
Título: Desarrollar Política de [X]
Prioridad: [P1/P2/P3/P4]
Esfuerzo: [Quick Win / Short-term / Medium-term / Long-term]

Plan de trabajo:
1. Semana 1: Revisar mejores prácticas y templates
2. Semana 2: Draft inicial con inputs de [stakeholders]
3. Semana 3: Review y feedback
4. Semana 4: Aprobación y publicación

Owner sugerido: [rol/persona]
Deadline propuesto: [fecha]

TEMPLATE INCLUIDO:
[outline de la política]"

B. PROCESO INMADURO:
"El proceso de [X] existe pero requiere mejora. Problemas detectados:
- [lista de issues]

PROPUESTA:
Mejorar proceso de [X] con:
1. [mejora específica]
2. [mejora específica]
..."

C. CONTROL FALTANTE:
"Control [ID] de [framework] no implementado. Este control mitiga [riesgos].

PROPUESTA:
Implementar [control específico]..."

NOTIFICACIONES:
- Envía notificaciones mensuales con resumen de gaps
- Alertas de políticas por vencer su review
- Celebra cuando gaps son cerrados

HERRAMIENTAS DISPONIBLES:
{tools}

DOCUMENTACIÓN ACTUAL:
{current_documentation}

FRAMEWORKS APLICABLES:
{applicable_frameworks}
"""
```

### 6.3 Herramientas

```python
proactive_agent_tools = [
    {
        "name": "analyze_knowledge_base",
        "description": "Analiza el contenido completo de la knowledge base para detectar gaps",
        "parameters": {
            "framework": "ISO27001|NIST_CSF|CIS|all",
            "scope": "policies|procedures|controls|all"
        }
    },
    {
        "name": "check_policy_coverage",
        "description": "Verifica qué políticas obligatorias existen vs requeridas",
        "parameters": {
            "framework": "string"
        }
    },
    {
        "name": "get_outdated_documents",
        "description": "Lista documentos que requieren review",
        "parameters": {
            "older_than_days": "int",
            "document_type": "policy|procedure|standard|all"
        }
    },
    {
        "name": "generate_work_plan",
        "description": "Genera un plan de trabajo detallado para cerrar un gap",
        "parameters": {
            "gap_description": "string",
            "priority": "P1|P2|P3|P4",
            "deadline": "date"
        }
    },
    {
        "name": "create_policy_template",
        "description": "Genera template/outline para una política",
        "parameters": {
            "policy_type": "string",
            "framework": "optional - ISO27001, etc"
        }
    },
    {
        "name": "send_gap_notification",
        "description": "Envía notificación sobre gaps detectados",
        "parameters": {
            "recipients": "list",
            "gaps": "list of gap objects",
            "priority": "high|medium|low"
        }
    },
    {
        "name": "schedule_review",
        "description": "Programa una review futura de documento/control",
        "parameters": {
            "document_id": "UUID",
            "review_date": "date",
            "assigned_to": "string"
        }
    }
]
```

### 6.4 Ejemplo de Ejecución Proactiva

```python
# Trigger: Cron job semanal

# 1. Analizar estado actual
analysis = proactive_agent.analyze_knowledge_base(
    framework="ISO27001",
    scope="all"
)

# Output del análisis:
{
    "total_required_policies": 45,
    "existing_policies": 30,
    "missing_policies": [
        {
            "name": "Access Control Policy",
            "control_id": "A.9.1.1",
            "priority": "P1",
            "reason": "Critical control, required for ISO 27001"
        },
        {
            "name": "Backup Policy",
            "control_id": "A.12.3.1",
            "priority": "P2",
            "reason": "Important for business continuity"
        }
        # ... más
    ],
    "outdated_documents": [
        {
            "name": "Incident Response Procedure",
            "last_review": "2024-02-01",
            "days_since_review": 368,
            "next_review_due": "2025-02-01 (overdue)"
        }
    ],
    "controls_not_implemented": [
        {
            "control_id": "A.8.5.4",
            "name": "Deletion of information",
            "priority": "P2"
        }
    ]
}

# 2. Generar propuesta para gap más crítico
proposal = proactive_agent.generate_work_plan(
    gap_description="Missing Access Control Policy (ISO 27001 A.9.1.1)",
    priority="P1",
    deadline="2026-03-15"
)

# Output:
{
    "title": "Develop Access Control Policy",
    "gap_description": "Currently missing formal Access Control Policy required by ISO 27001 control A.9.1.1",
    "business_impact": "Gap in compliance, potential audit finding, unclear access control procedures for staff",
    "priority": "P1",
    "effort": "Short-term (2-3 weeks)",
    
    "work_plan": {
        "phase_1": {
            "name": "Research and Template",
            "duration": "Week 1",
            "activities": [
                "Review ISO 27001 A.9.x requirements",
                "Research industry best practices",
                "Obtain template from similar organizations",
                "Draft initial outline"
            ],
            "deliverable": "Policy outline approved by CISO"
        },
        "phase_2": {
            "name": "Content Development",
            "duration": "Week 2",
            "activities": [
                "Draft policy content",
                "Include: user access provisioning, access reviews, privileged access management",
                "Get input from IT and HR",
                "Address current gaps in access management"
            ],
            "deliverable": "Policy draft v1"
        },
        "phase_3": {
            "name": "Review and Approval",
            "duration": "Week 3",
            "activities": [
                "Circulate for stakeholder review",
                "Incorporate feedback",
                "Final CISO approval",
                "Publish to policy portal"
            ],
            "deliverable": "Approved and published policy"
        }
    },
    
    "resources_needed": [
        "CISO time: 4 hours",
        "IT Manager input: 2 hours",
        "HR input: 1 hour"
    ],
    
    "success_criteria": [
        "Policy addresses all A.9.x controls",
        "Stakeholders have reviewed and approved",
        "Policy published and accessible to all staff",
        "Training plan created for policy rollout"
    ],
    
    "owner_suggested": "Information Security Manager",
    "deadline": "2026-03-15",
    
    "template_provided": true,
    "template_outline": """
    1. Purpose and Scope
    2. Definitions
    3. Policy Statements:
       3.1 User Access Management
       3.2 User Responsibilities
       3.3 Access Provisioning Process
       3.4 Access Review Process
       3.5 Access Revocation
       3.6 Privileged Access Management
    4. Roles and Responsibilities
    5. Compliance and Enforcement
    6. Related Documents
    7. Review and Update
    """
}

# 3. Enviar notificación
proactive_agent.send_gap_notification(
    recipients=["ciso@company.com", "infosec-team@company.com"],
    gaps=[proposal],
    priority="high"
)
```

---

## 7. Sistema RAG Avanzado

### 7.1 Pipeline RAG Completo

```python
class AdvancedRAGSystem:
    def __init__(self, qdrant_client, embedding_model, reranker=None):
        self.qdrant = qdrant_client
        self.embedding_model = embedding_model
        self.reranker = reranker  # Cohere Rerank o similar
        
    async def search(
        self,
        query: str,
        top_k: int = 5,
        collection: str = "security_knowledge",
        filters: dict = None,
        enable_hybrid: bool = True,
        enable_rerank: bool = True
    ) -> List[Document]:
        
        # 1. Query Understanding & Expansion
        expanded_query = await self._expand_query(query)
        
        # 2. Generate embedding
        query_vector = self.embedding_model.embed(expanded_query)
        
        # 3. Vector search en Qdrant
        vector_results = self.qdrant.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k * 2,  # Pedimos más para luego rerank
            query_filter=self._build_filter(filters)
        )
        
        # 4. Hybrid search (opcional): combinar con keyword search
        if enable_hybrid:
            keyword_results = await self._keyword_search(query, filters)
            combined_results = self._fusion(vector_results, keyword_results)
        else:
            combined_results = vector_results
        
        # 5. Re-ranking (opcional)
        if enable_rerank and self.reranker:
            reranked_results = await self.reranker.rerank(
                query=query,
                documents=[r.payload['content'] for r in combined_results],
                top_k=top_k
            )
            final_results = [combined_results[idx] for idx in reranked_results.indices]
        else:
            final_results = combined_results[:top_k]
        
        # 6. Convert to Document objects
        documents = [self._to_document(r) for r in final_results]
        
        return documents
    
    async def _expand_query(self, query: str) -> str:
        """Expande el query con sinónimos y términos relacionados"""
        # Ejemplo simple, podría usar un LLM para esto
        expansions = {
            "policy": ["policy", "procedure", "standard", "guideline"],
            "risk": ["risk", "threat", "vulnerability", "exposure"],
            "incident": ["incident", "event", "breach", "compromise"]
        }
        
        expanded = query
        for term, synonyms in expansions.items():
            if term in query.lower():
                expanded += " " + " ".join(synonyms)
        
        return expanded
    
    def _build_filter(self, filters: dict):
        """Construye filtros de Qdrant"""
        if not filters:
            return None
            
        conditions = []
        for key, value in filters.items():
            if isinstance(value, list):
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchAny(any=value)
                    )
                )
            else:
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
        
        return Filter(must=conditions)
    
    async def _keyword_search(self, query: str, filters: dict):
        """Búsqueda por keywords en PostgreSQL full-text search"""
        # Implementación de búsqueda keyword complementaria
        pass
    
    def _fusion(self, vector_results, keyword_results, alpha=0.7):
        """Combina resultados de vector y keyword search usando Reciprocal Rank Fusion"""
        # RRF: score(doc) = Σ 1/(k + rank_i(doc))
        # donde k=60 es constante común
        pass
```

### 7.2 Prompt Engineering para RAG

```python
def build_rag_prompt(
    user_query: str,
    retrieved_docs: List[Document],
    agent_system_prompt: str,
    context: dict
) -> str:
    """Construye prompt óptimo con contexto RAG"""
    
    # Formatear documentos recuperados
    docs_text = ""
    for i, doc in enumerate(retrieved_docs, 1):
        docs_text += f"""
        [DOCUMENT {i}]
        Source: {doc.metadata['title']}
        Type: {doc.metadata['document_type']}
        Relevance Score: {doc.score:.2f}
        
        Content:
        {doc.content}
        
        ---
        """
    
    # Construir prompt final
    prompt = f"""
    {agent_system_prompt}
    
    CONTEXT FROM KNOWLEDGE BASE:
    The following documents were retrieved as potentially relevant to the user's query.
    Use this information to provide accurate, context-aware responses.
    
    {docs_text}
    
    IMPORTANT INSTRUCTIONS:
    - If the retrieved documents contain information relevant to the query, use it
    - If the documents don't contain relevant information, rely on your training
    - Always cite which document you're referencing when using specific information
    - If unsure, acknowledge uncertainty rather than making up information
    
    CONVERSATIONAL CONTEXT:
    {context.get('recent_exchanges', 'No recent conversation history')}
    
    USER QUERY:
    {user_query}
    
    YOUR RESPONSE:
    """
    
    return prompt
```

---

## 8. Coordinación Multi-Agente

### 8.1 Ejemplo: Query Complejo

**Query del Usuario**: "Tenemos una vulnerabilidad crítica en nuestro servidor de base de datos. ¿Qué riesgo representa y cómo debemos responder?"

**Orchestrator Decision**:
- Necesita Risk Agent (evaluar riesgo)
- Necesita Incident Agent (respuesta si ya hay compromiso)
- Necesita Compliance Agent (verificar si afecta cumplimiento)

**Ejecución Secuencial**:

```python
# 1. Risk Agent primero
risk_analysis = await risk_agent.execute(
    query="Evaluate risk of critical DB vulnerability",
    context={
        "asset_id": "db-prod-001",
        "cve_id": "CVE-2024-XXXX"
    }
)
# Output: Risk Score 20/25 (CRITICAL), immediate patching required

# 2. Si riesgo es alto, consultar Incident Agent
if risk_analysis.risk_score >= 15:
    incident_check = await incident_agent.execute(
        query="Check if vulnerability already exploited",
        context={
            "asset_id": "db-prod-001",
            "indicators": risk_analysis.potential_indicators
        }
    )
    # Output: No active exploitation detected, but immediate patching advised

# 3. Compliance Agent verifica impacto regulatorio
compliance_check = await compliance_agent.execute(
    query="Does this affect our compliance status?",
    context={
        "asset_id": "db-prod-001",
        "data_stored": "customer PII"
    }
)
# Output: Affects GDPR compliance (A.12.6.1), must document in next audit

# 4. Orchestrator consolida
final_response = orchestrator.consolidate([
    risk_analysis,
    incident_check,
    compliance_check
])
```

**Respuesta Final al Usuario**:
```
ANÁLISIS DE RIESGO CRÍTICO - Acción Inmediata Requerida

EVALUACIÓN DE RIESGO:
Esta vulnerabilidad (CVE-2024-XXXX) en db-prod-001 representa un riesgo CRÍTICO 
(score 20/25). El servidor almacena PII de clientes y es accesible desde la red interna.

Likelihood: 5/5 (Certain) - Exploit público disponible
Impact: 4/5 (Major) - Potencial data breach

ESTADO ACTUAL:
✓ No se detectó explotación activa (logs revisados)
⚠️ Ventana de vulnerabilidad: 3 días desde publicación de CVE

ACCIONES REQUERIDAS (INMEDIATAS):
1. [URGENTE - 4 horas] Aplicar patch de seguridad
   - Ventana de mantenimiento: Coordinar con ops
   - Backup completo antes de patchear
   
2. [INMEDIATO] Incrementar monitoreo
   - Activar alertas adicionales en SIEM
   - Monitorear accesos a db-prod-001
   
3. [24 horas] Verificación post-patch
   - Vulnerability scan para confirmar mitigación
   - Pruebas de funcionalidad

IMPACTO DE CUMPLIMIENTO:
- Afecta requisito GDPR de seguridad de datos personales
- Debe documentarse como incidente de seguridad en próxima auditoría
- No requiere notificación a autoridad (sin explotación confirmada)

¿Procedemos con el plan de emergencia de patching?
```

---

## Conclusión

Esta arquitectura de agentes proporciona:

✅ **Especialización**: Cada agente es experto en su dominio

✅ **Coordinación**: Orchestrator maneja flujos complejos

✅ **Proactividad**: Proactive Planning Agent identifica gaps automáticamente

✅ **Escalabilidad**: Fácil agregar nuevos agentes especializados

✅ **RAG Avanzado**: Búsqueda semántica + reranking para máxima relevancia

✅ **Actionability**: Respuestas específicas y ejecutables

**Siguiente documento**: `04-sistema-proactivo.md` - Detalles del sistema proactivo
