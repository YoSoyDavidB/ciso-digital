#!/usr/bin/env python3
"""
Incident Seeding Script para CISO Digital.

Este script genera datos de prueba realistas de incidentes de seguridad
para desarrollo y testing. Es idempotente y distribuye incidentes
en los últimos 90 días.

Usage:
    python scripts/seed_incidents.py

Features:
    - Genera 15 incidentes con datos realistas
    - Variación de tipos, severidades y estados
    - Distribución temporal en últimos 90 días
    - Idempotente (no duplica si ya existen)
    - Progress bar y resumen al final
"""

import asyncio
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

# Add backend to path para imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.features.incident_response.models.incident import Incident
from app.shared.models.enums import IncidentSeverity, IncidentStatus, IncidentType


# ============================================================================
# Configuration
# ============================================================================

NUM_INCIDENTS = 15
DAYS_BACK = 90

# SLA hours by severity for realistic resolution times
SLA_HOURS = {
    "critical": 1,
    "high": 4,
    "medium": 24,
    "low": 72,
}


# ============================================================================
# Realistic Incident Data Templates
# ============================================================================

INCIDENT_TEMPLATES = [
    {
        "type": IncidentType.RANSOMWARE,
        "title": "Ransomware Attack on {asset}",
        "description": "Detected ransomware encryption activity on {asset}. Files being encrypted with .locked extension. Immediate containment required.",
        "assets": ["Production DB Server", "File Server", "Backup Server"],
        "severity_options": [IncidentSeverity.CRITICAL, IncidentSeverity.HIGH],
    },
    {
        "type": IncidentType.PHISHING,
        "title": "Phishing Campaign Targeting {department} Department",
        "description": "Multiple employees in {department} received suspicious emails claiming to be from IT department requesting password reset. Links lead to credential harvesting site.",
        "departments": ["Finance", "HR", "Sales", "Engineering"],
        "severity_options": [IncidentSeverity.HIGH, IncidentSeverity.MEDIUM],
    },
    {
        "type": IncidentType.DATA_BREACH,
        "title": "Unauthorized Access to {system}",
        "description": "Detected unauthorized data exfiltration from {system}. Approximately {records} records potentially compromised. Investigation ongoing to determine scope.",
        "systems": ["Customer Database", "Employee Records", "Financial System", "CRM Platform"],
        "records": [5000, 10000, 25000, 50000],
        "severity_options": [IncidentSeverity.CRITICAL, IncidentSeverity.HIGH],
    },
    {
        "type": IncidentType.MALWARE,
        "title": "Malware Detected on {asset}",
        "description": "Endpoint protection detected {malware_type} on {asset}. System isolated from network pending analysis.",
        "assets": ["Employee Laptop", "Development Workstation", "Admin Desktop"],
        "malware_types": ["Trojan", "Spyware", "Keylogger", "Backdoor"],
        "severity_options": [IncidentSeverity.MEDIUM, IncidentSeverity.LOW],
    },
    {
        "type": IncidentType.DDOS,
        "title": "DDoS Attack Against {target}",
        "description": "Distributed denial of service attack detected against {target}. Traffic volume increased by {multiplier}x normal levels. CDN and WAF engaged.",
        "targets": ["Corporate Website", "API Gateway", "Customer Portal"],
        "multipliers": [10, 25, 50, 100],
        "severity_options": [IncidentSeverity.HIGH, IncidentSeverity.MEDIUM],
    },
    {
        "type": IncidentType.UNAUTHORIZED_ACCESS,
        "title": "Suspicious Login Activity for {account}",
        "description": "Detected login attempts to {account} from {country}. Account does not normally access from this location. MFA challenge failed multiple times.",
        "accounts": ["Administrator Account", "Service Account", "Privileged User Account"],
        "countries": ["Russia", "China", "North Korea", "Iran", "Unknown"],
        "severity_options": [IncidentSeverity.HIGH, IncidentSeverity.MEDIUM],
    },
    {
        "type": IncidentType.INSIDER_THREAT,
        "title": "Unusual Data Access Pattern by {employee}",
        "description": "Employee {employee} accessed {records} records outside normal working hours. Access pattern inconsistent with job role. HR notified for investigation.",
        "employees": ["John Doe (Finance)", "Jane Smith (IT)", "Bob Johnson (Sales)"],
        "records": [500, 1000, 2000],
        "severity_options": [IncidentSeverity.MEDIUM, IncidentSeverity.LOW],
    },
]


