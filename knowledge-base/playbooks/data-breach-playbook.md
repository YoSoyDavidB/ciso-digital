# Data Breach Incident Response Playbook

## Metadata
- **Incident Type**: Data Breach / Unauthorized Data Access
- **Severity Range**: High to Critical
- **Framework References**: NIST SP 800-61 Rev. 2, ISO/IEC 27035, GDPR, HIPAA Breach Notification Rule
- **Last Updated**: February 2026
- **Version**: 1.0

---

## Executive Summary

This playbook provides a structured approach to responding to data breach incidents involving unauthorized access, acquisition, or disclosure of sensitive data including PII (Personally Identifiable Information), PHI (Protected Health Information), financial data, intellectual property, or confidential business information.

**Key Objectives:**
- Contain the breach within 1 hour of detection
- Assess the scope and impact of compromised data
- Meet legal and regulatory notification requirements (GDPR 72-hour, HIPAA 60-day)
- Preserve forensic evidence for investigation and potential legal action
- Prevent recurrence through security improvements

**Critical**: Data breaches trigger legal obligations. Involve Legal and Compliance teams IMMEDIATELY.

---

## Triggers (When to Use This Playbook)

Use this playbook when:
- ✅ Unauthorized access to databases containing sensitive data detected
- ✅ Data exfiltration detected (large data transfers to external systems)
- ✅ Database dump files found in unauthorized locations
- ✅ Customer/employee PII exposed or stolen
- ✅ Protected Health Information (PHI) accessed by unauthorized parties
- ✅ Financial data (credit cards, bank accounts) compromised
- ✅ Intellectual property or trade secrets stolen
- ✅ Cloud storage misconfiguration exposing sensitive data
- ✅ Backup tapes or devices containing sensitive data lost/stolen
- ✅ Ransomware with confirmed data exfiltration
- ✅ Insider threat with data theft
- ✅ Third-party/vendor breach affecting your data

---

## Legal and Regulatory Context

### Key Regulations

| Regulation | Jurisdiction | Notification Timeline | Penalties |
|------------|--------------|----------------------|-----------|
| **GDPR** | EU/EEA | 72 hours to regulator, "without undue delay" to individuals | Up to €20M or 4% global revenue |
| **CCPA/CPRA** | California, US | "Without unreasonable delay" | Up to $7,500 per intentional violation |
| **HIPAA** | US Healthcare | 60 days for breaches >500 records | Up to $1.5M per year per violation type |
| **PIPEDA** | Canada | "As soon as feasible" | Up to CAD $100,000 |
| **LGPD** | Brazil | Reasonable timeframe | Up to 2% of revenue (max R$50M) |
| **SOX** | US Public Companies | Immediate (material events) | Criminal charges possible |

### Breach Notification Thresholds

- **GDPR**: Any breach with risk to individuals (no minimum threshold)
- **HIPAA**: 500+ records = public notification; <500 = annual notification
- **State Laws (US)**: Varies by state, typically "personal information" exposed
- **Credit Card Data (PCI DSS)**: Any compromise of cardholder data

---

## Incident Response Phases

### Phase 0: Pre-Incident Preparation (Ongoing)

**Ensure these are in place BEFORE a breach**:
- [ ] Data inventory and classification (know what data you have)
- [ ] Data flow mapping (know where data goes)
- [ ] Legal team contact information
- [ ] PR/Communications team contact
- [ ] Cyber insurance policy and contact
- [ ] Forensic investigation firm on retainer
- [ ] Attorney-client privilege protocol for investigations
- [ ] Pre-drafted breach notification templates
- [ ] Dedicated breach response budget

---

### Phase 1: Detection & Analysis (Time: 0-2 hours)

#### Step 1.1: Initial Triage (15 minutes) 🚨 CRITICAL
**Objective**: Quickly assess the incident and activate the breach response team.

**IMMEDIATE ACTIONS**:
1. **Document Detection**:
   - How was breach detected? (SIEM alert, user report, external notification)
   - Date/time of detection
   - Initial indicators

