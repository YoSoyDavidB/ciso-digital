# Prompt Engineering Guide for CISO Digital

## 📋 Table of Contents

1. [Overview](#overview)
2. [General Principles](#general-principles)
3. [Prompt Structure Template](#prompt-structure-template)
4. [Common Variables](#common-variables)
5. [Few-Shot Learning Examples](#few-shot-learning-examples)
6. [RAG Context Integration](#rag-context-integration)
7. [Structured Output (JSON)](#structured-output-json)
8. [Temperature & Model Settings](#temperature--model-settings)
9. [Token Budget Management](#token-budget-management)
10. [Agent-Specific Examples](#agent-specific-examples)
11. [Best Practices](#best-practices)
12. [Common Pitfalls](#common-pitfalls)

---

## 🎯 Overview

This document provides comprehensive guidelines for crafting effective prompts for the CISO Digital AI agents. Following these patterns ensures:

- **Consistency**: All agents follow similar patterns
- **Reliability**: Prompts produce predictable outputs
- **Maintainability**: Easy to update and improve
- **Performance**: Optimal token usage and response quality

**Supported Models:**
- Primary: Claude Sonnet 4.5 (via GitHub Copilot SDK)
- Fallback: GPT-4 Turbo (Azure OpenAI)
- Embeddings: text-embedding-3-small (Azure OpenAI)

---

## 🔑 General Principles

### 1. **Be Specific and Clear**
✅ **Good**: "Analyze this vulnerability and rate its severity from 1-10 based on CVSS metrics"
❌ **Bad**: "What do you think about this vulnerability?"

### 2. **Provide Context**
Always include relevant context about:
- The user's role and organization
- The specific asset or system being analyzed
- Historical context or related incidents
- Relevant policies or compliance requirements

### 3. **Use Structured Format**
```
Role: [Who the AI should act as]
Task: [What needs to be done]
Context: [Background information]
Constraints: [Limitations or requirements]
Output Format: [How to structure the response]
```

### 4. **Request JSON When Possible**
Structured output is easier to parse and validate:
```json
{
  "analysis": "...",
  "severity": "high",
  "confidence": 0.85,
  "recommendations": [...]
}
```

### 5. **Iterative Refinement**
Start simple, then add:
- Examples (few-shot learning)
- Edge cases
- Error handling
- Validation criteria

---

## 📝 Prompt Structure Template

```python
SYSTEM_PROMPT = """
# Role
You are a [ROLE] for a [ORGANIZATION_TYPE] organization.

# Capabilities
- [CAPABILITY_1]
- [CAPABILITY_2]
- [CAPABILITY_3]

# Your Task
[DETAILED_TASK_DESCRIPTION]

# Context
[BACKGROUND_INFORMATION]

# Guidelines
1. [GUIDELINE_1]
2. [GUIDELINE_2]
3. [GUIDELINE_3]

# Output Format
Return your response as a JSON object with the following structure:
```json
{
  "field1": "type",
  "field2": "type",
  "field3": ["array", "of", "items"]
}
```

# Important Notes
- [NOTE_1]
- [NOTE_2]
- [NOTE_3]
"""

USER_PROMPT = """
# Request
[SPECIFIC_REQUEST]

# Input Data
[STRUCTURED_INPUT_DATA]

# Additional Context
[RAG_DOCUMENTS_OR_RELATED_INFO]

# Question
[EXPLICIT_QUESTION_TO_ANSWER]
"""
```

---

## 🔧 Common Variables

### Asset Information
```python
{
  "asset_id": "string",
  "asset_name": "string",
  "asset_type": "server | application | database | network_device",
  "criticality": "critical | high | medium | low",
  "business_unit": "string",
  "environment": "production | staging | development"
}
```

### Vulnerability Data
```python
{
  "cve_id": "CVE-YYYY-NNNNN",
  "cvss_score": float,  # 0.0-10.0
  "cvss_vector": "string",
  "description": "string",
  "affected_versions": ["string"],
  "exploit_available": boolean,
  "patch_available": boolean
}
```

### Incident Context
```python
{
  "incident_id": "string",
  "detection_time": "ISO8601 datetime",
  "severity": "critical | high | medium | low | informational",
  "status": "new | investigating | contained | resolved",
  "affected_assets": ["asset_id"],
  "indicators": ["string"]
}
```

### User Context
```python
{
  "user_email": "string",
  "role": "ciso | security_analyst | compliance_officer | engineer",
  "permissions": ["string"],
  "preferences": {
    "detail_level": "summary | detailed | technical",
    "language": "en | es"
  }
}
```

---

## 📚 Few-Shot Learning Examples

Few-shot learning dramatically improves response quality and consistency.

### Example 1: Vulnerability Severity Assessment

```python
FEW_SHOT_EXAMPLES = """
# Example 1: Critical Vulnerability
Input:
- CVE: CVE-2021-44228 (Log4Shell)
- CVSS: 10.0
- Asset: Production API Server
- Exploit Available: Yes
- Patch Available: Yes

Expected Output:
```json
{
  "severity": "critical",
  "risk_score": 10.0,
  "urgency": "immediate",
  "reasoning": "Remote code execution vulnerability with active exploitation in the wild. Affects critical production asset with public exposure.",
  "recommendations": [
    "Apply emergency patch immediately",
    "Isolate affected systems until patched",
    "Review logs for signs of exploitation",
    "Implement WAF rules as temporary mitigation"
  ],
  "confidence": 0.98
}
```

# Example 2: Medium Vulnerability
Input:
- CVE: CVE-2023-12345
- CVSS: 6.5
- Asset: Internal Dev Server
- Exploit Available: No
- Patch Available: Yes

Expected Output:
```json
{
  "severity": "medium",
  "risk_score": 5.2,
  "urgency": "high",
  "reasoning": "Moderate CVSS score but affects low-criticality asset in non-production environment. No known exploits.",
  "recommendations": [
    "Schedule patch during next maintenance window",
    "Monitor for exploit development",
    "Consider network segmentation"
  ],
  "confidence": 0.85
}
```

# Example 3: Low Vulnerability
Input:
- CVE: CVE-2023-67890
- CVSS: 3.1
- Asset: Isolated Test Environment
- Exploit Available: No
- Patch Available: Yes

Expected Output:
```json
{
  "severity": "low",
  "risk_score": 2.1,
  "urgency": "low",
  "reasoning": "Low CVSS score, isolated environment, no known exploits. Minimal business impact.",
  "recommendations": [
    "Include in regular patching cycle",
    "Document for compliance purposes",
    "No urgent action required"
  ],
  "confidence": 0.92
}
```
"""
```

### Example 2: Incident Classification

```python
INCIDENT_CLASSIFICATION_EXAMPLES = """
# Example 1: Malware Detected
Input: "Multiple antivirus alerts on workstation WS-1234. Suspicious file 'invoice.exe' blocked."

Output:
```json
{
  "incident_type": "malware",
  "sub_type": "trojan",
  "severity": "high",
  "indicators": ["invoice.exe", "WS-1234"],
  "recommended_actions": [
    "Isolate workstation WS-1234 from network",
    "Run full system scan",
    "Analyze invoice.exe in sandbox",
    "Check for lateral movement"
  ],
  "confidence": 0.88
}
```

# Example 2: Failed Login Attempts
Input: "500+ failed SSH login attempts from 185.220.101.45 targeting server PROD-WEB-01"

Output:
```json
{
  "incident_type": "unauthorized_access_attempt",
  "sub_type": "brute_force",
  "severity": "medium",
  "indicators": ["185.220.101.45", "PROD-WEB-01", "SSH"],
  "recommended_actions": [
    "Block IP 185.220.101.45 at firewall",
    "Enable rate limiting on SSH",
    "Review SSH access logs",
    "Consider implementing 2FA"
  ],
  "confidence": 0.95
}
```
"""
```

---

## 🔍 RAG Context Integration

RAG (Retrieval-Augmented Generation) enhances prompts with relevant documentation.

### Pattern 1: Knowledge Base Context

```python
def build_prompt_with_rag(query: str, rag_documents: list[dict]) -> str:
    """
    Integrates RAG documents into prompt.
    
    Args:
        query: User's question
        rag_documents: Retrieved documents from vector store
    
    Returns:
        Enhanced prompt with context
    """
    context_section = "# Relevant Documentation\\n\\n"
    
    for i, doc in enumerate(rag_documents, 1):
        context_section += f"## Document {i}: {doc['title']}\\n"
        context_section += f"Source: {doc['source']}\\n"
        context_section += f"Content: {doc['content'][:500]}...\\n"
        context_section += f"Relevance Score: {doc['score']:.2f}\\n\\n"
    
    prompt = f"""
# Context from Knowledge Base
{context_section}

# User Question
{query}

# Instructions
Based on the documentation provided above, answer the user's question.
If the documentation doesn't contain enough information, clearly state this.
Always cite the source document numbers (e.g., "According to Document 1...").
"""
    return prompt
```

### Pattern 2: Policy-Aware Responses

```python
POLICY_AWARE_PROMPT = """
# Your Role
You are a security compliance assistant with access to organizational policies.

# Available Policies (from RAG)
{rag_policies}

# Task
Analyze the following security event and determine if it violates any policies:

Event: {event_description}

# Output Format
```json
{
  "policy_violations": [
    {
      "policy_name": "string",
      "policy_section": "string",
      "violation_description": "string",
      "severity": "critical | high | medium | low"
    }
  ],
  "compliant": boolean,
  "recommended_remediation": ["string"]
}
```

# Guidelines
- Reference specific policy sections
- Explain WHY something is a violation
- Provide actionable remediation steps
- Consider organizational context
"""
```

### Pattern 3: Historical Context

```python
HISTORICAL_CONTEXT_PROMPT = """
# Similar Past Incidents (from RAG)
{rag_similar_incidents}

# Current Incident
{current_incident}

# Task
Compare the current incident with similar past incidents and provide:
1. What worked well in past resolutions
2. What should be avoided based on past mistakes
3. Estimated time to resolution based on historical data
4. Resource requirements based on similar incidents

# Output Format
```json
{
  "similarity_score": float,
  "similar_incidents": ["incident_id"],
  "lessons_learned": ["string"],
  "estimated_resolution_time_hours": int,
  "recommended_approach": "string",
  "confidence": float
}
```
"""
```

---

## 📊 Structured Output (JSON)

### JSON Schema Validation

Always provide a clear JSON schema:

```python
RISK_ASSESSMENT_SCHEMA = """
# Output JSON Schema
```json
{
  "type": "object",
  "required": ["risk_score", "severity", "recommendations", "confidence"],
  "properties": {
    "risk_score": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 10.0,
      "description": "Calculated risk score"
    },
    "severity": {
      "type": "string",
      "enum": ["critical", "high", "medium", "low", "informational"]
    },
    "recommendations": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    },
    "reasoning": {
      "type": "string",
      "description": "Explanation of the assessment"
    },
    "affected_assets": {
      "type": "array",
      "items": {"type": "string"}
    },
    "estimated_impact": {
      "type": "string",
      "enum": ["catastrophic", "major", "moderate", "minor", "negligible"]
    }
  }
}
```

# Important
- Return ONLY valid JSON
- Do not include markdown code blocks
- Ensure all required fields are present
- Use null for optional fields if no data available
"""
```

### Parsing JSON Responses

```python
import json
from typing import Optional

def extract_json_from_response(response: str) -> Optional[dict]:
    """
    Safely extract JSON from LLM response.
    
    Handles:
    - Plain JSON
    - JSON in markdown code blocks
    - Malformed JSON with helpful error messages
    """
    # Remove markdown code blocks if present
    if "```json" in response:
        response = response.split("```json")[1].split("```")[0]
    elif "```" in response:
        response = response.split("```")[1].split("```")[0]
    
    # Try to parse
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        logger.debug(f"Response was: {response}")
        return None
```

---

## 🌡️ Temperature & Model Settings

### Temperature Guidelines

```python
# Factual, deterministic tasks (risk calculation, compliance checking)
TEMPERATURE_FACTUAL = 0.0  # Most deterministic

# Analytical tasks (threat analysis, incident investigation)
TEMPERATURE_ANALYTICAL = 0.3  # Slightly creative but mostly factual

# Creative tasks (security awareness content, phishing simulations)
TEMPERATURE_CREATIVE = 0.7  # More varied outputs

# Brainstorming tasks (threat modeling, red team scenarios)
TEMPERATURE_BRAINSTORMING = 0.9  # Maximum creativity
```

### Model-Specific Settings

```python
# Claude Sonnet 4.5 (Primary - via GitHub Copilot SDK)
CLAUDE_SETTINGS = {
    "model": "claude-sonnet-4.5",
    "max_tokens": 4096,
    "temperature": 0.3,  # Default for most tasks
    "top_p": 1.0,
    "stop_sequences": ["\\n\\nHuman:", "\\n\\nAssistant:"],
}

# GPT-4 Turbo (Fallback - Azure OpenAI)
GPT4_SETTINGS = {
    "model": "gpt-4-turbo",
    "max_tokens": 4096,
    "temperature": 0.3,
    "top_p": 0.95,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
}
```

### Task-Specific Configurations

```python
TASK_CONFIGS = {
    "risk_assessment": {
        "temperature": 0.2,
        "max_tokens": 2048,
        "rationale": "Need consistent, factual risk scoring"
    },
    "incident_classification": {
        "temperature": 0.1,
        "max_tokens": 1024,
        "rationale": "Deterministic classification critical for playbooks"
    },
    "compliance_checking": {
        "temperature": 0.0,
        "max_tokens": 3072,
        "rationale": "Binary compliance decisions, no creativity needed"
    },
    "threat_intel_summary": {
        "temperature": 0.4,
        "max_tokens": 2048,
        "rationale": "Analytical but allow some synthesis of information"
    },
    "security_recommendations": {
        "temperature": 0.5,
        "max_tokens": 3072,
        "rationale": "Creative solutions but grounded in best practices"
    },
    "phishing_simulation": {
        "temperature": 0.8,
        "max_tokens": 1024,
        "rationale": "Need varied, realistic phishing scenarios"
    }
}
```

---

## 💰 Token Budget Management

### Token Estimation

```python
def estimate_tokens(text: str) -> int:
    """
    Rough estimation: 1 token ≈ 4 characters
    More accurate: use tiktoken library
    """
    return len(text) // 4

# Example
prompt = "Analyze this vulnerability..."
estimated_tokens = estimate_tokens(prompt)
print(f"Estimated tokens: {estimated_tokens}")
```

### Token Budgets by Task

```python
TOKEN_BUDGETS = {
    # Input (Prompt) budgets
    "simple_query": {
        "input_max": 500,
        "output_max": 1000,
        "total_max": 1500
    },
    "risk_assessment": {
        "input_max": 2000,   # Asset data + vulnerabilities + RAG context
        "output_max": 2000,  # Detailed analysis + recommendations
        "total_max": 4000
    },
    "incident_response": {
        "input_max": 3000,   # Incident data + logs + historical context
        "output_max": 3000,  # Analysis + playbook steps
        "total_max": 6000
    },
    "compliance_report": {
        "input_max": 4000,   # Controls + evidence + policies
        "output_max": 4000,  # Detailed report
        "total_max": 8000
    },
    "threat_intelligence": {
        "input_max": 5000,   # Multiple threat feeds + context
        "output_max": 3000,  # Summary + recommendations
        "total_max": 8000
    }
}
```

### Cost Optimization Strategies

```python
# Strategy 1: Truncate RAG Context
def truncate_rag_context(documents: list[dict], max_tokens: int = 1000) -> list[dict]:
    """
    Keep only most relevant RAG documents within token budget.
    """
    current_tokens = 0
    truncated = []
    
    for doc in sorted(documents, key=lambda x: x['score'], reverse=True):
        doc_tokens = estimate_tokens(doc['content'])
        if current_tokens + doc_tokens > max_tokens:
            break
        truncated.append(doc)
        current_tokens += doc_tokens
    
    return truncated

# Strategy 2: Summarize Long Context
async def summarize_if_needed(text: str, max_tokens: int = 500) -> str:
    """
    Summarize text if it exceeds token budget.
    """
    if estimate_tokens(text) <= max_tokens:
        return text
    
    # Use cheaper model to summarize
    summary = await llm_service.summarize(text, max_length=max_tokens)
    return summary

# Strategy 3: Progressive Detail
def format_with_progressive_detail(data: dict, detail_level: str = "summary") -> str:
    """
    Include more/less detail based on user preference.
    """
    if detail_level == "summary":
        return format_summary(data)  # ~200 tokens
    elif detail_level == "detailed":
        return format_detailed(data)  # ~1000 tokens
    else:  # technical
        return format_technical(data)  # ~3000 tokens
```

### Real-Time Token Tracking

```python
from app.core.logging import log_llm_call

async def track_token_usage(
    agent_name: str,
    prompt_tokens: int,
    completion_tokens: int,
    model: str
):
    """
    Track token usage for cost analysis and optimization.
    """
    total_tokens = prompt_tokens + completion_tokens
    
    # Log for monitoring
    log_llm_call(
        agent_name=agent_name,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=0,  # Set actual latency
        success=True
    )
    
    # Calculate cost (example rates)
    COST_PER_1K_TOKENS = {
        "claude-sonnet-4.5": {"input": 0.003, "output": 0.015},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    }
    
    rates = COST_PER_1K_TOKENS.get(model, {"input": 0, "output": 0})
    cost = (prompt_tokens / 1000 * rates["input"]) + (completion_tokens / 1000 * rates["output"])
    
    logger.info(f"LLM call cost: ${cost:.4f}, Total tokens: {total_tokens}")
```

---

## 🤖 Agent-Specific Examples

### 1. Risk Assessment Agent

```python
RISK_ASSESSMENT_SYSTEM_PROMPT = """
# Role
You are an expert cybersecurity risk analyst for enterprise security operations.

# Your Expertise
- CVSS scoring and vulnerability analysis
- Asset criticality assessment
- Business impact evaluation
- Risk quantification methodologies (FAIR, OCTAVE)
- Threat landscape awareness

# Task
Assess security risks by analyzing:
1. Asset criticality and business value
2. Vulnerability severity (CVSS scores)
3. Exploit availability and threat intelligence
4. Existing security controls
5. Potential business impact

# Risk Scoring Formula
risk_score = (cvss_score * asset_criticality_multiplier * threat_multiplier) / controls_effectiveness

Where:
- cvss_score: 0.0-10.0 (from vulnerability data)
- asset_criticality_multiplier: critical=1.5, high=1.2, medium=1.0, low=0.7
- threat_multiplier: exploit_available=1.5, proof_of_concept=1.2, none=1.0
- controls_effectiveness: 0.0-1.0 (reduce risk based on existing controls)

# Output Format
```json
{
  "risk_score": float,  // 0.0-10.0
  "severity": "critical" | "high" | "medium" | "low",
  "reasoning": "string",  // 2-3 sentences explaining the score
  "affected_assets": ["asset_id"],
  "recommendations": ["string"],  // Prioritized list
  "estimated_impact": "catastrophic" | "major" | "moderate" | "minor",
  "confidence": float,  // 0.0-1.0
  "references": ["string"]  // CVEs, CWEs, or documentation
}
```

# Guidelines
1. Be conservative - err on the side of higher risk scores for production systems
2. Consider cascading effects (e.g., compromised DB affects all dependent apps)
3. Factor in compliance requirements (PCI-DSS, HIPAA, SOC2)
4. Provide actionable, prioritized recommendations
5. Explain your reasoning clearly for audit purposes
"""

RISK_ASSESSMENT_USER_PROMPT_TEMPLATE = """
# Risk Assessment Request

## Asset Information
- ID: {asset_id}
- Name: {asset_name}
- Type: {asset_type}
- Criticality: {asset_criticality}
- Environment: {environment}
- Business Unit: {business_unit}

## Vulnerabilities Detected
{vulnerabilities_list}

## Existing Security Controls
{security_controls}

## Threat Intelligence Context
{threat_intel_summary}

## Related Documentation (RAG)
{rag_documents}

## Question
Assess the overall security risk for this asset given the vulnerabilities and context above.
Focus on immediate threats and provide prioritized remediation steps.
"""

# Example Usage
user_prompt = RISK_ASSESSMENT_USER_PROMPT_TEMPLATE.format(
    asset_id="PROD-DB-001",
    asset_name="Customer Database - Primary",
    asset_type="database",
    asset_criticality="critical",
    environment="production",
    business_unit="Customer Services",
    vulnerabilities_list="""
    1. CVE-2023-12345 (CVSS: 9.8)
       - Description: SQL injection in query parser
       - Exploit Available: Yes (Metasploit module)
       - Patch Available: Yes (v2.4.1)
    
    2. CVE-2023-67890 (CVSS: 7.5)
       - Description: Weak encryption in data at rest
       - Exploit Available: No
       - Patch Available: No (configuration change required)
    """,
    security_controls="""
    - Firewall rules: Restricted to application subnet only
    - IDS/IPS: Enabled with signature updates
    - Access controls: Database-level RBAC implemented
    - Backup: Daily automated backups to encrypted storage
    - Monitoring: Real-time query logging enabled
    - Missing: Web Application Firewall, DDoS protection
    """,
    threat_intel_summary="""
    - CVE-2023-12345 actively exploited in the wild (CISA KEV list)
    - Ransomware groups targeting databases with this vulnerability
    - Average time to exploitation: 72 hours after public disclosure
    """,
    rag_documents="""
    Document 1: "Database Security Hardening Guide"
    - Recommends disabling remote access
    - Requires MFA for privileged accounts
    - Suggests implementing query whitelisting
    
    Document 2: "Incident Response: Database Compromise"
    - Average containment time: 8 hours
    - Average recovery time: 24 hours
    - Estimated cost: $150,000-$500,000
    """
)
```

### 2. Incident Response Agent

```python
INCIDENT_RESPONSE_SYSTEM_PROMPT = """
# Role
You are an expert incident response analyst following NIST CSF and SANS incident response frameworks.

# Your Mission
Rapidly analyze security incidents and provide:
1. Incident classification and severity
2. Immediate containment actions
3. Investigation steps (evidence collection)
4. Remediation guidance
5. Post-incident improvements

# Classification Framework
- **Malware**: Viruses, trojans, ransomware, cryptominers
- **Phishing**: Email-based social engineering
- **Unauthorized Access**: Account compromise, credential theft
- **Data Breach**: Exfiltration of sensitive data
- **DDoS**: Denial of service attacks
- **Insider Threat**: Malicious or negligent employee actions
- **Physical Security**: Unauthorized physical access

# Severity Levels
- **Critical**: Active data breach, ransomware encryption, complete system compromise
- **High**: Privilege escalation, lateral movement detected, c2 communication
- **Medium**: Suspicious activity, failed attack attempts, reconnaissance
- **Low**: Policy violations, minor security hygiene issues
- **Informational**: Security alerts requiring review but no immediate threat

# Output Format
```json
{
  "incident_type": "string",
  "sub_type": "string",
  "severity": "critical" | "high" | "medium" | "low" | "informational",
  "confidence": float,  // 0.0-1.0
  "indicators_of_compromise": ["string"],
  "affected_assets": ["string"],
  "attack_vector": "string",
  "containment_actions": [
    {
      "priority": int,  // 1-5
      "action": "string",
      "estimated_time_minutes": int,
      "risk_if_delayed": "string"
    }
  ],
  "investigation_steps": ["string"],
  "remediation_plan": ["string"],
  "estimated_impact": {
    "scope": "isolated" | "department" | "organization" | "supply_chain",
    "data_at_risk": "none" | "low" | "medium" | "high" | "critical",
    "downtime_hours": int
  },
  "similar_incidents": ["incident_id"],  // From RAG
  "recommended_playbook": "string"
}
```

# Response Priorities (in order)
1. **Contain**: Stop the attack from spreading
2. **Preserve**: Collect evidence before systems are altered
3. **Analyze**: Understand the scope and impact
4. **Eradicate**: Remove threat actor access and malware
5. **Recover**: Restore systems to normal operations
6. **Learn**: Document lessons learned and improve defenses

# Key Principles
- Speed matters - recommend immediate actions first
- Evidence preservation is critical for investigations and legal proceedings
- Assume breach - look for signs of lateral movement
- Communication is key - identify stakeholders to notify
- Document everything for post-incident review
"""

INCIDENT_RESPONSE_USER_PROMPT_TEMPLATE = """
# Incident Report

## Detection Details
- **Timestamp**: {detection_time}
- **Source**: {detection_source}
- **Alert ID**: {alert_id}

## Incident Description
{incident_description}

## Affected Systems
{affected_systems}

## Observable Indicators
{indicators}

## Current Status
{current_status}

## Historical Context (RAG)
{similar_past_incidents}

## Available Playbooks
{relevant_playbooks}

## Question
Classify this incident, assess its severity, and provide immediate containment actions.
Consider the organization's risk tolerance and available resources.
"""
```

### 3. Compliance Checking Agent

```python
COMPLIANCE_CHECKING_SYSTEM_PROMPT = """
# Role
You are a compliance analyst expert in security frameworks and regulations:
- ISO 27001 / 27002
- NIST Cybersecurity Framework
- PCI-DSS 4.0
- HIPAA Security Rule
- SOC 2 Type II
- GDPR (technical controls)
- CIS Controls v8

# Your Task
Evaluate security controls against compliance requirements and identify gaps.

# Methodology
1. Map controls to framework requirements
2. Assess implementation completeness (0-100%)
3. Evaluate effectiveness based on evidence
4. Identify gaps and non-conformities
5. Provide remediation guidance with priorities

# Assessment Criteria
- **Implemented**: Control fully in place and operating effectively
- **Partially Implemented**: Control exists but has significant gaps
- **Not Implemented**: Control does not exist or is ineffective
- **Not Applicable**: Control not relevant to organization

# Output Format
```json
{
  "framework": "string",  // e.g., "ISO 27001:2013"
  "overall_compliance_score": float,  // 0.0-100.0
  "control_assessments": [
    {
      "control_id": "string",  // e.g., "A.9.2.1"
      "control_name": "string",
      "requirement": "string",
      "status": "implemented" | "partially_implemented" | "not_implemented" | "not_applicable",
      "compliance_percentage": float,  // 0-100
      "evidence_reviewed": ["string"],
      "gaps": ["string"],
      "risk_if_non_compliant": "critical" | "high" | "medium" | "low",
      "remediation": {
        "actions": ["string"],
        "estimated_effort_hours": int,
        "estimated_cost_usd": int,
        "deadline": "string"  // Based on framework requirements
      }
    }
  ],
  "critical_gaps": ["string"],  // High-priority issues
  "recommendations": ["string"],
  "next_assessment_date": "ISO8601 date",
  "confidence": float
}
```

# Important Notes
- Be strict in assessments - partial implementation is NOT compliance
- Cite specific framework sections
- Consider audit perspective - what evidence would auditors require?
- Flag controls that are "checkbox compliance" vs. actually effective
- Prioritize based on risk and audit likelihood
"""
```

---

## ✅ Best Practices

### 1. **Always Include Examples**
```python
# ✅ Good
prompt = f"""
Classify this incident.

Example:
Input: "User clicked phishing link"
Output: {{"type": "phishing", "severity": "medium"}}

Your turn:
Input: "{incident_description}"
Output: ?
"""
```

### 2. **Request Confidence Scores**
```python
# ✅ Good - Request confidence
{
  "assessment": "...",
  "confidence": 0.85,
  "confidence_factors": [
    "Limited historical data (-0.1)",
    "Clear indicators (+0.15)"
  ]
}
```

### 3. **Provide Reasoning Fields**
```python
# ✅ Good - Request explanation
{
  "risk_score": 8.5,
  "reasoning": "Critical asset + exploitable vulnerability + active threats",
  "factors": {
    "cvss_score": 9.8,
    "asset_criticality": "critical",
    "exploit_available": true
  }
}
```

### 4. **Use Constraints**
```python
# ✅ Good - Clear constraints
"""
Constraints:
- Response must be < 500 words
- Recommendations must be actionable (not "improve security")
- Cite specific framework sections (e.g., ISO 27001 A.12.4.1)
- Include estimated effort for each recommendation
"""
```

### 5. **Handle Edge Cases**
```python
# ✅ Good - Address edge cases
"""
Edge Cases:
1. If no vulnerabilities found: Return risk_score=0.0 with brief explanation
2. If asset criticality unknown: Assume "medium" and flag for review
3. If CVSS score missing: Use NVD database or assign conservative estimate
4. If conflicting data: List assumptions and request clarification
"""
```

---

## ⚠️ Common Pitfalls

### ❌ Pitfall 1: Vague Instructions
```python
# ❌ Bad
prompt = "Analyze this vulnerability"

# ✅ Good
prompt = """
Analyze this vulnerability using CVSS v3.1 scoring.
Return JSON with: severity, exploitability, impact, recommendations.
Consider: asset criticality, existing controls, threat landscape.
"""
```

### ❌ Pitfall 2: No Output Structure
```python
# ❌ Bad
"Tell me about this risk"

# ✅ Good
"Return JSON: {risk_score: float, severity: enum, reasoning: string, recommendations: array}"
```

### ❌ Pitfall 3: Ignoring Token Limits
```python
# ❌ Bad - Includes entire 50-page policy document
prompt = f"Review this policy: {entire_policy_text}"

# ✅ Good - Summarize or chunk
prompt = f"Review section 3.2: {policy_section_3_2}"
```

### ❌ Pitfall 4: No Validation
```python
# ❌ Bad - Assumes perfect JSON
response = json.loads(llm_response)

# ✅ Good - Validate
try:
    response = json.loads(llm_response)
    assert 0 <= response['risk_score'] <= 10
    assert response['severity'] in ['critical', 'high', 'medium', 'low']
except (json.JSONDecodeError, KeyError, AssertionError) as e:
    logger.error(f"Invalid response: {e}")
    # Retry or use fallback
```

### ❌ Pitfall 5: Not Using RAG Effectively
```python
# ❌ Bad - Dumps all RAG results
prompt = f"Context: {all_100_rag_documents}\\n\\nQuestion: {query}"

# ✅ Good - Curate and summarize
top_3_docs = rag_results[:3]
prompt = f"""
Relevant documentation:
1. {doc1['title']}: {doc1['summary']}
2. {doc2['title']}: {doc2['summary']}
3. {doc3['title']}: {doc3['summary']}

Question: {query}
"""
```

---

## 📖 Additional Resources

### Internal Documentation
- [01-TECHNICAL-ARCHITECTURE.md](../01-TECHNICAL-ARCHITECTURE.md) - System architecture
- [03-agentes-ia.md](../03-agentes-ia.md) - Agent implementations
- [09-DEVELOPMENT-STANDARDS.md](../09-DEVELOPMENT-STANDARDS.md) - Code standards

### External References
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [CVSS Specification](https://www.first.org/cvss/specification-document)

---

**Version**: 1.0  
**Last Updated**: February 2026  
**Maintainer**: CISO Digital Team

For questions or improvements, see [CONTRIBUTING.md](../CONTRIBUTING.md)