# ============================================================================
# Helper Functions
# ============================================================================


def generate_random_date(days_back: int) -> datetime:
    """
    Generate random datetime within the last N days.
    
    Args:
        days_back: Number of days to look back
        
    Returns:
        Timezone-aware datetime
    """
    now = datetime.now(timezone.utc)
    days_offset = random.randint(0, days_back)
    hours_offset = random.randint(0, 23)
    minutes_offset = random.randint(0, 59)
    
    return now - timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)


def generate_incident_data(template: Dict[str, Any], index: int) -> Dict[str, Any]:
    """
    Generate realistic incident data from template.
    
    Args:
        template: Incident template with placeholders
        index: Incident index for unique numbering
        
    Returns:
        Dictionary with incident data
    """
    # Select random severity from options
    severity = random.choice(template["severity_options"])
    
    # Replace placeholders in title and description
    title = template["title"]
    description = template["description"]
    
    # Handle different placeholder types
    if "{asset}" in title or "{asset}" in description:
        asset = random.choice(template.get("assets", ["Unknown Asset"]))
        title = title.format(asset=asset)
        description = description.format(asset=asset)
    
    if "{department}" in description:
        department = random.choice(template.get("departments", ["IT"]))
        description = description.format(department=department)
    
    if "{system}" in title or "{system}" in description:
        system = random.choice(template.get("systems", ["System"]))
        title = title.format(system=system)
        description = description.format(
            system=system,
            records=random.choice(template.get("records", [1000]))
        )
    
    if "{malware_type}" in description:
        malware_type = random.choice(template.get("malware_types", ["Malware"]))
        description = description.format(malware_type=malware_type, asset=random.choice(template.get("assets", ["Asset"])))
    
    if "{target}" in title or "{target}" in description:
        target = random.choice(template.get("targets", ["Target"]))
        description = description.format(
            target=target,
            multiplier=random.choice(template.get("multipliers", [10]))
        )
        title = title.format(target=target)
    
    if "{account}" in title or "{account}" in description:
        account = random.choice(template.get("accounts", ["User Account"]))
        country = random.choice(template.get("countries", ["Unknown"]))
        title = title.format(account=account)
        description = description.format(account=account, country=country)
    
    if "{employee}" in title or "{employee}" in description:
        employee = random.choice(template.get("employees", ["Employee"]))
        records = random.choice(template.get("records", [100]))
        title = title.format(employee=employee)
        description = description.format(employee=employee, records=records)
    
    # Generate timestamps
    detected_at = generate_random_date(DAYS_BACK)
    reported_at = detected_at + timedelta(minutes=random.randint(5, 60))
    
    # Determine status based on how old the incident is
    days_old = (datetime.now(timezone.utc) - detected_at).days
    
    # 70% of incidents should be resolved if they're old enough
    if days_old > 7 and random.random() < 0.7:
        status = IncidentStatus.CLOSED
        contained_at = reported_at + timedelta(hours=random.randint(1, 12))
        resolved_at = contained_at + timedelta(hours=random.randint(4, 48))
    elif days_old > 3 and random.random() < 0.5:
        status = random.choice([IncidentStatus.CONTAINED, IncidentStatus.INVESTIGATING])
        contained_at = reported_at + timedelta(hours=random.randint(1, 24)) if status == IncidentStatus.CONTAINED else None
        resolved_at = None
    else:
        status = random.choice([IncidentStatus.DETECTED, IncidentStatus.INVESTIGATING])
        contained_at = None
        resolved_at = None
    
    # Generate response plan
    response_plan = generate_response_plan(template["type"], severity)
    
    # Generate actions taken
    actions_taken = generate_actions_taken(template["type"], status, detected_at)
    
    # Generate incident number
    year = detected_at.year
    incident_number = f"INC-{year}-{index:03d}"
    
    return {
        "incident_number": incident_number,
        "title": title,
        "description": description,
        "incident_type": template["type"],
        "severity": severity,
        "status": status,
        "detected_at": detected_at,
        "reported_at": reported_at,
        "contained_at": contained_at,
        "resolved_at": resolved_at,
        "assigned_to": random.choice([
            "security@company.com",
            "soc.analyst@company.com",
            "incident.response@company.com",
            None
        ]),
        "response_plan": response_plan,
        "actions_taken": actions_taken,
        "related_assets": [f"asset-{random.randint(1, 100)}"],
        "impact_assessment": generate_impact_assessment(severity, status) if status in [IncidentStatus.CONTAINED, IncidentStatus.CLOSED] else None,
        "root_cause": generate_root_cause(template["type"]) if status == IncidentStatus.CLOSED else None,
        "lessons_learned": generate_lessons_learned(template["type"]) if status == IncidentStatus.CLOSED else None,
    }