2. **Activate Breach Response Team**:
   - **CISO**: Overall incident command
   - **Legal Counsel**: Regulatory requirements, privilege
   - **Compliance Officer**: Notification obligations
   - **Forensics Lead**: Evidence collection
   - **Privacy Officer**: Individual notification
   - **Communications/PR**: Public statements
   - **IT/Security**: Technical response
   - **HR**: Insider threat cases
   - **Insurance**: Cyber insurance claim

3. **Establish Attorney-Client Privilege** (if possible):
   - Have legal counsel direct the investigation
   - Communications through legal to protect privilege
   - Mark all documents "Attorney Work Product"

4. **Initial Severity Assessment**:
   - **Critical**: PII/PHI of >10,000 individuals, payment card data, HIPAA breach
   - **High**: PII/PHI of 100-10,000 individuals, trade secrets
   - **Medium**: PII/PHI of <100 individuals, internal data

**Output**: Breach response team activated with legal oversight

---

#### Step 1.2: Scope Assessment (45 minutes)
**Objective**: Determine WHAT data was accessed/stolen and HOW MANY individuals affected.

**Actions**:
1. **Identify Affected Systems**:
   - Databases accessed
   - File servers compromised
   - Cloud storage exposed
   - Backup systems accessed
   - Applications affected

2. **Identify Data Types Compromised**:
   - [ ] **PII**: Names, SSN, driver's license, passport, addresses, DOB
   - [ ] **PHI**: Medical records, diagnoses, prescriptions, insurance info
   - [ ] **Financial**: Credit card numbers, bank accounts, financial statements
   - [ ] **Authentication**: Passwords, security questions, biometrics
   - [ ] **Proprietary**: Trade secrets, IP, source code, business plans
   - [ ] **Employee Data**: HR records, performance reviews, compensation
   - [ ] **Customer Data**: Purchase history, communication records
   - [ ] **Children's Data**: COPPA-protected data (<13 years old)

3. **Determine Number of Affected Individuals**:
   - Query databases for record counts
   - Check access logs for files accessed
   - Identify unique individuals (deduplicate)
   - Categorize by: Customers, Employees, Partners, Other

4. **Assess Data Sensitivity**:
   - Was data encrypted? (If yes, breach may be less severe)
   - Was data anonymized/pseudonymized?
   - Was data already public?
   - What is the harm potential? (Identity theft, financial fraud, discrimination)

**Output**: Data breach scope document with affected individual count

---

#### Step 1.3: Timeline Reconstruction (60 minutes)
**Objective**: Determine WHEN the breach occurred and HOW it happened.

**Actions**:
1. **Establish Timeline**:
   - **Initial Compromise Date**: When did attacker first gain access?
   - **Data Access Date**: When was sensitive data first accessed?
   - **Exfiltration Date**: When was data stolen/exfiltrated?
   - **Detection Date**: When was breach discovered?
   - **Containment Date**: When was attacker access terminated?

2. **Forensic Evidence Collection**:
   - **System Logs**: Authentication, access, database queries
   - **Network Logs**: Traffic captures, firewall logs, proxy logs
   - **Application Logs**: Web server, application, API logs
   - **Database Logs**: Query logs, audit logs, backup logs
   - **Email Logs**: If spear phishing or BEC involved
   - **Cloud Logs**: AWS CloudTrail, Azure Activity Log, GCP Logging
   - **Take Forensic Images**: Affected servers, workstations, databases

3. **Analyze Attack Vector**:
   - How did attacker gain initial access?
     - Phishing/social engineering
     - Vulnerability exploitation
     - Stolen credentials
     - Insider threat
     - Third-party/vendor compromise
     - Misconfiguration (S3 bucket, database)
     - SQL injection
     - API abuse
   - What tools/techniques were used?
   - Was this a targeted attack or opportunistic?

4. **Preserve Evidence**:
   - Create forensic images BEFORE remediation
   - Chain of custody documentation
   - Store evidence securely (encrypted, access controlled)
   - Consider law enforcement involvement

