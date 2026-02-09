# Security Incident Response Playbooks

This directory contains detailed, actionable incident response playbooks for common security incidents. These playbooks are designed to be ingested into the RAG (Retrieval Augmented Generation) system and used by the IncidentResponseAgent to provide context-aware guidance during security incidents.

## Available Playbooks

### 1. Malware Incident Playbook (`malware-incident-playbook.md`)
- **Incident Types**: Malware, viruses, trojans, ransomware, rootkits
- **Severity Range**: Medium to Critical
- **Key Phases**:
  - Detection & Analysis (0-30 min)
  - Containment (30-45 min)
  - Eradication (45-120 min)
  - Recovery (2-8 hours)
  - Post-Incident Activities (1-3 days)
- **Time Estimate**: 4 hours (low) to 2-5 days (critical ransomware)
- **Framework References**: NIST SP 800-61 Rev. 2, ISO/IEC 27035

### 2. Phishing Incident Playbook (`phishing-incident-playbook.md`)
- **Incident Types**: Email phishing, spear phishing, whaling, smishing (SMS phishing)
- **Severity Range**: Low to High
- **Key Phases**:
  - Detection & Analysis (0-30 min)
  - Containment (30-60 min)
  - Eradication (1-2 hours)
  - Recovery (1-2 days)
  - Post-Incident Activities (1-3 days)
- **Time Estimate**: 2 hours (low) to 8 hours (high)
- **Framework References**: NIST SP 800-61 Rev. 2, Anti-Phishing Working Group (APWG)

### 3. Data Breach Playbook (`data-breach-playbook.md`)
- **Incident Types**: Unauthorized data access, data exfiltration, PII/PHI breach
- **Severity Range**: High to Critical
- **Key Phases**:
  - Detection & Analysis (0-2 hours)
  - Containment (1-4 hours)
  - Legal & Regulatory Response (2-72 hours)
  - Individual Notification (1-60 days)
  - Eradication & Recovery (1-4 weeks)
  - Post-Incident Activities (1-6 months)
- **Time Estimate**: Varies based on scope and regulatory requirements
- **Framework References**: NIST SP 800-61 Rev. 2, ISO/IEC 27035, GDPR, HIPAA, CCPA
- **Special Features**:
  - Legal and regulatory notification requirements
  - Multi-jurisdiction compliance guidance
  - Data breach notification templates
  - Cost estimates and impact analysis

## Playbook Structure

Each playbook follows a consistent structure for easy navigation and use:

### 1. **Metadata**
- Incident type
- Severity range
- Framework references
- Version and last updated date

### 2. **Executive Summary**
- High-level overview
- Key objectives
- Critical success factors

### 3. **Triggers**
- When to use this playbook
- Detection indicators
- Escalation criteria

### 4. **Incident Response Phases**
Detailed step-by-step procedures organized by NIST phases:
- **Detection & Analysis**: Initial triage, evidence collection, scope assessment
- **Containment**: Immediate actions to stop the incident
- **Eradication**: Remove threat and close vulnerabilities
- **Recovery**: Restore systems and operations
- **Post-Incident Activities**: Lessons learned, improvements

Each step includes:
- Objective
- Time estimate
- Detailed actions
- Expected output
- Priority indicators (🚨 for critical steps)

### 5. **Checklists**
- Comprehensive checklists for each phase
- Ensures no steps are missed
- Useful for incident documentation

### 6. **Roles and Responsibilities**
- Key roles involved in response
- Specific responsibilities for each role
- Escalation paths

### 7. **Time Estimates**
- Severity-based time estimates
- Helps with resource planning
- Sets realistic expectations

### 8. **Escalation Criteria**
- When to escalate to higher severity
- Red flags requiring immediate attention
- Executive notification triggers

### 9. **References and Resources**
- Framework documentation
- Tools and software
- Threat intelligence sources
- Additional playbooks

## Using Playbooks with RAG

These playbooks are designed to be chunked and embedded into the Qdrant vector database for semantic search. The IncidentResponseAgent can then retrieve relevant sections based on the incident context.

### Ingesting Playbooks into Qdrant

