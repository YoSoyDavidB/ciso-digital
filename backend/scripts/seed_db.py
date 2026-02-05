#!/usr/bin/env python3
"""
Database Seeding Script for CISO Digital Risk Assessment Platform.

This script populates the database with realistic test data for development
and testing purposes. It creates sample risks with varied severities, statuses,
and categories.

Usage:
    python scripts/seed_db.py

Features:
    - Creates 10 realistic risk records
    - Idempotent (checks for existing data)
    - Uses async SQLAlchemy
    - Shows progress during execution
    - Safe to run multiple times
"""

import asyncio
import sys
from datetime import date, timedelta
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session_local
from app.shared.models.risk import Risk
from app.shared.models.enums import (
    RiskCategory,
    RiskLikelihood,
    RiskSeverity,
    RiskStatus,
)


# Sample risk data with realistic scenarios
SAMPLE_RISKS = [
    {
        "title": "Unpatched SQL Injection Vulnerability in Web Application",
        "description": (
            "Critical SQL injection vulnerability discovered in the main web application's "
            "login endpoint. Attackers could potentially access or modify sensitive customer data. "
            "The vulnerability exists in the user authentication module and has been confirmed "
            "through penetration testing. Immediate patching required."
        ),
        "severity": RiskSeverity.CRITICAL,
        "likelihood": RiskLikelihood.HIGH,
        "impact_score": 9.8,
        "status": RiskStatus.IN_PROGRESS,
        "category": RiskCategory.TECHNICAL,
        "assigned_to": "security-team@company.com",
        "mitigation_plan": (
            "1. Apply emergency patch to sanitize SQL inputs\n"
            "2. Implement prepared statements across all database queries\n"
            "3. Deploy Web Application Firewall (WAF) rules\n"
            "4. Conduct full code review of authentication module\n"
            "5. Schedule security training for development team"
        ),
        "deadline": date.today() + timedelta(days=7),
    },
    {
        "title": "Missing Multi-Factor Authentication on Admin Portal",
        "description": (
            "The administrative portal lacks multi-factor authentication (MFA), exposing "
            "privileged accounts to credential theft attacks. Current authentication relies "
            "solely on username and password, which is insufficient for admin-level access. "
            "Recent phishing campaigns targeting employees increase the risk."
        ),
        "severity": RiskSeverity.HIGH,
        "likelihood": RiskLikelihood.MEDIUM,
        "impact_score": 8.5,
        "status": RiskStatus.OPEN,
        "category": RiskCategory.TECHNICAL,
        "assigned_to": "infosec@company.com",
        "mitigation_plan": (
            "1. Implement MFA using TOTP (Time-based One-Time Password)\n"
            "2. Enforce MFA for all admin accounts\n"
            "3. Configure backup authentication methods\n"
            "4. Update access policies documentation\n"
            "5. Communicate changes to all administrators"
        ),
        "deadline": date.today() + timedelta(days=30),
    },
    {
        "title": "Outdated SSL/TLS Certificates on Production Servers",
        "description": (
            "Several production servers are using SSL/TLS certificates that are approaching "
            "expiration. Some certificates will expire in less than 30 days, which could cause "
            "service disruptions and security warnings for users. Additionally, some servers "
            "still support TLS 1.0/1.1 which are deprecated protocols."
        ),
        "severity": RiskSeverity.MEDIUM,
        "likelihood": RiskLikelihood.HIGH,
        "impact_score": 6.5,
        "status": RiskStatus.IN_PROGRESS,
        "category": RiskCategory.OPERATIONAL,
        "assigned_to": "devops@company.com",
        "mitigation_plan": (
            "1. Renew all expiring certificates immediately\n"
            "2. Implement automated certificate renewal with Let's Encrypt\n"
            "3. Disable TLS 1.0 and 1.1 support\n"
            "4. Configure minimum TLS version to 1.2\n"
            "5. Set up monitoring alerts for certificate expiration"
        ),
        "deadline": date.today() + timedelta(days=14),
    },
    {
        "title": "Insufficient Data Backup and Disaster Recovery Plan",
        "description": (
            "Current backup procedures are inconsistent and lack proper testing. The disaster "
            "recovery plan hasn't been updated in over 2 years and recovery time objectives (RTO) "
            "are undefined. Recent audits revealed that some critical databases are not included "
            "in the backup schedule."
        ),
        "severity": RiskSeverity.HIGH,
        "likelihood": RiskLikelihood.MEDIUM,
        "impact_score": 8.0,
        "status": RiskStatus.OPEN,
        "category": RiskCategory.OPERATIONAL,
        "assigned_to": "infrastructure@company.com",
        "mitigation_plan": (
            "1. Conduct comprehensive backup audit\n"
            "2. Implement automated daily backups for all critical systems\n"
            "3. Update disaster recovery plan with clear RTOs and RPOs\n"
            "4. Schedule quarterly DR drills\n"
            "5. Document backup verification procedures"
        ),
        "deadline": date.today() + timedelta(days=60),
    },
    {
        "title": "Non-Compliant GDPR Data Processing Procedures",
        "description": (
            "Current data processing procedures do not fully comply with GDPR requirements. "
            "Issues include: missing data processing agreements with third-party vendors, "
            "insufficient documentation of data flows, and lack of automated data retention "
            "policies. Recent legal review highlighted potential regulatory risks."
        ),
        "severity": RiskSeverity.HIGH,
        "likelihood": RiskLikelihood.MEDIUM,
        "impact_score": 7.5,
        "status": RiskStatus.OPEN,
        "category": RiskCategory.COMPLIANCE,
        "assigned_to": "compliance@company.com",
        "mitigation_plan": (
            "1. Review and update all data processing agreements\n"
            "2. Create comprehensive data flow documentation\n"
            "3. Implement automated data retention and deletion\n"
            "4. Conduct GDPR compliance training for all staff\n"
            "5. Establish quarterly compliance audits"
        ),
        "deadline": date.today() + timedelta(days=90),
    },
    {
        "title": "Weak Password Policy Across Organization",
        "description": (
            "Current password policy allows weak passwords (minimum 6 characters, no complexity "
            "requirements). Password reuse is common, and there's no forced password rotation. "
            "Recent credential stuffing attacks exploited these weak passwords to gain unauthorized "
            "access to employee accounts."
        ),
        "severity": RiskSeverity.MEDIUM,
        "likelihood": RiskLikelihood.HIGH,
        "impact_score": 6.0,
        "status": RiskStatus.IN_PROGRESS,
        "category": RiskCategory.TECHNICAL,
        "assigned_to": "iam-team@company.com",
        "mitigation_plan": (
            "1. Enforce minimum 12-character passwords with complexity requirements\n"
            "2. Implement password history to prevent reuse\n"
            "3. Enable password expiration after 90 days\n"
            "4. Deploy password manager to all employees\n"
            "5. Monitor for compromised credentials using breach databases"
        ),
        "deadline": date.today() + timedelta(days=45),
    },
    {
        "title": "Unencrypted Sensitive Data in Cloud Storage",
        "description": (
            "Multiple S3 buckets containing sensitive customer data (PII, financial information) "
            "are not using encryption at rest. While access controls are in place, the lack of "
            "encryption violates internal security policies and compliance requirements. "
            "This was discovered during a security audit."
        ),
        "severity": RiskSeverity.CRITICAL,
        "likelihood": RiskLikelihood.MEDIUM,
        "impact_score": 9.0,
        "status": RiskStatus.OPEN,
        "category": RiskCategory.TECHNICAL,
        "assigned_to": "cloud-security@company.com",
        "mitigation_plan": (
            "1. Enable S3 bucket encryption using AWS KMS\n"
            "2. Rotate encryption keys quarterly\n"
            "3. Audit all cloud storage for encryption compliance\n"
            "4. Implement automated compliance checks\n"
            "5. Update cloud security policies and training"
        ),
        "deadline": date.today() + timedelta(days=21),
    },
    {
        "title": "Insufficient Logging and Monitoring for Security Events",
        "description": (
            "Current logging infrastructure doesn't capture sufficient security events, and "
            "log retention is only 7 days. There's no centralized SIEM solution, making incident "
            "detection and forensic analysis extremely difficult. Recent security incidents "
            "couldn't be fully investigated due to missing logs."
        ),
        "severity": RiskSeverity.MEDIUM,
        "likelihood": RiskLikelihood.MEDIUM,
        "impact_score": 7.0,
        "status": RiskStatus.OPEN,
        "category": RiskCategory.OPERATIONAL,
        "assigned_to": "security-ops@company.com",
        "mitigation_plan": (
            "1. Deploy centralized SIEM solution (Splunk/ELK Stack)\n"
            "2. Extend log retention to 1 year for critical systems\n"
            "3. Configure comprehensive security event logging\n"
            "4. Implement automated alerting for suspicious activities\n"
            "5. Establish 24/7 security monitoring capability"
        ),
        "deadline": date.today() + timedelta(days=120),
    },
    {
        "title": "Outdated Third-Party Dependencies with Known Vulnerabilities",
        "description": (
            "Automated dependency scanning revealed 47 outdated libraries and frameworks with "
            "known security vulnerabilities, including 12 critical and 23 high-severity issues. "
            "Some dependencies are 3+ versions behind current stable releases. This significantly "
            "increases the attack surface of our applications."
        ),
        "severity": RiskSeverity.HIGH,
        "likelihood": RiskLikelihood.HIGH,
        "impact_score": 8.0,
        "status": RiskStatus.MITIGATED,
        "category": RiskCategory.TECHNICAL,
        "assigned_to": "development@company.com",
        "mitigation_plan": (
            "1. Update all critical dependencies to latest stable versions\n"
            "2. Implement automated dependency scanning in CI/CD pipeline\n"
            "3. Establish monthly dependency review process\n"
            "4. Create policy for maximum allowed dependency age\n"
            "5. Configure automated alerts for new vulnerabilities"
        ),
        "deadline": date.today() - timedelta(days=10),  # Already past deadline but mitigated
    },
    {
        "title": "Lack of Security Awareness Training for Employees",
        "description": (
            "Employee security awareness training hasn't been conducted in over 18 months. "
            "Recent phishing simulation campaigns showed 35% of employees clicking malicious links. "
            "This represents a significant human-factor vulnerability that attackers actively exploit. "
            "Industry best practices recommend quarterly training."
        ),
        "severity": RiskSeverity.MEDIUM,
        "likelihood": RiskLikelihood.HIGH,
        "impact_score": 6.5,
        "status": RiskStatus.ACCEPTED,
        "category": RiskCategory.OPERATIONAL,
        "assigned_to": "hr-security@company.com",
        "mitigation_plan": (
            "1. Develop comprehensive security awareness curriculum\n"
            "2. Implement quarterly mandatory training for all employees\n"
            "3. Conduct monthly phishing simulations\n"
            "4. Create security champions program across departments\n"
            "5. Track and report training completion metrics to leadership"
        ),
        "deadline": date.today() + timedelta(days=180),
    },
]


