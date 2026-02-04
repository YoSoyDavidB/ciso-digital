# 03 - ESPECIFICACIÓN DE API: CISO Digital

## 1. INFORMACIÓN GENERAL

### 1.1 Base URL

```
Development: http://localhost:8000/api/v1
Production: https://ciso.davidbuitrago.dev/api/v1
```

### 1.2 Autenticación

Todas las APIs (excepto `/auth/*`) requieren autenticación mediante JWT Bearer token:

```http
Authorization: Bearer <access_token>
```

### 1.3 Formato de Respuestas

Todas las respuestas siguen el formato estandarizado:

```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message",
  "timestamp": "2026-02-04T08:00:00Z"
}
```

Errores:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { ... }
  },
  "timestamp": "2026-02-04T08:00:00Z"
}
```

### 1.4 Códigos de Estado HTTP

| Código | Significado | Uso |
|--------|-------------|-----|
| 200 | OK | Request exitoso |
| 201 | Created | Recurso creado exitosamente |
| 400 | Bad Request | Datos inválidos |
| 401 | Unauthorized | Token inválido o ausente |
| 403 | Forbidden | Sin permisos |
| 404 | Not Found | Recurso no encontrado |
| 429 | Too Many Requests | Rate limit excedido |
| 500 | Internal Server Error | Error del servidor |

## 2. AUTENTICACIÓN

### 2.1 POST /auth/register

Registrar nuevo usuario.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "organization": "Acme Corp"
}
```

**Response: 201 Created**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "John Doe",
      "roles": ["user"]
    }
  }
}
```

### 2.2 POST /auth/login

Autenticar usuario.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### 2.3 POST /auth/refresh

Refrescar access token.

**Request:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "access_token": "new_token...",
    "expires_in": 1800
  }
}
```

## 3. CHAT / CONVERSACIÓN

### 3.1 POST /chat/message

Enviar mensaje al CISO Digital.

**Request:**
```json
{
  "message": "¿Cuáles son los riesgos críticos actuales?",
  "session_id": "optional-session-uuid",
  "context": {
    "include_history": true,
    "max_history_messages": 10
  }
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "response": "Actualmente tenemos 3 riesgos críticos identificados...",
    "session_id": "session-uuid",
    "agent_used": "risk_assessment",
    "confidence": 0.95,
    "sources": [
      {
        "type": "database",
        "reference": "risks table"
      },
      {
        "type": "document",
        "title": "Risk Assessment Policy",
        "relevance_score": 0.89
      }
    ],
    "suggested_actions": [
      {
        "action": "View risk details",
        "endpoint": "/api/v1/risks?severity=critical"
      }
    ]
  }
}
```

### 3.2 GET /chat/sessions

Obtener sesiones de conversación del usuario.

**Query Parameters:**
- `limit`: int (default: 20)
- `offset`: int (default: 0)
- `from_date`: ISO date (optional)

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": "uuid",
        "title": "Discusión sobre riesgos críticos",
        "message_count": 15,
        "created_at": "2026-02-01T10:00:00Z",
        "updated_at": "2026-02-01T11:30:00Z"
      }
    ],
    "total": 45,
    "limit": 20,
    "offset": 0
  }
}
```

### 3.3 GET /chat/sessions/{session_id}

Obtener historial de una sesión.

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "session": {
      "id": "uuid",
      "title": "...",
      "messages": [
        {
          "id": "msg-uuid",
          "role": "user",
          "content": "¿Cuáles son los riesgos críticos?",
          "timestamp": "2026-02-01T10:00:00Z"
        },
        {
          "id": "msg-uuid",
          "role": "assistant",
          "content": "Actualmente tenemos...",
          "timestamp": "2026-02-01T10:00:05Z",
          "agent": "risk_assessment"
        }
      ]
    }
  }
}
```

## 4. GESTIÓN DE RIESGOS

### 4.1 GET /risks

Listar riesgos con filtros.