**Output**: Attack timeline, attack vector analysis, forensic evidence secured

---

### Phase 2: Containment (Time: 1-4 hours)

#### Step 2.1: Immediate Containment (1 hour) 🚨 CRITICAL
**Objective**: Stop ongoing data exfiltration and prevent further unauthorized access.

**Actions**:
1. **Block Attacker Access**:
   - Disable compromised user accounts
   - Revoke API keys/tokens
   - Block attacker IP addresses at firewall
   - Terminate suspicious sessions
   - Disable external database access temporarily
   - Shut down affected servers (if actively being exploited)

2. **Isolate Affected Systems**:
   - Network segmentation to prevent lateral movement
   - Isolate databases from internet
   - Place affected systems in quarantine VLAN

3. **Stop Data Exfiltration**:
   - Block outbound connections to attacker IPs/domains
   - Monitor for continued data transfer attempts
   - Implement DLP rules to block sensitive data egress

4. **Secure Backups**:
   - Verify backups are not compromised
   - Isolate backup systems from production
   - Take clean backups before remediation

**Output**: Attacker access terminated, systems isolated

---

#### Step 2.2: Credential Reset (30 minutes)
**Objective**: Ensure attacker cannot regain access via stolen credentials.

**Actions**:
1. **Reset Passwords**:
   - All users with access to affected systems
   - All administrative/privileged accounts
   - All service accounts
   - All database passwords
   - All API keys and tokens

2. **Revoke Access Tokens**:
   - OAuth tokens
   - JWT tokens
   - Session cookies
   - Certificate-based authentication

3. **Enable MFA**:
   - Mandatory MFA for all users
   - Privileged accounts require hardware MFA (FIDO2)

4. **Review Access Controls**:
   - Remove unnecessary privileges
   - Review group memberships
   - Audit admin account usage

**Output**: All credentials secured and MFA enforced

---

#### Step 2.3: Vulnerability Remediation (2 hours)
**Objective**: Close the vulnerability that enabled the breach.

**Actions**:
1. **Patch Vulnerabilities**:
   - Apply security patches for exploited vulnerabilities
   - Emergency patching for critical systems
   - Vulnerability scan to identify similar weaknesses

2. **Fix Misconfigurations**:
   - Secure cloud storage (S3 buckets, Azure Blob)
   - Close open database ports
   - Remove default credentials
   - Implement principle of least privilege

3. **Deploy Compensating Controls** (if patching delayed):
   - WAF rules to block exploitation
   - IPS signatures
   - Network ACLs
   - Temporary workarounds

4. **Harden Systems**:
   - CIS benchmarks
   - Security baseline configurations
   - Disable unnecessary services
   - Enable audit logging

**Output**: Initial attack vector closed and systems hardened

---

### Phase 3: Legal and Regulatory Response (Time: 2-72 hours)

#### Step 3.1: Regulatory Notification Assessment (2 hours)
**Objective**: Determine legal obligations and notification requirements.

**Actions** (Led by Legal/Compliance):
1. **Identify Applicable Regulations**:
   - Where are affected individuals located? (determines applicable laws)
   - What type of data was compromised? (determines notification rules)
   - How many individuals affected? (determines notification thresholds)

2. **Assess Notification Requirements**:
   ```
   GDPR (EU):
   - Notify supervisory authority within 72 hours
   - Notify individuals "without undue delay" if high risk
   - Document all breaches (even if no notification required)

   HIPAA (US Healthcare):
   - ≥500 individuals: Notify HHS and media within 60 days
   - <500 individuals: Annual notification to HHS
   - Notify individuals within 60 days

   CCPA/CPRA (California):
   - Notify California AG if >500 CA residents affected
   - Notify individuals without unreasonable delay

   State Laws (US):
   - Most states require notification without unreasonable delay
   - Some have specific timelines (e.g., Colorado: 30 days)
   ```

3. **Evaluate Exceptions**:
   - Was data encrypted with strong encryption? (May exempt from some notifications)
   - Was data already public?
   - Is breach unlikely to result in harm? (GDPR: may not need to notify individuals)

