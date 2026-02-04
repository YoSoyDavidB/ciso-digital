"""
RiskCalculator Service - Calcula risk scores basado en vulnerabilidades y criticidad.

🔵 REFACTOR: Código mejorado con validaciones, logging y mejor estructura.
"""

import logging
from typing import Any, Literal, Protocol


# =============================================================================
# Module Logger
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# Type Definitions
# =============================================================================

# Type alias para criticidad de assets
AssetCriticality = Literal["critical", "high", "medium", "low"]


class VulnerabilityProtocol(Protocol):
    """Protocol para objetos tipo Vulnerability que tienen cvss_score."""

    cvss_score: float


# =============================================================================
# Service Class
# =============================================================================


class RiskCalculator:
    """
    Servicio para calcular risk scores basado en vulnerabilidades y criticidad del asset.

    El cálculo toma en cuenta:
    - CVSS scores de las vulnerabilidades (rango válido: 0.0-10.0)
    - Criticidad del asset (critical, high, medium, low)
    - Score máximo de 10.0

    Attributes:
        CRITICALITY_MULTIPLIERS: Multiplicadores por nivel de criticidad
        MAX_SCORE: Score máximo permitido (10.0)
        MIN_SCORE: Score mínimo permitido (0.0)
        MIN_CVSS: CVSS score mínimo válido (0.0)
        MAX_CVSS: CVSS score máximo válido (10.0)
    """

    # Constantes de configuración
    CRITICALITY_MULTIPLIERS: dict[str, float] = {
        "critical": 1.5,
        "high": 1.2,
        "medium": 1.0,
        "low": 0.8,
    }

    MAX_SCORE: float = 10.0
    MIN_SCORE: float = 0.0
    MIN_CVSS: float = 0.0
    MAX_CVSS: float = 10.0

    def calculate_score(
        self,
        vulnerabilities: list[Any],
        asset_criticality: str,
    ) -> float:
        """
        Calcula el risk score basado en vulnerabilidades y criticidad del asset.

        Lógica del cálculo:
        1. Si no hay vulnerabilidades, retorna 0.0
        2. Valida CVSS scores (0.0-10.0)
        3. Valida criticidad del asset
        4. Calcula el promedio de CVSS scores
        5. Aplica multiplicador según criticidad del asset
        6. Limita el resultado al máximo de 10.0

        Args:
            vulnerabilities: Lista de vulnerabilidades con cvss_score.
                Cada vulnerabilidad debe tener un atributo cvss_score: float (0.0-10.0).
            asset_criticality: Nivel de criticidad del asset.
                Debe ser uno de: 'critical', 'high', 'medium', 'low'.

        Returns:
            float: Risk score entre 0.0 y 10.0, donde:
                - 0.0: Sin riesgo o sin vulnerabilidades
                - 10.0: Riesgo máximo

        Raises:
            ValueError: Si asset_criticality no es un valor válido.
            ValueError: Si algún cvss_score está fuera del rango 0.0-10.0.

        Example:
            >>> calculator = RiskCalculator()
            >>> vulns = [Vulnerability(cvss_score=8.0)]
            >>> score = calculator.calculate_score(vulns, "critical")
            >>> print(score)
            10.0  # 8.0 * 1.5 = 12.0, capped at 10.0
        """
        logger.debug(
            f"Calculating risk score for {len(vulnerabilities)} vulnerabilities "
            f"with asset criticality: {asset_criticality}"
        )

        # 1. Sin vulnerabilidades → score 0.0
        if not vulnerabilities:
            logger.debug("No vulnerabilities provided, returning 0.0")
            return self.MIN_SCORE

        # 2. Validar criticidad del asset
        self._validate_asset_criticality(asset_criticality)

        # 3. Calcular promedio de CVSS scores (con validación)
        average_cvss = self._calculate_average_cvss(vulnerabilities)

        # 4. Aplicar multiplicador por criticidad
        multiplier = self._get_criticality_multiplier(asset_criticality)
        raw_risk_score = average_cvss * multiplier

        # 5. Limitar al rango válido [MIN_SCORE, MAX_SCORE]
        final_score = self._cap_score(raw_risk_score)

        logger.debug(
            f"Risk score calculated: avg_cvss={average_cvss:.2f}, "
            f"multiplier={multiplier:.2f}, raw={raw_risk_score:.2f}, "
            f"final={final_score:.2f}"
        )

        return final_score

    # =========================================================================
    # Private Helper Methods
    # =========================================================================

    def _validate_asset_criticality(self, criticality: str) -> None:
        """
        Valida que la criticidad del asset sea un valor válido.

        Args:
            criticality: Nivel de criticidad a validar.

        Raises:
            ValueError: Si criticality no es un valor válido.
        """
        valid_criticalities = set(self.CRITICALITY_MULTIPLIERS.keys())
        if criticality not in valid_criticalities:
            error_msg = (
                f"Invalid asset_criticality: '{criticality}'. "
                f"Must be one of: {sorted(valid_criticalities)}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _calculate_average_cvss(self, vulnerabilities: list[Any]) -> float:
        """
        Calcula el promedio de CVSS scores, validando cada score.

        Args:
            vulnerabilities: Lista de vulnerabilidades con cvss_score.

        Returns:
            float: Promedio de CVSS scores.

        Raises:
            ValueError: Si algún cvss_score está fuera del rango válido.
        """
        cvss_scores = []

        for idx, vuln in enumerate(vulnerabilities):
            cvss = vuln.cvss_score

            # Validar rango de CVSS
            if not (self.MIN_CVSS <= cvss <= self.MAX_CVSS):
                error_msg = (
                    f"Invalid CVSS score at index {idx}: {cvss}. "
                    f"Must be between {self.MIN_CVSS} and {self.MAX_CVSS}"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)

            cvss_scores.append(cvss)

        total_cvss = sum(cvss_scores)
        average: float = total_cvss / len(cvss_scores)

        return average

    def _get_criticality_multiplier(self, criticality: str) -> float:
        """
        Obtiene el multiplicador para una criticidad dada.

        Args:
            criticality: Nivel de criticidad del asset.

        Returns:
            float: Multiplicador correspondiente.
        """
        # Usamos .get() con default 1.0 por si acaso, aunque ya validamos antes
        return self.CRITICALITY_MULTIPLIERS.get(criticality, 1.0)

    def _cap_score(self, score: float) -> float:
        """
        Limita el score al rango válido [MIN_SCORE, MAX_SCORE].

        Args:
            score: Score a limitar.

        Returns:
            float: Score limitado al rango válido.
        """
        return max(self.MIN_SCORE, min(score, self.MAX_SCORE))
