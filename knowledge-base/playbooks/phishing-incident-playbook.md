# Phishing Incident Response Playbook

## Metadata
- **Incident Type**: Phishing / Social Engineering
- **Severity Range**: Low to High
- **Framework References**: NIST SP 800-61 Rev. 2, Anti-Phishing Working Group (APWG)
- **Last Updated**: February 2026
- **Version**: 1.0

---

## Executive Summary

This playbook provides a structured approach to responding to phishing incidents, including email phishing, spear phishing, whaling, and smishing (SMS phishing). The goal is to rapidly identify compromised users, prevent further attacks, and educate the organization to reduce future risk.

**Key Objectives:**
- Identify and contain phishing campaign within 30 minutes
- Block malicious senders and URLs immediately
- Identify compromised credentials or systems
- Remove phishing emails from all mailboxes
- Educate users to prevent recurrence

---

## Triggers (When to Use This Playbook)

Use this playbook when:
- ✅ User reports suspicious email with malicious link or attachment
- ✅ Email security gateway flags phishing attempt
- ✅ Multiple users report similar suspicious emails
- ✅ User clicked phishing link or opened malicious attachment
- ✅ Credentials entered on fake login page
- ✅ CEO/executive receives targeted spear phishing email (whaling)
- ✅ Wire transfer requested via suspicious email
- ✅ SMS phishing (smishing) campaign detected
- ✅ Brand impersonation detected (fake company email)

---

## Incident Response Phases

### Phase 1: Detection & Analysis (Time: 0-30 minutes)

#### Step 1.1: Initial Triage (5 minutes)
**Objective**: Quickly assess the phishing incident scope and potential impact.

**Actions**:
1. **Collect Initial Information**:
   - Email subject line and sender address
   - Date/time email received
   - Number of recipients (if known)
   - Reported by user or detected by system?
   - Has anyone clicked the link or opened attachment?
   - Has anyone entered credentials?

2. **Document in Ticket**:
   - Incident ID
   - Reporter name and contact
   - Initial timestamp
   - Affected user(s)

3. **Determine Severity**:
   - **Low**: Generic phishing, no clicks, caught by filter
   - **Medium**: Targeted phishing, some clicks, no credential compromise
   - **High**: Credentials compromised, wire transfer request, executive targeted

**Output**: Incident documented with initial severity

---

#### Step 1.2: Email Analysis (15 minutes)
**Objective**: Analyze the phishing email to extract IOCs and understand the attack.

**Actions**:
1. **Obtain Email Sample**:
   - Export full email with headers (.eml or .msg format)
   - Get from user's mailbox or quarantine
   - Store in secure incident folder

2. **Analyze Email Headers**:
   ```
   Key headers to check:
   - From: (sender address - check if spoofed)
   - Reply-To: (often differs from From)
   - Return-Path: (actual sending server)
   - X-Originating-IP: (sender's IP address)
   - Received: (mail server path)
   - SPF/DKIM/DMARC: (authentication results)
   ```

3. **Analyze Email Body**:
   - Suspicious language (urgency, threats, grammar errors)
   - Links (hover to see actual URL, check redirects)
   - Attachments (file name, extension, hash)
   - Impersonation tactics (fake logos, branding)

4. **Extract Indicators of Compromise (IOCs)**:
   - Sender email address and domain
   - Reply-To address
   - Originating IP addresses
   - All URLs in email (including hidden/obfuscated)
   - Attachment file hashes (MD5, SHA-256)
   - Malicious domains

5. **Check URLs/Files**:
   - Submit URLs to VirusTotal, URLScan.io
   - Submit attachments to VirusTotal, Hybrid Analysis
   - Check domain registration (WHOIS) - newly registered is suspicious
   - Check SSL certificate (if HTTPS) - self-signed or mismatch is suspicious

**Output**: IOC list with email headers, URLs, attachment hashes

---

#### Step 1.3: Victim Identification (10 minutes)
**Objective**: Identify all recipients and users who interacted with the phishing email.

**Actions**:
1. **Search Email Gateway Logs**:
   - Find all recipients of the phishing email
   - Check how many emails were delivered vs quarantined
   - Identify delivery timestamps

2. **Check Email Security Tool**:
   - Query for similar emails (same sender, subject pattern)
   - Check click-tracking data (if available)
   - Identify users who clicked links

