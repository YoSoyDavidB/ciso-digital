# CISO Digital - API Documentation

**Version:** 1.0  
**Last Updated:** 2026-02-06  
**Base URL:** `https://api.ciso-digital.com/api/v1`  

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Chat Endpoints](#chat-endpoints)
3. [Incident Response Endpoints](#incident-response-endpoints)
4. [Risk Management Endpoints](#risk-management-endpoints)
5. [Compliance Endpoints](#compliance-endpoints)
6. [Conversation History Endpoints](#conversation-history-endpoints)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)

---

## 🔐 Authentication

All API requests require authentication using JWT tokens.

### Get Access Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@company.com",
  "password": "your-secure-password"
}

Response 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Refresh Token

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Using Token

Include the access token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 💬 Chat Endpoints

### Send Message

Send a message to the CISO assistant and get a response.

```http
POST /api/v1/chat/message
Content-Type: application/json
Authorization: Bearer <token>

{
  "message": "¿Cuáles son los riesgos críticos en nuestro servidor web?",
  "session_id": "sess-abc-123",
  "context": {
    "asset_id": "asset-456",
    "environment": "production"
  }
}

Response 200:
{
  "message_id": "msg-789",
  "response": "Identifiqué 3 riesgos críticos en el servidor web de producción:\n\n1. **CVE-2025-1234** (CVSS 9.8) - Vulnerabilidad RCE en Apache Struts...",
  "intent": "risk_assessment",
  "confidence": 0.95,
  "agent_used": "RiskAssessmentAgent",
  "sources": [
    {
      "type": "knowledge_base",
      "document": "CVE Database",
      "relevance": 0.92
    },
    {
      "type": "recent_scans",
      "scan_id": "scan-321",
      "timestamp": "2026-02-06T10:00:00Z"
    }
  ],
  "metadata": {
    "processing_time_ms": 1234,
    "tokens_used": 450,
    "context_messages": 3
  },
  "suggested_actions": [
    {
      "action": "patch_system",
      "priority": "critical",
      "description": "Apply security patch for CVE-2025-1234"
    }
  ],
  "timestamp": "2026-02-06T11:15:00Z"
}
```

### Get Chat History

Retrieve conversation history for a session.

```http
GET /api/v1/chat/history/{session_id}?limit=20&offset=0
Authorization: Bearer <token>

Response 200:
{
  "session_id": "sess-abc-123",
  "messages": [
    {
      "message_id": "msg-001",
      "role": "user",
      "content": "Hola, necesito ayuda",
      "timestamp": "2026-02-06T11:00:00Z"
    },
    {
      "message_id": "msg-002",
      "role": "assistant",
      "content": "Hola, ¿en qué puedo ayudarte?",
      "timestamp": "2026-02-06T11:00:05Z",
      "metadata": {
        "agent": "GeneralAgent",
        "confidence": 0.99
      }
    }
  ],
  "total_messages": 42,
  "page": 1,
  "per_page": 20
}
```

### Search Conversations

Search previous conversations semantically.

```http
POST /api/v1/chat/search
Content-Type: application/json
Authorization: Bearer <token>

{
  "query": "configuración firewall AWS",
  "limit": 5,
  "min_score": 0.7,
  "date_from": "2026-01-01T00:00:00Z",
  "date_to": "2026-02-06T23:59:59Z"
}

Response 200:
{
  "results": [
    {
      "message_id": "msg-456",
      "session_id": "sess-xyz-789",
      "content": "Para configurar el firewall de AWS, debes...",
      "score": 0.89,
      "timestamp": "2026-01-15T14:30:00Z",
      "highlights": [
        "configurar el <mark>firewall</mark> de <mark>AWS</mark>"
      ]
    }
  ],
  "total_results": 3,
  "query_time_ms": 45
}
```

### Create New Session

Start a new conversation session.

```http
POST /api/v1/chat/sessions
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "AWS Security Review",
  "metadata": {
    "project": "infrastructure-audit",
    "environment": "production"
  }
}

Response 201:
{
  "session_id": "sess-new-001",
  "title": "AWS Security Review",
  "created_at": "2026-02-06T11:20:00Z",
  "status": "active"
}
```

### Delete Session

Delete a conversation session and all its messages.

```http
DELETE /api/v1/chat/sessions/{session_id}
Authorization: Bearer <token>

Response 204: No Content
```

---

## 🚨 Incident Response Endpoints

### Report Incident

Create a new security incident.

```http
POST /api/v1/incidents
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "Ransomware detected on file server",
  "description": "Files being encrypted with .locked extension. Communication detected with suspicious IPs.",
  "severity": "critical",
  "type": "ransomware",
  "affected_systems": [
    "file-server-01",
    "file-server-02"
  ],
  "indicators": [
    "Rapid file modifications",
    "Process: encryption.exe",
    "C&C communication: 192.0.2.100"
  ],
  "reporter_id": "user-456"
}

Response 201:
{
  "incident_id": "INC-2026-042",
  "status": "open",
  "severity": "critical",
  "type": "ransomware",
  "title": "Ransomware detected on file server",
  "created_at": "2026-02-06T11:30:00Z",
  "assigned_to": "incident-response-team",
  "response_plan": {
    "playbook": "ransomware",
    "total_steps": 10,
    "estimated_duration_hours": 8,
    "immediate_actions": [
      {
        "step": 1,
        "title": "Isolate Infected Systems",
        "priority": "immediate",
        "estimated_duration_minutes": 2,
        "automated": true,
        "status": "in_progress"
      },
      {
        "step": 2,
        "title": "Block C&C Communication",
        "priority": "immediate",
        "estimated_duration_minutes": 5,
        "automated": true,
        "status": "pending"
      }
    ]
  },
  "notifications_sent": [
    {
      "recipient": "ciso@company.com",
      "type": "email",
      "sent_at": "2026-02-06T11:30:05Z"
    },
    {
      "recipient": "security-team@company.com",
      "type": "slack",
      "sent_at": "2026-02-06T11:30:06Z"
    }
  ]
}
```

### Get Incident Details

```http
GET /api/v1/incidents/{incident_id}
Authorization: Bearer <token>

Response 200:
{
  "incident_id": "INC-2026-042",
  "status": "in_progress",
  "severity": "critical",
  "type": "ransomware",
  "title": "Ransomware detected on file server",
  "description": "...",
  "created_at": "2026-02-06T11:30:00Z",
  "updated_at": "2026-02-06T12:15:00Z",
  "resolved_at": null,
  "assigned_to": "incident-response-team",
  "affected_systems": ["file-server-01", "file-server-02"],
  "timeline": [
    {
      "timestamp": "2026-02-06T11:30:00Z",
      "event": "Incident created",
      "user": "user-456",
      "automated": false
    },
    {
      "timestamp": "2026-02-06T11:32:00Z",
      "event": "Systems isolated from network",
      "automated": true,
      "details": {
        "systems": ["file-server-01", "file-server-02"],
        "method": "firewall_block"
      }
    },
    {
      "timestamp": "2026-02-06T11:35:00Z",
      "event": "C&C communication blocked",
      "automated": true,
      "details": {
        "blocked_ips": ["192.0.2.100"],
        "blocked_domains": ["evil-c2.com"]
      }
    }
  ],
  "response_plan": {
    "playbook": "ransomware",
    "steps": [
      {
        "step_number": 1,
        "title": "Isolate Infected Systems",
        "status": "completed",
        "completed_at": "2026-02-06T11:32:00Z",
        "duration_minutes": 2
      },
      {
        "step_number": 2,
        "title": "Block C&C Communication",
        "status": "completed",
        "completed_at": "2026-02-06T11:35:00Z",
        "duration_minutes": 3
      },
      {
        "step_number": 3,
        "title": "Preserve Evidence",
        "status": "in_progress",
        "started_at": "2026-02-06T11:35:00Z"
      }
    ]
  },
  "evidence": [
    {
      "id": "evidence-001",
      "type": "memory_dump",
      "location": "s3://forensics/INC-2026-042/memory.dmp",
      "size_bytes": 8589934592,
      "collected_at": "2026-02-06T11:33:00Z"
    },
    {
      "id": "evidence-002",
      "type": "network_capture",
      "location": "s3://forensics/INC-2026-042/traffic.pcap",
      "size_bytes": 524288000,
      "collected_at": "2026-02-06T11:34:00Z"
    }
  ],
  "metrics": {
    "time_to_detect_minutes": 5,
    "time_to_respond_minutes": 2,
    "containment_time_minutes": 5,
    "estimated_downtime_hours": 4
  }
}
```

### Update Incident

```http
PATCH /api/v1/incidents/{incident_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "status": "resolved",
  "resolution_notes": "Malware eradicated from all systems. Files restored from backup. All systems verified clean.",
  "lessons_learned": [
    "Need faster backup verification process",
    "Improve endpoint detection rules",
    "Update incident response training"
  ],
  "root_cause": "Phishing email with malicious attachment",
  "remediation_actions": [
    "Deployed updated antivirus signatures",
    "Implemented email filtering rules",
    "Conducted user awareness training"
  ]
}

Response 200:
{
  "incident_id": "INC-2026-042",
  "status": "resolved",
  "resolved_at": "2026-02-06T19:45:00Z",
  "resolution_time_hours": 8.25,
  "updated_at": "2026-02-06T19:45:00Z"
}
```

### List Incidents

```http
GET /api/v1/incidents?status=open&severity=critical&limit=10&offset=0
Authorization: Bearer <token>

Response 200:
{
  "incidents": [
    {
      "incident_id": "INC-2026-042",
      "severity": "critical",
      "type": "ransomware",
      "status": "in_progress",
      "title": "Ransomware detected on file server",
      "created_at": "2026-02-06T11:30:00Z",
      "assigned_to": "incident-response-team"
    },
    {
      "incident_id": "INC-2026-041",
      "severity": "critical",
      "type": "data_breach",
      "status": "open",
      "title": "Unauthorized data access detected",
      "created_at": "2026-02-06T09:15:00Z",
      "assigned_to": "security-team"
    }
  ],
  "total": 2,
  "page": 1,
  "per_page": 10,
  "filters_applied": {
    "status": "open",
    "severity": "critical"
  }
}
```

### Get Incident Metrics

```http
GET /api/v1/incidents/metrics?period=30d&group_by=type
Authorization: Bearer <token>

Response 200:
{
  "period": "30d",
  "date_from": "2026-01-07T00:00:00Z",
  "date_to": "2026-02-06T23:59:59Z",
  "total_incidents": 47,
  "by_severity": {
    "critical": 5,
    "high": 12,
    "medium": 20,
    "low": 10
  },
  "by_type": {
    "ransomware": 2,
    "phishing": 15,
    "malware": 8,
    "data_breach": 3,
    "ddos": 4,
    "insider_threat": 3,
    "other": 12
  },
  "by_status": {
    "open": 3,
    "in_progress": 2,
    "resolved": 42
  },
  "metrics": {
    "mean_time_to_detect_minutes": 12.5,
    "mean_time_to_respond_minutes": 8.2,
    "mean_time_to_resolve_hours": 6.5,
    "resolution_rate": 93.6,
    "recurring_incidents": 3
  },
  "trends": {
    "incidents_per_week": [8, 12, 10, 11, 6],
    "average_severity": 2.8
  }
}
```

### Execute Playbook Step

```http
POST /api/v1/incidents/{incident_id}/steps/{step_number}/execute
Content-Type: application/json
Authorization: Bearer <token>

{
  "executed_by": "user-456",
  "notes": "Successfully isolated all affected systems using firewall rules",
  "evidence": [
    {
      "type": "screenshot",
      "url": "s3://evidence/firewall-screenshot.png"
    }
  ]
}

Response 200:
{
  "incident_id": "INC-2026-042",
  "step_number": 1,
  "status": "completed",
  "executed_at": "2026-02-06T11:32:00Z",
  "executed_by": "user-456",
  "duration_minutes": 2,
  "next_step": {
    "step_number": 2,
    "title": "Block C&C Communication",
    "priority": "immediate"
  }
}
```

---

## 🎯 Risk Management Endpoints

### List Risks

```http
GET /api/v1/risks?severity=critical&status=open&limit=10
Authorization: Bearer <token>

Response 200:
{
  "risks": [
    {
      "risk_id": "RISK-2026-001",
      "title": "CVE-2025-1234 in production web server",
      "severity": "critical",
      "cvss_score": 9.8,
      "status": "open",
      "asset": {
        "asset_id": "asset-web-01",
        "name": "Production Web Server",
        "criticality": "critical"
      },
      "created_at": "2026-02-05T10:00:00Z",
      "due_date": "2026-02-06T10:00:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "per_page": 10
}
```

### Get Risk Details

```http
GET /api/v1/risks/{risk_id}
Authorization: Bearer <token>

Response 200:
{
  "risk_id": "RISK-2026-001",
  "title": "CVE-2025-1234 in production web server",
  "description": "Critical RCE vulnerability in Apache Struts",
  "severity": "critical",
  "cvss_score": 9.8,
  "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
  "status": "open",
  "asset": {...},
  "vulnerability": {...},
  "recommendations": [...],
  "remediation_plan": {...}
}
```

---

## ✅ Compliance Endpoints

### Check Compliance

```http
POST /api/v1/compliance/check
Content-Type: application/json
Authorization: Bearer <token>

{
  "framework": "ISO_27001",
  "scope": "production_infrastructure",
  "controls": ["A.8.1", "A.8.2", "A.8.3"]
}

Response 200:
{
  "framework": "ISO_27001",
  "overall_compliance": 78.5,
  "controls_checked": 3,
  "controls_passed": 2,
  "controls_failed": 1,
  "results": [
    {
      "control": "A.8.1",
      "title": "Inventory of assets",
      "status": "compliant",
      "score": 100,
      "evidence": [...]
    },
    {
      "control": "A.8.2",
      "title": "Ownership of assets",
      "status": "compliant",
      "score": 95,
      "evidence": [...]
    },
    {
      "control": "A.8.3",
      "title": "Acceptable use of assets",
      "status": "non_compliant",
      "score": 45,
      "gaps": [
        "Policy not updated in last 12 months",
        "No user acknowledgment tracking"
      ],
      "recommendations": [...]
    }
  ]
}
```

---

## 📚 Conversation History Endpoints

### Export Conversation

```http
GET /api/v1/chat/sessions/{session_id}/export?format=json
Authorization: Bearer <token>

Response 200:
{
  "session_id": "sess-abc-123",
  "exported_at": "2026-02-06T11:45:00Z",
  "format": "json",
  "messages": [...],
  "metadata": {...}
}
```

### Get User Statistics

```http
GET /api/v1/users/me/stats
Authorization: Bearer <token>

Response 200:
{
  "user_id": "user-456",
  "total_sessions": 45,
  "total_messages": 320,
  "total_incidents_reported": 5,
  "most_used_agent": "RiskAssessmentAgent",
  "average_session_length_minutes": 12.5,
  "period_days": 30
}
```

---

## ⚠️ Error Handling

### Error Response Format

All errors follow this standard format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request body is invalid",
    "details": [
      {
        "field": "severity",
        "issue": "Must be one of: critical, high, medium, low"
      }
    ],
    "request_id": "req-xyz-789",
    "timestamp": "2026-02-06T11:50:00Z"
  }
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content to return |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (e.g., duplicate) |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_REQUIRED` | Missing authentication token |
| `INVALID_TOKEN` | Token is invalid or expired |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions |
| `INVALID_REQUEST` | Request validation failed |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist |
| `RESOURCE_CONFLICT` | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_ERROR` | Server error occurred |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable |

---

## 🚦 Rate Limiting

### Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/v1/chat/message` | 30 requests | 1 minute |
| `/api/v1/incidents` (POST) | 10 requests | 1 minute |
| `/api/v1/chat/search` | 20 requests | 1 minute |
| Other endpoints | 60 requests | 1 minute |

### Rate Limit Headers

```http
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1675685400
```

### Rate Limit Exceeded Response

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1675685400
Retry-After: 60

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 60 seconds.",
    "retry_after_seconds": 60
  }
}
```

---

## 📊 Webhook Events

Subscribe to webhook events for real-time updates.

### Configure Webhook

```http
POST /api/v1/webhooks
Content-Type: application/json
Authorization: Bearer <token>

{
  "url": "https://your-app.com/webhooks/ciso-digital",
  "events": ["incident.created", "incident.resolved"],
  "secret": "your-webhook-secret"
}

Response 201:
{
  "webhook_id": "webhook-001",
  "url": "https://your-app.com/webhooks/ciso-digital",
  "events": ["incident.created", "incident.resolved"],
  "active": true,
  "created_at": "2026-02-06T12:00:00Z"
}
```

### Webhook Payload

```json
{
  "event": "incident.created",
  "timestamp": "2026-02-06T11:30:00Z",
  "data": {
    "incident_id": "INC-2026-042",
    "severity": "critical",
    "type": "ransomware",
    "title": "Ransomware detected on file server"
  }
}
```

### Available Events

- `incident.created`
- `incident.updated`
- `incident.resolved`
- `risk.detected`
- `compliance.failed`
- `chat.message.sent`

---

## 🔗 Related Documentation

- [CISO Orchestrator](./ORCHESTRATOR.md)
- [Incident Response](./INCIDENT-RESPONSE.md)
- [Conversation Memory](./CONVERSATION-MEMORY.md)

---

**Maintained by:** CISO Digital API Team  
**Support:** api-support@ciso-digital.com  
**Status Page:** https://status.ciso-digital.com