**Query Parameters:**
- `severity`: critical|high|medium|low
- `status`: open|in_progress|mitigated|accepted
- `category`: technical|operational|compliance
- `assigned_to`: user email
- `limit`: int (default: 50)
- `offset`: int (default: 0)
- `sort`: field name (default: severity)
- `order`: asc|desc (default: desc)

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "risks": [
      {
        "id": "uuid",
        "risk_number": "RISK-2026-001",
        "title": "Unpatched critical vulnerability in web server",
        "description": "CVE-2025-1234 affects Apache 2.4.x...",
        "severity": "critical",
        "likelihood": "high",
        "impact_score": 9.5,
        "status": "open",
        "category": "technical",
        "assigned_to": "security-team@example.com",
        "mitigation_plan": "Apply security patch within 24h",
        "deadline": "2026-02-05T00:00:00Z",
        "created_at": "2026-02-04T08:00:00Z",
        "updated_at": "2026-02-04T08:00:00Z"
      }
    ],
    "total": 47,
    "limit": 50,
    "offset": 0
  }
}
```

### 4.2 POST /risks

Crear nuevo riesgo.

**Request:**
```json
{
  "title": "Weak password policy",
  "description": "Current policy allows passwords < 8 characters",
  "severity": "medium",
  "category": "operational",
  "affected_assets": ["user-portal", "admin-panel"],
  "mitigation_plan": "Update password policy to require 12+ chars"
}
```

**Response: 201 Created**
```json
{
  "success": true,
  "data": {
    "risk": {
      "id": "uuid",
      "risk_number": "RISK-2026-048",
      ...
    }
  }
}
```

### 4.3 PUT /risks/{risk_id}

Actualizar riesgo existente.

**Request:**
```json
{
  "status": "in_progress",
  "mitigation_plan": "Updated plan with additional steps...",
  "assigned_to": "john.doe@example.com"
}
```

**Response: 200 OK**

### 4.4 POST /risks/{risk_id}/assess

Solicitar evaluación de riesgo por el CISO.

**Request:**
```json
{
  "include_recommendations": true,
  "context": "Recent security audit findings"
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "assessment": {
      "overall_score": 8.5,
      "likelihood": "high",
      "impact": "high",
      "recommendations": [
        "Immediate patching required",
        "Implement WAF rules",
        "Enable monitoring for exploitation attempts"
      ],
      "estimated_cost": "$5,000",
      "estimated_time": "2 days",
      "confidence": 0.92
    }
  }
}
```

## 5. GESTIÓN DE INCIDENTES

### 5.1 GET /incidents

Listar incidentes.

**Query Parameters:** Similar a `/risks`

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "incidents": [
      {
        "id": "uuid",
        "incident_number": "INC-2026-001",
        "title": "Suspicious login attempts detected",
        "severity": "high",
        "status": "investigating",
        "detection_time": "2026-02-04T07:30:00Z",
        "affected_assets": ["user-database", "auth-service"],
        "indicators_of_compromise": {
          "ip_addresses": ["192.168.1.100"],
          "user_accounts": ["admin@example.com"]
        },
        "assigned_to": "incident-response@example.com"
      }
    ],
    "total": 12
  }
}
```

### 5.2 POST /incidents

Crear incident (típicamente automático, pero también manual).

**Request:**
```json
{
  "title": "DDoS attack detected",
  "description": "High volume of requests from multiple IPs",
  "severity": "critical",
  "affected_assets": ["web-server-1", "web-server-2"],
  "indicators_of_compromise": {
    "ip_addresses": ["1.2.3.4", "5.6.7.8"],
    "attack_type": "HTTP flood"
  }
}
```

**Response: 201 Created**

### 5.3 POST /incidents/{incident_id}/respond

Solicitar respuesta automática del CISO.

**Request:**
```json
{
  "execute_playbook": true,
  "confirm_actions": false  // true = requiere confirmación manual
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "response_plan": {
      "playbook_used": "ddos-response-v1",
      "actions_taken": [
        {
          "action": "Enable rate limiting",
          "status": "completed",
          "timestamp": "2026-02-04T08:01:00Z"
        },
        {
          "action": "Block malicious IPs",
          "status": "completed",
          "ip_count": 45
        }
      ],
      "actions_pending": [
        {
          "action": "Contact ISP for upstream filtering",
          "requires": "manual_action"
        }
      ],
      "estimated_impact": "Attack mitigated within 5 minutes"
    }
  }
}
```

## 6. CUMPLIMIENTO NORMATIVO

### 6.1 GET /compliance/frameworks

Listar frameworks soportados.

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "frameworks": [
      {
        "id": "iso27001",
        "name": "ISO/IEC 27001:2022",
        "description": "Information Security Management",
        "control_count": 93,
        "compliance_rate": 0.85
      },
      {
        "id": "nist-csf",
        "name": "NIST Cybersecurity Framework",
        "control_count": 108,
        "compliance_rate": 0.78
      }
    ]
  }
}
```

### 6.2 GET /compliance/frameworks/{framework_id}/controls

Obtener controles de un framework.

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "controls": [
      {
        "id": "A.8.1",
        "title": "Inventory of assets",
        "description": "Assets associated with information...",
        "status": "compliant",
        "last_check": "2026-02-01T00:00:00Z",
        "evidence": [
          {
            "type": "document",
            "title": "Asset Inventory Q1 2026",
            "uploaded_at": "2026-01-15T10:00:00Z"
          }
        ],
        "notes": "Updated quarterly"
      }
    ]
  }
}
```