3. **Contact Reporting Users**:
   - Call or email users who reported
   - Ask: "Did you click the link?"
   - Ask: "Did you enter credentials or download attachment?"
   - Ask: "What action did you take after clicking?"

4. **Check Web Proxy Logs**:
   - Search for access to malicious URLs
   - Identify which users visited phishing site
   - Check timestamps and duration

**Output**: Complete list of recipients and users who clicked/interacted

---

### Phase 2: Containment (Time: 30-60 minutes)

#### Step 2.1: Immediate Blocking (10 minutes) 🚨 CRITICAL
**Objective**: Block the phishing attack immediately to prevent further victims.

**Actions**:
1. **Block Sender at Email Gateway**:
   - Add sender email address to blocklist
   - Add sender domain to blocklist
   - Block sending IP addresses

2. **Block Malicious URLs**:
   - Add URLs to web proxy blacklist
   - Add domains to DNS blacklist
   - Update URL filtering rules

3. **Block Attachments**:
   - Add file hashes to email gateway blacklist
   - Block file name patterns (if applicable)
   - Update anti-malware signatures

4. **Update Email Security Rules**:
   - Create custom detection rule for this campaign
   - Increase scanning sensitivity for similar patterns

**Output**: Phishing attack blocked at multiple layers

---

#### Step 2.2: Email Removal (20 minutes)
**Objective**: Remove phishing emails from all mailboxes.

**Actions**:
1. **Search All Mailboxes**:
   ```powershell
   # Exchange Online PowerShell example
   Get-Mailbox -ResultSize Unlimited | Search-Mailbox -SearchQuery 'Subject:"Urgent: Account Verification Required"' -TargetMailbox "DiscoveryMailbox" -TargetFolder "PhishingIncident-2026-02-05" -LogLevel Full
   ```

