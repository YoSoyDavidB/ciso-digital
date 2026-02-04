# 06 - ESTRUCTURA DE KNOWLEDGE BASE: CISO Digital

## 1. VISIÓN GENERAL

La Knowledge Base es el cerebro del CISO Digital. Contiene toda la información de seguridad, frameworks, políticas, procedimientos y lecciones aprendidas que el sistema usa para RAG (Retrieval Augmented Generation).

### 1.1 Almacenamiento

**Qdrant Vector Database:**
- Embeddings de documentos para búsqueda semántica
- Múltiples colecciones por tipo de contenido
- Metadata estructurada para filtros

**PostgreSQL:**
- Referencias a documentos originales
- Metadata estructurada adicional
- Relaciones entre documentos

## 2. COLECCIONES DE QDRANT

### 2.1 Collection: `security_knowledge`

**Propósito:** Documentación general de seguridad, políticas, procedimientos, best practices

**Schema:**
```python
{
    "vector": [1536 floats],  # OpenAI text-embedding-3-large
    "payload": {
        "document_id": "uuid",
        "document_type": "policy | procedure | guideline | best_practice",
        "title": "string",
        "content": "text",  # Chunk del documento
        "source": "string",  # Archivo original
        "framework": "iso27001 | nist_csf | cis | gdpr | custom",
        "control_ids": ["A.5.1", "A.8.2"],  # Controles relacionados
        "tags": ["access_control", "data_protection"],
        "language": "es | en",
        "version": "1.0",
        "author": "string",
        "approved_by": "string",
        "approval_date": "ISO datetime",
        "last_updated": "ISO datetime",
        "next_review_date": "ISO datetime",
        "review_frequency_days": 365,
        "status": "draft | active | deprecated",
        "classification": "public | internal | confidential",
        "chunk_index": 0,  # Para documentos largos divididos
        "total_chunks": 5,
        "relevance_score": 0.95  # Calculado por uso
    }
}
```

**Tamaño Estimado:** 5,000-10,000 documentos

### 2.2 Collection: `incident_memory`

**Propósito:** Histórico de incidentes para aprender de experiencias pasadas

**Schema:**
```python
{
    "vector": [1536 floats],
    "payload": {
        "incident_id": "uuid",
        "incident_number": "INC-2026-001",
        "title": "string",
        "description": "text",  # Descripción del incidente
        "incident_type": "malware | ddos | data_breach | unauthorized_access",
        "severity": "critical | high | medium | low",
        "affected_systems": ["web-server-1", "database-prod"],
        "detection_method": "SIEM | user_report | automated_scan",
        "detection_time": "ISO datetime",
        "response_time": "ISO datetime",
        "resolution_time": "ISO datetime",
        "mttr_minutes": 120,  # Mean Time To Resolve
        "actions_taken": [
            {
                "action": "Blocked malicious IPs",
                "timestamp": "ISO datetime",
                "actor": "automated | john_doe"
            }
        ],
        "playbook_used": "ddos-response-v1",
        "lessons_learned": "text",
        "recommendations": ["Implement rate limiting"],
        "cost_impact": 5000.00,
        "tags": ["ddos", "web_attack"],
        "false_positive": false
    }
}
```

**Tamaño Estimado:** 500-2,000 incidentes

### 2.3 Collection: `conversation_context`

**Propósito:** Memoria conversacional para mantener contexto entre sesiones

**Schema:**
```python
{
    "vector": [1536 floats],
    "payload": {
        "conversation_id": "uuid",
        "session_id": "uuid",
        "user_id": "uuid",
        "message_id": "uuid",
        "role": "user | assistant",
        "content": "text",
        "intent": "risk_assessment | compliance_check | general_query",
        "entities_extracted": {
            "assets": ["web-server-1"],
            "risks": ["RISK-2026-001"],
            "frameworks": ["iso27001"]
        },
        "agent_used": "risk_assessment | incident_response",
        "confidence": 0.95,
        "timestamp": "ISO datetime",
        "context_summary": "text",  # Resumen del contexto hasta este punto
        "decisions_made": [
            "User decided to accept risk RISK-2026-045"
        ],
        "action_items": [
            {
                "action": "Update firewall rules",
                "deadline": "2026-02-10",
                "status": "pending"
            }
        ]
    }
}
```

**Tamaño Estimado:** 10,000-100,000 mensajes

### 2.4 Collection: `threat_intelligence`

**Propósito:** IOCs, TTPs, threat reports de fuentes externas