4. **Credit Monitoring Obligation**:
   - Some states require free credit monitoring (e.g., SSN exposed)
   - Typical: 1-2 years of credit monitoring

**Output**: Legal notification requirements documented with deadlines

---

#### Step 3.2: Regulator Notification (within 72 hours for GDPR)
**Objective**: Meet regulatory notification obligations.

**Actions**:
1. **GDPR Notification to Supervisory Authority**:
   - Use official notification form for your jurisdiction
   - Include:
     - Nature of the breach
     - Categories and approximate number of affected individuals
     - Categories and approximate number of affected data records
     - Contact point for more information (DPO)
     - Likely consequences of the breach
     - Measures taken or proposed to address the breach
   - Submit within 72 hours of becoming aware of breach
   - If not possible within 72 hours, explain delay in notification

2. **HIPAA Notification to HHS**:
   - For breaches ≥500 records: https://ocrportal.hhs.gov/ocr/breach/wizard_breach.jsf
   - Include covered entity info, breach details, affected individuals count
   - Submit within 60 days

3. **State AG Notification** (US):
   - Most states require AG notification
   - Usually same timeline as individual notification
   - Some require specific forms

4. **Other Regulators**:
   - Financial regulators (if financial data)
   - Payment card brands (if card data) - PCI DSS Incident Reporting
   - Industry-specific regulators

**Output**: Regulatory notifications submitted on time

---

#### Step 3.3: Law Enforcement Notification (as appropriate)
**Objective**: Involve law enforcement for criminal investigation.

**Actions**:
1. **Assess Need for Law Enforcement**:
   - Consider involving law enforcement if:
     - Organized cybercrime suspected
     - Nation-state actor suspected
     - Large-scale breach
     - Financial fraud involved
     - Potential criminal prosecution desired
   - Consider NOT involving if:
     - Want to keep breach private (law enforcement may disclose)
     - Regulatory notification is sufficient
     - Minor incident with no criminal intent

2. **Contact Appropriate Agency**:
   - **FBI Cyber Division**: Major breaches, organized crime, nation-state
   - **US Secret Service**: Financial crimes, payment card fraud
   - **Local Police**: Physical theft (backup tapes, laptops)
   - **IC3 (Internet Crime Complaint Center)**: https://www.ic3.gov
   - **Interpol**: International incidents

3. **Provide Evidence Package**:
   - Timeline of events
   - Forensic evidence
   - Indicators of compromise
   - Affected individual count
   - Data types compromised

4. **Coordination**:
   - Law enforcement may request delay in disclosure (for investigation)
   - Document this request (may extend notification timeline)

**Output**: Law enforcement engaged if appropriate

---

### Phase 4: Individual Notification (Time: 1-60 days depending on regulation)

#### Step 4.1: Notification Content Preparation (1 day)
**Objective**: Draft clear, compliant breach notification letters.

**Actions** (Led by Legal and Communications):
1. **Required Content** (varies by jurisdiction):
   ```
   Most jurisdictions require:
   - Date or estimated date of breach
   - Description of breach (what happened)
   - Types of personal information involved
   - Steps taken to address the breach
   - Contact information for questions
   - Steps individuals can take to protect themselves
   - Contact information for credit bureaus (if SSN exposed)
   - Information about credit monitoring offered (if any)
   ```