2. **Delete Phishing Emails**:
   - Use email admin tools to delete from all mailboxes
   - Move to admin-controlled folder (don't just delete - preserve evidence)
   - Confirm deletion with sample of users

3. **Quarantine Related Emails**:
   - Search for similar emails (same sender, subject pattern)
   - Quarantine for review

4. **Document**:
   - Number of emails removed
   - Mailboxes affected
   - Deletion timestamp

**Output**: Phishing emails removed from all mailboxes

---

#### Step 2.3: User Account Security (30 minutes)
**Objective**: Secure accounts of users who may have been compromised.

**Actions**:
1. **For Users Who Entered Credentials**:
   - **Immediately reset password**
   - Disable account temporarily (if high risk)
   - Revoke all active sessions/tokens
   - Enable MFA if not already enabled
   - Check for suspicious account activity:
     - Recent logins (location, time, device)
     - Email forwarding rules
     - Mailbox delegation changes
     - Recent sent emails
     - File access/downloads

2. **For Users Who Clicked Link Only**:
   - Monitor account for suspicious activity
   - Notify user to watch for strange behavior
   - Consider password reset if phishing site mimicked login page

3. **For Users Who Downloaded Attachment**:
   - Follow Malware Incident Playbook
   - Isolate system if malware suspected
   - Run EDR/AV scan

4. **Check for Lateral Movement**:
   - Review authentication logs for affected users
   - Check for unusual access to systems/data
   - Review VPN connections
   - Check admin account usage (if privileged user affected)

**Output**: Compromised accounts secured and monitored

---

### Phase 3: Eradication (Time: 1-2 hours)

#### Step 3.1: Credential Reset (30 minutes)
**Objective**: Ensure attacker cannot use stolen credentials.

**Actions**:
1. **Password Reset for Compromised Users**:
   - Force password change on next login
   - Ensure new password meets complexity requirements
   - Cannot reuse previous passwords

2. **Revoke Active Sessions**:
   - End all browser sessions
   - Revoke OAuth tokens
   - Clear cached credentials

3. **MFA Enrollment** (if not already enrolled):
   - Require MFA registration
   - Recommend authenticator app (more secure than SMS)
   - Provide setup instructions

4. **Check Connected Apps**:
   - Review third-party app permissions
   - Revoke suspicious OAuth grants
   - Check for unusual API access

**Output**: All affected credentials secured with MFA

---

#### Step 3.2: Malicious Infrastructure Takedown (30 minutes - 1 hour)
**Objective**: Attempt to disable the phishing infrastructure.

**Actions**:
1. **Report to Hosting Provider**:
   - Identify hosting provider (WHOIS lookup)
   - Email abuse contact (abuse@domain.com)
   - Request site takedown
   - Provide evidence (email, screenshots)

2. **Report to Domain Registrar**:
   - Identify registrar (WHOIS)
   - File abuse complaint
   - Request domain suspension

3. **Report to Phishing Databases**:
   - PhishTank (www.phishtank.com)
   - Google Safe Browsing
   - Microsoft SmartScreen
   - APWG (reportphishing@apwg.org)

4. **Report to Brand Owner** (if brand impersonation):
   - Contact impersonated company (if external brand)
   - Provide evidence for their legal action

5. **Law Enforcement** (if severe):
   - File report with FBI IC3 (for US incidents)
   - Contact local cybercrime unit
   - Provide full evidence package

**Output**: Phishing site reported and takedown initiated

---

#### Step 3.3: Remediate Compromised Data (varies)
**Objective**: Address any data accessed or exfiltrated by the attacker.

**Actions**:
1. **Identify Accessed Data**:
   - Review mailbox access logs
   - Check file server access
   - Review database queries (if database credentials stolen)
   - Check cloud storage access (OneDrive, SharePoint)

2. **Assess Data Sensitivity**:
   - PII (Personally Identifiable Information)
   - PHI (Protected Health Information)
   - Financial data
   - Intellectual property
   - Customer data

3. **Data Breach Notification** (if applicable):
   - Consult with Legal team
   - Determine regulatory requirements (GDPR, HIPAA, CCPA, etc.)
   - Prepare breach notification
   - Notify affected individuals (if required)
   - Notify regulators (if required)

4. **Change Sensitive Information**:
   - Rotate API keys if exposed
   - Change system passwords if accessed
   - Revoke certificates if compromised

**Output**: Data breach assessed, notifications completed if required

---

### Phase 4: Recovery (Time: 1-2 days)

#### Step 4.1: User Notification and Education (1 hour)
**Objective**: Inform users and provide education to prevent future incidents.

**Actions**:
1. **Send Organization-Wide Alert**:
   ```
   Subject: SECURITY ALERT: Phishing Campaign Detected

   We detected a phishing campaign targeting our organization. 
   The malicious emails have been removed from mailboxes.

   Email characteristics:
   - Subject: "Urgent: Account Verification Required"
   - Sender: appears to be from IT Support
   - Requests login credentials

   If you received this email:
   - DO NOT click links or open attachments
   - Report to security@company.com
   - If you clicked or entered credentials, contact SOC immediately

   Red flags to watch for:
   - Urgent or threatening language
   - Requests for credentials or money
   - Suspicious sender addresses
   - Poor grammar/spelling
   - Unusual requests from executives

   Report suspicious emails: security@company.com
   ```

2. **Direct Communication with Affected Users**:
   - Call or email users who interacted with phishing
   - Confirm password has been changed
   - Verify MFA is enabled
   - Provide 1-on-1 security coaching

3. **Schedule Security Awareness Training**:
   - Mandatory for all affected users
   - Recommended for entire organization
   - Cover phishing red flags
   - Demo phishing examples
   - Practice reporting procedure

4. **Launch Phishing Simulation** (within 2 weeks):
   - Test user awareness
   - Identify users needing additional training
   - Measure improvement over time

**Output**: Users informed and educated

---

#### Step 4.2: Enhanced Monitoring (30 days)
**Objective**: Monitor for follow-up attacks or account misuse.

**Actions**:
1. **Monitor Affected User Accounts**:
   - Daily review of login activity
   - Alert on logins from new locations/devices
   - Monitor for email forwarding rule creation
   - Check for unusual file downloads/uploads

2. **Email Gateway Monitoring**:
   - Watch for similar phishing patterns
   - Monitor for sender reputation changes
   - Track email security rule effectiveness

3. **Web Traffic Monitoring**:
   - Watch for access to similar phishing domains
   - Monitor for C2 communication (if malware involved)

4. **Threat Intelligence**:
   - Subscribe to phishing threat feeds
   - Monitor for company name in phishing databases
   - Track related phishing campaigns

**Output**: Enhanced monitoring in place for 30 days

---

### Phase 5: Post-Incident Activities (Time: 1-3 days)

#### Step 5.1: Lessons Learned (1 hour)
**Objective**: Improve security posture to prevent future phishing attacks.

**Agenda**:
1. **What Happened**:
   - How did phishing email bypass filters?
   - Why did users click/enter credentials?
   - What was the attacker's goal?
   - What was the business impact?

2. **What Went Well**:
   - User reporting (if applicable)
   - Detection speed
   - Response effectiveness
   - Communication

3. **What Could Improve**:
   - Email filtering rules
   - User awareness
   - Response procedures
   - Detection tools

4. **Action Items**:
   - Technical improvements (filters, MFA, etc.)
   - Process improvements
   - Training enhancements
   - Budget needs

**Output**: Action items with owners and deadlines

---

#### Step 5.2: Technical Improvements (ongoing)
**Objective**: Implement controls to prevent similar phishing attacks.

**Actions**:
1. **Email Security Enhancements**:
   - Tune email gateway rules based on this incident
   - Implement DMARC policy (reject)
   - Enable advanced threat protection
   - Deploy link protection (URL rewriting)
   - Implement attachment sandboxing
   - Enable external email warning banners

2. **Authentication Hardening**:
   - Roll out MFA to all users (if not universal)
   - Implement conditional access policies
   - Require passwordless authentication for privileged accounts
   - Deploy FIDO2 security keys for high-risk users

3. **Email Client Protections**:
   - Disable automatic link preview
   - Block macros in Office documents from internet
   - Implement protected view for email attachments

4. **Network Protections**:
   - Implement DNS filtering
   - Deploy web isolation/browser isolation
   - Improve URL filtering rules

5. **User Reporting**:
   - Deploy phishing report button in email client
   - Integrate with SOAR for automated response
   - Provide feedback to users who report

**Output**: Technical improvements implemented

---

#### Step 5.3: Security Awareness Program Enhancement (ongoing)
**Objective**: Build a security-aware culture to resist phishing.

**Actions**:
1. **Regular Training**:
   - Quarterly security awareness training
   - New hire security orientation
   - Annual refresher for all staff
   - Executive-specific training (whaling prevention)

2. **Phishing Simulations**:
   - Monthly simulated phishing campaigns
   - Varied tactics (email, SMS, phone)
   - Track click rates and reporting rates
   - Provide immediate feedback/training

3. **Communication Campaign**:
   - Monthly security tips newsletter
   - Posters/signage in office
   - Slack/Teams security channel
   - Share real phishing examples (sanitized)

4. **Gamification**:
   - Rewards for users who report phishing
   - "Security Champion" program
   - Leaderboard for phishing detection

5. **Metrics Tracking**:
   - Phishing click rate (goal: <5%)
   - Reporting rate (goal: >70%)
   - Time to report (goal: <15 minutes)

**Output**: Improved security awareness culture

---

## Incident Response Checklist

### ✅ Detection & Analysis
- [ ] Incident documented with ID and timestamp
- [ ] Phishing email sample obtained
- [ ] Email headers analyzed (sender, originating IP, authentication)
- [ ] Email body analyzed (links, attachments)
- [ ] IOCs extracted (sender, URLs, file hashes, domains)
- [ ] URLs checked in VirusTotal/URLScan
- [ ] Attachments checked in VirusTotal/Sandbox
- [ ] All recipients identified
- [ ] Users who clicked/interacted identified
- [ ] Severity determined
- [ ] Stakeholders notified

### ✅ Containment
- [ ] Sender email/domain blocked at gateway
- [ ] Malicious URLs blocked at web proxy
- [ ] Attachment hashes blocked
- [ ] Phishing emails removed from all mailboxes
- [ ] Similar emails quarantined
- [ ] Compromised user accounts identified
- [ ] Passwords reset for compromised accounts
- [ ] MFA enabled for affected users
- [ ] Active sessions revoked
- [ ] Account activity reviewed for suspicious behavior

### ✅ Eradication
- [ ] All affected user passwords changed
- [ ] MFA enforced
- [ ] OAuth tokens revoked
- [ ] Suspicious email rules removed
- [ ] Phishing site reported to hosting provider
- [ ] Phishing domain reported to registrar
- [ ] URLs submitted to phishing databases
- [ ] Brand owner notified (if impersonation)
- [ ] Law enforcement contacted (if appropriate)
- [ ] Data breach assessment completed

### ✅ Recovery
- [ ] Organization-wide security alert sent
- [ ] Affected users contacted directly
- [ ] Security awareness training scheduled
- [ ] Phishing simulation campaign planned
- [ ] Enhanced monitoring configured
- [ ] Email gateway rules updated
- [ ] Threat intelligence feeds subscribed

### ✅ Post-Incident
- [ ] Lessons learned meeting conducted
- [ ] Incident report completed
- [ ] Email filtering improvements implemented
- [ ] MFA rollout plan updated
- [ ] Security awareness program enhanced
- [ ] Phishing report button deployed
- [ ] Action items tracked to completion

---

## Key Roles and Responsibilities

| Role | Responsibilities |
|------|-----------------|
| **SOC Analyst** | Email analysis, IOC extraction, user identification, monitoring |
| **Email Administrator** | Email removal, sender blocking, gateway rule updates |
| **Identity Team** | Password resets, MFA enrollment, account security |
| **Security Awareness** | User education, training programs, phishing simulations |
| **Communications** | Organization alerts, executive communications |
| **Legal/Compliance** | Data breach notification, regulatory requirements |
| **CISO** | Escalation decisions, stakeholder management |

---

## Time Estimates by Severity

| Severity | Detection | Containment | Eradication | Recovery | Total |
|----------|-----------|-------------|-------------|----------|-------|
| **Low** (caught by filter, no clicks) | 15 min | 15 min | 30 min | 1 hour | ~2 hours |
| **Medium** (clicks but no credential compromise) | 30 min | 30 min | 1 hour | 2 hours | ~4 hours |
| **High** (credentials compromised or executive targeted) | 30 min | 1 hour | 2 hours | 4 hours | ~8 hours |

---

## Escalation Criteria

Escalate to **HIGH** priority if:
- 🚨 Credentials confirmed compromised
- 🚨 Executive/C-level targeted (whaling)
- 🚨 Wire transfer or financial fraud attempted
- 🚨 Sensitive data accessed
- 🚨 Malware delivered via phishing
- 🚨 Business Email Compromise (BEC) indicators
- 🚨 Attacker has established persistence

---

## Common Phishing Types

| Type | Description | Target | Risk Level |
|------|-------------|--------|------------|
| **Spear Phishing** | Targeted, personalized phishing | Specific individuals | High |
| **Whaling** | Phishing targeting executives | C-level, executives | Critical |
| **Clone Phishing** | Legitimate email duplicated with malicious links | Previous email recipients | Medium |
| **BEC (Business Email Compromise)** | CEO fraud, invoice fraud, payroll redirect | Finance, executives | Critical |
| **Smishing** | Phishing via SMS | Mobile users | Medium |
| **Vishing** | Phishing via phone call | All users | Medium |
| **Credential Harvesting** | Fake login pages steal credentials | All users | High |

---

## References and Resources

### Frameworks
- **NIST SP 800-61 Rev. 2**: Computer Security Incident Handling Guide
- **Anti-Phishing Working Group (APWG)**: Phishing trends and guidance
- **M-3-16-04**: Federal Cybersecurity Incident Response

### Tools
- **Email Analysis**: Message Header Analyzer, MxToolbox
- **URL Analysis**: VirusTotal, URLScan.io, Unfurl
- **Phishing Databases**: PhishTank, OpenPhish, Google Safe Browsing
- **Training**: KnowBe4, Cofense, Proofpoint Security Awareness

### Reporting
- **APWG**: reportphishing@apwg.org
- **FBI IC3**: https://www.ic3.gov
- **PhishTank**: https://www.phishtank.com
- **US-CERT**: https://www.us-cert.gov/report-phishing

### Standards
- **DMARC**: Email authentication policy
- **SPF**: Sender Policy Framework
- **DKIM**: DomainKeys Identified Mail

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Feb 2026 | Security Team | Initial version |

---

**END OF PLAYBOOK**

**Remember**: User education is your best defense against phishing. Invest in security awareness training and make reporting easy.

**Emergency Contact**: SOC Hotline: [INSERT NUMBER] | Email: soc@company.com | Phishing Reports: phishing-report@company.com