### 6.3 POST /compliance/check

Ejecutar verificación de cumplimiento.

**Request:**
```json
{
  "framework_id": "iso27001",
  "controls": ["A.8.1", "A.8.2"],  // vacío = todos
  "generate_report": true
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "check_id": "uuid",
    "framework": "iso27001",
    "compliance_rate": 0.85,
    "results": {
      "compliant": 79,
      "non_compliant": 8,
      "partial": 6,
      "not_applicable": 0
    },
    "gaps": [
      {
        "control_id": "A.9.2",
        "issue": "Missing evidence for user access review",
        "priority": "high",
        "recommendation": "Upload Q1 2026 access review report"
      }
    ],
    "report_url": "/reports/compliance-check-uuid.pdf"
  }
}
```

## 7. GESTIÓN DE ACTIVOS

### 7.1 GET /assets

Listar activos de la organización.

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "assets": [
      {
        "id": "uuid",
        "name": "Production Web Server",
        "type": "server",
        "criticality": "critical",
        "owner": "infrastructure-team@example.com",
        "location": "AWS us-east-1",
        "ip_addresses": ["52.1.2.3"],
        "technologies": {
          "os": "Ubuntu 22.04",
          "web_server": "Nginx 1.24",
          "runtime": "Node.js 20"
        },
        "vulnerabilities_count": 3,
        "last_scan": "2026-02-03T00:00:00Z",
        "compliance_status": {
          "iso27001": true,
          "pci_dss": false
        }
      }
    ]
  }
}
```

### 7.2 POST /assets

Registrar nuevo activo.

**Request:**
```json
{
  "name": "Database Server - Customer Data",
  "type": "database",
  "criticality": "critical",
  "owner": "database-team@example.com",
  "location": "On-premise DC1",
  "ip_addresses": ["10.0.1.50"],
  "technologies": {
    "dbms": "PostgreSQL 16",
    "encryption": "AES-256"
  }
}
```

**Response: 201 Created**

### 7.3 POST /assets/{asset_id}/scan

Iniciar escaneo de vulnerabilidades.

**Request:**
```json
{
  "scan_type": "full",  // full|quick
  "scanner": "nessus"   // nessus|openvas|auto
}
```

**Response: 202 Accepted**
```json
{
  "success": true,
  "data": {
    "scan_id": "uuid",
    "status": "queued",
    "estimated_duration": "15 minutes"
  }
}
```

## 8. REPORTES

### 8.1 POST /reports/generate

Generar reporte personalizado.

**Request:**
```json
{
  "report_type": "executive_summary",
  "period": {
    "start_date": "2026-01-01",
    "end_date": "2026-01-31"
  },
  "sections": [
    "risks_overview",
    "incidents_summary",
    "compliance_status",
    "key_metrics"
  ],
  "format": "pdf"  // pdf|html|json
}
```

**Response: 202 Accepted**
```json
{
  "success": true,
  "data": {
    "report_id": "uuid",
    "status": "generating",
    "estimated_time": "30 seconds",
    "webhook_url": "/reports/{report_id}/status"
  }
}
```

### 8.2 GET /reports/{report_id}

Descargar reporte generado.

**Response: 200 OK**
- Content-Type: application/pdf (o según formato)
- Binary file download

### 8.3 GET /reports/templates

Listar plantillas de reporte disponibles.

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "templates": [
      {
        "id": "executive_summary",
        "name": "Executive Summary Report",
        "description": "High-level overview for C-level executives",
        "sections": ["risks", "incidents", "compliance", "metrics"]
      },
      {
        "id": "technical_details",
        "name": "Technical Security Report",
        "description": "Detailed technical report for security team"
      }
    ]
  }
}
```

## 9. PROACTIVIDAD

### 9.1 POST /proactive/review

Solicitar revisión proactiva del CISO.