2. **Template Letter**:
   ```
   [Date]

   Dear [Name],

   We are writing to inform you of a data security incident that may affect your personal information.

   WHAT HAPPENED
   On [date], we discovered that an unauthorized party gained access to our systems 
   between [date range]. We immediately launched an investigation with cybersecurity 
   experts and law enforcement.

   WHAT INFORMATION WAS INVOLVED
   The investigation determined that the following types of your information may have 
   been accessed:
   - [List specific data types: name, address, SSN, etc.]

   WHAT WE ARE DOING
   We have taken the following steps:
   - Secured our systems and terminated unauthorized access
   - Engaged leading cybersecurity firm to investigate
   - Notified law enforcement and regulatory authorities
   - Implemented additional security measures to prevent recurrence

   WHAT YOU CAN DO
   We recommend you:
   - Monitor your accounts for suspicious activity
   - Place a fraud alert or credit freeze (instructions below)
   - Review your credit reports (free at www.annualcreditreport.com)
   - Be alert for phishing attempts related to this incident

   We are offering [12/24 months] of free credit monitoring and identity theft protection 
   services through [Provider]. To enroll, [instructions].

   FOR MORE INFORMATION
   We sincerely apologize for this incident. For questions, please contact:
   - Phone: [Toll-free number]
   - Email: [Dedicated email address]
   - Website: [Dedicated breach response page]

   Credit Bureau Contact Information:
   [List Equifax, Experian, TransUnion with phone numbers]

   Sincerely,
   [CISO or CEO Name]
   [Company]
   ```

3. **Translation**:
   - Translate to languages of affected individuals
   - Meet accessibility requirements (large print, etc.)

4. **Legal Review**:
   - Have outside counsel review all communications
   - Ensure compliance with all applicable laws
   - Avoid admissions of liability

**Output**: Approved notification letter ready for distribution

---

#### Step 4.2: Notification Distribution (varies by scale)
**Objective**: Notify all affected individuals within required timeline.

**Actions**:
1. **Notification Method** (in order of preference):
   - **Email**: Fastest, most common (but may not reach all)
   - **Postal Mail**: Required if email unavailable or for certain data types
   - **Substitute Notice** (if contact info inadequate):
     - Post on website homepage
     - Notification to major media
     - Some jurisdictions require this if >50% of individuals can't be directly contacted

2. **Notification Timing**:
   - GDPR: "Without undue delay"
   - HIPAA: Within 60 days
   - CCPA: Without unreasonable delay
   - State laws: Typically "without unreasonable delay" or specific timeline

3. **Call Center Setup**:
   - Dedicated toll-free phone number
   - Train call center staff on breach details and FAQs
   - Extended hours for first 2 weeks
   - Script for responding to questions

4. **Credit Monitoring Enrollment**:
   - Set up enrollment portal
   - Provide unique enrollment codes
   - Track enrollment rates

5. **Track Notifications**:
   - Log notification date for each individual
   - Track bounced emails and returned mail
   - Follow up with corrected addresses

**Output**: All affected individuals notified within legal timelines

---

#### Step 4.3: Public Communication (if required)
**Objective**: Manage public disclosure and reputation impact.

**Actions**:
1. **Public Notification** (required for):
   - HIPAA: Breaches ≥500 records (notice to prominent media outlets)
   - Some state laws: Public notice if large scale
   - SEC: Material events for public companies

2. **Website Posting**:
   - Create dedicated breach response page
   - Post FAQ
   - Provide steps individuals should take
   - Include timeline of events (high-level)
   - Regularly update with new information

3. **Media Statement**:
   - Prepare press release (if proactive disclosure)
   - Designate media spokesperson (usually CEO or CISO)
   - Key messages:
     - What happened (facts, not speculation)
     - When we discovered it
     - What we've done to respond
     - What we're doing to prevent recurrence
     - What affected individuals should do
   - **What NOT to say**:
     - Minimizing the breach ("only a few records")
     - Blaming others (vendors, users)
     - Speculation on attacker identity
     - Admissions of negligence

4. **Social Media Monitoring**:
   - Monitor for breach discussions
   - Respond to questions/concerns
   - Correct misinformation

**Output**: Public communications managed professionally

---

### Phase 5: Eradication & Recovery (Time: 1-4 weeks)

#### Step 5.1: Complete Remediation (1-2 weeks)
**Objective**: Fully remove attacker presence and strengthen security.

**Actions**:
1. **Thorough Attacker Eviction**:
   - Remove all attacker access points, backdoors, malware
   - Hunt for persistence mechanisms
   - Review all administrative accounts for unauthorized access
   - Rebuild compromised systems from clean images

