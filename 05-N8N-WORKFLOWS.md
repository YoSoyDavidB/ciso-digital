# 05 - N8N WORKFLOWS: CISO Digital

## 1. VISIÓN GENERAL DE WORKFLOWS

N8N actúa como el orquestador de tareas automatizadas y la capa de integración con sistemas externos. Los workflows se dividen en categorías:

1. **Monitoreo Continuo** - Ejecutan cada 5-15 minutos
2. **Escaneos Programados** - Diarios/semanales
3. **Compliance Checks** - Mensuales
4. **Reportes Automáticos** - Semanales/mensuales
5. **Respuesta a Eventos** - Triggereados por webhooks

## 2. WORKFLOW: MONITOREO CONTINUO DE SEGURIDAD

### 2.1 Descripción
Monitorea logs de SIEM, detecta anomalías y crea incidentes automáticamente.

### 2.2 Configuración

**Trigger:** Cron - Cada 15 minutos  
**Timeout:** 5 minutos  
**Retry:** 3 intentos con backoff exponencial

### 2.3 Flujo

```
┌─────────────────┐
│  Cron Trigger   │
│  */15 * * * *   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SIEM Query     │
│  (Elastic/      │
│   Splunk)       │
│  - Get logs     │
│    últimos 15m  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Filter Logs    │
│  - Severity ≥   │
│    WARNING      │
│  - Exclude      │
│    known false  │
│    positives    │
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │ Hay     │
    │ eventos?│
    └────┬────┘
         │
    ┌────┴────┐
    │   SI    │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL     │
│  Query          │
│  - Check if     │
│    event        │
│    already      │
│    exists       │
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │ Nuevo?  │
    └────┬────┘
         │
    ┌────┴────┐
    │   SI    │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│  HTTP Request   │
│  POST /api/v1   │
│  /chat/message  │
│                 │
│  Body:          │
│  "Analiza este  │
│   evento de     │
│   seguridad:    │
│   {event}"      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parse AI       │
│  Response       │
│  - Extract      │
│    severity     │
│  - Get          │
│    recommended  │
│    actions      │
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │Severity │
    │Critical?│
    └────┬────┘
         │
    ┌────┴────┐
    │   SI    │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│  Create         │
│  Incident       │
│  in PostgreSQL  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Send           │
│  Notifications  │
│  - Slack        │
│  - Email        │
│  - PagerDuty    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Execute        │
│  Automated      │
│  Response       │
│  (If enabled)   │
│  - Block IPs    │
│  - Isolate      │
│    systems      │
└─────────────────┘
```

### 2.4 Código N8N (JSON Export)

```json
{
  "name": "Security Monitoring - Continuous",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "triggerAtMinute": 15
            }
          ]
        }
      },
      "name": "Every 15 minutes",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "={{$env.SIEM_URL}}/api/search",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "elasticsearchApi",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Authorization",
              "value": "={{$env.SIEM_TOKEN}}"
            }
          ]
        },
        "sendQuery": true,
        "queryParameters": {
          "parameters": [
            {
              "name": "query",
              "value": "level:WARNING OR level:ERROR OR level:CRITICAL"
            },
            {
              "name": "from",
              "value": "now-15m"
            },
            {
              "name": "size",
              "value": "100"
            }
          ]
        }
      },
      "name": "Query SIEM",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300]
    },
    {
      "parameters": {
        "conditions": {
          "number": [
            {
              "value1": "={{$json.hits.length}}",
              "operation": "larger",
              "value2": 0
            }
          ]
        }
      },
      "name": "Has Events?",
      "type": "n8n-nodes-base.if",
      "position": [650, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT id FROM incidents WHERE event_hash = MD5($1)",
        "options": {
          "queryParameters": "={{$json.event_hash}}"
        }
      },
      "name": "Check Existing",
      "type": "n8n-nodes-base.postgres",
      "credentials": {
        "postgres": {
          "id": "1",
          "name": "PostgreSQL CISO"
        }
      },
      "position": [850, 300]
    }
  ],
  "connections": {
    "Every 15 minutes": {
      "main": [[{"node": "Query SIEM", "type": "main", "index": 0}]]
    },
    "Query SIEM": {
      "main": [[{"node": "Has Events?", "type": "main", "index": 0}]]
    }
  }
}
```

## 3. WORKFLOW: VULNERABILITY SCANNING

### 3.1 Descripción
Ejecuta escaneos de vulnerabilidades en assets y procesa resultados.

### 3.2 Configuración

**Trigger:** Cron - Diario a las 02:00 AM  
**Timeout:** 2 horas  
**Assets:** Todos con `auto_scan: true`