**Request:**
```json
{
  "review_type": "documentation_gaps",  // documentation_gaps|policy_review|all
  "scope": {
    "frameworks": ["iso27001", "nist-csf"],
    "include_recommendations": true
  }
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "review": {
      "id": "uuid",
      "review_type": "documentation_gaps",
      "executed_at": "2026-02-04T08:00:00Z",
      "findings": {
        "missing_documents": [
          {
            "framework": "iso27001",
            "control": "A.5.1",
            "required_document": "Information Security Policy",
            "priority": "critical",
            "deadline": "2026-03-01"
          }
        ],
        "outdated_documents": [
          {
            "document": "Incident Response Plan",
            "last_updated": "2024-06-01",
            "review_frequency": "annually",
            "status": "overdue"
          }
        ],
        "incomplete_controls": 5
      },
      "action_plan": {
        "immediate_actions": [
          {
            "action": "Create Information Security Policy",
            "priority": "critical",
            "deadline": "2026-02-15",
            "assigned_to": "CISO_AI_will_draft"
          }
        ],
        "short_term_actions": [...],
        "long_term_improvements": [...]
      },
      "estimated_effort": {
        "hours": 40,
        "cost": "$6000"
      }
    }
  }
}
```

### 9.2 GET /proactive/recommendations

Obtener recomendaciones proactivas actuales.

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "id": "uuid",
        "category": "policy_improvement",
        "title": "Strengthen password policy",
        "description": "Current policy allows 8-char passwords...",
        "priority": "medium",
        "impact": "Reduces brute-force attack risk by 80%",
        "effort": "low",
        "status": "pending"
      }
    ]
  }
}
```

## 10. MÉTRICAS Y KPIs

### 10.1 GET /metrics/security

Obtener métricas de seguridad.

**Query Parameters:**
- `period`: day|week|month|quarter|year
- `start_date`: ISO date
- `end_date`: ISO date

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "period": {
      "start": "2026-01-01",
      "end": "2026-01-31"
    },
    "metrics": {
      "risks": {
        "total": 47,
        "critical": 3,
        "high": 12,
        "medium": 20,
        "low": 12,
        "trend": "+5% vs previous month"
      },
      "incidents": {
        "total": 8,
        "by_severity": {
          "critical": 1,
          "high": 2,
          "medium": 5
        },
        "mttr": "4.5 hours",
        "resolved": 7
      },
      "compliance": {
        "overall_rate": 0.87,
        "by_framework": {
          "iso27001": 0.89,
          "nist-csf": 0.85
        }
      },
      "vulnerabilities": {
        "total": 124,
        "critical": 5,
        "patched_this_month": 18
      }
    }
  }
}
```

### 10.2 GET /metrics/performance

Métricas de performance del sistema CISO.

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "system_metrics": {
      "avg_response_time": "450ms",
      "api_uptime": 0.998,
      "active_users": 15,
      "queries_processed_today": 342
    },
    "ai_metrics": {
      "accuracy": 0.94,
      "false_positives": 0.02,
      "avg_confidence": 0.91
    }
  }
}
```

## 11. WEBHOOKS

### 11.1 Configuración de Webhooks

Los usuarios pueden configurar webhooks para recibir notificaciones en tiempo real.

**POST /webhooks**

```json
{
  "url": "https://your-app.com/webhooks/ciso",
  "events": [
    "incident.created",
    "incident.critical",
    "risk.critical_detected",
    "compliance.gap_found"
  ],
  "secret": "your-webhook-secret"
}
```

### 11.2 Eventos de Webhook

Ejemplo de payload enviado:

```json
{
  "event": "incident.critical",
  "timestamp": "2026-02-04T08:00:00Z",
  "data": {
    "incident_id": "uuid",
    "title": "Critical security breach detected",
    "severity": "critical",
    "immediate_actions_required": true
  },
  "signature": "sha256=..."
}
```

## 12. RATE LIMITING

| Endpoint Category | Authenticated | Anonymous |
|-------------------|---------------|-----------|
| /auth/* | N/A | 10/minute |
| /chat/* | 30/minute | N/A |
| /risks, /incidents | 100/minute | N/A |
| /reports/generate | 10/hour | N/A |
| Todo lo demás | 100/minute | N/A |

Headers en respuesta:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1675498800
```

## 13. PYDANTIC MODELS (Schemas)

### User Model
```python
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    organization: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    roles: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### Risk Model
```python
class RiskBase(BaseModel):
    title: str
    description: str
    severity: Literal["critical", "high", "medium", "low"]
    category: Literal["technical", "operational", "compliance"]
    
class RiskCreate(RiskBase):
    affected_assets: List[str] = []
    mitigation_plan: Optional[str] = None

class RiskResponse(RiskBase):
    id: str
    risk_number: str
    status: str
    impact_score: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

---

**Versión:** 1.0  
**Última Actualización:** Febrero 2026  
**Próximo Documento:** [04-AGENT-DEFINITIONS.md](04-AGENT-DEFINITIONS.md)