def generate_response_plan(incident_type: IncidentType, severity: IncidentSeverity) -> Dict[str, Any]:
    """Generate realistic response plan based on incident type."""
    base_steps = [
        {"step": 1, "action": "Identify and isolate affected systems", "owner": "SOC Team"},
        {"step": 2, "action": "Collect forensic evidence", "owner": "Security Analyst"},
        {"step": 3, "action": "Notify stakeholders", "owner": "Incident Manager"},
    ]
    
    type_specific_steps = {
        IncidentType.RANSOMWARE: [
            {"step": 4, "action": "Disconnect from network immediately", "owner": "Network Team"},
            {"step": 5, "action": "Identify ransomware variant", "owner": "Malware Analyst"},
            {"step": 6, "action": "Restore from clean backups", "owner": "IT Operations"},
        ],
        IncidentType.PHISHING: [
            {"step": 4, "action": "Block sender domains and URLs", "owner": "Email Security Team"},
            {"step": 5, "action": "Reset credentials for affected users", "owner": "IAM Team"},
            {"step": 6, "action": "Conduct security awareness training", "owner": "Security Team"},
        ],
        IncidentType.DATA_BREACH: [
            {"step": 4, "action": "Identify scope of data exposure", "owner": "Security Analyst"},
            {"step": 5, "action": "Notify legal and compliance teams", "owner": "CISO"},
            {"step": 6, "action": "Prepare breach notification", "owner": "Legal Team"},
        ],
    }
    
    steps = base_steps + type_specific_steps.get(incident_type, [
        {"step": 4, "action": "Implement containment measures", "owner": "Security Team"},
        {"step": 5, "action": "Eradicate threat", "owner": "Security Team"},
        {"step": 6, "action": "Recover and validate systems", "owner": "IT Operations"},
    ])
    
    return {
        "steps": steps,
        "priority": severity.value,
        "estimated_duration_hours": SLA_HOURS.get(severity.value, 24),
    }


