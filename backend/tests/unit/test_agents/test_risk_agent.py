"""
🔴 RED: Tests para RiskAssessmentAgent - TDD Phase

Estos tests DEBEN FALLAR porque RiskAssessmentAgent no existe aún.

El RiskAssessmentAgent debe:
1. Recibir información de un asset
2. Recibir lista de vulnerabilidades
3. Usar RAG para buscar contexto sobre riesgos similares
4. Llamar al LLM con un prompt estructurado
5. Retornar evaluación de riesgo con score, severity, recommendations
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import Task

# 🔴 RED: Este import DEBE fallar porque RiskAssessmentAgent no existe
from app.agents.risk_agent import RiskAssessment, RiskAssessmentAgent
from app.services.copilot_service import CopilotService
from app.services.rag_service import RAGService


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def sample_asset():
    """
    Asset de prueba - servidor web de producción.
    """
    return {
        "id": "asset-001",
        "name": "Production Web Server",
        "type": "server",
        "criticality": "critical",
        "ip_address": "192.168.1.100",
        "environment": "production",
        "owner": "security-team@company.com",
    }


@pytest.fixture
def critical_vulnerabilities():
    """
    Lista de vulnerabilidades críticas para testing.
    """
    return [
        {
            "cve_id": "CVE-2025-1234",
            "cvss_score": 9.8,
            "severity": "critical",
            "description": "Remote Code Execution in Apache Struts",
            "affected_component": "apache-struts-2.5.0",
            "exploit_available": True,
        },
        {
            "cve_id": "CVE-2025-5678",
            "cvss_score": 8.9,
            "severity": "high",
            "description": "SQL Injection in database layer",
            "affected_component": "custom-db-module-1.2",
            "exploit_available": False,
        },
    ]


@pytest.fixture
def no_vulnerabilities():
    """Lista vacía de vulnerabilidades para testing."""
    return []


@pytest.fixture
def medium_vulnerabilities():
    """Vulnerabilidades de severidad media."""
    return [
        {
            "cve_id": "CVE-2025-9999",
            "cvss_score": 5.3,
            "severity": "medium",
            "description": "Information disclosure through error messages",
            "affected_component": "web-framework-3.1",
            "exploit_available": False,
        }
    ]


@pytest.fixture
def mock_rag_context():
    """
    Contexto RAG simulado con documentos sobre gestión de riesgos.
    """
    return [
        {
            "text": "Critical vulnerabilities with CVSS > 9.0 require immediate patching within 24 hours per ISO 27001.",
            "score": 0.92,
            "source": "ISO 27001:A.12.6.1",
        },
        {
            "text": "Remote Code Execution vulnerabilities should be prioritized and mitigated immediately.",
            "score": 0.89,
            "source": "NIST 800-53:SI-2",
        },
        {
            "text": "Production systems classified as critical must have 24/7 monitoring and immediate incident response.",
            "score": 0.85,
            "source": "risk-management-guide.md",
        },
    ]


@pytest.fixture
def mock_llm_critical_response():
    """
    Respuesta simulada del LLM para vulnerabilidades críticas.
    """
    return {
        "risk_score": 9.5,
        "severity": "critical",
        "recommendations": [
            "Immediately patch Apache Struts to version 2.5.30 or higher",
            "Implement Web Application Firewall (WAF) rules to block exploit attempts",
            "Isolate affected server from production network until patched",
            "Conduct emergency security audit of all systems running Apache Struts",
            "Enable enhanced monitoring and alerting for this asset",
        ],
        "confidence": 0.95,
        "reasoning": "Two critical vulnerabilities detected with active exploits in production environment. Immediate action required per ISO 27001 and NIST guidelines.",
    }


@pytest.fixture
def mock_llm_no_risk_response():
    """
    Respuesta simulada del LLM cuando no hay vulnerabilidades.
    """
    return {
        "risk_score": 0.5,
        "severity": "low",
        "recommendations": [
            "Maintain regular vulnerability scanning schedule",
            "Continue security patch management program",
            "Monitor for new CVEs affecting current software versions",
        ],
        "confidence": 0.85,
        "reasoning": "No vulnerabilities detected. Asset appears secure but requires ongoing monitoring.",
    }


@pytest.fixture
def mock_copilot_service(mock_llm_critical_response):
    """
    Fixture for properly mocked CopilotService.

    Returns AsyncMock with chat() method that returns dict with "text" key
    containing JSON string of the LLM response.
    """
    import json

    mock = AsyncMock(spec=CopilotService)
    # Mock create_session
    mock.create_session.return_value = {"provider": "mock", "messages": []}
    # Mock chat to return dict with "text" key containing JSON
    mock.chat.return_value = {
        "text": json.dumps(mock_llm_critical_response),
        "model": "test-model",
        "provider": "test",
        "tokens": 100,
        "tool_calls": [],
    }
    return mock


def create_mock_copilot_with_response(llm_response_dict: dict) -> AsyncMock:
    """
    Helper function to create properly configured CopilotService mock.

    Args:
        llm_response_dict: Dictionary with LLM response (will be JSON-serialized)

    Returns:
        AsyncMock configured to return the response in correct format
    """
    import json

    mock = AsyncMock(spec=CopilotService)
    # Mock create_session
    mock.create_session.return_value = {"provider": "mock", "messages": []}
    # Mock chat to return dict with "text" key containing JSON
    mock.chat.return_value = {
        "text": json.dumps(llm_response_dict),
        "model": "test-model",
        "provider": "test",
        "tokens": 100,
        "tool_calls": [],
    }
    return mock


# ============================================================================
# TEST CLASSES
# ============================================================================


class TestRiskAssessmentAgentInitialization:
    """Tests de inicialización del RiskAssessmentAgent."""

    def test_risk_agent_inherits_from_base_agent(self):
        """
        🔴 RED: RiskAssessmentAgent debe heredar de BaseAgent.

        Given: RiskAssessmentAgent class
        When: Se verifica herencia
        Then: Es subclase de BaseAgent
        """
        from app.agents.base_agent import BaseAgent

        assert issubclass(RiskAssessmentAgent, BaseAgent)

    def test_risk_agent_can_be_instantiated(self):
        """
        🔴 RED: RiskAssessmentAgent puede instanciarse con dependencias.

        Given: Dependencias mockeadas
        When: Se instancia RiskAssessmentAgent
        Then: Se crea correctamente
        """
        mock_copilot = MagicMock(spec=CopilotService)
        mock_rag = MagicMock(spec=RAGService)
        mock_db = MagicMock(spec=AsyncSession)

        agent = RiskAssessmentAgent(
            copilot_service=mock_copilot, rag_service=mock_rag, db_session=mock_db
        )

        assert agent is not None
        assert agent.name == "RiskAssessmentAgent"
        assert hasattr(agent, "assess_risk")


class TestRiskAssessmentWithCriticalVulnerabilities:
    """Tests de assessment con vulnerabilidades críticas."""

    @pytest.mark.asyncio
    async def test_assess_risk_with_critical_vulnerabilities(
        self, sample_asset, critical_vulnerabilities, mock_rag_context, mock_llm_critical_response
    ):
        """
        🔴 RED: assess_risk retorna score alto para vulnerabilidades críticas.

        Given: Asset crítico con 2 vulnerabilidades críticas
        When: Se ejecuta assess_risk
        Then: risk_score > 8.0 y severity = critical
        """
        # Setup mocks using helper function
        mock_copilot = create_mock_copilot_with_response(mock_llm_critical_response)

        mock_rag = AsyncMock(spec=RAGService)
        mock_rag.search.return_value = mock_rag_context

        # Create agent
        agent = RiskAssessmentAgent(
            copilot_service=mock_copilot, rag_service=mock_rag, db_session=MagicMock()
        )

        # Execute
        result = await agent.assess_risk(
            asset=sample_asset, vulnerabilities=critical_vulnerabilities
        )

        # Assert
        assert isinstance(result, RiskAssessment)
        assert result.risk_score > 8.0, (
            f"Expected critical risk score > 8.0, got {result.risk_score}"
        )
        assert result.severity == "critical", f"Expected severity 'critical', got {result.severity}"
        assert len(result.recommendations) > 0, "Expected recommendations for critical risk"
        assert 0.0 <= result.confidence <= 1.0, f"Confidence {result.confidence} out of range"

        # Verify RAG was used
        mock_rag.search.assert_called_once()

        # Verify copilot_service.chat was called
        mock_copilot.chat.assert_called_once()


class TestRiskAssessmentWithNoVulnerabilities:
    """Tests de assessment sin vulnerabilidades."""

    @pytest.mark.asyncio
    async def test_assess_risk_with_no_vulnerabilities(
        self, sample_asset, no_vulnerabilities, mock_llm_no_risk_response
    ):
        """
        🔴 RED: assess_risk retorna score bajo sin vulnerabilidades.

        Given: Asset sin vulnerabilidades
        When: Se ejecuta assess_risk
        Then: risk_score < 3.0 y severity = low
        """
        # Setup mocks using helper function
        mock_copilot = create_mock_copilot_with_response(mock_llm_no_risk_response)

        mock_rag = AsyncMock(spec=RAGService)
        mock_rag.search.return_value = []

        # Create agent
        agent = RiskAssessmentAgent(
            copilot_service=mock_copilot, rag_service=mock_rag, db_session=MagicMock()
        )

        # Execute
        result = await agent.assess_risk(asset=sample_asset, vulnerabilities=no_vulnerabilities)

        # Assert
        assert result.risk_score < 3.0, f"Expected low risk score < 3.0, got {result.risk_score}"
        assert result.severity in ["low", "info"], f"Expected low severity, got {result.severity}"
        assert len(result.recommendations) > 0, "Should still provide best practice recommendations"


class TestRiskAssessmentRAGIntegration:
    """Tests de integración con RAG Service."""

    @pytest.mark.asyncio
    async def test_assess_risk_uses_rag_context(
        self, sample_asset, critical_vulnerabilities, mock_rag_context
    ):
        """
        🔴 RED: assess_risk debe buscar contexto con RAG.

        Given: Asset con vulnerabilidades
        When: Se ejecuta assess_risk
        Then: Llama a RAG service para buscar contexto relevante
        """
        # Setup mocks - use simple response dict for this test
        simple_response = {
            "risk_score": 9.0,
            "severity": "critical",
            "recommendations": ["patch"],
            "confidence": 0.9,
            "reasoning": "test",
        }
        mock_copilot = create_mock_copilot_with_response(simple_response)

        mock_rag = AsyncMock(spec=RAGService)
        mock_rag.search.return_value = mock_rag_context

        # Create agent
        agent = RiskAssessmentAgent(
            copilot_service=mock_copilot, rag_service=mock_rag, db_session=MagicMock()
        )

        # Execute
        await agent.assess_risk(asset=sample_asset, vulnerabilities=critical_vulnerabilities)

        # Verify RAG was called with appropriate query
        mock_rag.search.assert_called_once()
        call_args = mock_rag.search.call_args

        # Check that search query mentions vulnerabilities or risk
        query = call_args.kwargs.get("query", "")
        assert any(term in query.lower() for term in ["vulnerability", "risk", "cve", "security"])

    @pytest.mark.asyncio
    async def test_assess_risk_includes_rag_context_in_prompt(
        self, sample_asset, critical_vulnerabilities, mock_rag_context
    ):
        """
        🔴 RED: assess_risk incluye contexto RAG en prompt al LLM.

        Given: RAG retorna documentos relevantes
        When: Se llama al LLM
        Then: El prompt incluye el contexto de RAG
        """
        # Setup mocks
        simple_response = {
            "risk_score": 9.0,
            "severity": "critical",
            "recommendations": ["patch"],
            "confidence": 0.9,
            "reasoning": "test",
        }
        mock_copilot = create_mock_copilot_with_response(simple_response)

        mock_rag = AsyncMock(spec=RAGService)
        mock_rag.search.return_value = mock_rag_context

        # Create agent
        agent = RiskAssessmentAgent(
            copilot_service=mock_copilot, rag_service=mock_rag, db_session=MagicMock()
        )

        # Execute
        await agent.assess_risk(asset=sample_asset, vulnerabilities=critical_vulnerabilities)

        # Verify copilot_service.chat was called with prompt that includes RAG context
        mock_copilot.chat.assert_called_once()
        # Get the second argument (message) from chat(session, message)
        call_args = mock_copilot.chat.call_args
        llm_prompt = call_args[0][1]  # Second positional arg

        # Check that at least one RAG document source is mentioned
        assert any(doc["source"] in llm_prompt for doc in mock_rag_context)


class TestRiskAssessmentValidation:
    """Tests de validación de resultados."""

    @pytest.mark.asyncio
    async def test_assess_risk_confidence_score_valid_range(
        self, sample_asset, critical_vulnerabilities
    ):
        """
        🔴 RED: confidence score debe estar entre 0.0 y 1.0.

        Given: Cualquier assessment
        When: Se ejecuta assess_risk
        Then: confidence está en rango válido [0.0, 1.0]
        """
        # Setup mocks
        test_response = {
            "risk_score": 8.0,
            "severity": "high",
            "recommendations": ["test"],
            "confidence": 0.88,
            "reasoning": "test",
        }
        mock_copilot = create_mock_copilot_with_response(test_response)

        mock_rag = AsyncMock(spec=RAGService)
        mock_rag.search.return_value = []

        # Create agent
        agent = RiskAssessmentAgent(
            copilot_service=mock_copilot, rag_service=mock_rag, db_session=MagicMock()
        )

        # Execute
        result = await agent.assess_risk(
            asset=sample_asset, vulnerabilities=critical_vulnerabilities
        )

        # Assert
        assert 0.0 <= result.confidence <= 1.0, (
            f"Confidence {result.confidence} must be between 0.0 and 1.0"
        )

    @pytest.mark.asyncio
    async def test_assess_risk_recommendations_not_empty_for_high_risk(
        self, sample_asset, critical_vulnerabilities
    ):
        """
        🔴 RED: Riesgos altos deben tener recomendaciones.

        Given: Assessment con risk_score > 7.0
        When: Se retorna resultado
        Then: recommendations no está vacía
        """
        # Setup mocks
        test_response = {
            "risk_score": 9.2,
            "severity": "critical",
            "recommendations": ["Patch immediately", "Isolate system"],
            "confidence": 0.94,
            "reasoning": "test",
        }
        mock_copilot = create_mock_copilot_with_response(test_response)

        mock_rag = AsyncMock(spec=RAGService)
        mock_rag.search.return_value = []

        # Create agent
        agent = RiskAssessmentAgent(
            copilot_service=mock_copilot, rag_service=mock_rag, db_session=MagicMock()
        )

        # Execute
        result = await agent.assess_risk(
            asset=sample_asset, vulnerabilities=critical_vulnerabilities
        )

        # Assert
        if result.risk_score > 7.0:
            assert len(result.recommendations) > 0, (
                "High/Critical risks must have actionable recommendations"
            )
            assert all(len(rec) > 10 for rec in result.recommendations), (
                "Recommendations should be meaningful (> 10 chars)"
            )

    @pytest.mark.asyncio
    async def test_assess_risk_score_range_validation(self, sample_asset, medium_vulnerabilities):
        """
        🔴 RED: risk_score debe estar entre 0.0 y 10.0.

        Given: Cualquier assessment
        When: Se retorna resultado
        Then: risk_score está en rango válido [0.0, 10.0]
        """
        # Setup mocks
        test_response = {
            "risk_score": 5.3,
            "severity": "medium",
            "recommendations": ["Monitor"],
            "confidence": 0.82,
            "reasoning": "test",
        }
        mock_copilot = create_mock_copilot_with_response(test_response)

        mock_rag = AsyncMock(spec=RAGService)
        mock_rag.search.return_value = []

        # Create agent
        agent = RiskAssessmentAgent(
            copilot_service=mock_copilot, rag_service=mock_rag, db_session=MagicMock()
        )

        # Execute
        result = await agent.assess_risk(asset=sample_asset, vulnerabilities=medium_vulnerabilities)

        # Assert
        assert 0.0 <= result.risk_score <= 10.0, (
            f"Risk score {result.risk_score} must be between 0.0 and 10.0"
        )


class TestRiskAssessmentType:
    """Tests del tipo RiskAssessment."""

    def test_risk_assessment_can_be_created(self):
        """
        🔴 RED: RiskAssessment puede crearse con datos válidos.

        Given: Datos de assessment
        When: Se crea RiskAssessment
        Then: Se crea correctamente con todos los campos
        """
        assessment = RiskAssessment(
            risk_score=8.5,
            severity="high",
            recommendations=["Patch urgently", "Monitor"],
            confidence=0.91,
            asset_id="asset-001",
            vulnerabilities_count=2,
            reasoning="Two critical CVEs detected",
        )

        assert assessment.risk_score == 8.5
        assert assessment.severity == "high"
        assert len(assessment.recommendations) == 2
        assert assessment.confidence == 0.91
        assert assessment.asset_id == "asset-001"

    def test_risk_assessment_validates_severity(self):
        """
        🔴 RED: RiskAssessment valida que severity sea válida.

        Given: severity inválida
        When: Se crea RiskAssessment
        Then: Lanza ValueError
        """
        with pytest.raises(ValueError, match="Severity must be one of"):
            RiskAssessment(
                risk_score=5.0,
                severity="invalid",  # Inválido
                recommendations=[],
                confidence=0.8,
            )