### 3.3 Flujo

```
Cron Daily 02:00
    ↓
Get Assets from PostgreSQL
  WHERE auto_scan = true
    ↓
For Each Asset
    ↓
    ├─→ Determine Scanner
    │   (Nessus/OpenVAS/AWS Inspector)
    ↓
    ├─→ Trigger Scan
    │   (API call to scanner)
    ↓
    ├─→ Wait for Completion
    │   (Poll every 5 minutes, max 2h)
    ↓
    ├─→ Get Scan Results
    ↓
    ├─→ Parse Vulnerabilities
    │   - Extract CVEs
    │   - Calculate CVSS scores
    │   - Identify critical vulns
    ↓
    ├─→ Save to PostgreSQL
    │   (vulnerabilities table)
    ↓
    ├─→ Update Asset
    │   (last_scan_date, vuln_count)
    ↓
    ├─→ IF critical vulns found
    │       ↓
    │       Create Risk
    │       ↓
    │       Notify Security Team
    │       ↓
    │       Ask CISO AI for
    │       mitigation plan
    ↓
Next Asset
```

## 4. WORKFLOW: COMPLIANCE AUTOMATED CHECK

### 4.1 Descripción
Verifica cumplimiento de controles automáticamente cada mes.

### 4.2 Configuración

**Trigger:** Cron - 1ro de cada mes a las 08:00 AM  
**Frameworks:** ISO 27001, NIST CSF, GDPR  
**Duration:** 1-2 horas

### 3.3 Flujo

```
Monthly Trigger
    ↓
Get Frameworks to Check
    ↓
For Each Framework
    ↓
    Get Controls
        ↓
        For Each Control
            ↓
            Check if has automated check
                ↓
                YES → Execute Check
                │       - Query systems
                │       - Verify configurations
                │       - Check for evidence
                │       - Validate policies
                ↓
                Evaluate Result
                │   - Compliant
                │   - Non-compliant
                │   - Partial
                │   - N/A
                ↓
                Save to compliance_checks
                ↓
                IF non-compliant
                    ↓
                    Ask CISO AI:
                    "How to address this gap?"
                    ↓
                    Create action item
                    ↓
                    Assign to responsible
        ↓
    Next Control
    ↓
Next Framework
    ↓
Generate Compliance Report
    ↓
Calculate overall compliance rate
    ↓
Send Report to Stakeholders
```

### 4.4 Automated Checks Examples

```javascript
// Example: Check A.9.2.1 - User registration and de-registration

// 1. Query user management system
const activeUsers = await queryAPI('/api/users?status=active');

// 2. Check last access review date
const lastReview = await db.query(
  'SELECT MAX(review_date) FROM user_access_reviews'
);

// 3. Verify review is within 90 days
const daysSinceReview = (Date.now() - lastReview) / (1000 * 60 * 60 * 24);

// 4. Determine compliance
const isCompliant = daysSinceReview <= 90;

// 5. Save result
await saveComplianceCheck({
  control_id: 'A.9.2.1',
  status: isCompliant ? 'compliant' : 'non_compliant',
  evidence: `Last review: ${daysSinceReview} days ago`,
  next_review_due: addDays(lastReview, 90)
});
```

## 5. WORKFLOW: WEEKLY EXECUTIVE REPORT

### 5.1 Descripción
Genera y envía reporte ejecutivo semanal automáticamente.

### 5.2 Configuración

**Trigger:** Cron - Lunes 09:00 AM  
**Recipients:** C-level executives  
**Format:** PDF + Email

### 5.3 Flujo

```
Weekly Monday 09:00
    ↓
Calculate Date Range
  (previous week)
    ↓
Gather Metrics
    ├─→ Risks (new, closed, critical)
    ├─→ Incidents (count, MTTR, severity)
    ├─→ Vulnerabilities (new, patched)
    ├─→ Compliance (overall rate, gaps)
    └─→ System metrics (uptime, queries)
    ↓
HTTP Request to Backend
  POST /api/v1/reports/generate
  {
    report_type: "executive_summary",
    period: { start, end },
    format: "pdf"
  }
    ↓
Wait for Report Generation
  (poll /reports/{id} until ready)
    ↓
Download PDF
    ↓
Send Email
  To: executives@company.com
  Subject: "Weekly Security Report - [Date]"
  Body: Executive summary text
  Attachment: report.pdf
    ↓
Archive Report
  (Save to document management)
```

## 6. WORKFLOW: PROACTIVE DOCUMENTATION REVIEW

