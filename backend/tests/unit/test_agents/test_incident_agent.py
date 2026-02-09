"""
Tests for IncidentResponseAgent.

This module tests the incident response agent that handles security incidents
using NIST CSF framework, playbooks from RAG, and automated response workflows.

🔴 RED PHASE: These tests are written BEFORE the IncidentResponseAgent implementation.
They define the expected behavior and will initially FAIL.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
from uuid import uuid4
from typing import Dict, Any

# 🔴 RED: These imports will FAIL because IncidentResponseAgent doesn't exist yet
from app.agents.incident_agent import (
    IncidentResponseAgent,
    SecurityEvent,
    IncidentClassification,
    ResponsePlan,
    Playbook,
    IncidentType,
    Severity
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_copilot_service():
    """Mock Copilot service for testing."""
    service = AsyncMock()
    # Mock chat method to return text response (will be overridden in individual tests)
    service.chat = AsyncMock(return_value={"text": "{}"})
    # Mock create_session to return a mock session
    service.create_session = AsyncMock(return_value={"session_id": "test-session"})
    return service


@pytest.fixture
def mock_llm_service(mock_copilot_service):
    """Mock LLM service for testing (alias for copilot_service for backward compatibility)."""
    return mock_copilot_service


@pytest.fixture
def mock_rag_service():
    """Mock RAG service for playbook retrieval."""
    service = AsyncMock()
    return service


@pytest.fixture
async def mock_db_session():
    """Mock database session."""
    session = AsyncMock()
    session.add = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def mock_notification_service():
    """Mock notification service for stakeholder alerts."""
    service = AsyncMock()
    service.send_email = AsyncMock()
    service.send_slack = AsyncMock()
    return service


@pytest.fixture
async def incident_agent(
    mock_copilot_service,
    mock_rag_service,
    mock_db_session,
    mock_notification_service
):
    """Create IncidentResponseAgent with mocked dependencies."""
    agent = IncidentResponseAgent(
        copilot_service=mock_copilot_service,
        rag_service=mock_rag_service,
        db_session=mock_db_session,
        notification_service=mock_notification_service
    )
    return agent


# ============================================================================
# TEST DATA - Security Events
# ============================================================================

@pytest.fixture
def malware_event():
    """Sample malware detection event."""
    return SecurityEvent(
        timestamp=datetime.now(),
        source="EDR-System",
        event_type="malware_detection",
        description="Suspicious executable detected on DESKTOP-PROD-01",
        raw_data={
            "file_hash": "d41d8cd98f00b204e9800998ecf8427e",
            "file_path": "C:\\Users\\john\\Downloads\\invoice.exe",
            "process_name": "invoice.exe",
            "threat_name": "Trojan.GenericKD.123456",
            "affected_host": "DESKTOP-PROD-01",
            "user": "john.doe@company.com"
        },
        severity_indicator="high",
        affected_assets=["DESKTOP-PROD-01"]
    )


@pytest.fixture
def phishing_event():
    """Sample phishing incident event."""
    return SecurityEvent(
        timestamp=datetime.now(),
        source="Email-Gateway",
        event_type="phishing_attempt",
        description="Phishing email bypassed filters and reached 15 users",
        raw_data={
            "email_subject": "Urgent: Password Reset Required",
            "sender": "noreply@c0mpany-secure.com",
            "recipients": 15,
            "malicious_url": "http://evil-domain.com/phish",
            "attachment_present": False,
            "users_clicked": 3
        },
        severity_indicator="medium",
        affected_assets=["email-server-01"]
    )


@pytest.fixture
def data_breach_event():
    """Sample data breach event."""
    return SecurityEvent(
        timestamp=datetime.now(),
        source="DLP-System",
        event_type="data_exfiltration",
        description="Large volume of sensitive data uploaded to external cloud storage",
        raw_data={
            "user": "contractor@company.com",
            "destination": "dropbox.com",
            "data_volume_mb": 2500,
            "file_types": ["xlsx", "pdf", "docx"],
            "contains_pii": True,
            "contains_financial": True,
            "classification": "confidential"
        },
        severity_indicator="critical",
        affected_assets=["file-server-prod", "user-workstation-45"]
    )


@pytest.fixture
def ddos_event():
    """Sample DDoS attack event."""
    return SecurityEvent(
        timestamp=datetime.now(),
        source="WAF",
        event_type="ddos_attack",
        description="Distributed denial of service attack targeting web application",
        raw_data={
            "target": "www.company.com",
            "requests_per_second": 50000,
            "source_ips": 1200,
            "attack_vector": "HTTP flood",
            "duration_minutes": 15,
            "service_degradation": True
        },
        severity_indicator="high",
        affected_assets=["web-app-prod", "load-balancer-01"]
    )


# ============================================================================
# TEST DATA - Expected Playbooks
# ============================================================================

@pytest.fixture
def malware_playbook():
    """Expected malware response playbook."""
    return Playbook(
        incident_type=IncidentType.MALWARE,
        title="Malware Incident Response",
        steps=[
            {
                "step": 1,
                "action": "Isolate affected system from network",
                "automated": True,
                "estimated_time": "5 minutes"
            },
            {
                "step": 2,
                "action": "Collect forensic artifacts (memory dump, disk image)",
                "automated": False,
                "estimated_time": "30 minutes"
            },
            {
                "step": 3,
                "action": "Analyze malware sample in sandbox",
                "automated": True,
                "estimated_time": "15 minutes"
            },
            {
                "step": 4,
                "action": "Check for lateral movement indicators",
                "automated": True,
                "estimated_time": "10 minutes"
            },
            {
                "step": 5,
                "action": "Remove malware and restore system",
                "automated": False,
                "estimated_time": "60 minutes"
            }
        ],
        references=[
            "NIST SP 800-61 Section 3.2.6",
            "MITRE ATT&CK T1204"
        ],
        estimated_total_time="120 minutes"
    )


# ============================================================================
# TESTS - Incident Classification
# ============================================================================

@pytest.mark.asyncio
async def test_classify_malware_incident_correctly(
    incident_agent,
    mock_llm_service,
    malware_event
):
    """
    Test that agent correctly classifies malware incidents.
    
    Given: A security event indicating malware detection
    When: Agent classifies the incident
    Then: Should identify it as MALWARE incident type with appropriate severity
    """
    # Arrange - Mock the copilot service chat response
    incident_agent.copilot_service.chat.return_value = {
        "text": '''```json
{
  "classification": {
    "incident_type": "malware",
    "severity": "high",
    "confidence": 0.95,
    "indicators": ["trojan signature"],
    "potential_impact": "EDR detected known trojan signature"
  },
  "response_plan": {
    "immediate_actions": [
      {"action": "Isolate host", "responsible": "SOC", "time_estimate": "5 min", "priority": "high", "automatable": true}
    ],
    "containment_steps": [],
    "eradication_steps": [],
    "recovery_steps": [],
    "lessons_learned_to_document": []
  },
  "automated_actions_executed": [],
  "stakeholders_to_notify": []
}
```'''
    }
    
    # Act
    classification = await incident_agent.classify_incident(malware_event)
    
    # Assert
    assert isinstance(classification, IncidentClassification)
    assert classification.incident_type == IncidentType.MALWARE
    assert classification.severity == Severity.HIGH
    assert classification.confidence >= 0.9
    assert "trojan" in classification.reasoning.lower() or "malware" in classification.reasoning.lower()
    
    # Verify Copilot was called
    assert incident_agent.copilot_service.chat.called


@pytest.mark.asyncio
async def test_classify_phishing_incident_correctly(
    incident_agent,
    mock_llm_service,
    phishing_event
):
    """
    Test that agent correctly classifies phishing incidents.
    
    Given: A security event indicating phishing attempt
    When: Agent classifies the incident
    Then: Should identify it as PHISHING incident type
    """
    # Arrange - Mock the copilot service chat response
    incident_agent.copilot_service.chat.return_value = {
        "text": '''```json
{
  "classification": {
    "incident_type": "phishing",
    "severity": "medium",
    "confidence": 0.88,
    "indicators": ["malicious link"],
    "potential_impact": "Phishing email bypassed filters, 3 users clicked malicious link"
  },
  "response_plan": {
    "immediate_actions": [
      {"action": "Block sender", "responsible": "SOC", "time_estimate": "5 min", "priority": "medium", "automatable": true}
    ],
    "containment_steps": [],
    "eradication_steps": [],
    "recovery_steps": [],
    "lessons_learned_to_document": []
  },
  "automated_actions_executed": [],
  "stakeholders_to_notify": []
}
```'''
    }
    
    # Act
    classification = await incident_agent.classify_incident(phishing_event)
    
    # Assert
    assert classification.incident_type == IncidentType.PHISHING
    assert classification.severity == Severity.MEDIUM
    assert classification.confidence >= 0.85


@pytest.mark.asyncio
async def test_classify_data_breach_incident_correctly(
    incident_agent,
    mock_llm_service,
    data_breach_event
):
    """
    Test that agent correctly classifies data breach incidents.
    
    Given: A security event indicating unauthorized data exfiltration
    When: Agent classifies the incident
    Then: Should identify it as DATA_BREACH with CRITICAL severity
    """
    # Arrange - Mock the copilot service chat response
    incident_agent.copilot_service.chat.return_value = {
        "text": '''```json
{
  "classification": {
    "incident_type": "data_breach",
    "severity": "critical",
    "confidence": 0.98,
    "indicators": ["PII exfiltration", "financial data"],
    "potential_impact": "Large volume of PII and financial data exfiltrated to external storage"
  },
  "response_plan": {
    "immediate_actions": [
      {"action": "Contain breach", "responsible": "CISO", "time_estimate": "immediate", "priority": "critical", "automatable": false}
    ],
    "containment_steps": [],
    "eradication_steps": [],
    "recovery_steps": [],
    "lessons_learned_to_document": []
  },
  "automated_actions_executed": [],
  "stakeholders_to_notify": ["CISO", "Legal", "Compliance"]
}
```'''
    }
    
    # Act
    classification = await incident_agent.classify_incident(data_breach_event)
    
    # Assert
    assert classification.incident_type == IncidentType.DATA_BREACH
    assert classification.severity == Severity.CRITICAL
    assert classification.confidence >= 0.95
    
    # Data breaches with PII should be critical
    assert "pii" in str(data_breach_event.raw_data).lower()


# ============================================================================
# TESTS - Severity Determination
# ============================================================================

@pytest.mark.asyncio
async def test_determine_severity_for_critical_incident(
    incident_agent,
    mock_llm_service,
    data_breach_event
):
    """
    Test that agent correctly determines CRITICAL severity.
    
    Given: An incident involving PII data breach
    When: Agent determines severity
    Then: Should assign CRITICAL severity level
    """
    # Arrange - Mock the copilot service chat response
    incident_agent.copilot_service.chat.return_value = {
        "text": '''```json
{
  "classification": {
    "incident_type": "data_breach",
    "severity": "critical",
    "confidence": 0.98,
    "indicators": ["PII compromise"],
    "potential_impact": "PII compromise requires immediate response"
  },
  "response_plan": {
    "immediate_actions": [
      {"action": "Immediate containment", "responsible": "CISO", "time_estimate": "immediate", "priority": "critical", "automatable": false}
    ],
    "containment_steps": [],
    "eradication_steps": [],
    "recovery_steps": [],
    "lessons_learned_to_document": []
  },
  "automated_actions_executed": [],
  "stakeholders_to_notify": ["CISO", "Legal"]
}
```'''
    }
    
    # Act
    classification = await incident_agent.classify_incident(data_breach_event)
    
    # Assert
    assert classification.severity == Severity.CRITICAL
    
    # Critical incidents should have high confidence
    assert classification.confidence > 0.9


@pytest.mark.asyncio
async def test_severity_escalation_based_on_impact(
    incident_agent,
    mock_llm_service,
    malware_event
):
    """
    Test that severity can be escalated based on business impact.
    
    Given: A malware incident on critical production system
    When: Agent evaluates with business context
    Then: Severity should be escalated appropriately
    """
    # Arrange
    # Modify event to indicate production system
    malware_event.raw_data["system_criticality"] = "production"
    malware_event.affected_assets = ["payment-gateway-prod"]
    
    # Mock the copilot service chat response
    incident_agent.copilot_service.chat.return_value = {
        "text": '''```json
{
  "classification": {
    "incident_type": "malware",
    "severity": "critical",
    "confidence": 0.93,
    "indicators": ["critical system affected"],
    "potential_impact": "Malware on critical payment system requires immediate action"
  },
  "response_plan": {
    "immediate_actions": [
      {"action": "Isolate payment gateway", "responsible": "SOC", "time_estimate": "5 min", "priority": "critical", "automatable": true}
    ],
    "containment_steps": [],
    "eradication_steps": [],
    "recovery_steps": [],
    "lessons_learned_to_document": []
  },
  "automated_actions_executed": [],
  "stakeholders_to_notify": ["CISO", "CTO"]
}
```'''
    }
    
    # Act
    classification = await incident_agent.classify_incident(malware_event)
    
    # Assert
    # Should escalate to critical due to business impact
    assert classification.severity == Severity.CRITICAL


# ============================================================================
# TESTS - Playbook Retrieval
# ============================================================================

@pytest.mark.asyncio
async def test_fetch_appropriate_playbook_from_rag(
    incident_agent,
    mock_rag_service,
    malware_event,
    malware_playbook
):
    """
    Test that agent fetches appropriate playbook from RAG.
    
    Given: A classified malware incident
    When: Agent retrieves playbook from RAG
    Then: Should fetch malware-specific response playbook
    """
    # Arrange
    mock_rag_service.search.return_value = [
        {
            "content": "Malware Incident Response Playbook...",
            "metadata": {
                "type": "playbook",
                "incident_type": "malware",
                "framework": "NIST"
            },
            "score": 0.95
        }
    ]
    
    classification = IncidentClassification(
        incident_type=IncidentType.MALWARE,
        severity=Severity.HIGH,
        confidence=0.95,
        reasoning="Trojan detected"
    )
    
    # Act
    playbook = await incident_agent.fetch_playbook(classification)
    
    # Assert
    assert isinstance(playbook, Playbook)
    assert playbook.incident_type == IncidentType.MALWARE
    assert len(playbook.steps) > 0
    
    # Verify RAG was queried with incident type
    mock_rag_service.search.assert_called_once()
    call_args = mock_rag_service.search.call_args
    assert "malware" in str(call_args).lower()


@pytest.mark.asyncio
async def test_playbook_contains_nist_references(
    incident_agent,
    mock_rag_service,
    data_breach_event
):
    """
    Test that playbooks include NIST CSF references.
    
    Given: Any incident type
    When: Playbook is retrieved
    Then: Should include NIST SP 800-61 references
    """
    # Arrange
    mock_rag_service.search.return_value = [
        {
            "content": "Data Breach Response according to NIST SP 800-61...",
            "metadata": {
                "type": "playbook",
                "incident_type": "data_breach",
                "framework": "NIST",
                "references": ["NIST SP 800-61", "GDPR Article 33"]
            },
            "score": 0.92
        }
    ]
    
    classification = IncidentClassification(
        incident_type=IncidentType.DATA_BREACH,
        severity=Severity.CRITICAL,
        confidence=0.98,
        reasoning="PII breach"
    )
    
    # Act
    playbook = await incident_agent.fetch_playbook(classification)
    
    # Assert
    assert playbook.references is not None
    assert len(playbook.references) > 0
    assert any("NIST" in ref for ref in playbook.references)


# ============================================================================
# TESTS - Response Plan Generation
# ============================================================================

@pytest.mark.asyncio
async def test_generate_response_plan_with_steps(
    incident_agent,
    mock_llm_service,
    malware_event,
    malware_playbook
):
    """
    Test that agent generates detailed response plan with specific steps.
    
    Given: A classified incident and retrieved playbook
    When: Agent generates response plan
    Then: Should produce plan with ordered steps, timelines, and priorities
    """
    # Arrange
    classification = IncidentClassification(
        incident_type=IncidentType.MALWARE,
        severity=Severity.HIGH,
        confidence=0.95,
        reasoning="Known trojan"
    )
    
    # Mock Copilot SDK response
    incident_agent.copilot_service.chat.return_value = {
        "text": '''```json
{
  "classification": {
    "incident_type": "malware",
    "severity": "high",
    "confidence": 0.95,
    "indicators": ["known trojan"],
    "potential_impact": "Known trojan on system"
  },
  "response_plan": {
    "immediate_actions": [
      {"action": "Isolate infected system", "responsible": "SOC", "time_estimate": "5 min", "priority": "high", "automatable": true},
      {"action": "Collect forensics", "responsible": "Security Analyst", "time_estimate": "30 min", "priority": "high", "automatable": false},
      {"action": "Analyze malware", "responsible": "Malware Analyst", "time_estimate": "15 min", "priority": "medium", "automatable": true}
    ],
    "containment_steps": [],
    "eradication_steps": [],
    "recovery_steps": [],
    "lessons_learned_to_document": []
  },
  "automated_actions_executed": ["isolate_host", "collect_logs"],
  "stakeholders_to_notify": []
}
```'''
    }
    
    # Act
    response_plan = await incident_agent.generate_response_plan(
        event=malware_event,
        classification=classification,
        playbook=malware_playbook
    )
    
    # Assert
    assert isinstance(response_plan, ResponsePlan)
    assert len(response_plan.steps) >= 3
    assert response_plan.priority in ["critical", "high", "medium", "low"]
    assert response_plan.estimated_time is not None
    
    # Steps should be ordered
    for i, step in enumerate(response_plan.steps, 1):
        assert step["step"] == i


@pytest.mark.asyncio
async def test_response_plan_includes_automated_actions(
    incident_agent,
    mock_llm_service,
    malware_event,
    malware_playbook
):
    """
    Test that response plans identify which actions can be automated.
    
    Given: A response playbook with automation capabilities
    When: Plan is generated
    Then: Should mark automated vs manual steps
    """
    # Arrange
    classification = IncidentClassification(
        incident_type=IncidentType.MALWARE,
        severity=Severity.HIGH,
        confidence=0.95,
        reasoning="EDR detection"
    )
    
    # Mock Copilot SDK response
    incident_agent.copilot_service.chat.return_value = {
        "text": '''```json
{
  "classification": {
    "incident_type": "malware",
    "severity": "high",
    "confidence": 0.95,
    "indicators": ["EDR detection"],
    "potential_impact": "EDR detected malware on system"
  },
  "response_plan": {
    "immediate_actions": [
      {"action": "Isolate host", "responsible": "SOC", "time_estimate": "5 min", "priority": "high", "automatable": true},
      {"action": "Manual forensics", "responsible": "Analyst", "time_estimate": "30 min", "priority": "medium", "automatable": false}
    ],
    "containment_steps": [],
    "eradication_steps": [],
    "recovery_steps": [],
    "lessons_learned_to_document": []
  },
  "automated_actions_executed": ["isolate_host", "collect_logs", "block_hash"],
  "stakeholders_to_notify": []
}
```'''
    }
    
    # Act
    response_plan = await incident_agent.generate_response_plan(
        event=malware_event,
        classification=classification,
        playbook=malware_playbook
    )
    
    # Assert
    assert response_plan.automated_actions is not None
    assert len(response_plan.automated_actions) > 0
    
    # At least one step should be marked as automated
    automated_steps = [s for s in response_plan.steps if s.get("automated")]
    assert len(automated_steps) > 0


# ============================================================================
# TESTS - Incident Record Creation
# ============================================================================

@pytest.mark.asyncio
async def test_create_incident_record_in_database(
    incident_agent,
    mock_db_session,
    malware_event
):
    """
    Test that agent creates incident record in database.
    
    Given: A fully processed incident with classification and plan
    When: Agent creates incident record
    Then: Should persist to database with all relevant details
    """
    # Arrange
    classification = IncidentClassification(
        incident_type=IncidentType.MALWARE,
        severity=Severity.HIGH,
        confidence=0.95,
        reasoning="EDR detection"
    )
    
    response_plan = ResponsePlan(
        steps=[{"step": 1, "action": "Isolate system", "automated": True}],
        estimated_time="60 minutes",
        priority="high",
        automated_actions=["isolate_host"]
    )
    
    # Act
    incident_record = await incident_agent.create_incident_record(
        event=malware_event,
        classification=classification,
        response_plan=response_plan
    )
    
    # Assert
    assert incident_record is not None
    assert incident_record.incident_id is not None
    assert incident_record.incident_type == IncidentType.MALWARE
    assert incident_record.severity == Severity.HIGH
    assert incident_record.status in ["open", "investigating", "contained", "resolved"]
    
    # Verify database interactions
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_incident_record_includes_timeline(
    incident_agent,
    mock_db_session,
    phishing_event
):
    """
    Test that incident records include timeline of events.
    
    Given: An incident with multiple events
    When: Incident record is created
    Then: Should include detection time, classification time, response start time
    """
    # Arrange
    classification = IncidentClassification(
        incident_type=IncidentType.PHISHING,
        severity=Severity.MEDIUM,
        confidence=0.88,
        reasoning="Phishing email"
    )
    
    response_plan = ResponsePlan(
        steps=[{"step": 1, "action": "Block sender domain"}],
        estimated_time="30 minutes",
        priority="medium",
        automated_actions=[]
    )
    
    # Act
    incident_record = await incident_agent.create_incident_record(
        event=phishing_event,
        classification=classification,
        response_plan=response_plan
    )
    
    # Assert
    assert incident_record.detected_at is not None
    assert incident_record.classified_at is not None
    assert incident_record.response_started_at is not None
    
    # Timeline should be chronological
    assert incident_record.detected_at <= incident_record.classified_at
    assert incident_record.classified_at <= incident_record.response_started_at


# ============================================================================
# TESTS - Stakeholder Notification
# ============================================================================

@pytest.mark.asyncio
async def test_notify_stakeholders_for_critical_incident(
    incident_agent,
    mock_notification_service,
    data_breach_event
):
    """
    Test that agent notifies stakeholders for critical incidents.
    
    Given: A CRITICAL severity incident (data breach)
    When: Incident record is created
    Then: Should send notifications to appropriate stakeholders
    """
    # Arrange
    classification = IncidentClassification(
        incident_type=IncidentType.DATA_BREACH,
        severity=Severity.CRITICAL,
        confidence=0.98,
        reasoning="PII breach"
    )
    
    response_plan = ResponsePlan(
        steps=[{"step": 1, "action": "Contain breach"}],
        estimated_time="immediate",
        priority="critical",
        automated_actions=[]
    )
    
    incident_record = Mock()
    incident_record.incident_id = "INC-2026-001"
    incident_record.severity = Severity.CRITICAL
    incident_record.incident_type = IncidentType.DATA_BREACH
    
    # Act
    await incident_agent.notify_stakeholders(
        incident_record=incident_record,
        classification=classification
    )
    
    # Assert
    # Should send email notification
    mock_notification_service.send_email.assert_called_once()
    
    # Verify email contains critical information
    email_call = mock_notification_service.send_email.call_args
    assert "critical" in str(email_call).lower() or "data breach" in str(email_call).lower()


@pytest.mark.asyncio
async def test_no_notification_for_low_severity_incident(
    incident_agent,
    mock_notification_service,
    phishing_event
):
    """
    Test that low/medium severity incidents don't trigger immediate notifications.
    
    Given: A MEDIUM severity incident
    When: Processing completes
    Then: Should NOT send urgent notifications (only log/ticket)
    """
    # Arrange
    classification = IncidentClassification(
        incident_type=IncidentType.PHISHING,
        severity=Severity.MEDIUM,
        confidence=0.85,
        reasoning="Phishing attempt"
    )
    
    response_plan = ResponsePlan(
        steps=[{"step": 1, "action": "Block sender"}],
        estimated_time="30 minutes",
        priority="medium",
        automated_actions=[]
    )
    
    incident_record = Mock()
    incident_record.incident_id = "INC-2026-002"
    incident_record.severity = Severity.MEDIUM
    incident_record.incident_type = IncidentType.PHISHING
    
    # Act
    await incident_agent.notify_stakeholders(
        incident_record=incident_record,
        classification=classification
    )
    
    # Assert
    # Should NOT send urgent email for medium severity
    assert mock_notification_service.send_email.call_count == 0


# ============================================================================
# TESTS - End-to-End Workflow
# ============================================================================

@pytest.mark.asyncio
async def test_complete_incident_response_workflow(
    incident_agent,
    mock_llm_service,
    mock_rag_service,
    mock_db_session,
    mock_notification_service,
    malware_event,
    malware_playbook
):
    """
    Test complete incident response workflow from event to resolution.
    
    Given: A security event
    When: Agent processes the complete workflow
    Then: Should classify, plan, record, and notify appropriately
    """
    # Arrange - Mock the copilot service chat response
    incident_agent.copilot_service.chat.return_value = {
        "text": '''```json
{
  "classification": {
    "incident_type": "malware",
    "severity": "high",
    "confidence": 0.95,
    "indicators": ["EDR detection"],
    "potential_impact": "EDR detection of known malware"
  },
  "response_plan": {
    "immediate_actions": [
      {"action": "Isolate host", "responsible": "SOC", "time_estimate": "5 min", "priority": "high", "automatable": true}
    ],
    "containment_steps": [],
    "eradication_steps": [],
    "recovery_steps": [],
    "lessons_learned_to_document": []
  },
  "automated_actions_executed": [],
  "stakeholders_to_notify": []
}
```'''
    }
    
    mock_rag_service.search.return_value = [
        {
            "content": "Malware playbook...",
            "metadata": {"type": "playbook", "incident_type": "malware"},
            "score": 0.95
        }
    ]
    
    # Act
    result = await incident_agent.process(
        query="Process this security event",
        context={"event": malware_event},
        entities=[],
        conversation_history=[]
    )
    
    # Assert
    assert result is not None
    assert "incident_id" in result or "response" in result
    
    # Verify all major steps were executed
    assert incident_agent.copilot_service.chat.called
    assert mock_db_session.add.called
    assert mock_db_session.commit.called


# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================

@pytest.mark.asyncio
async def test_handle_unknown_incident_type_gracefully(
    incident_agent,
    mock_llm_service
):
    """
    Test that agent handles unknown incident types gracefully.
    
    Given: An event that doesn't match known incident types
    When: Classification is attempted
    Then: Should fallback to UNKNOWN type with manual review flag
    """
    # Arrange
    unknown_event = SecurityEvent(
        timestamp=datetime.now(),
        source="Unknown-System",
        event_type="strange_behavior",
        description="Unusual activity that doesn't match known patterns",
        raw_data={},
        severity_indicator="medium",
        affected_assets=[]
    )
    
    # Mock Copilot SDK response for unknown incident type
    incident_agent.copilot_service.chat.return_value = {
        "text": '''```json
{
  "classification": {
    "incident_type": "unknown",
    "severity": "medium",
    "confidence": 0.45,
    "indicators": ["unusual patterns"],
    "potential_impact": "Unusual activity that doesn't match known patterns - requires manual analysis"
  },
  "response_plan": {
    "immediate_actions": [
      {"action": "Flag for manual review", "responsible": "Security Analyst", "time_estimate": "manual", "priority": "medium", "automatable": false}
    ],
    "containment_steps": [],
    "eradication_steps": [],
    "recovery_steps": [],
    "lessons_learned_to_document": []
  },
  "automated_actions_executed": [],
  "stakeholders_to_notify": []
}
```'''
    }
    
    # Act
    classification = await incident_agent.classify_incident(unknown_event)
    
    # Assert
    assert classification.incident_type == IncidentType.UNKNOWN
    assert classification.confidence < 0.7  # Low confidence for unknown
    assert "manual" in classification.reasoning.lower()


@pytest.mark.asyncio
async def test_handle_rag_service_failure(
    incident_agent,
    mock_rag_service,
    malware_event
):
    """
    Test that agent handles RAG service failures gracefully.
    
    Given: RAG service is unavailable
    When: Playbook fetch is attempted
    Then: Should fallback to default generic playbook
    """
    # Arrange
    mock_rag_service.search.side_effect = Exception("RAG service unavailable")
    
    classification = IncidentClassification(
        incident_type=IncidentType.MALWARE,
        severity=Severity.HIGH,
        confidence=0.95,
        reasoning="EDR detection"
    )
    
    # Act
    playbook = await incident_agent.fetch_playbook(classification)
    
    # Assert
    assert playbook is not None  # Should have fallback
    assert playbook.incident_type == classification.incident_type
    assert len(playbook.steps) > 0  # Default playbook should have steps