def generate_actions_taken(
    incident_type: IncidentType,
    status: IncidentStatus,
    detected_at: datetime
) -> List[Dict[str, Any]]:
    """Generate realistic actions taken based on status."""
    actions = []
    current_time = detected_at
    
    # Initial detection action
    actions.append({
        "timestamp": current_time.isoformat(),
        "action": "Initial Detection",
        "description": f"Incident detected via automated monitoring",
        "performed_by": "SIEM System",
        "status": "completed"
    })
    
    # Add actions based on status progression
    if status in [IncidentStatus.INVESTIGATING, IncidentStatus.CONTAINED, IncidentStatus.CLOSED]:
        current_time += timedelta(minutes=random.randint(10, 30))
        actions.append({
            "timestamp": current_time.isoformat(),
            "action": "Isolation",
            "description": "Affected systems isolated from network",
            "performed_by": "SOC Analyst",
            "status": "completed"
        })
    
    if status in [IncidentStatus.CONTAINED, IncidentStatus.CLOSED]:
        current_time += timedelta(hours=random.randint(1, 4))
        actions.append({
            "timestamp": current_time.isoformat(),
            "action": "Containment",
            "description": "Threat contained, spread prevented",
            "performed_by": "Incident Response Team",
            "status": "completed"
        })
    
    if status == IncidentStatus.CLOSED:
        current_time += timedelta(hours=random.randint(4, 24))
        actions.append({
            "timestamp": current_time.isoformat(),
            "action": "Remediation",
            "description": "Systems cleaned and restored to normal operation",
            "performed_by": "IT Operations",
            "status": "completed"
        })
    
    return actions


def generate_impact_assessment(severity: IncidentSeverity, status: IncidentStatus) -> str:
    """Generate realistic impact assessment."""
    impacts = {
        IncidentSeverity.CRITICAL: "Critical business impact. Production systems affected. Potential data loss and regulatory implications.",
        IncidentSeverity.HIGH: "Significant business impact. Multiple systems affected. Operational disruption observed.",
        IncidentSeverity.MEDIUM: "Moderate business impact. Limited systems affected. No critical operations disrupted.",
        IncidentSeverity.LOW: "Minimal business impact. Single system affected. No operational disruption.",
    }
    return impacts.get(severity, "Impact assessment pending.")


def generate_root_cause(incident_type: IncidentType) -> str:
    """Generate realistic root cause analysis."""
    causes = {
        IncidentType.RANSOMWARE: "Unpatched vulnerability in remote desktop protocol allowed initial access. Lack of network segmentation facilitated lateral movement.",
        IncidentType.PHISHING: "User clicked malicious link despite security awareness training. Email filtering rules did not catch sophisticated phishing attempt.",
        IncidentType.DATA_BREACH: "Misconfigured database security settings allowed unauthorized external access. Insufficient access logging delayed detection.",
        IncidentType.MALWARE: "User downloaded infected file from untrusted source. Antivirus signatures were out of date.",
        IncidentType.DDOS: "Lack of rate limiting and DDoS protection on public-facing infrastructure.",
        IncidentType.UNAUTHORIZED_ACCESS: "Weak password policy and lack of multi-factor authentication enforcement.",
        IncidentType.INSIDER_THREAT: "Insufficient user activity monitoring and data access controls.",
    }
    return causes.get(incident_type, "Root cause analysis in progress.")


def generate_lessons_learned(incident_type: IncidentType) -> str:
    """Generate realistic lessons learned."""
    lessons = {
        IncidentType.RANSOMWARE: "1. Implement network segmentation to limit blast radius. 2. Enforce regular patching schedule. 3. Test backup restoration procedures quarterly.",
        IncidentType.PHISHING: "1. Enhance email filtering rules with AI-based detection. 2. Implement mandatory security awareness training. 3. Deploy email banner warnings for external emails.",
        IncidentType.DATA_BREACH: "1. Conduct regular security configuration audits. 2. Implement comprehensive access logging. 3. Enable real-time alerts for suspicious data access.",
        IncidentType.MALWARE: "1. Keep endpoint protection up to date. 2. Implement application whitelisting. 3. Enhance user education on safe computing practices.",
        IncidentType.DDOS: "1. Implement DDoS protection and rate limiting. 2. Use CDN for public-facing services. 3. Establish incident response playbook for DDoS attacks.",
        IncidentType.UNAUTHORIZED_ACCESS: "1. Enforce strong password policy. 2. Mandate MFA for all accounts. 3. Implement geolocation-based access controls.",
        IncidentType.INSIDER_THREAT: "1. Enhance user activity monitoring. 2. Implement principle of least privilege. 3. Conduct regular access reviews.",
    }
    return lessons.get(incident_type, "Lessons learned documentation pending.")