### 6.1 Descripción
Revisa periódicamente la documentación existente y propone mejoras.

### 6.2 Configuración

**Trigger:** Cron - Mensual, primer día a las 10:00 AM  
**Duration:** 30-60 minutos

### 6.3 Flujo

```
Monthly 1st, 10:00 AM
    ↓
Scan Knowledge Base
  (Qdrant collection: security_knowledge)
    ↓
List All Documents
    ↓
For Each Document
    ↓
    Check Metadata
    ├─→ last_updated
    ├─→ review_frequency
    ├─→ next_review_date
    └─→ framework_required
    ↓
    IF document outdated
        ↓
        Mark for review
        ↓
        Add to outdated_list
    ↓
Next Document
    ↓
Get Required Documents
  (from frameworks)
    ↓
Compare with Existing
    ↓
Identify Gaps
    ↓
HTTP Request to Backend
  POST /api/v1/proactive/review
  {
    review_type: "documentation_gaps"
  }
    ↓
Get AI Analysis
  - Missing documents
  - Outdated policies
  - Recommended updates
    ↓
Create Action Plan
    ↓
For Each Missing Document
    ↓
    Create Task in Project Management
    Assign to appropriate owner
    Set deadline based on priority
    ↓
Send Summary Email
  To: CISO, Security Team
  Subject: "Monthly Documentation Review"
  Content:
    - X documents need update
    - Y documents missing
    - Action plan attached
```

## 7. WORKFLOW: INCIDENT AUTO-RESPONSE

### 7.1 Descripción
Responde automáticamente a ciertos tipos de incidentes.

### 7.2 Configuración

**Trigger:** Webhook desde SIEM o sistemas de monitoreo  
**Auto-execute:** Solo para incidentes de tipo específico  
**Human approval:** Required para acciones destructivas

### 7.3 Flujo

```
Webhook Received
    ↓
Parse Incident Data
  - Type
  - Severity
  - Affected systems
  - IOCs (Indicators of Compromise)
    ↓
Query PostgreSQL
  "Is this a known incident?"
    ↓
    NO → Classify with AI
         ↓
         Get Incident Type
    ↓
Load Response Playbook
  (from playbooks table)
    ↓
Execute Automated Actions
    │
    ├─→ IF type == "ddos"
    │       ↓
    │       Enable rate limiting
    │       ↓
    │       Block malicious IPs (if < 100)
    │       ↓
    │       Scale infrastructure
    │
    ├─→ IF type == "malware_detected"
    │       ↓
    │       Isolate affected system
    │       ↓
    │       Stop suspicious processes
    │       ↓
    │       Snapshot for forensics
    │
    ├─→ IF type == "brute_force"
    │       ↓
    │       Block attacking IPs
    │       ↓
    │       Enable 2FA enforcement
    │       ↓
    │       Reset compromised accounts
    │
    └─→ IF type == "data_exfiltration"
            ↓
            REQUEST HUMAN APPROVAL
            ↓
            IF approved
                ↓
                Revoke access
                ↓
                Block network egress
                ↓
                Alert legal team
    ↓
Log All Actions
    ↓
Create Incident Record
  in PostgreSQL
    ↓
Notify Stakeholders
  (Slack, Email, PagerDuty)
    ↓
Ask CISO AI for
  Post-Incident Analysis
    ↓
Generate Incident Report
```

## 8. WORKFLOW: THREAT INTELLIGENCE INGESTION

### 8.1 Descripción
Recopila threat intelligence de fuentes externas y actualiza knowledge base.

### 8.2 Configuración

**Trigger:** Cron - Cada 6 horas  
**Sources:** AlienVault OTX, MISP, custom feeds  
**Processing:** Embeddings + storage in Qdrant

### 8.3 Flujo

```
Every 6 hours
    ↓
For Each TI Source
    ↓
    Fetch Latest IOCs
    (IPs, domains, hashes, etc.)
        ↓
        Filter by relevance
        - Confidence > 70%
        - Recent (< 30 days)
        - Applicable to our environment
        ↓
        For Each IOC
            ↓
            Check if exists
              in PostgreSQL (iocs table)
            ↓
            IF new
                ↓
                Save to PostgreSQL
                ↓
                Generate embedding
                  (for semantic search)
                ↓
                Store in Qdrant
                  collection: threat_intel
            ↓
        Next IOC
    ↓
    Fetch Threat Reports
        ↓
        Parse reports
        ↓
        Extract TTPs
          (MITRE ATT&CK mapping)
        ↓
        Generate embeddings
        ↓
        Store in Qdrant
    ↓
Next TI Source
    ↓
Cross-reference with Assets
  "Are we vulnerable to these threats?"
    ↓
    IF matches found
        ↓
        Create proactive alerts
        ↓
        Ask CISO AI:
        "Assess risk from [threat]"
        ↓
        Propose mitigation
```