2. **Security Architecture Changes**:
   - Implement data encryption (at rest and in transit)
   - Deploy DLP (Data Loss Prevention) solutions
   - Implement database activity monitoring
   - Deploy CASB (Cloud Access Security Broker) for cloud data
   - Implement network segmentation
   - Deploy deception technology (honeypots)

3. **Access Control Improvements**:
   - Implement least privilege access
   - Deploy PAM (Privileged Access Management)
   - Require MFA for all access to sensitive data
   - Implement just-in-time access for administrative tasks

4. **Monitoring Enhancements**:
   - Deploy EDR/XDR on all systems
   - Implement UEBA (User and Entity Behavior Analytics)
   - Enhanced SIEM rules for data access
   - Alert on bulk data exports
   - Monitor for IOCs related to this breach

**Output**: Attacker fully eradicated, security significantly improved

---

#### Step 5.2: System Restoration (1-2 weeks)
**Objective**: Restore full operations with enhanced security.

**Actions**:
1. **Rebuild Affected Systems**:
   - Restore from clean, pre-breach backups OR
   - Rebuild from scratch (preferred if feasible)
   - Apply all security patches
   - Implement security hardening (CIS benchmarks)

2. **Data Restoration**:
   - Restore data from verified clean backups
   - Verify data integrity
   - Implement encryption for sensitive data

3. **Phased Reconnection**:
   - Phase 1: Isolated testing (1-2 days)
   - Phase 2: Limited production with monitoring (3-5 days)
   - Phase 3: Full production with enhanced monitoring (ongoing)

4. **Validation**:
   - Penetration testing of remediated systems
   - Vulnerability assessment
   - Security control validation
   - Monitoring effectiveness check

**Output**: Systems restored to secure operations

---

### Phase 6: Post-Incident Activities (Time: 1-6 months)

#### Step 6.1: Lessons Learned (1 week after containment)
**Objective**: Identify improvements to prevent future breaches.

**Participants**: Breach response team, executive leadership, board (if material breach)

**Agenda**:
1. **Incident Review**:
   - What was the root cause?
   - How did attacker gain access?
   - Why did existing controls fail?
   - What was the detection lag? (compromise to detection time)
   - What was the response effectiveness?

2. **Process Improvements**:
   - Was breach response plan adequate?
   - Was team prepared?
   - Were roles/responsibilities clear?
   - Were notification timelines met?
   - Was communication effective?

3. **Technical Improvements**:
   - What security controls need to be added?
   - What controls need to be improved?
   - Are there architectural changes needed?
   - Are third-party risks properly managed?

4. **Budget and Resources**:
   - What is the total cost of this breach?
     - Forensic investigation
     - Legal fees
     - Regulatory fines
     - Credit monitoring
     - System replacement
     - Business disruption
     - Reputation damage
   - What budget is needed to prevent recurrence?

**Output**: Comprehensive action plan with owners and deadlines

---

#### Step 6.2: Compliance and Audit (1-3 months)
**Objective**: Address regulatory follow-up and audit findings.

**Actions**:
1. **Respond to Regulator Inquiries**:
   - Provide additional information requested
   - Submit corrective action plans
   - Attend hearings or meetings if required

2. **Cooperate with Investigations**:
   - Law enforcement (if involved)
   - Regulators
   - Payment card brands (if PCI breach)
   - Cyber insurance investigators

3. **Internal Audit**:
   - Security control audit
   - Privacy practice review
   - Third-party risk assessment
   - Incident response plan review

4. **External Audit** (if required):
   - HIPAA compliance audit
   - PCI DSS validation
   - SOC 2 Type II re-examination
   - ISO 27001 re-certification

**Output**: Compliance obligations met, audits passed

---

#### Step 6.3: Long-Term Security Transformation (3-12 months)
**Objective**: Implement sustainable security improvements.

**Actions**:
1. **Security Program Maturity**:
   - Adopt formal frameworks (NIST CSF, ISO 27001)
   - Implement security metrics and KPIs
   - Regular security assessments
   - Continuous monitoring program

