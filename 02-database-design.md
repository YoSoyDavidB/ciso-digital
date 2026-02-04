# Diseño de Bases de Datos - CISO Digital

## 1. Visión General de Persistencia

### 1.1 Estrategia Multi-Database

El sistema utiliza múltiples bases de datos, cada una optimizada para su caso de uso específico:

| Base de Datos | Propósito | Datos Almacenados | Volumen Estimado |
|---------------|-----------|-------------------|------------------|
| PostgreSQL | Datos estructurados transaccionales | Riesgos, Incidentes, Activos, Políticas | 10-100 GB |
| Qdrant | Búsqueda semántica (vectores) | Knowledge base, Conversaciones | 5-50 GB |
| Redis | Cache y sesiones | Sessions, query cache, rate limiting | 1-10 GB |
| TimescaleDB | Series temporales | Métricas, eventos, logs | 50-500 GB |

### 1.2 Principios de Diseño

**Normalización**: PostgreSQL normalizado hasta 3NF para evitar redundancia

**Desnormalización selectiva**: Algunos campos duplicados para performance (cached values)

**Soft Deletes**: Uso de `deleted_at` en lugar de DELETE físico para auditabilidad

**Audit Trail**: Tabla `audit_log` para tracking de todos los cambios

**Timestamps**: Todas las tablas incluyen `created_at` y `updated_at`

**UUIDs**: Uso de UUIDs para primary keys (mejor para sistemas distribuidos)

**JSONB para flexibilidad**: Columnas JSONB para metadata variable

---

## 2. PostgreSQL - Schema Detallado

### 2.1 Tablas Core

#### 2.1.1 Tabla: `risks`

Gestión de riesgos de seguridad identificados

```sql
CREATE TABLE risks (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_number VARCHAR(50) UNIQUE NOT NULL, -- Ej: RISK-2026-001
    
    -- Información básica
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL, -- technical, operational, strategic, compliance
    
    -- Evaluación de riesgo
    severity VARCHAR(50) NOT NULL, -- critical, high, medium, low
    likelihood VARCHAR(50) NOT NULL, -- certain, likely, possible, unlikely, rare
    impact_score INT CHECK (impact_score BETWEEN 1 AND 5),
    likelihood_score INT CHECK (likelihood_score BETWEEN 1 AND 5),
    risk_score INT GENERATED ALWAYS AS (impact_score * likelihood_score) STORED,
    
    -- Estado y asignación
    status VARCHAR(50) NOT NULL DEFAULT 'open', -- open, in_progress, mitigated, accepted, closed
    priority VARCHAR(50), -- urgent, high, medium, low
    assigned_to VARCHAR(255),
    owner VARCHAR(255) NOT NULL,
    
    -- Mitigación
    mitigation_plan TEXT,
    mitigation_status VARCHAR(50), -- not_started, in_progress, completed
    mitigation_cost DECIMAL(12,2),
    residual_risk_score INT,
    
    -- Tracking
    identified_date DATE NOT NULL DEFAULT CURRENT_DATE,
    target_closure_date DATE,
    actual_closure_date DATE,
    last_reviewed_date DATE,
    next_review_date DATE,
    
    -- Relaciones
    related_asset_ids UUID[],
    related_incident_ids UUID[],
    related_vulnerability_ids UUID[],
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    tags TEXT[],
    
    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    deleted_at TIMESTAMP
);

-- Índices
CREATE INDEX idx_risks_status ON risks(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_risks_severity ON risks(severity) WHERE deleted_at IS NULL;
CREATE INDEX idx_risks_assigned ON risks(assigned_to) WHERE deleted_at IS NULL;
CREATE INDEX idx_risks_risk_score ON risks(risk_score DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_risks_review_date ON risks(next_review_date) WHERE deleted_at IS NULL;
CREATE INDEX idx_risks_metadata ON risks USING gin(metadata);

-- Trigger para updated_at
CREATE TRIGGER update_risks_updated_at 
    BEFORE UPDATE ON risks 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

#### 2.1.2 Tabla: `incidents`

Registro y gestión de incidentes de seguridad

```sql
CREATE TABLE incidents (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_number VARCHAR(50) UNIQUE NOT NULL, -- Ej: INC-2026-001
    
    -- Información básica
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    incident_type VARCHAR(100) NOT NULL, -- malware, phishing, data_breach, unauthorized_access, dos, other
    
    -- Clasificación
    severity VARCHAR(50) NOT NULL, -- critical, high, medium, low
    priority VARCHAR(50) NOT NULL, -- p1, p2, p3, p4
    confidentiality_impact VARCHAR(50), -- high, medium, low, none
    integrity_impact VARCHAR(50),
    availability_impact VARCHAR(50),
    
    -- Estado y asignación
    status VARCHAR(50) NOT NULL DEFAULT 'detected', -- detected, investigating, contained, eradicating, recovering, resolved, closed
    assigned_to VARCHAR(255),
    incident_manager VARCHAR(255),
    team_involved TEXT[],
    
    -- Timeline
    detection_time TIMESTAMP NOT NULL,
    notification_time TIMESTAMP,
    response_start_time TIMESTAMP,
    containment_time TIMESTAMP,
    eradication_time TIMESTAMP,
    recovery_time TIMESTAMP,
    resolution_time TIMESTAMP,
    closure_time TIMESTAMP,
    
    -- Tiempos calculados (en minutos)
    time_to_detect INT, -- desde ocurrencia hasta detección
    time_to_respond INT, -- desde detección hasta respuesta
    time_to_contain INT, -- desde respuesta hasta contención
    time_to_resolve INT, -- desde detección hasta resolución
    
    -- Análisis técnico
    attack_vector VARCHAR(100), -- email, web, network, physical, social_engineering
    attack_source TEXT, -- IP, domain, user account
    affected_assets TEXT[] NOT NULL,
    affected_systems TEXT[],
    affected_data_types TEXT[],
    estimated_records_affected INT,
    
    -- Indicadores de compromiso
    indicators_of_compromise JSONB DEFAULT '[]',
    /*
    [
      {"type": "ip", "value": "192.168.1.100", "description": "Malicious IP"},
      {"type": "hash", "value": "abc123...", "description": "Malware hash"},
      {"type": "domain", "value": "evil.com", "description": "C2 domain"}
    ]
    */
    
    -- Respuesta
    response_actions JSONB DEFAULT '[]',
    /*
    [
      {"timestamp": "2026-02-04T10:00:00Z", "action": "Isolated affected host", "performed_by": "admin"},
      {"timestamp": "2026-02-04T10:15:00Z", "action": "Reset user credentials", "performed_by": "admin"}
    ]
    */
    playbook_used VARCHAR(255),
    automation_triggered BOOLEAN DEFAULT false,
    
    -- Impacto
    business_impact TEXT,
    financial_impact DECIMAL(12,2),
    reputational_impact VARCHAR(50), -- high, medium, low, none
    regulatory_impact TEXT,
    
    -- Comunicación
    stakeholders_notified TEXT[],
    external_parties_notified TEXT[], -- law_enforcement, regulators, customers
    public_disclosure_required BOOLEAN DEFAULT false,
    disclosure_date DATE,
    
    -- Post-Mortem
    root_cause TEXT,
    contributing_factors TEXT[],
    lessons_learned TEXT,
    recommendations TEXT,
    preventive_measures TEXT[],
    
    -- Follow-up
    follow_up_tasks JSONB DEFAULT '[]',
    related_incidents UUID[],
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    tags TEXT[],
    
    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    deleted_at TIMESTAMP
);