**Schema:**
```python
{
    "vector": [1536 floats],
    "payload": {
        "ioc_id": "uuid",
        "ioc_type": "ip | domain | hash | url | email",
        "ioc_value": "192.168.1.1 | malicious.com | hash...",
        "threat_type": "malware | phishing | ransomware | apt",
        "threat_actor": "APT28 | Unknown",
        "campaign_name": "Operation XYZ",
        "first_seen": "ISO datetime",
        "last_seen": "ISO datetime",
        "confidence": 0.85,  # Confidence in the threat intelligence
        "source": "alienvault_otx | misp | custom_feed",
        "source_reliability": 0.9,
        "description": "text",
        "ttps": ["T1566.001", "T1059.001"],  # MITRE ATT&CK
        "tags": ["banking_trojan", "europe"],
        "related_iocs": ["other-ioc-id"],
        "false_positive_rate": 0.02,
        "applicable_to_organization": true  # Relevancia para nuestra org
    }
}
```

**Tamaño Estimado:** 50,000-500,000 IOCs

## 3. ESTRUCTURA DE DIRECTORIOS (Fuente)

```
knowledge-base/
│
├── security-policies/
│   ├── information-security-policy-v2.0.pdf
│   ├── acceptable-use-policy-v1.5.pdf
│   ├── incident-response-policy-v1.2.pdf
│   ├── data-classification-policy-v1.0.pdf
│   ├── access-control-policy-v2.1.pdf
│   └── backup-policy-v1.3.pdf
│
├── procedures/
│   ├── incident-response/
│   │   ├── incident-classification-procedure.md
│   │   ├── malware-response-playbook.md
│   │   ├── data-breach-response-playbook.md
│   │   └── ddos-response-playbook.md
│   │
│   ├── access-management/
│   │   ├── user-provisioning-procedure.md
│   │   ├── access-review-procedure.md
│   │   └── privileged-access-management.md
│   │
│   └── business-continuity/
│       ├── backup-restore-procedure.md
│       ├── disaster-recovery-plan.md
│       └── business-continuity-plan.pdf
│
├── frameworks/
│   ├── iso27001/
│   │   ├── annex-a-controls.json
│   │   ├── control-a.5.1-policy.md
│   │   ├── control-a.8.2-classification.md
│   │   └── gap-analysis-template.xlsx
│   │
│   ├── nist-csf/
│   │   ├── framework-core.json
│   │   ├── identify-functions.md
│   │   ├── protect-functions.md
│   │   └── implementation-guidance.md
│   │
│   ├── cis-controls/
│   │   ├── cis-controls-v8.json
│   │   └── implementation-groups.md
│   │
│   └── gdpr/
│       ├── articles-summary.md
│       ├── data-protection-measures.md
│       └── privacy-by-design.md
│
├── threat-intelligence/
│   ├── industry-reports/
│   │   ├── verizon-dbir-2025.pdf
│   │   ├── mandiant-apt-trends-2025.pdf
│   │   └── owasp-top-10-2025.md
│   │
│   ├── iocs/
│   │   ├── malware-hashes.csv
│   │   ├── malicious-domains.txt
│   │   └── phishing-indicators.json
│   │
│   └── ttps/
│       ├── mitre-attck-mappings.json
│       └── common-attack-patterns.md
│
├── best-practices/
│   ├── secure-coding/
│   │   ├── owasp-secure-coding-practices.md
│   │   ├── input-validation.md
│   │   └── authentication-best-practices.md
│   │
│   ├── infrastructure/
│   │   ├── server-hardening-guide.md
│   │   ├── network-segmentation.md
│   │   └── cloud-security-aws.md
│   │
│   └── operational/
│       ├── security-monitoring.md
│       ├── log-management.md
│       └── vulnerability-management.md
│
├── training/
│   ├── security-awareness/
│   │   ├── phishing-awareness.md
│   │   ├── password-best-practices.md
│   │   └── social-engineering.md
│   │
│   └── technical/
│       ├── secure-development-training.pdf
│       └── incident-response-training.pdf
│
└── templates/
    ├── risk-assessment-template.xlsx
    ├── incident-report-template.docx
    ├── security-review-checklist.md
    └── policy-template.docx
```

## 4. PROCESO DE INGESTA DE DOCUMENTOS

### 4.1 Pipeline de Ingesta