2. **Data Protection Program**:
   - Data discovery and classification
   - Data minimization (don't keep what you don't need)
   - Privacy by design for new systems
   - Regular privacy impact assessments

3. **Third-Party Risk Management**:
   - Vendor security assessments
   - Contractual security requirements
   - Regular vendor audits
   - Supply chain risk management

4. **Security Culture**:
   - Security awareness training
   - Phishing simulations
   - Insider threat program
   - Security champions program

5. **Incident Readiness**:
   - Regular IR plan updates
   - Tabletop exercises (quarterly)
   - Full breach simulation (annually)
   - IR team training
   - Vendor relationships (forensics, legal, PR)

**Output**: Mature, sustainable security program

---

## Incident Response Checklist

### ✅ Detection & Analysis (0-2 hours)
- [ ] Breach response team activated (CISO, Legal, Compliance, Forensics, PR)
- [ ] Attorney-client privilege established
- [ ] Initial incident documentation created
- [ ] Affected systems identified
- [ ] Data types compromised identified
- [ ] Number of affected individuals determined
- [ ] Data sensitivity assessed (encrypted? anonymized?)
- [ ] Breach timeline reconstructed
- [ ] Attack vector identified
- [ ] Forensic evidence collected and preserved
- [ ] Chain of custody established
- [ ] Cyber insurance notified

### ✅ Containment (1-4 hours)
- [ ] Attacker access blocked (accounts disabled, IPs blocked)
- [ ] Affected systems isolated
- [ ] Data exfiltration stopped
- [ ] Backups secured and verified clean
- [ ] All affected user passwords reset
- [ ] All admin/service account passwords reset
- [ ] MFA enabled for all users
- [ ] API keys and tokens revoked
- [ ] Exploited vulnerability patched
- [ ] Systems hardened
- [ ] Compensating controls deployed

### ✅ Legal & Regulatory (2-72 hours)
- [ ] Applicable regulations identified (GDPR, HIPAA, CCPA, etc.)
- [ ] Notification requirements determined
- [ ] Notification timelines documented
- [ ] Exceptions evaluated (encryption, etc.)
- [ ] Regulatory notifications submitted (within 72 hours for GDPR)
- [ ] Law enforcement contacted (if appropriate)
- [ ] Cyber insurance claim filed
- [ ] Attorney work product privilege maintained

### ✅ Individual Notification (1-60 days)
- [ ] Notification letter drafted and legal-reviewed
- [ ] Translations prepared
- [ ] Credit monitoring service procured
- [ ] Call center set up and staff trained
- [ ] Notification sent to all affected individuals (email/postal)
- [ ] Substitute notice published (if applicable)
- [ ] Dedicated breach response website created
- [ ] FAQ document published
- [ ] Public notification completed (if required)
- [ ] Press release issued (if appropriate)
- [ ] Media spokesperson prepared

### ✅ Eradication & Recovery (1-4 weeks)
- [ ] Attacker fully evicted from environment
- [ ] Compromised systems rebuilt or restored
- [ ] Data encryption implemented
- [ ] DLP solution deployed
- [ ] Database activity monitoring enabled
- [ ] Network segmentation implemented
- [ ] Enhanced monitoring deployed (EDR, SIEM rules)
- [ ] Penetration testing completed
- [ ] Vulnerability assessment completed
- [ ] Systems returned to production with monitoring

### ✅ Post-Incident (1-6 months)
- [ ] Lessons learned meeting conducted
- [ ] Incident report completed and distributed
- [ ] Total breach cost calculated
- [ ] Regulator inquiries responded to
- [ ] Law enforcement investigation supported
- [ ] Internal audit completed
- [ ] External audit completed (if required)
- [ ] Long-term security improvements implemented
- [ ] Data protection program enhanced
- [ ] Third-party risk management improved
- [ ] IR plan updated based on lessons learned
- [ ] Tabletop exercise scheduled
- [ ] Board of directors briefed

---

## Key Roles and Responsibilities