# ============================================================================
# Database Operations
# ============================================================================


async def check_existing_incidents(session: AsyncSession) -> int:
    """
    Check how many incidents already exist.
    
    Args:
        session: Database session
        
    Returns:
        Count of existing incidents
    """
    result = await session.execute(select(Incident))
    incidents = result.scalars().all()
    return len(incidents)


async def seed_incidents(session: AsyncSession) -> Dict[str, Any]:
    """
    Seed incident data into database.
    
    Args:
        session: Database session
        
    Returns:
        Summary statistics
    """
    print("\n" + "=" * 70)
    print("🔐 CISO Digital - Incident Seeding Script")
    print("=" * 70)
    
    # Check existing incidents
    existing_count = await check_existing_incidents(session)
    print(f"\n📊 Current state: {existing_count} incidents in database")
    
    if existing_count >= NUM_INCIDENTS:
        print(f"✅ Database already has {existing_count} incidents. Skipping seed.")
        return {
            "created": 0,
            "skipped": existing_count,
            "total": existing_count
        }
    
    print(f"🌱 Generating {NUM_INCIDENTS} incident records...")
    print(f"📅 Distribution: Last {DAYS_BACK} days")
    print()
    
    # Generate incidents
    incidents_to_create = NUM_INCIDENTS - existing_count
    created = 0
    skipped = 0
    
    # Select random templates for variety
    selected_templates = []
    for i in range(incidents_to_create):
        template = random.choice(INCIDENT_TEMPLATES)
        selected_templates.append(template)
    
    # Create incidents with progress
    for idx, template in enumerate(selected_templates, start=1):
        try:
            # Generate incident data
            incident_data = generate_incident_data(template, existing_count + idx)
            
            # Check if incident_number already exists (idempotent)
            result = await session.execute(
                select(Incident).where(Incident.incident_number == incident_data["incident_number"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"⏭️  [{idx}/{incidents_to_create}] Skipping {incident_data['incident_number']} (already exists)")
                skipped += 1
                continue
            
            # Create incident
            incident = Incident(**incident_data)
            session.add(incident)
            
            # Progress indicator
            status_emoji = {
                IncidentStatus.CLOSED: "✅",
                IncidentStatus.CONTAINED: "🟡",
                IncidentStatus.INVESTIGATING: "🔍",
                IncidentStatus.DETECTED: "🚨"
            }.get(incident_data["status"], "📝")
            
            severity_emoji = {
                IncidentSeverity.CRITICAL: "🔴",
                IncidentSeverity.HIGH: "🟠",
                IncidentSeverity.MEDIUM: "🟡",
                IncidentSeverity.LOW: "🟢"
            }.get(incident_data["severity"], "⚪")
            
            print(f"{status_emoji} [{idx}/{incidents_to_create}] {severity_emoji} {incident_data['incident_number']}: {incident_data['title'][:50]}...")
            created += 1
            
        except Exception as e:
            print(f"❌ Error creating incident {idx}: {e}")
            continue
    
    # Commit all changes
    print("\n💾 Committing to database...")
    await session.commit()
    
    # Summary
    print("\n" + "=" * 70)
    print("📈 SEED SUMMARY")
    print("=" * 70)
    print(f"✨ Created:  {created} new incidents")
    print(f"⏭️  Skipped:  {skipped} duplicates")
    print(f"📊 Total:    {existing_count + created} incidents in database")
    print("=" * 70)
    print("✅ Seeding complete!\n")
    
    return {
        "created": created,
        "skipped": skipped,
        "total": existing_count + created
    }


# ============================================================================
# Main Execution
# ============================================================================


async def main():
    """Main execution function."""
    try:
        # Create async engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_pre_ping=True
        )
        
        # Create session factory
        async_session_factory = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Execute seeding
        async with async_session_factory() as session:
            await seed_incidents(session)
        
        # Cleanup
        await engine.dispose()
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("\n🚀 Starting incident seeding...")
    asyncio.run(main())