```python
async def ingest_document(file_path: str):
    """
    Pipeline completo de ingesta de documento
    """
    
    # 1. Extraer texto según tipo de archivo
    text = await extract_text(file_path)
    
    # 2. Extraer metadata del documento
    metadata = await extract_metadata(file_path)
    
    # 3. Dividir en chunks (si es muy largo)
    chunks = await chunk_document(
        text=text,
        chunk_size=1000,  # tokens
        overlap=200  # overlap entre chunks
    )
    
    # 4. Para cada chunk
    for i, chunk in enumerate(chunks):
        
        # 4.1 Generar embedding
        embedding = await embedding_service.embed(chunk)
        
        # 4.2 Preparar payload
        payload = {
            **metadata,
            "content": chunk,
            "chunk_index": i,
            "total_chunks": len(chunks)
        }
        
        # 4.3 Guardar en Qdrant
        await qdrant_client.upsert(
            collection_name="security_knowledge",
            points=[{
                "id": str(uuid4()),
                "vector": embedding,
                "payload": payload
            }]
        )
        
        # 4.4 Guardar referencia en PostgreSQL
        await db.execute("""
            INSERT INTO documents (id, filename, metadata)
            VALUES ($1, $2, $3)
        """, str(uuid4()), file_path, metadata)
    
    logger.info(f"Document {file_path} ingested successfully")
```

### 4.2 Extracción de Texto por Tipo

```python
async def extract_text(file_path: str) -> str:
    """Extrae texto según el tipo de archivo"""
    
    ext = Path(file_path).suffix.lower()
    
    if ext == ".pdf":
        return await extract_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return await extract_docx(file_path)
    elif ext == ".md":
        return await extract_markdown(file_path)
    elif ext in [".txt", ".log"]:
        return await extract_text_file(file_path)
    elif ext in [".json", ".yaml"]:
        return await extract_structured(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
```

### 4.3 Estrategia de Chunking

```python
async def chunk_document(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200
) -> List[str]:
    """
    Divide documento en chunks con overlap
    
    Estrategias:
    1. Semantic chunking - dividir por párrafos/secciones
    2. Fixed size chunking - tamaño fijo con overlap
    3. Hybrid - combinar ambas
    """
    
    # Estrategia semántica preferida
    chunks = []
    
    # 1. Dividir por headers/secciones primero
    sections = split_by_markdown_headers(text)
    
    for section in sections:
        # 2. Si la sección es muy larga, subdivide
        if len(section) > chunk_size * 4:  # 4 tokens ≈ 1 char
            sub_chunks = fixed_size_chunk(
                section,
                size=chunk_size,
                overlap=overlap
            )
            chunks.extend(sub_chunks)
        else:
            chunks.append(section)
    
    return chunks
```

## 5. DOCUMENTACIÓN EXISTENTE (User-Provided)

David ya tiene:
1. **Business Continuity Plan** - Ingesting ahora
2. **Política de Seguridad de la Información** - Ingesting ahora

### 5.1 Script de Ingesta Inicial

```bash
#!/bin/bash
# ingest-existing-docs.sh

# Ingestar documentación existente de David

python scripts/ingest_document.py \
  --file "/path/to/business-continuity-plan.pdf" \
  --type "procedure" \
  --framework "iso27001" \
  --controls "A.17.1.1,A.17.1.2" \
  --classification "confidential"

python scripts/ingest_document.py \
  --file "/path/to/politica-seguridad-informacion.pdf" \
  --type "policy" \
  --framework "iso27001" \
  --controls "A.5.1.1,A.5.1.2" \
  --classification "internal"

echo "Initial documents ingested successfully"
```

## 6. DOCUMENTACIÓN A CREAR PROACTIVAMENTE

El CISO Digital debe identificar qué documentación falta y proponerla.

### 6.1 Documentos Críticos ISO 27001

```python
REQUIRED_ISO27001_DOCUMENTS = {
    "A.5.1": {
        "document": "Information Security Policy",
        "priority": "critical",
        "template": "policy-template.docx"
    },
    "A.6.1": {
        "document": "Roles and Responsibilities",
        "priority": "high",
        "template": "roles-template.docx"
    },
    "A.8.1": {
        "document": "Asset Inventory",
        "priority": "critical",
        "template": "asset-inventory-template.xlsx"
    },
    "A.8.2": {
        "document": "Data Classification Policy",
        "priority": "high",
        "template": "classification-template.docx"
    },
    "A.9.2": {
        "document": "User Access Management Procedure",
        "priority": "high"
    },
    # ... más controles
}
```

### 6.2 Detección Automática de Gaps

```python
async def detect_documentation_gaps():
    """
    Detecta documentación faltante automáticamente
    """
    
    gaps = []
    
    # 1. Obtener frameworks aplicables
    frameworks = await get_applicable_frameworks()
    
    for framework in frameworks:
        # 2. Obtener documentos requeridos
        required_docs = get_required_documents(framework)
        
        # 3. Obtener documentos actuales
        current_docs = await qdrant_client.scroll(
            collection_name="security_knowledge",
            scroll_filter={
                "must": [
                    {"key": "framework", "match": {"value": framework}}
                ]
            }
        )
        
        # 4. Identificar missing
        for req_doc in required_docs:
            if not document_exists(req_doc, current_docs):
                gaps.append({
                    "framework": framework,
                    "missing_document": req_doc,
                    "priority": req_doc["priority"],
                    "control_id": req_doc["control"],
                    "template_available": req_doc.get("template")
                })
    
    return gaps
```