## 9. INTEGRACIÓN CON BACKEND PYTHON

### 9.1 Llamadas desde N8N a FastAPI

```javascript
// N8N HTTP Request Node Configuration
{
  "method": "POST",
  "url": "http://backend:8000/api/v1/chat/message",
  "authentication": "predefinedCredentialType",
  "nodeCredentialType": "httpHeaderAuth",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Authorization",
        "value": "Bearer {{$env.BACKEND_API_KEY}}"
      }
    ]
  },
  "sendBody": true,
  "bodyParameters": {
    "parameters": [
      {
        "name": "message",
        "value": "={{$json.query}}"
      },
      {
        "name": "context",
        "value": "={{$json.context}}"
      }
    ]
  }
}
```

### 9.2 Webhooks desde FastAPI a N8N

```python
# En FastAPI backend

import httpx

async def trigger_n8n_workflow(
    workflow_url: str,
    data: dict
):
    """Trigger N8N workflow from backend"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.N8N_URL}/webhook/{workflow_url}",
            json=data,
            headers={
                "Authorization": f"Bearer {settings.N8N_API_KEY}"
            }
        )
        return response.json()

# Usage
await trigger_n8n_workflow(
    "vulnerability-scan",
    {
        "asset_id": asset.id,
        "scan_type": "full"
    }
)
```

## 10. CONFIGURACIÓN Y VARIABLES DE ENTORNO

### 10.1 Variables Globales en N8N

```javascript
// N8N Environment Variables
{
  "BACKEND_URL": "http://backend:8000",
  "BACKEND_API_KEY": "sk-...",
  "POSTGRES_HOST": "postgres",
  "POSTGRES_DB": "ciso_db",
  "POSTGRES_USER": "user",
  "POSTGRES_PASSWORD": "***",
  "SIEM_URL": "https://elastic.company.com",
  "SIEM_TOKEN": "***",
  "SLACK_WEBHOOK": "https://hooks.slack.com/...",
  "EMAIL_SMTP_HOST": "smtp.gmail.com",
  "EMAIL_FROM": "ciso-ai@company.com"
}
```

### 10.2 Credentials en N8N

```yaml
Credentials a configurar:
  - PostgreSQL: ciso_db connection
  - Elasticsearch/Splunk: SIEM access
  - AWS: For scanners and cloud integrations
  - Slack: For notifications
  - SMTP: For email sending
  - Nessus/OpenVAS: Scanner APIs
  - PagerDuty: For critical alerts
```

## 11. MONITOREO DE WORKFLOWS

### 11.1 Métricas a Trackear

```javascript
// Metrics to monitor for each workflow

{
  "workflow_name": "Security Monitoring",
  "metrics": {
    "executions_total": 2880,  // per month
    "executions_success": 2850,
    "executions_failed": 30,
    "success_rate": 0.989,
    "avg_duration": "45s",
    "p95_duration": "120s",
    "last_execution": "2026-02-04T08:15:00Z",
    "next_execution": "2026-02-04T08:30:00Z"
  }
}
```

### 11.2 Alertas

```yaml
Alerts:
  - name: "Workflow failure rate > 5%"
    condition: failed_executions / total_executions > 0.05
    action: Send to Slack #devops
    
  - name: "Workflow not executed for 1 hour"
    condition: now - last_execution > 3600s
    action: Page on-call engineer
    
  - name: "Duration > 10 minutes"
    condition: execution_duration > 600s
    action: Log warning, investigate
```

## 12. BACKUP Y DISASTER RECOVERY

### 12.1 Backup de Workflows

```bash
# Export all N8N workflows daily
n8n export:workflow --all --output=/backups/n8n-workflows-$(date +%Y%m%d).json

# Backup N8N database (PostgreSQL)
pg_dump -h postgres -U user n8n > /backups/n8n-db-$(date +%Y%m%d).sql
```

### 12.2 Restore

```bash
# Import workflows
n8n import:workflow --input=/backups/n8n-workflows-20260204.json

# Restore database
psql -h postgres -U user n8n < /backups/n8n-db-20260204.sql
```

---

**Versión:** 1.0  
**Última Actualización:** Febrero 2026  
**Próximo Documento:** [06-KNOWLEDGE-BASE-STRUCTURE.md](06-KNOWLEDGE-BASE-STRUCTURE.md)
