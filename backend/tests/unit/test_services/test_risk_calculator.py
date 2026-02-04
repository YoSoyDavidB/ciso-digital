"""
Tests para RiskCalculator Service.

🔴 RED: Estos tests deben FALLAR inicialmente porque RiskCalculator no existe.

El servicio calcula risk scores basado en:
- Lista de vulnerabilidades (cvss_score 0.0-10.0)
- Criticidad del asset (critical, high, medium, low)

Lógica:
1. Sin vulnerabilidades → 0.0
2. Promedio de CVSS scores
3. Multiplicador por criticidad: critical=1.5x, high=1.2x, medium=1.0x, low=0.8x
4. Score máximo: 10.0
"""

from dataclasses import dataclass

import pytest


# =============================================================================
# Test Data Models (para tests antes de que existan los reales)
# =============================================================================


@dataclass
class VulnerabilityData:
    """Datos de vulnerabilidad para tests."""

    cvss_score: float
    cve_id: str = "CVE-2025-0001"
    description: str = "Test vulnerability"


# =============================================================================
# Test Class
# =============================================================================


class TestRiskCalculator:
    """Tests para el servicio RiskCalculator."""

    # =========================================================================
    # Test: No Vulnerabilities
    # =========================================================================

    @pytest.mark.unit
    def test_calculate_score_no_vulnerabilities_returns_zero(self) -> None:
        """
        Test que sin vulnerabilidades el score es 0.0.

        Given: Lista vacía de vulnerabilidades
        When: Se calcula el risk score
        Then: Debe retornar 0.0
        """
        from app.services.risk_calculator import RiskCalculator

        calculator = RiskCalculator()
        vulnerabilities: list[VulnerabilityData] = []

        score = calculator.calculate_score(
            vulnerabilities=vulnerabilities,
            asset_criticality="high",
        )

        assert score == 0.0

    # =========================================================================
    # Test: Single Vulnerability
    # =========================================================================

    @pytest.mark.unit
    def test_calculate_score_single_vulnerability(self) -> None:
        """
        Test con una sola vulnerabilidad.

        Given: Una vulnerabilidad con CVSS 8.0, asset medium
        When: Se calcula el risk score
        Then: Debe retornar 8.0 (8.0 * 1.0 para medium)
        """
        from app.services.risk_calculator import RiskCalculator

        calculator = RiskCalculator()
        vulnerabilities = [
            VulnerabilityData(cvss_score=8.0, cve_id="CVE-2025-1234"),
        ]

        score = calculator.calculate_score(
            vulnerabilities=vulnerabilities,
            asset_criticality="medium",
        )

        assert score == 8.0

    # =========================================================================
    # Test: Multiple Vulnerabilities
    # =========================================================================

    @pytest.mark.unit
    def test_calculate_score_multiple_vulnerabilities(self) -> None:
        """
        Test con múltiples vulnerabilidades.

        Given: Tres vulnerabilidades con CVSS 6.0, 8.0, 10.0, asset medium
        When: Se calcula el risk score
        Then: Debe retornar 8.0 (promedio: (6+8+10)/3 = 8.0, * 1.0)
        """
        from app.services.risk_calculator import RiskCalculator

        calculator = RiskCalculator()
        vulnerabilities = [
            VulnerabilityData(cvss_score=6.0, cve_id="CVE-2025-0001"),
            VulnerabilityData(cvss_score=8.0, cve_id="CVE-2025-0002"),
            VulnerabilityData(cvss_score=10.0, cve_id="CVE-2025-0003"),
        ]

        score = calculator.calculate_score(
            vulnerabilities=vulnerabilities,
            asset_criticality="medium",
        )

        assert score == 8.0

    # =========================================================================
    # Test: Critical Asset Multiplier
    # =========================================================================

    @pytest.mark.unit
    def test_calculate_score_critical_asset_applies_multiplier(self) -> None:
        """
        Test que asset crítico aplica multiplicador 1.5x.

        Given: Una vulnerabilidad con CVSS 6.0, asset critical
        When: Se calcula el risk score
        Then: Debe retornar 9.0 (6.0 * 1.5)
        """
        from app.services.risk_calculator import RiskCalculator

        calculator = RiskCalculator()
        vulnerabilities = [
            VulnerabilityData(cvss_score=6.0, cve_id="CVE-2025-1234"),
        ]

        score = calculator.calculate_score(
            vulnerabilities=vulnerabilities,
            asset_criticality="critical",
        )

        assert score == 9.0  # 6.0 * 1.5

    @pytest.mark.unit
    def test_calculate_score_high_asset_applies_multiplier(self) -> None:
        """
        Test que asset high aplica multiplicador 1.2x.

        Given: Una vulnerabilidad con CVSS 5.0, asset high
        When: Se calcula el risk score
        Then: Debe retornar 6.0 (5.0 * 1.2)
        """
        from app.services.risk_calculator import RiskCalculator

        calculator = RiskCalculator()
        vulnerabilities = [
            VulnerabilityData(cvss_score=5.0, cve_id="CVE-2025-1234"),
        ]

        score = calculator.calculate_score(
            vulnerabilities=vulnerabilities,
            asset_criticality="high",
        )

        assert score == 6.0  # 5.0 * 1.2

    @pytest.mark.unit
    def test_calculate_score_low_asset_applies_multiplier(self) -> None:
        """
        Test que asset low aplica multiplicador 0.8x.

        Given: Una vulnerabilidad con CVSS 10.0, asset low
        When: Se calcula el risk score
        Then: Debe retornar 8.0 (10.0 * 0.8)
        """
        from app.services.risk_calculator import RiskCalculator

        calculator = RiskCalculator()
        vulnerabilities = [
            VulnerabilityData(cvss_score=10.0, cve_id="CVE-2025-1234"),
        ]

        score = calculator.calculate_score(
            vulnerabilities=vulnerabilities,
            asset_criticality="low",
        )

        assert score == 8.0  # 10.0 * 0.8

    # =========================================================================
    # Test: Max Score Cap
    # =========================================================================

    @pytest.mark.unit
    def test_calculate_score_never_exceeds_max(self) -> None:
        """
        Test que el score nunca excede 10.0.

        Given: Vulnerabilidades con CVSS alto + asset critical
        When: El cálculo excedería 10.0
        Then: Debe retornar exactamente 10.0
        """
        from app.services.risk_calculator import RiskCalculator

        calculator = RiskCalculator()
        vulnerabilities = [
            VulnerabilityData(cvss_score=9.0, cve_id="CVE-2025-0001"),
            VulnerabilityData(cvss_score=10.0, cve_id="CVE-2025-0002"),
        ]

        score = calculator.calculate_score(
            vulnerabilities=vulnerabilities,
            asset_criticality="critical",
        )

        # Promedio: 9.5, * 1.5 = 14.25, pero max es 10.0
        assert score == 10.0

    @pytest.mark.unit
    def test_calculate_score_exactly_at_max(self) -> None:
        """
        Test cuando el cálculo da exactamente 10.0.

        Given: Vulnerabilidad CVSS 10.0, asset medium
        When: Se calcula el risk score
        Then: Debe retornar 10.0
        """
        from app.services.risk_calculator import RiskCalculator

        calculator = RiskCalculator()
        vulnerabilities = [
            VulnerabilityData(cvss_score=10.0, cve_id="CVE-2025-1234"),
        ]

        score = calculator.calculate_score(
            vulnerabilities=vulnerabilities,
            asset_criticality="medium",
        )

        assert score == 10.0

    # =========================================================================
    # Test: Edge Cases
    # =========================================================================

    @pytest.mark.unit
    def test_calculate_score_with_zero_cvss(self) -> None:
        """
        Test con vulnerabilidad de CVSS 0.0.

        Given: Vulnerabilidad con CVSS 0.0
        When: Se calcula el risk score
        Then: Debe retornar 0.0
        """
        from app.services.risk_calculator import RiskCalculator

        calculator = RiskCalculator()
        vulnerabilities = [
            VulnerabilityData(cvss_score=0.0, cve_id="CVE-2025-1234"),
        ]

        score = calculator.calculate_score(
            vulnerabilities=vulnerabilities,
            asset_criticality="critical",
        )

        assert score == 0.0  # 0.0 * 1.5 = 0.0

    @pytest.mark.unit
    def test_calculate_score_mixed_cvss_values(self) -> None:
        """
        Test con valores CVSS mixtos incluyendo 0.

        Given: Vulnerabilidades con CVSS 0.0, 5.0, 10.0, asset high
        When: Se calcula el risk score
        Then: Debe calcular correctamente el promedio con multiplicador
        """
        from app.services.risk_calculator import RiskCalculator

        calculator = RiskCalculator()
        vulnerabilities = [
            VulnerabilityData(cvss_score=0.0, cve_id="CVE-2025-0001"),
            VulnerabilityData(cvss_score=5.0, cve_id="CVE-2025-0002"),
            VulnerabilityData(cvss_score=10.0, cve_id="CVE-2025-0003"),
        ]

        score = calculator.calculate_score(
            vulnerabilities=vulnerabilities,
            asset_criticality="high",
        )

        # Promedio: (0+5+10)/3 = 5.0, * 1.2 = 6.0
        assert score == 6.0