| Role | Responsibilities |
|------|-----------------|
| **CISO** | Incident commander, executive decisions, board reporting |
| **Legal Counsel** | Regulatory obligations, attorney-client privilege, contracts, litigation |
| **Compliance Officer** | Notification requirements, regulator liaison, documentation |
| **Privacy Officer / DPO** | Individual notifications, privacy impact assessment, regulator coordination |
| **Forensics Team** | Evidence collection, timeline reconstruction, attack analysis |
| **IT/Security Ops** | Containment, remediation, system restoration |
| **Communications/PR** | Public statements, media relations, reputation management |
| **HR** | Insider threat cases, employee notifications, workforce communications |
| **Risk/Insurance** | Cyber insurance claim, risk assessment, financial impact |
| **CEO** | Executive decisions, major communications, board reporting |

---

## Cost Estimates

**Average Cost of Data Breach (2024 data)**:
- Global average: $4.45 million per breach
- United States: $9.48 million per breach
- Healthcare sector: $10.93 million per breach

**Cost Components**:
- Detection and escalation: ~29%
- Notification: ~14%
- Post-breach response: ~27%
- Lost business: ~30%

**Per-Record Costs**:
- Average: $165 per compromised record
- Healthcare: $429 per record
- Financial: $277 per record

**Additional Costs**:
- Credit monitoring: $15-25 per person per year
- Forensic investigation: $100,000 - $1,000,000+
- Legal fees: $500,000 - $5,000,000+
- Regulatory fines: Varies widely (GDPR: up to €20M or 4% revenue)

---

## Red Flags: Escalate Immediately If...

- 🚨 More than 10,000 individuals affected
- 🚨 PHI or payment card data compromised
- 🚨 Children's data involved (COPPA)
- 🚨 Ransomware with confirmed exfiltration
- 🚨 Nation-state actor suspected
- 🚨 Insider threat with malicious intent
- 🚨 Attacker still has access and is actively exfiltrating
- 🚨 Data is already being sold on dark web
- 🚨 Media has learned of the breach before notification complete

---

## References and Resources

### Regulations & Guidance
- **GDPR**: https://gdpr.eu/
- **HIPAA Breach Notification Rule**: https://www.hhs.gov/hipaa/for-professionals/breach-notification/
- **CCPA**: https://oag.ca.gov/privacy/ccpa
- **NIST SP 800-61**: Computer Security Incident Handling Guide
- **State Breach Notification Laws**: https://www.ncsl.org/technology-and-communication/security-breach-notification-laws

### Notification Tools
- **HHS Breach Portal** (HIPAA): https://ocrportal.hhs.gov/ocr/breach/wizard_breach.jsf
- **State AG Contacts**: Varies by state
- **FBI IC3**: https://www.ic3.gov

### Forensics & Investigation
- CrowdStrike, Mandiant, Kroll, Stroz Friedberg, Trustwave

### Legal
- Privacy-specialized law firms (Morrison Foerster, DLA Piper, Hunton Andrews Kurth, etc.)

### Credit Monitoring Services
- Experian, Equifax, TransUnion, Identity Guard, LifeLock

### Free Resources for Victims
- **Free Credit Reports**: https://www.annualcreditreport.com
- **FTC Identity Theft Resources**: https://www.identitytheft.gov
- **Credit Freeze Instructions**: https://www.consumer.ftc.gov/articles/what-know-about-credit-freezes-and-fraud-alerts

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Feb 2026 | Security Team + Legal | Initial version |

---

**END OF PLAYBOOK**

**CRITICAL REMINDER**: 
- Involve Legal and Compliance teams IMMEDIATELY upon breach detection
- Protect attorney-client privilege by having legal direct the investigation
- Meet notification timelines - they are LEGAL OBLIGATIONS with severe penalties
- Document EVERYTHING - you will need detailed records for regulators and litigation

**Emergency Contacts**: 
- **SOC**: [INSERT NUMBER]
- **Legal (24/7)**: [INSERT NUMBER]
- **CISO**: [INSERT NUMBER]
- **Forensics Firm**: [INSERT NUMBER]
- **Cyber Insurance**: [INSERT NUMBER]