async def check_existing_risks(session: AsyncSession) -> int:
    """
    Check how many risks already exist in the database.

    Args:
        session: Async database session

    Returns:
        int: Number of existing risk records
    """
    result = await session.execute(select(Risk))
    risks = result.scalars().all()
    return len(risks)


async def seed_risks(session: AsyncSession) -> int:
    """
    Seed the database with sample risk data.

    Args:
        session: Async database session

    Returns:
        int: Number of risks created

    Note:
        This function is idempotent - it won't create duplicate risks
        if they already exist (based on title matching).
    """
    created_count = 0

    for idx, risk_data in enumerate(SAMPLE_RISKS, start=1):
        # Check if risk with this title already exists
        result = await session.execute(
            select(Risk).where(Risk.title == risk_data["title"])
        )
        existing_risk = result.scalar_one_or_none()

        if existing_risk:
            print(f"  [{idx:2d}/10] [SKIP] '{risk_data['title'][:60]}...' (already exists)")
            continue

        # Create new risk using the model's create method
        try:
            risk = await Risk.create(
                db=session,
                **risk_data
            )
            created_count += 1
            
            # Show progress with risk details
            status_label = {
                RiskStatus.OPEN: "OPEN",
                RiskStatus.IN_PROGRESS: "IN_PROGRESS",
                RiskStatus.MITIGATED: "MITIGATED",
                RiskStatus.ACCEPTED: "ACCEPTED",
            }
            
            severity_label = {
                RiskSeverity.CRITICAL: "CRITICAL",
                RiskSeverity.HIGH: "HIGH",
                RiskSeverity.MEDIUM: "MEDIUM",
                RiskSeverity.LOW: "LOW",
            }
            
            print(
                f"  [{idx:2d}/10] [OK] {risk.risk_number} - "
                f"{severity_label.get(risk.severity, '')} - "
                f"{status_label.get(risk.status, '')} - "
                f"'{risk.title[:40]}...'"
            )
            
        except Exception as e:
            print(f"  [{idx:2d}/10] [FAIL] '{risk_data['title'][:60]}...' - Error: {e}")
            continue

    return created_count