## 7. MANTENIMIENTO Y ACTUALIZACIÓN

### 7.1 Review Automático de Documentos

```python
async def review_documents_schedule():
    """
    Revisa documentos según su review_frequency
    """
    
    # Obtener documentos que necesitan review
    docs_to_review = await qdrant_client.scroll(
        collection_name="security_knowledge",
        scroll_filter={
            "must": [
                {
                    "key": "next_review_date",
                    "range": {
                        "lte": datetime.now().isoformat()
                    }
                }
            ]
        }
    )
    
    for doc in docs_to_review:
        # Notificar owner
        await notify_document_review(
            document=doc,
            owner=doc.payload["author"],
            message=f"Document '{doc.payload['title']}' is due for review"
        )
        
        # Crear task en project management
        await create_review_task(doc)
```

### 7.2 Versionado de Documentos

```python
# Cuando se actualiza un documento:

async def update_document(document_id: str, new_content: str):
    """
    Actualiza documento manteniendo histórico
    """
    
    # 1. Obtener versión actual
    current = await get_document(document_id)
    
    # 2. Archivar versión actual
    await archive_version(
        document_id=document_id,
        version=current.version,
        content=current.content,
        timestamp=datetime.now()
    )
    
    # 3. Incrementar versión
    new_version = increment_version(current.version)
    
    # 4. Actualizar en Qdrant
    new_embedding = await embedding_service.embed(new_content)
    
    await qdrant_client.upsert(
        collection_name="security_knowledge",
        points=[{
            "id": document_id,
            "vector": new_embedding,
            "payload": {
                **current.payload,
                "content": new_content,
                "version": new_version,
                "last_updated": datetime.now().isoformat()
            }
        }]
    )
```

## 8. BÚSQUEDA Y RETRIEVAL

### 8.1 Búsqueda Semántica Básica

```python
async def semantic_search(
    query: str,
    collection: str = "security_knowledge",
    top_k: int = 5,
    filters: Optional[Dict] = None
) -> List[Document]:
    """
    Búsqueda semántica en knowledge base
    """
    
    # 1. Generar embedding del query
    query_vector = await embedding_service.embed(query)
    
    # 2. Construir filtros
    query_filter = None
    if filters:
        query_filter = build_qdrant_filter(filters)
    
    # 3. Buscar en Qdrant
    results = await qdrant_client.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=top_k,
        query_filter=query_filter
    )
    
    # 4. Convertir a documentos
    documents = [
        Document(
            content=r.payload["content"],
            metadata=r.payload,
            score=r.score
        )
        for r in results
    ]
    
    return documents
```

### 8.2 Búsqueda Híbrida (Vector + Keyword)

```python
async def hybrid_search(
    query: str,
    keywords: List[str],
    top_k: int = 5
) -> List[Document]:
    """
    Combina búsqueda semántica con keywords
    """
    
    # 1. Búsqueda vectorial
    vector_results = await semantic_search(query, top_k=top_k*2)
    
    # 2. Búsqueda por keywords en payload
    keyword_results = await qdrant_client.scroll(
        collection_name="security_knowledge",
        scroll_filter={
            "should": [
                {"key": "tags", "match": {"any": keywords}},
                {"key": "control_ids", "match": {"any": keywords}}
            ]
        },
        limit=top_k*2
    )
    
    # 3. Combinar y re-rankear
    all_results = merge_and_rerank(vector_results, keyword_results)
    
    return all_results[:top_k]
```

## 9. MÉTRICAS DE KNOWLEDGE BASE

```python
# Métricas a trackear:

knowledge_base_metrics = {
    "total_documents": 5247,
    "by_type": {
        "policy": 15,
        "procedure": 42,
        "guideline": 68,
        "best_practice": 134
    },
    "by_framework": {
        "iso27001": 892,
        "nist_csf": 456,
        "custom": 234
    },
    "languages": {
        "es": 3456,
        "en": 1791
    },
    "status": {
        "active": 4980,
        "draft": 145,
        "deprecated": 122
    },
    "needs_review": 23,
    "overdue_reviews": 5,
    "avg_chunk_size": 950,  # tokens
    "avg_relevance_score": 0.87,
    "last_ingestion": "2026-02-04T08:00:00Z",
    "storage_size_gb": 2.3
}
```

---

**Versión:** 1.0  
**Última Actualización:** Febrero 2026  
**Próximo Documento:** [08-IMPLEMENTATION-ROADMAP.md](08-IMPLEMENTATION-ROADMAP.md)