```bash
# Navigate to backend directory
cd backend

# Ingest playbooks into incident_playbooks collection
python scripts/seed_knowledge_base.py \
  --collection incident_playbooks \
  --directory knowledge-base/playbooks/

# Reset collection and re-ingest (if updating playbooks)
python scripts/seed_knowledge_base.py \
  --collection incident_playbooks \
  --directory knowledge-base/playbooks/ \
  --reset

# Ingest a specific playbook
python scripts/seed_knowledge_base.py \
  --collection incident_playbooks \
  --file knowledge-base/playbooks/malware-incident-playbook.md
```

### RAG Search Examples

The IncidentResponseAgent uses the `get_playbook` tool to search for relevant playbook sections:

```python
# Example: Agent searching for malware response steps
results = await rag_service.search(
    query="malware incident response playbook containment steps",
    collection_name="incident_playbooks",
    limit=3
)
```

## Customizing Playbooks

When customizing these playbooks for your organization:

1. **Update Contact Information**:
   - Replace `[INSERT NUMBER]` with actual emergency contact numbers
   - Update email addresses (e.g., `soc@company.com`)
   - Add internal communication channels (Slack, Teams)

2. **Adjust Timelines**:
   - Time estimates may vary based on your team size and tools
   - Update based on your organization's RTO/RPO

3. **Add Organization-Specific Steps**:
   - Internal approval processes
   - Specific tools or systems
   - Regulatory requirements for your industry

4. **Update References**:
   - Add links to internal documentation
   - Include contacts for third-party vendors (forensics, legal)
   - Reference internal policies and procedures

5. **Re-ingest After Updates**:
   ```bash
   python scripts/seed_knowledge_base.py \
     --collection incident_playbooks \
     --directory knowledge-base/playbooks/ \
     --reset
   ```

## Adding New Playbooks

To create a new playbook:

1. **Use the Template Structure**:
   - Follow the format of existing playbooks
   - Include all standard sections
   - Maintain consistent formatting

2. **Standard Sections to Include**:
   ```markdown
   # [Incident Type] Incident Response Playbook
   
   ## Metadata
   ## Executive Summary
   ## Triggers
   ## Incident Response Phases
   ## Incident Response Checklist
   ## Key Roles and Responsibilities
   ## Time Estimates
   ## Escalation Criteria
   ## References and Resources
   ## Document Control
   ```

3. **Naming Convention**:
   - Use lowercase with hyphens
   - End with `-playbook.md`
   - Examples:
     - `ransomware-incident-playbook.md`
     - `ddos-attack-playbook.md`
     - `insider-threat-playbook.md`

4. **Ingest the New Playbook**:
   ```bash
   python scripts/seed_knowledge_base.py \
     --collection incident_playbooks \
     --file knowledge-base/playbooks/new-playbook.md
   ```

## Future Playbooks (Planned)

Additional playbooks to be developed:

- [ ] **Ransomware-Specific Playbook**: Detailed procedures for ransomware incidents with decryption strategies
- [ ] **DDoS Attack Playbook**: Distributed denial of service attack response
- [ ] **Insider Threat Playbook**: Handling malicious insider activities
- [ ] **Supply Chain Compromise Playbook**: Third-party/vendor breach response
- [ ] **Cloud Security Incident Playbook**: AWS/Azure/GCP-specific incident response
- [ ] **API Security Incident Playbook**: API abuse and compromise response
- [ ] **Cryptojacking Playbook**: Cryptocurrency mining malware response
- [ ] **Business Email Compromise (BEC) Playbook**: CEO fraud and wire transfer fraud

## Maintenance and Updates

- **Review Frequency**: Quarterly review and updates recommended
- **Version Control**: Update version and date in metadata when making changes
- **Testing**: Conduct tabletop exercises using these playbooks
- **Feedback Loop**: Update based on lessons learned from actual incidents

## Support and Questions

For questions about these playbooks or to report issues:
- **Internal**: Contact the Security Team or CISO
- **Updates**: Submit pull request with changes
- **New Playbooks**: Create issue with playbook request

---

**Last Updated**: February 2026  
**Maintained By**: Security Team  
**Version**: 1.0