async def main():
    """
    Main entry point for the seeding script.

    This function orchestrates the database seeding process:
    1. Connects to the database
    2. Checks for existing data
    3. Seeds new risk records if needed
    4. Reports results
    """
    print("=" * 80)
    print("CISO Digital - Database Seeding Script")
    print("=" * 80)
    print()

    try:
        # Get session factory
        SessionLocal = get_async_session_local()
        
        # Create async session
        async with SessionLocal() as session:
            # Check existing data
            print("[CHECK] Checking existing data...")
            existing_count = await check_existing_risks(session)
            print(f"        Found {existing_count} existing risk(s) in database")
            print()

            if existing_count >= 10:
                print("[OK] Database already contains sufficient test data (10+ risks)")
                print("    Re-run this script to add more sample risks")
                print()
                return

            # Seed data
            print("[SEED] Seeding risk data...")
            print()
            created_count = await seed_risks(session)
            print()

            # Verify final count
            final_count = await check_existing_risks(session)

            # Report results
            print("=" * 80)
            if created_count > 0:
                print(f"[SUCCESS] Created {created_count} new risk(s)")
                print(f"[TOTAL]   Total risks in database: {final_count}")
            else:
                print("[INFO] No new risks created (all sample data already exists)")
                print(f"[TOTAL] Total risks in database: {final_count}")
            print("=" * 80)
            print()

            # Show helpful commands
            print("[NEXT STEPS]")
            print("  - View risks in database:")
            print("    docker-compose exec postgres psql -U ciso_user -d ciso_db -c 'SELECT risk_number, title, severity, status FROM risks;'")
            print()
            print("  - Start API server:")
            print("    uvicorn app.main:app --reload")
            print()
            print("  - Test API endpoints:")
            print("    curl http://localhost:8000/api/v1/risks")
            print()

    except Exception as e:
        print()
        print("=" * 80)
        print(f"[ERROR] Failed to seed database")
        print(f"        {type(e).__name__}: {e}")
        print("=" * 80)
        print()
        print("[TROUBLESHOOTING]")
        print("  1. Ensure PostgreSQL is running: docker-compose ps")
        print("  2. Check database connection in .env file")
        print("  3. Verify migrations are applied: alembic current")
        print()
        sys.exit(1)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