-- Índices
CREATE INDEX idx_incidents_status ON incidents(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_incidents_severity ON incidents(severity) WHERE deleted_at IS NULL;
CREATE INDEX idx_incidents_detection_time ON incidents(detection_time DESC);
CREATE INDEX idx_incidents_assigned ON incidents(assigned_to) WHERE deleted_at IS NULL;
CREATE INDEX idx_incidents_type ON incidents(incident_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_incidents_ioc ON incidents USING gin(indicators_of_compromise);
CREATE INDEX idx_incidents_affected_assets ON incidents USING gin(affected_assets);

-- Trigger
CREATE TRIGGER update_incidents_updated_at 
    BEFORE UPDATE ON incidents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

#### 2.1.3 Tabla: `assets`

Inventario de activos de TI

```sql
CREATE TABLE assets (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_tag VARCHAR(100) UNIQUE NOT NULL,
    
    -- Información básica
    name VARCHAR(255) NOT NULL,
    description TEXT,
    asset_type VARCHAR(100) NOT NULL, -- server, workstation, network_device, database, application, cloud_service, mobile_device
    
    -- Clasificación
    criticality VARCHAR(50) NOT NULL, -- critical, high, medium, low
    data_classification VARCHAR(50), -- confidential, internal, public
    business_function VARCHAR(255),
    
    -- Propiedad y responsabilidad
    owner VARCHAR(255) NOT NULL,
    custodian VARCHAR(255),
    department VARCHAR(255),
    cost_center VARCHAR(100),
    
    -- Ubicación
    location VARCHAR(255), -- physical location or cloud region
    datacenter VARCHAR(100),
    rack_position VARCHAR(50),
    
    -- Detalles técnicos
    ip_addresses TEXT[],
    mac_addresses TEXT[],
    hostnames TEXT[],
    operating_system VARCHAR(255),
    os_version VARCHAR(100),
    
    -- Configuración
    software_installed JSONB DEFAULT '[]',
    /*
    [
      {"name": "Apache", "version": "2.4.51", "vendor": "Apache Software Foundation"},
      {"name": "MySQL", "version": "8.0.28", "vendor": "Oracle"}
    ]
    */
    
    technologies JSONB DEFAULT '{}',
    /*
    {
      "languages": ["Python", "JavaScript"],
      "frameworks": ["Django", "React"],
      "databases": ["PostgreSQL", "Redis"]
    }
    */
    
    ports_services JSONB DEFAULT '[]',
    /*
    [
      {"port": 22, "service": "SSH", "state": "open"},
      {"port": 443, "service": "HTTPS", "state": "open"}
    ]
    */
    
    -- Seguridad
    vulnerabilities JSONB DEFAULT '[]', -- Lista de CVE IDs
    last_vulnerability_scan_date TIMESTAMP,
    next_vulnerability_scan_date TIMESTAMP,
    patch_level VARCHAR(255),
    last_patch_date DATE,
    
    compliance_requirements TEXT[], -- ISO27001, PCI-DSS, HIPAA, etc.
    compliance_status JSONB DEFAULT '{}',
    /*
    {
      "ISO27001": {"status": "compliant", "last_audit": "2026-01-15"},
      "PCI-DSS": {"status": "non_compliant", "findings": ["Missing encryption"]}
    }
    */
    
    encryption_status VARCHAR(50), -- encrypted, partial, unencrypted
    backup_status VARCHAR(50), -- backed_up, not_backed_up
    last_backup_date TIMESTAMP,
    
    -- Lifecycle
    purchase_date DATE,
    installation_date DATE,
    warranty_expiry_date DATE,
    end_of_life_date DATE,
    disposal_date DATE,
    asset_status VARCHAR(50) DEFAULT 'active', -- active, inactive, decommissioned, maintenance
    
    -- Relaciones
    depends_on UUID[], -- Other asset IDs this asset depends on
    supports UUID[], -- Other asset IDs that depend on this asset
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    tags TEXT[],
    notes TEXT,
    
    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    deleted_at TIMESTAMP
);

-- Índices
CREATE INDEX idx_assets_type ON assets(asset_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_assets_criticality ON assets(criticality) WHERE deleted_at IS NULL;
CREATE INDEX idx_assets_owner ON assets(owner) WHERE deleted_at IS NULL;
CREATE INDEX idx_assets_status ON assets(asset_status) WHERE deleted_at IS NULL;
CREATE INDEX idx_assets_scan_date ON assets(next_vulnerability_scan_date) WHERE deleted_at IS NULL;
CREATE INDEX idx_assets_technologies ON assets USING gin(technologies);
CREATE INDEX idx_assets_ip_addresses ON assets USING gin(ip_addresses);

-- Trigger
CREATE TRIGGER update_assets_updated_at 
    BEFORE UPDATE ON assets 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

#### 2.1.4 Tabla: `vulnerabilities`

Vulnerabilidades identificadas en activos

```sql
CREATE TABLE vulnerabilities (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cve_id VARCHAR(50), -- CVE-2024-1234 (puede ser NULL para vulns sin CVE)
    vuln_id VARCHAR(100) UNIQUE NOT NULL, -- Internal ID: VULN-2026-001
    
    -- Relación con activo
    asset_id UUID NOT NULL REFERENCES assets(id),
    
    -- Información básica
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    vulnerability_type VARCHAR(100), -- sql_injection, xss, buffer_overflow, misconfiguration, etc.
    
    -- Scoring
    severity VARCHAR(50) NOT NULL, -- critical, high, medium, low, informational
    cvss_version VARCHAR(10), -- 3.1, 3.0, 2.0
    cvss_vector VARCHAR(255),
    cvss_score DECIMAL(3,1), -- 0.0 to 10.0
    cvss_base_score DECIMAL(3,1),
    cvss_temporal_score DECIMAL(3,1),
    cvss_environmental_score DECIMAL(3,1),
    
    -- Contexto
    discovery_method VARCHAR(100), -- automated_scan, penetration_test, bug_bounty, incident_response
    discovered_by VARCHAR(255),
    
    -- Estado
    status VARCHAR(50) NOT NULL DEFAULT 'open', -- open, in_remediation, patched, mitigated, accepted, false_positive, closed
    priority VARCHAR(50), -- urgent, high, medium, low
    
    -- Exploit information
    exploit_available BOOLEAN DEFAULT false,
    exploit_maturity VARCHAR(50), -- unproven, proof_of_concept, functional, high
    exploit_urls TEXT[],
    public_disclosure BOOLEAN DEFAULT false,
    
    -- Patch information
    patch_available BOOLEAN DEFAULT false,
    patch_version VARCHAR(100),
    patch_release_date DATE,
    patch_url TEXT,
    
    -- Remediación
    remediation_plan TEXT,
    remediation_steps TEXT[],
    temporary_mitigation TEXT,
    workaround TEXT,
    assigned_to VARCHAR(255),
    
    -- Plazos
    discovery_date TIMESTAMP NOT NULL DEFAULT NOW(),
    first_seen_date DATE,
    remediation_deadline TIMESTAMP,
    target_remediation_date DATE,
    actual_remediation_date DATE,
    verification_date DATE,
    
    -- SLA tracking
    sla_deadline TIMESTAMP,
    sla_status VARCHAR(50), -- within_sla, at_risk, breached
    days_open INT GENERATED ALWAYS AS (
        EXTRACT(DAY FROM (COALESCE(actual_remediation_date::timestamp, NOW()) - discovery_date))
    ) STORED,
    
    -- Impacto
    affected_components TEXT[],
    business_impact TEXT,
    risk_score INT, -- Business risk score (separate from CVSS)
    
    -- Referencias
    references JSONB DEFAULT '[]',
    /*
    [
      {"type": "vendor_advisory", "url": "https://..."},
      {"type": "exploit_db", "url": "https://..."},
      {"type": "cwe", "id": "CWE-79"}
    ]
    */
    
    cwe_ids TEXT[], -- Common Weakness Enumeration
    
    -- Verificación
    verified BOOLEAN DEFAULT false,
    verified_by VARCHAR(255),
    verification_notes TEXT,
    retest_required BOOLEAN DEFAULT false,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    tags TEXT[],
    notes TEXT,
    
    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    deleted_at TIMESTAMP
);

-- Índices
CREATE INDEX idx_vulnerabilities_asset ON vulnerabilities(asset_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_vulnerabilities_cve ON vulnerabilities(cve_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_vulnerabilities_severity ON vulnerabilities(severity) WHERE deleted_at IS NULL;
CREATE INDEX idx_vulnerabilities_status ON vulnerabilities(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_vulnerabilities_cvss_score ON vulnerabilities(cvss_score DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_vulnerabilities_deadline ON vulnerabilities(remediation_deadline) WHERE deleted_at IS NULL;
CREATE INDEX idx_vulnerabilities_sla_status ON vulnerabilities(sla_status) WHERE deleted_at IS NULL;

-- Trigger
CREATE TRIGGER update_vulnerabilities_updated_at 
    BEFORE UPDATE ON vulnerabilities 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

#### 2.1.5 Tabla: `policies`

Políticas y procedimientos de seguridad

```sql
CREATE TABLE policies (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_number VARCHAR(50) UNIQUE NOT NULL, -- POL-SEC-001
    
    -- Información básica
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL, -- information_security, access_control, data_protection, incident_response, etc.
    policy_type VARCHAR(50) NOT NULL, -- policy, procedure, standard, guideline
    
    -- Contenido
    content TEXT NOT NULL, -- Full policy text (or reference to document)
    document_url TEXT, -- Link to document if stored externally
    
    -- Framework mapping
    framework VARCHAR(100), -- ISO27001, NIST_CSF, CIS_Controls, COBIT
    control_ids TEXT[], -- Specific control IDs: ["A.5.1.1", "A.5.1.2"]
    
    -- Estado
    status VARCHAR(50) NOT NULL DEFAULT 'draft', -- draft, under_review, approved, active, deprecated, archived
    version VARCHAR(20) NOT NULL, -- 1.0, 1.1, 2.0
    
    -- Responsabilidad
    owner VARCHAR(255) NOT NULL,
    approver VARCHAR(255),
    responsible_parties TEXT[],
    
    -- Lifecycle
    effective_date DATE,
    approval_date DATE,
    approved_by VARCHAR(255),
    publication_date DATE,
    
    -- Revisión
    review_frequency_days INT NOT NULL DEFAULT 365,
    last_review_date DATE,
    next_review_date DATE,
    reviewed_by VARCHAR(255),
    
    -- Aplicabilidad
    applies_to TEXT[], -- departments, roles, or "all"
    exceptions TEXT,
    
    -- Compliance
    mandatory BOOLEAN DEFAULT true,
    regulatory_requirement TEXT[], -- GDPR, HIPAA, SOX, PCI-DSS
    
    -- Relaciones
    supersedes UUID, -- Previous policy version
    related_policies UUID[],
    related_procedures UUID[],
    
    -- Training
    training_required BOOLEAN DEFAULT false,
    training_url TEXT,
    acknowledgment_required BOOLEAN DEFAULT false,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    tags TEXT[],
    attachments JSONB DEFAULT '[]',
    /*
    [
      {"name": "Appendix A", "url": "https://...", "type": "pdf"}
    ]
    */
    
    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    deleted_at TIMESTAMP
);

-- Índices
CREATE INDEX idx_policies_category ON policies(category) WHERE deleted_at IS NULL;
CREATE INDEX idx_policies_status ON policies(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_policies_framework ON policies(framework) WHERE deleted_at IS NULL;
CREATE INDEX idx_policies_review_date ON policies(next_review_date) WHERE deleted_at IS NULL;
CREATE INDEX idx_policies_owner ON policies(owner) WHERE deleted_at IS NULL;
CREATE INDEX idx_policies_control_ids ON policies USING gin(control_ids);

-- Trigger
CREATE TRIGGER update_policies_updated_at 
    BEFORE UPDATE ON policies 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

#### 2.1.6 Tabla: `compliance_checks`

Verificaciones de cumplimiento normativo

```sql
CREATE TABLE compliance_checks (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    check_id VARCHAR(100) UNIQUE NOT NULL, -- COMP-ISO-A.5.1.1
    
    -- Framework y control
    framework VARCHAR(100) NOT NULL, -- ISO27001, NIST_CSF, CIS_Controls, PCI_DSS, HIPAA, GDPR
    domain VARCHAR(255), -- Organizational Controls, Asset Management, etc.
    control_id VARCHAR(100) NOT NULL, -- A.5.1.1, PR.AC-1, etc.
    control_name VARCHAR(255) NOT NULL,
    control_description TEXT NOT NULL,
    
    -- Requerimiento
    requirement TEXT NOT NULL, -- What needs to be in place
    testing_procedure TEXT, -- How to verify compliance
    
    -- Estado
    status VARCHAR(50) NOT NULL DEFAULT 'not_assessed', -- compliant, non_compliant, partially_compliant, not_applicable, not_assessed
    compliance_score INT CHECK (compliance_score BETWEEN 0 AND 100),
    
    -- Assessment
    assessment_method VARCHAR(100), -- automated, manual_review, interview, observation, documentation_review
    last_check_date TIMESTAMP,
    next_check_date TIMESTAMP,
    check_frequency_days INT DEFAULT 90,
    
    -- Evidencias
    evidence_location TEXT,
    evidence_type VARCHAR(100), -- screenshot, document, log_file, configuration, certificate
    evidence_urls TEXT[],
    evidence_description TEXT,
    
    -- Hallazgos
    findings TEXT, -- Issues identified if non-compliant
    gap_analysis TEXT,
    impact VARCHAR(50), -- high, medium, low
    
    -- Remediación
    remediation_plan TEXT,
    remediation_owner VARCHAR(255),
    remediation_deadline DATE,
    remediation_status VARCHAR(50), -- not_started, in_progress, completed
    remediation_notes TEXT,
    
    -- Responsabilidad
    responsible VARCHAR(255) NOT NULL, -- Person/team responsible for maintaining compliance
    assessor VARCHAR(255), -- Person who performed assessment
    reviewer VARCHAR(255),
    
    -- Relaciones
    related_policy_ids UUID[],
    related_asset_ids UUID[],
    related_risk_ids UUID[],
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    tags TEXT[],
    notes TEXT,
    
    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    deleted_at TIMESTAMP
);

-- Índices
CREATE INDEX idx_compliance_framework ON compliance_checks(framework) WHERE deleted_at IS NULL;
CREATE INDEX idx_compliance_status ON compliance_checks(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_compliance_next_check ON compliance_checks(next_check_date) WHERE deleted_at IS NULL;
CREATE INDEX idx_compliance_responsible ON compliance_checks(responsible) WHERE deleted_at IS NULL;
CREATE INDEX idx_compliance_control_id ON compliance_checks(control_id) WHERE deleted_at IS NULL;

-- Trigger
CREATE TRIGGER update_compliance_checks_updated_at 
    BEFORE UPDATE ON compliance_checks 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

### 2.2 Tablas de Soporte

#### 2.2.1 Tabla: `scheduled_tasks`

Tareas programadas del CISO Digital

```sql
CREATE TABLE scheduled_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_name VARCHAR(255) NOT NULL,
    task_type VARCHAR(100) NOT NULL, -- vulnerability_scan, compliance_check, risk_review, report_generation, policy_review
    description TEXT,
    
    -- Programación
    cron_expression VARCHAR(100), -- 0 2 * * * (daily at 2 AM)
    timezone VARCHAR(50) DEFAULT 'UTC',
    enabled BOOLEAN DEFAULT true,
    
    -- Ejecución
    next_execution TIMESTAMP,
    last_execution TIMESTAMP,
    last_status VARCHAR(50), -- success, failed, skipped, in_progress
    last_error TEXT,
    execution_count INT DEFAULT 0,
    failure_count INT DEFAULT 0,
    
    -- Configuración
    parameters JSONB DEFAULT '{}',
    /*
    {
      "scan_type": "full",
      "targets": ["all_assets"],
      "notification_channels": ["slack", "email"]
    }
    */
    
    timeout_seconds INT DEFAULT 3600,
    retry_on_failure BOOLEAN DEFAULT true,
    max_retries INT DEFAULT 3,
    
    -- Historial
    execution_history JSONB DEFAULT '[]',
    /*
    [
      {
        "timestamp": "2026-02-04T02:00:00Z",
        "status": "success",
        "duration_seconds": 120,
        "results": {...}
      }
    ]
    */
    
    -- Notificaciones
    notify_on_success BOOLEAN DEFAULT false,
    notify_on_failure BOOLEAN DEFAULT true,
    notification_recipients TEXT[],
    
    -- Metadata
    priority VARCHAR(50) DEFAULT 'normal', -- critical, high, normal, low
    owner VARCHAR(255),
    tags TEXT[],
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_scheduled_tasks_next_execution ON scheduled_tasks(next_execution) WHERE enabled = true AND deleted_at IS NULL;
CREATE INDEX idx_scheduled_tasks_type ON scheduled_tasks(task_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_scheduled_tasks_enabled ON scheduled_tasks(enabled) WHERE deleted_at IS NULL;
```

#### 2.2.2 Tabla: `security_metrics`

KPIs y métricas de seguridad

```sql
CREATE TABLE security_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identificación de métrica
    metric_name VARCHAR(255) NOT NULL,
    metric_category VARCHAR(100) NOT NULL, -- risk, incident, compliance, vulnerability, operational
    metric_type VARCHAR(100) NOT NULL, -- count, percentage, ratio, time, score
    
    -- Valor
    value DECIMAL(12,2) NOT NULL,
    unit VARCHAR(50), -- count, %, minutes, score, days
    
    -- Periodo
    period_type VARCHAR(50), -- daily, weekly, monthly, quarterly, yearly
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    
    -- Target y status
    target_value DECIMAL(12,2),
    threshold_warning DECIMAL(12,2),
    threshold_critical DECIMAL(12,2),
    status VARCHAR(50), -- on_target, warning, critical, exceeding
    
    -- Cálculo
    calculation_method TEXT,
    data_source VARCHAR(255),
    
    -- Contexto
    breakdown JSONB DEFAULT '{}',
    /*
    {
      "by_severity": {"critical": 5, "high": 12, "medium": 45},
      "by_department": {"IT": 30, "Finance": 15, "HR": 17}
    }
    */
    
    -- Comparación
    previous_period_value DECIMAL(12,2),
    change_percentage DECIMAL(5,2),
    trend VARCHAR(50), -- improving, stable, degrading
    
    -- Metadata
    notes TEXT,
    tags TEXT[],
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255)
);

CREATE INDEX idx_metrics_name ON security_metrics(metric_name);
CREATE INDEX idx_metrics_category ON security_metrics(metric_category);
CREATE INDEX idx_metrics_period ON security_metrics(period_start, period_end);
CREATE INDEX idx_metrics_status ON security_metrics(status);
```

#### 2.2.3 Tabla: `conversations`

Historial de conversaciones con el CISO Digital

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Sesión
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    
    -- Mensaje
    message TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'user', -- user, system, agent
    
    -- Respuesta
    response TEXT,
    response_time_ms INT,
    
    -- Análisis
    intent VARCHAR(100), -- risk_assessment, incident_query, compliance_check, report_request
    entities JSONB DEFAULT '{}',
    /*
    {
      "risk_ids": ["RISK-2026-001"],
      "asset_ids": ["asset-123"],
      "frameworks": ["ISO27001"]
    }
    */
    
    -- Agente ejecutado
    agent_used VARCHAR(100), -- orchestrator, risk_agent, incident_agent, etc.
    agents_invoked TEXT[], -- Multiple agents if needed
    
    -- Decisiones y acciones
    decisions_made JSONB DEFAULT '[]',
    /*
    [
      {"type": "risk_escalation", "details": {...}},
      {"type": "incident_created", "incident_id": "INC-2026-001"}
    ]
    */
    
    actions_triggered JSONB DEFAULT '[]',
    /*
    [
      {"action": "create_ticket", "system": "Jira", "ticket_id": "SEC-123"},
      {"action": "send_notification", "channel": "slack", "status": "sent"}
    ]
    */
    
    -- Context utilizado
    rag_documents_used INT,
    tokens_used INT,
    llm_model VARCHAR(100),
    
    -- Feedback
    user_feedback VARCHAR(50), -- thumbs_up, thumbs_down
    feedback_comment TEXT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_timestamp ON conversations(timestamp DESC);
CREATE INDEX idx_conversations_intent ON conversations(intent);
```

#### 2.2.4 Tabla: `audit_log`

Registro de auditoría completo

```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Entidad afectada
    entity_type VARCHAR(100) NOT NULL, -- risk, incident, asset, policy, etc.
    entity_id UUID NOT NULL,
    
    -- Acción
    action VARCHAR(100) NOT NULL, -- create, update, delete, execute, approve, reject
    action_result VARCHAR(50), -- success, failure, partial
    
    -- Actor
    actor_type VARCHAR(50) NOT NULL, -- user, system, ciso_ai, automated_task
    actor VARCHAR(255) NOT NULL, -- user_id or system component
    
    -- Cambios
    changes JSONB,
    /*
    {
      "old_values": {"status": "open", "severity": "medium"},
      "new_values": {"status": "in_progress", "severity": "high"}
    }
    */
    
    -- Contexto
    reason TEXT,
    source VARCHAR(100), -- web_ui, api, n8n_workflow, scheduled_task
    session_id VARCHAR(255),
    request_id VARCHAR(255),
    
    -- Metadata técnica
    ip_address INET,
    user_agent TEXT,
    
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_actor ON audit_log(actor);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_action ON audit_log(action);
```

### 2.3 Funciones Auxiliares

```sql
-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Función para calcular SLA status
CREATE OR REPLACE FUNCTION calculate_sla_status(deadline TIMESTAMP)
RETURNS VARCHAR(50) AS $$
BEGIN
    IF deadline IS NULL THEN
        RETURN NULL;
    ELSIF NOW() > deadline THEN
        RETURN 'breached';
    ELSIF NOW() > (deadline - INTERVAL '24 hours') THEN
        RETURN 'at_risk';
    ELSE
        RETURN 'within_sla';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Función para generar risk score
CREATE OR REPLACE FUNCTION calculate_risk_score(likelihood INT, impact INT)
RETURNS INT AS $$
BEGIN
    RETURN likelihood * impact;
END;
$$ LANGUAGE plpgsql;
```

---

## 3. Qdrant - Colecciones de Vectores

### 3.1 Colección: `security_knowledge`

Base de conocimiento de seguridad

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(host="localhost", port=6333)

client.create_collection(
    collection_name="security_knowledge",
    vectors_config=VectorParams(
        size=1536,  # OpenAI ada-002 embedding dimension
        distance=Distance.COSINE
    )
)

# Payload structure
payload_example = {
    "document_id": "doc_001",
    "document_type": "policy",  # policy, procedure, standard, guideline, best_practice, threat_intel
    "title": "Access Control Policy",
    "content": "Full text of the policy...",
    "content_chunk": "This specific chunk of text...", # For large docs split into chunks
    "chunk_index": 1,
    "total_chunks": 5,
    
    # Metadata
    "source": "internal",  # internal, external, public
    "framework": "ISO27001",  # ISO27001, NIST, CIS, GDPR, etc.
    "control_ids": ["A.9.1.1", "A.9.1.2"],
    "category": "access_control",
    "subcategory": "user_access_management",
    
    # Status
    "status": "active",  # active, draft, archived
    "version": "1.0",
    "effective_date": "2026-01-01",
    
    # Relevance
    "importance_score": 0.9,  # 0-1
    "usage_frequency": 15,  # Times referenced
    "last_updated": "2026-02-01T00:00:00Z",
    
    # Relations
    "related_policy_ids": ["pol_002", "pol_003"],
    "applies_to": ["all_employees", "contractors"],
    
    # Search optimization
    "keywords": ["access", "authentication", "authorization", "mfa"],
    "tags": ["security", "access_control", "mandatory"],
    
    # Additional context
    "author": "CISO",
    "department": "IT Security",
    "language": "en",
    "word_count": 1500
}
```

### 3.2 Colección: `incident_memory`

Memoria de incidentes históricos para aprendizaje

```python
client.create_collection(
    collection_name="incident_memory",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE
    )
)

payload_example = {
    "incident_id": "INC-2026-001",
    "incident_number": "INC-2026-001",
    "title": "Phishing Attack - Executive Targeted",
    
    # Descripción completa para embedding
    "description": "Complete incident description...",
    "summary": "Executive received phishing email impersonating CEO...",
    
    # Clasificación
    "incident_type": "phishing",
    "severity": "high",
    "attack_vector": "email",
    
    # Análisis técnico
    "attack_pattern": "Spear phishing with social engineering",
    "indicators_of_compromise": ["email@malicious.com", "192.168.1.100"],
    "affected_assets": ["exec_laptop_001", "email_server"],
    
    # Respuesta y resolución
    "response_summary": "Immediate account lockdown, password reset...",
    "resolution": "Account secured, user trained, email filtering updated",
    "playbook_used": "phishing_response_v2",
    
    # Lecciones aprendidas (esto es oro para RAG)
    "root_cause": "Lack of advanced email filtering",
    "lessons_learned": "Need to implement DMARC and better user training",
    "preventive_measures": [
        "Deployed advanced email filtering",
        "Implemented mandatory security awareness training",
        "Enabled MFA for all executive accounts"
    ],
    
    # Timeline
    "detection_time": "2026-01-15T09:30:00Z",
    "resolution_time": "2026-01-15T14:00:00Z",
    "time_to_resolve_minutes": 270,
    
    # Context
    "similar_incidents": ["INC-2025-089", "INC-2025-102"],
    "related_risks": ["RISK-2026-003"],
    
    # Metadata
    "timestamp": "2026-01-15T00:00:00Z",
    "handled_by": ["security_team", "incident_response_agent"],
    "final_status": "resolved",
    
    # Search optimization
    "keywords": ["phishing", "email", "social_engineering", "executive"],
    "tags": ["phishing", "email_security", "user_training"]
}
```

### 3.3 Colección: `conversation_context`

Memoria conversacional de largo plazo

```python
client.create_collection(
    collection_name="conversation_context",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE
    )
)

payload_example = {
    "conversation_id": "conv_123456",
    "message_id": "msg_789",
    "session_id": "sess_abc",
    "user_id": "user_david",
    
    # Contenido
    "user_message": "What are the top 3 risks we need to address urgently?",
    "assistant_response": "Based on current assessments, here are the top 3...",
    "exchange": "User asked about top risks. Assistant provided: ...",  # Combined for embedding
    
    # Contexto
    "intent": "risk_query",
    "entities_discussed": {
        "risks": ["RISK-2026-001", "RISK-2026-005"],
        "assets": ["web_server_prod"],
        "topics": ["data_breach", "vulnerability_management"]
    },
    
    # Decisiones importantes
    "decisions_made": [
        {
            "decision": "Escalate RISK-2026-001 to critical",
            "reason": "Recent exploit published",
            "timestamp": "2026-02-04T10:00:00Z"
        }
    ],
    
    "actions_taken": [
        {
            "action": "Created incident INC-2026-010",
            "result": "success",
            "timestamp": "2026-02-04T10:05:00Z"
        }
    ],
    
    # Metadata
    "timestamp": "2026-02-04T10:00:00Z",
    "agent_used": "risk_assessment_agent",
    "quality_score": 0.85,  # Based on user feedback
    
    # Search optimization
    "keywords": ["risks", "urgent", "top_priority"],
    "topics": ["risk_management", "prioritization"],
    
    # Retention
    "importance": "high",  # high, medium, low
    "retain_until": "2027-02-04T00:00:00Z"  # Auto-cleanup after 1 year
}
```

### 3.4 Colección: `threat_intelligence`

Inteligencia de amenazas y TTPs

```python
client.create_collection(
    collection_name="threat_intelligence",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE
    )
)

payload_example = {
    "threat_id": "THR-2026-001",
    "threat_name": "APT29 Phishing Campaign",
    
    # Descripción
    "description": "Advanced persistent threat group targeting...",
    "summary": "State-sponsored phishing campaign using...",
    
    # Clasificación
    "threat_type": "phishing",  # malware, phishing, ransomware, ddos, apt
    "threat_actor": "APT29",
    "sophistication": "high",  # low, medium, high, advanced
    
    # MITRE ATT&CK
    "mitre_tactics": ["Initial Access", "Credential Access"],
    "mitre_techniques": ["T1566.001", "T1078"],
    "attack_pattern": "Spear phishing with credential harvesting",
    
    # Indicadores
    "iocs": {
        "domains": ["malicious-domain.com"],
        "ips": ["192.0.2.1"],
        "file_hashes": ["abc123def456..."],
        "email_patterns": ["*@fake-company.com"]
    },
    
    # Recomendaciones
    "detection_methods": [
        "Monitor for unusual email attachments",
        "Check for domains registered recently"
    ],
    "mitigation_steps": [
        "Block known malicious domains",
        "Increase email filtering sensitivity"
    ],
    
    # Contexto
    "first_seen": "2026-01-01T00:00:00Z",
    "last_seen": "2026-02-01T00:00:00Z",
    "affected_industries": ["finance", "healthcare"],
    "affected_regions": ["North America", "Europe"],
    
    # Fuentes
    "source": "MISP",  # MISP, AlienVault, internal
    "source_reliability": "high",
    "reference_urls": ["https://..."],
    
    # Metadata
    "severity": "high",
    "confidence": "confirmed",  # confirmed, probable, possible
    "tlp": "amber",  # white, green, amber, red
    "tags": ["apt", "phishing", "state_sponsored"],
    "timestamp": "2026-02-04T00:00:00Z"
}
```

### 3.5 Estrategias de Búsqueda en Qdrant

#### Búsqueda Básica
```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

# Buscar políticas de ISO 27001
results = client.search(
    collection_name="security_knowledge",
    query_vector=query_embedding,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="framework",
                match=MatchValue(value="ISO27001")
            ),
            FieldCondition(
                key="status",
                match=MatchValue(value="active")
            )
        ]
    ),
    limit=5
)
```

#### Búsqueda Híbrida (Vector + Metadata)
```python
# Buscar incidentes similares de alta severidad
results = client.search(
    collection_name="incident_memory",
    query_vector=incident_description_embedding,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="severity",
                match=MatchValue(value="high")
            )
        ]
    ),
    limit=10,
    score_threshold=0.7  # Solo resultados con similitud > 0.7
)
```

---

## 4. Redis - Estructura de Cache

### 4.1 Patrones de Keys

```redis
# Sesiones de usuario
session:{session_id} -> JSON
{
  "user_id": "user_123",
  "context": {...},
  "last_activity": "2026-02-04T10:00:00Z",
  "active_conversation": "conv_456"
}
TTL: 30 minutos

# Cache de queries RAG
query_cache:{hash_of_query} -> JSON
{
  "query": "What are our top risks?",
  "results": [...],
  "timestamp": "2026-02-04T10:00:00Z"
}
TTL: 5 minutos

# Rate limiting
rate_limit:{user_id}:{endpoint} -> INT
COUNT: number of requests
TTL: 60 segundos (sliding window)

# Estado de agentes
agent:{agent_id}:status -> JSON
{
  "status": "active",
  "current_task": "analyzing_risk_001",
  "started_at": "2026-02-04T10:00:00Z"
}
TTL: 1 hora

# Locks distribuidos (para evitar race conditions)
lock:task:{task_id} -> STRING
VALUE: worker_id
TTL: 5 minutos

# Colas de tareas (Celery)
celery:task:{priority} -> LIST
PUSH/POP: task_ids

# Métricas en tiempo real
metrics:realtime:{metric_name} -> STRING
VALUE: current value
TTL: 1 minuto

# Notificaciones pendientes
notifications:{user_id} -> LIST
PUSH: notification objects
```

### 4.2 Ejemplo de Uso

```python
import redis
import json
from datetime import timedelta

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Guardar sesión
session_data = {
    "user_id": "user_123",
    "context": {"last_query": "Show me risks"},
    "last_activity": "2026-02-04T10:00:00Z"
}
redis_client.setex(
    f"session:sess_abc123",
    timedelta(minutes=30),
    json.dumps(session_data)
)

# Obtener sesión
session = json.loads(redis_client.get("session:sess_abc123"))

# Rate limiting check
user_key = f"rate_limit:user_123:/api/query"
current_count = redis_client.incr(user_key)
if current_count == 1:
    redis_client.expire(user_key, 60)
if current_count > 60:  # Max 60 requests per minute
    raise RateLimitExceeded()
```

---

## 5. TimescaleDB - Métricas Time-Series

### 5.1 Tabla Principal: `security_events`

```sql
-- Crear hypertable para time-series
CREATE TABLE security_events (
    time TIMESTAMPTZ NOT NULL,
    
    -- Identificación del evento
    event_id UUID DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL, -- login_attempt, file_access, network_connection, api_call
    event_source VARCHAR(255) NOT NULL, -- firewall, ids, siem, application
    
    -- Actor
    user_id VARCHAR(255),
    user_name VARCHAR(255),
    user_role VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    
    -- Target
    target_type VARCHAR(100), -- asset, file, api_endpoint, database
    target_id VARCHAR(255),
    target_name VARCHAR(255),
    
    -- Acción
    action VARCHAR(100) NOT NULL, -- access, modify, delete, execute, deny
    action_result VARCHAR(50), -- success, failure, blocked
    
    -- Contexto
    severity VARCHAR(50), -- info, warning, high, critical
    risk_score INT,
    confidence DECIMAL(3,2), -- 0.00 to 1.00
    
    -- Detalles
    details JSONB DEFAULT '{}',
    
    -- Metadata
    tags TEXT[]
);

-- Convertir a hypertable
SELECT create_hypertable('security_events', 'time');

-- Crear índices
CREATE INDEX idx_security_events_type_time ON security_events (event_type, time DESC);
CREATE INDEX idx_security_events_user_time ON security_events (user_id, time DESC);
CREATE INDEX idx_security_events_severity_time ON security_events (severity, time DESC);
CREATE INDEX idx_security_events_result_time ON security_events (action_result, time DESC);

-- Retention policy: mantener 90 días
SELECT add_retention_policy('security_events', INTERVAL '90 days');
```

### 5.2 Continuous Aggregates (Vistas Materializadas)

```sql
-- Eventos por hora
CREATE MATERIALIZED VIEW security_events_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    event_type,
    severity,
    COUNT(*) as event_count,
    COUNT(*) FILTER (WHERE action_result = 'failure') as failure_count,
    COUNT(*) FILTER (WHERE action_result = 'success') as success_count
FROM security_events
GROUP BY bucket, event_type, severity;

-- Refresh policy
SELECT add_continuous_aggregate_policy('security_events_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

-- Eventos por día
CREATE MATERIALIZED VIEW security_events_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    event_type,
    COUNT(*) as event_count,
    AVG(risk_score) as avg_risk_score,
    MAX(risk_score) as max_risk_score,
    COUNT(DISTINCT user_id) as unique_users
FROM security_events
GROUP BY bucket, event_type;
```

### 5.3 Queries de Ejemplo

```sql
-- Intentos de login fallidos en las últimas 24 horas
SELECT
    time_bucket('1 hour', time) AS hour,
    COUNT(*) as failed_attempts,
    COUNT(DISTINCT ip_address) as unique_ips
FROM security_events
WHERE event_type = 'login_attempt'
  AND action_result = 'failure'
  AND time > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;

-- Top 10 usuarios con más eventos de riesgo alto
SELECT
    user_name,
    COUNT(*) as high_risk_events,
    AVG(risk_score) as avg_risk_score
FROM security_events
WHERE severity IN ('high', 'critical')
  AND time > NOW() - INTERVAL '7 days'
GROUP BY user_name
ORDER BY high_risk_events DESC
LIMIT 10;

-- Anomalías: usuarios con actividad inusual
WITH user_baseline AS (
    SELECT
        user_id,
        AVG(daily_events) as avg_daily_events,
        STDDEV(daily_events) as stddev_daily_events
    FROM (
        SELECT
            user_id,
            DATE_TRUNC('day', time) as day,
            COUNT(*) as daily_events
        FROM security_events
        WHERE time > NOW() - INTERVAL '30 days'
        GROUP BY user_id, day
    ) daily_counts
    GROUP BY user_id
)
SELECT
    e.user_id,
    COUNT(*) as events_today,
    b.avg_daily_events,
    (COUNT(*) - b.avg_daily_events) / b.stddev_daily_events as z_score
FROM security_events e
JOIN user_baseline b ON e.user_id = b.user_id
WHERE e.time > DATE_TRUNC('day', NOW())
GROUP BY e.user_id, b.avg_daily_events, b.stddev_daily_events
HAVING (COUNT(*) - b.avg_daily_events) / b.stddev_daily_events > 3  -- 3 sigma threshold
ORDER BY z_score DESC;
```

---

## 6. Estrategias de Backup y Disaster Recovery

### 6.1 PostgreSQL

**Backup Strategy**:
```bash
# Continuous archiving (WAL)
archive_mode = on
archive_command = 'test ! -f /backup/archive/%f && cp %p /backup/archive/%f'

# Daily full backup con pg_dump
0 2 * * * pg_dump -Fc ciso_digital > /backup/daily/ciso_$(date +\%Y\%m\%d).dump

# Incremental backup con pg_basebackup
0 */4 * * * pg_basebackup -D /backup/base -Ft -z -P
```

**Retention**:
- Daily backups: 30 días
- Weekly backups: 12 semanas
- Monthly backups: 12 meses

### 6.2 Qdrant

**Backup**:
```bash
# Snapshot API
curl -X POST 'http://localhost:6333/collections/security_knowledge/snapshots'

# Download snapshot
curl 'http://localhost:6333/collections/security_knowledge/snapshots/{snapshot-name}' \
  --output snapshot.dat
```

**Estrategia**:
- Snapshots diarios
- Sincronización a S3 con encryption
- Retention: 30 días

### 6.3 Redis

**Persistence**:
```
# RDB snapshots
save 900 1      # After 900 sec if at least 1 key changed
save 300 10     # After 300 sec if at least 10 keys changed
save 60 10000   # After 60 sec if at least 10000 keys changed

# AOF (Append Only File) para durabilidad
appendonly yes
appendfsync everysec
```

---

## Conclusión

Este diseño de bases de datos proporciona:

✅ **Separación de responsabilidades**: Cada BD optimizada para su caso de uso

✅ **Escalabilidad**: Sharding, replicación, y partitioning donde es necesario

✅ **Performance**: Índices optimizados, caching estratégico, y aggregates precalculados

✅ **Auditabilidad**: Tracking completo de cambios y acciones

✅ **Flexibilidad**: JSONB para datos variables, mantiene esquema estructurado

✅ **Disaster Recovery**: Backups automáticos y estrategias de recuperación

**Siguiente documento**: `03-agentes-ia.md` - Arquitectura y especificación de agentes
