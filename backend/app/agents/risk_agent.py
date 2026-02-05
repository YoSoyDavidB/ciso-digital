"""
RiskAssessmentAgent - AI agent for security risk assessment.

🔵 REFACTOR PHASE: Improved structure with Copilot SDK tools and separated concerns.

This agent analyzes assets and vulnerabilities to provide risk scores,
severity ratings, and actionable recommendations using LLM, RAG, and tool calling.
"""

import ast
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from copilot import define_tool

from app.agents.base_agent import AgentResponse, BaseAgent, Task
from app.core.logging import get_logger, log_llm_call, log_rag_retrieval


logger = get_logger(__name__)

# Constants
PROMPT_DIR = Path(__file__).parent / "prompts"
SYSTEM_PROMPT_FILE = PROMPT_DIR / "risk_assessment_system.txt"
USER_PROMPT_FILE = PROMPT_DIR / "risk_assessment_user.txt"

# Risk score thresholds for severity classification
SEVERITY_THRESHOLDS = {
    "critical": 9.0,
    "high": 7.0,
    "medium": 4.0,
    "low": 1.0,
    "info": 0.0,
}


@dataclass
class RiskAssessment:
    """
    Risk assessment result from RiskAssessmentAgent.

    Attributes:
        risk_score: Risk score from 0.0 (no risk) to 10.0 (critical)
        severity: Risk severity level (critical, high, medium, low, info)
        recommendations: List of actionable remediation steps
        confidence: Confidence in assessment (0.0-1.0)
        asset_id: ID of the assessed asset
        vulnerabilities_count: Number of vulnerabilities analyzed
        reasoning: Explanation of the risk assessment
    """

    risk_score: float
    severity: str
    recommendations: list[str]
    confidence: float
    asset_id: str = ""
    vulnerabilities_count: int = 0
    reasoning: str = ""

    def __post_init__(self):
        """Validate risk assessment data after initialization."""
        self._validate_severity()
        self._validate_risk_score()
        self._validate_confidence()

    def _validate_severity(self) -> None:
        """Validate severity is one of the allowed values."""
        valid_severities = {"critical", "high", "medium", "low", "info"}
        if self.severity not in valid_severities:
            raise ValueError(f"Severity must be one of {valid_severities}, got '{self.severity}'")

    def _validate_risk_score(self) -> None:
        """Validate risk score is within valid range."""
        if not (0.0 <= self.risk_score <= 10.0):
            raise ValueError(f"Risk score must be between 0.0 and 10.0, got {self.risk_score}")

    def _validate_confidence(self) -> None:
        """Validate confidence score is within valid range."""
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")


class RiskAssessmentAgent(BaseAgent):
    """
    AI agent specialized in security risk assessment.

    Evaluates assets and vulnerabilities using:
    - GitHub Copilot SDK for LLM analysis with tool calling
    - RAG for context from security knowledge base
    - CVSS scoring and asset criticality assessment
    - Industry frameworks (ISO 27001, NIST 800-53)

    Returns structured risk assessments with scores, severity, and recommendations.
    """

    async def get_system_prompt(self) -> str:
        """
        Load system prompt from template file.

        Returns:
            System prompt defining agent role and response format

        Raises:
            FileNotFoundError: If prompt template file is missing
        """
        try:
            with open(SYSTEM_PROMPT_FILE, encoding="utf-8") as f:
                prompt = f.read().strip()
            logger.debug(f"📄 Loaded system prompt from {SYSTEM_PROMPT_FILE}")
            return prompt
        except FileNotFoundError:
            logger.warning(f"⚠️ Prompt file not found: {SYSTEM_PROMPT_FILE}, using fallback")
            return self._get_fallback_system_prompt()

    def _get_fallback_system_prompt(self) -> str:
        """
        Fallback system prompt if template file is missing.

        Returns:
            Hardcoded system prompt
        """
        return """You are a cybersecurity risk assessment expert with deep knowledge of:
- ISO 27001 and ISO 27005 risk management standards
- NIST 800-53 security controls
- CVSS vulnerability scoring
- Industry best practices for risk assessment

Your role is to analyze assets and their vulnerabilities to provide:
1. Accurate risk scores (0.0-10.0)
2. Severity classification (critical/high/medium/low/info)
3. Actionable remediation recommendations
4. Confidence assessment of your analysis

Always respond in JSON format with: risk_score, severity, recommendations, confidence, reasoning."""

    def get_tools(self) -> list:
        """
        Get tools available to this agent for enhanced risk assessment.

        Returns:
            List of tool functions decorated with @define_tool

        Note:
            Tools enable the agent to:
            - Search security knowledge base
            - Calculate risk scores programmatically
            - Query vulnerability databases
        """

        @define_tool
        async def search_risk_knowledge(query: str) -> str:
            """
            Search security knowledge base for relevant risk information.

            Args:
                query: Search query for risk-related information

            Returns:
                JSON string with search results
            """
            try:
                logger.debug(f"🔍 Tool: search_risk_knowledge(query='{query[:50]}...')")
                results = await self.gather_context(query=query, limit=5)

                formatted_results = [
                    {
                        "text": doc.get("text", "")[:200],
                        "source": doc.get("source", "unknown"),
                        "score": doc.get("score", 0.0),
                    }
                    for doc in results
                ]

                return json.dumps(
                    {"success": True, "results": formatted_results, "count": len(formatted_results)}
                )

            except Exception as e:
                logger.error(f"❌ Tool error in search_risk_knowledge: {e}")
                return json.dumps({"success": False, "error": str(e), "results": []})

        @define_tool
        async def calculate_severity_from_score(risk_score: float) -> str:
            """
            Calculate severity classification from numeric risk score.

            Args:
                risk_score: Numeric risk score (0.0-10.0)

            Returns:
                JSON string with severity classification
            """
            try:
                logger.debug(f"🎯 Tool: calculate_severity_from_score(risk_score={risk_score})")

                if risk_score >= SEVERITY_THRESHOLDS["critical"]:
                    severity = "critical"
                elif risk_score >= SEVERITY_THRESHOLDS["high"]:
                    severity = "high"
                elif risk_score >= SEVERITY_THRESHOLDS["medium"]:
                    severity = "medium"
                elif risk_score >= SEVERITY_THRESHOLDS["low"]:
                    severity = "low"
                else:
                    severity = "info"

                return json.dumps(
                    {
                        "success": True,
                        "severity": severity,
                        "risk_score": risk_score,
                        "threshold": SEVERITY_THRESHOLDS[severity],
                    }
                )

            except Exception as e:
                logger.error(f"❌ Tool error in calculate_severity_from_score: {e}")
                return json.dumps({"success": False, "error": str(e)})

        @define_tool
        async def get_cvss_context(cvss_score: float) -> str:
            """
            Get contextual information about CVSS score severity.

            Args:
                cvss_score: CVSS vulnerability score (0.0-10.0)

            Returns:
                JSON string with CVSS severity context
            """
            try:
                logger.debug(f"📊 Tool: get_cvss_context(cvss_score={cvss_score})")

                # CVSS severity ranges per NIST
                if cvss_score == 0.0:
                    category = "None"
                    description = "No vulnerability"
                elif cvss_score < 4.0:
                    category = "Low"
                    description = "Limited impact, difficult to exploit"
                elif cvss_score < 7.0:
                    category = "Medium"
                    description = "Moderate impact, somewhat difficult to exploit"
                elif cvss_score < 9.0:
                    category = "High"
                    description = "Significant impact, relatively easy to exploit"
                else:
                    category = "Critical"
                    description = "Severe impact, easy to exploit"

                return json.dumps(
                    {
                        "success": True,
                        "cvss_score": cvss_score,
                        "category": category,
                        "description": description,
                        "requires_immediate_action": cvss_score >= 9.0,
                    }
                )

            except Exception as e:
                logger.error(f"❌ Tool error in get_cvss_context: {e}")
                return json.dumps({"success": False, "error": str(e)})

        logger.debug("🔧 Registered 3 tools for RiskAssessmentAgent")
        return [search_risk_knowledge, calculate_severity_from_score, get_cvss_context]

    async def execute(self, task: Task) -> AgentResponse:
        """
        Execute risk assessment task.

        Args:
            task: Task with context containing 'asset' and 'vulnerabilities'

        Returns:
            AgentResponse with risk assessment summary
        """
        logger.info(f"▶️ Executing RiskAssessmentAgent task: {task.query[:50]}...")

        asset = task.context.get("asset", {})
        vulnerabilities = task.context.get("vulnerabilities", [])

        # Perform risk assessment
        result = await self.assess_risk(asset=asset, vulnerabilities=vulnerabilities)

        # Build response message
        response_text = self._format_assessment_response(result)

        logger.info(f"✅ RiskAssessmentAgent task complete: score={result.risk_score:.1f}")

        return AgentResponse(
            response=response_text,
            confidence=result.confidence,
            sources=[],
            actions_taken=["risk_assessment"],
        )

    async def assess_risk(
        self, asset: dict[str, Any], vulnerabilities: list[dict[str, Any]]
    ) -> RiskAssessment:
        """
        Assess risk for an asset based on its vulnerabilities.

        Uses Copilot SDK with tool calling for enhanced analysis:
        1. Gathers context from RAG knowledge base (via tools)
        2. Builds structured prompt with asset/vulnerability details
        3. Calls LLM with tool access for analysis
        4. Parses and validates response
        5. Returns structured RiskAssessment

        Args:
            asset: Asset information including id, name, type, criticality
            vulnerabilities: List of vulnerabilities with cvss_score, cve_id, description

        Returns:
            RiskAssessment with score, severity, recommendations, and confidence

        Raises:
            ValueError: If asset or vulnerability data is invalid
            json.JSONDecodeError: If LLM response is not valid JSON
        """
        # Start timing for performance metrics
        start_time = time.time()

        asset_id = asset.get("id", "unknown")
        asset_name = asset.get("name", "unknown")
        asset_criticality = asset.get("criticality", "medium")
        vuln_count = len(vulnerabilities)

        # Log assessment start with structured data
        logger.info(
            "risk_assessment_started",
            asset_id=asset_id,
            asset_name=asset_name,
            asset_criticality=asset_criticality,
            vulnerabilities_count=vuln_count,
        )

        # 1. Gather context from RAG knowledge base
        rag_start = time.time()
        context_docs = await self._gather_risk_context(asset, vulnerabilities)
        rag_latency_ms = int((time.time() - rag_start) * 1000)

        # Log RAG retrieval with metrics
        log_rag_retrieval(
            query=f"risk assessment {asset.get('type', 'system')}",
            num_results=len(context_docs),
            latency_ms=rag_latency_ms,
        )

        logger.info(
            "rag_retrieval_completed",
            asset_id=asset_id,
            documents_retrieved=len(context_docs),
            latency_ms=rag_latency_ms,
        )

        # 2. Build structured prompt using template
        prompt = self._build_assessment_prompt(asset, vulnerabilities, context_docs)
        prompt_length = len(prompt)
        estimated_prompt_tokens = prompt_length // 4  # Rough estimate

        logger.debug(
            "assessment_prompt_built",
            asset_id=asset_id,
            prompt_length_chars=prompt_length,
            estimated_tokens=estimated_prompt_tokens,
        )

        # 3. Call LLM with Copilot SDK (tools available automatically)
        llm_start = time.time()

        logger.info(
            "llm_call_started",
            asset_id=asset_id,
            agent="risk_assessment",
            model="claude-sonnet-4.5",  # Default model
        )

        try:
            llm_response = await self.chat(prompt)
            llm_success = True
        except Exception as e:
            logger.error(
                "llm_call_failed",
                asset_id=asset_id,
                error=str(e),
                exc_info=True,
            )
            raise

        llm_latency_ms = int((time.time() - llm_start) * 1000)

        # Estimate tokens (more accurate tracking would come from LLM response metadata)
        estimated_completion_tokens = len(llm_response) // 4

        # Log LLM call with metrics
        log_llm_call(
            agent_name="risk_assessment",
            model="claude-sonnet-4.5",  # Default model
            prompt_tokens=estimated_prompt_tokens,
            completion_tokens=estimated_completion_tokens,
            latency_ms=llm_latency_ms,
            success=llm_success,
        )

        logger.info(
            "llm_call_completed",
            asset_id=asset_id,
            latency_ms=llm_latency_ms,
            response_length=len(llm_response),
        )

        # 4. Parse response (handle both dict and JSON string)
        try:
            parsed_result = self._parse_llm_response(llm_response)

            logger.debug(
                "llm_response_parsed",
                asset_id=asset_id,
                risk_score=parsed_result.get("risk_score"),
                severity=parsed_result.get("severity"),
                recommendations_count=len(parsed_result.get("recommendations", [])),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(
                "llm_response_parse_failed",
                asset_id=asset_id,
                error=str(e),
                response_preview=llm_response[:200] if llm_response else "",
                exc_info=True,
            )
            raise

        # 5. Create and validate RiskAssessment
        try:
            assessment = RiskAssessment(
                risk_score=float(parsed_result["risk_score"]),
                severity=parsed_result["severity"],
                recommendations=parsed_result["recommendations"],
                confidence=float(parsed_result["confidence"]),
                asset_id=asset_id,
                vulnerabilities_count=vuln_count,
                reasoning=parsed_result.get("reasoning", ""),
            )
        except (KeyError, ValueError, TypeError) as e:
            logger.error(
                "risk_assessment_validation_failed",
                asset_id=asset_id,
                error=str(e),
                parsed_result=parsed_result,
                exc_info=True,
            )
            raise

        # 6. Log action for audit trail
        await self.log_action(
            "risk_assessment",
            {
                "asset_id": asset_id,
                "risk_score": assessment.risk_score,
                "severity": assessment.severity,
                "vulnerabilities_count": vuln_count,
            },
        )

        # Calculate total processing time
        total_latency_ms = int((time.time() - start_time) * 1000)

        # Log successful completion with comprehensive metrics
        logger.info(
            "risk_assessment_completed",
            asset_id=asset_id,
            asset_name=asset_name,
            asset_criticality=asset_criticality,
            vulnerabilities_count=vuln_count,
            risk_score=assessment.risk_score,
            severity=assessment.severity,
            confidence=assessment.confidence,
            recommendations_count=len(assessment.recommendations),
            rag_documents_retrieved=len(context_docs),
            llm_latency_ms=llm_latency_ms,
            rag_latency_ms=rag_latency_ms,
            total_latency_ms=total_latency_ms,
        )

        return assessment

    async def _gather_risk_context(
        self, asset: dict[str, Any], vulnerabilities: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Gather relevant context from knowledge base using RAG.

        Args:
            asset: Asset being assessed
            vulnerabilities: List of vulnerabilities

        Returns:
            List of relevant documents from knowledge base
        """
        # Build search query from asset and vulnerability info
        asset_type = asset.get("type", "system")
        vuln_count = len(vulnerabilities)

        # Extract CVE IDs for specific searches
        cve_ids = [v.get("cve_id", "") for v in vulnerabilities if v.get("cve_id")]
        cve_text = " ".join(cve_ids[:3])  # Limit to top 3 CVEs

        query = (
            f"risk assessment {asset_type} vulnerabilities {vuln_count} "
            f"security controls mitigation {cve_text}"
        )

        logger.debug(
            "rag_query_building",
            asset_type=asset_type,
            vuln_count=vuln_count,
            cve_count=len(cve_ids),
        )

        try:
            context_docs = await self.gather_context(query=query, limit=5)

            logger.debug(
                "rag_documents_retrieved",
                query=query,
                documents_count=len(context_docs),
                sources=[
                    doc.get("source", "unknown") for doc in context_docs[:3]
                ],  # Log first 3 sources
            )

            return context_docs
        except Exception as e:
            logger.warning(
                "rag_retrieval_failed",
                query=query,
                error=str(e),
                exc_info=True,
            )
            return []

    def _build_assessment_prompt(
        self,
        asset: dict[str, Any],
        vulnerabilities: list[dict[str, Any]],
        context_docs: list[dict[str, Any]],
    ) -> str:
        """
        Build structured prompt for LLM risk assessment using template.

        Args:
            asset: Asset information
            vulnerabilities: List of vulnerabilities
            context_docs: Relevant context from knowledge base

        Returns:
            Formatted prompt string
        """
        try:
            # Load template
            with open(USER_PROMPT_FILE, encoding="utf-8") as f:
                template = f.read()

            # Format vulnerabilities list
            if vulnerabilities:
                vuln_list = []
                for vuln in vulnerabilities:
                    cvss = vuln.get("cvss_score", 0.0)
                    cve_id = vuln.get("cve_id", "Unknown")
                    description = vuln.get("description", "No description")
                    vuln_list.append(f"- **{cve_id}** (CVSS: {cvss}): {description}")
                vulnerabilities_list = "\n".join(vuln_list)
            else:
                vulnerabilities_list = "- No vulnerabilities detected"

            # Format RAG context
            if context_docs:
                rag_lines = ["## RELEVANT SECURITY GUIDANCE\n"]
                for i, doc in enumerate(context_docs, 1):
                    text = doc.get("text", "")
                    source = doc.get("source", "unknown")
                    text_preview = text[:300] + "..." if len(text) > 300 else text
                    rag_lines.append(f"{i}. {text_preview}")
                    rag_lines.append(f"   (Source: {source})\n")
                rag_context_section = "\n".join(rag_lines)
            else:
                rag_context_section = ""

            # Fill template
            prompt = template.format(
                asset_id=asset.get("id", "N/A"),
                asset_name=asset.get("name", "N/A"),
                asset_type=asset.get("type", "N/A"),
                asset_criticality=asset.get("criticality", "unknown"),
                asset_environment=asset.get("environment", "unknown"),
                vulnerabilities_count=len(vulnerabilities),
                vulnerabilities_list=vulnerabilities_list,
                rag_context_section=rag_context_section,
            )

            return prompt

        except FileNotFoundError:
            logger.warning(f"⚠️ Prompt template not found: {USER_PROMPT_FILE}, using fallback")
            return self._build_fallback_prompt(asset, vulnerabilities, context_docs)

    def _build_fallback_prompt(
        self,
        asset: dict[str, Any],
        vulnerabilities: list[dict[str, Any]],
        context_docs: list[dict[str, Any]],
    ) -> str:
        """
        Fallback prompt builder if template file is missing.

        Args:
            asset: Asset information
            vulnerabilities: List of vulnerabilities
            context_docs: RAG context documents

        Returns:
            Formatted prompt string
        """
        prompt = "# RISK ASSESSMENT REQUEST\n\n"

        # Asset information
        prompt += "## ASSET DETAILS\n"
        prompt += f"- ID: {asset.get('id', 'N/A')}\n"
        prompt += f"- Name: {asset.get('name', 'N/A')}\n"
        prompt += f"- Type: {asset.get('type', 'N/A')}\n"
        prompt += f"- Criticality: {asset.get('criticality', 'unknown')}\n"
        prompt += f"- Environment: {asset.get('environment', 'unknown')}\n\n"

        # Vulnerabilities
        prompt += f"## VULNERABILITIES ({len(vulnerabilities)})\n"
        if vulnerabilities:
            for vuln in vulnerabilities:
                cvss = vuln.get("cvss_score", 0.0)
                cve_id = vuln.get("cve_id", "Unknown")
                description = vuln.get("description", "No description")
                prompt += f"- **{cve_id}** (CVSS: {cvss}): {description}\n"
        else:
            prompt += "- No vulnerabilities detected\n"
        prompt += "\n"

        # Context from knowledge base
        if context_docs:
            prompt += "## RELEVANT SECURITY GUIDANCE\n"
            for i, doc in enumerate(context_docs, 1):
                text = doc.get("text", "")
                source = doc.get("source", "unknown")
                text_preview = text[:300] + "..." if len(text) > 300 else text
                prompt += f"{i}. {text_preview}\n"
                prompt += f"   (Source: {source})\n\n"

        prompt += """
Provide risk assessment as JSON:
{
    "risk_score": <0.0-10.0>,
    "severity": "<critical|high|medium|low|info>",
    "recommendations": [<list>],
    "confidence": <0.0-1.0>,
    "reasoning": "<explanation>"
}"""

        return prompt

    def _parse_llm_response(self, response: Any) -> dict[str, Any]:
        """
        Parse LLM response into structured data.

        Handles multiple response formats:
        - Python dict (direct from mock)
        - JSON string (from LLM)
        - Markdown code blocks with JSON
        - Python dict string representation (from str(dict))

        Args:
            response: LLM response (dict, JSON string, or Python dict string)

        Returns:
            Parsed response as dictionary

        Raises:
            ValueError: If response format is invalid or missing required fields
        """
        logger.debug(f"🔍 Parsing LLM response (type: {type(response).__name__})")

        # Handle dict responses (from mocks or direct returns)
        if isinstance(response, dict):
            result = response

        # Handle string responses (most common case)
        elif isinstance(response, str):
            result = self._parse_string_response(response)

        else:
            raise ValueError(f"Unexpected response type: {type(response)}")

        # Validate required fields
        self._validate_response_fields(result)

        logger.debug(f"✅ Parsed response successfully: {list(result.keys())}")
        return result

    def _parse_string_response(self, response: str) -> dict[str, Any]:
        """
        Parse string response (JSON or Python dict string).

        Args:
            response: String response to parse

        Returns:
            Parsed dictionary

        Raises:
            ValueError: If string cannot be parsed
        """
        # Clean response - remove markdown code blocks
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        # Try JSON parsing first (most common case)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # If JSON fails, try Python literal eval for str(dict) format
            # This handles test mocks that use str(dict)
            try:
                result = ast.literal_eval(response)
                if not isinstance(result, dict):
                    raise ValueError(f"Expected dict, got {type(result)}")
                return result
            except (ValueError, SyntaxError) as e:
                raise ValueError(
                    f"Could not parse LLM response as JSON or Python dict: {e}\nResponse: {response[:200]}"
                )

    def _validate_response_fields(self, result: dict[str, Any]) -> None:
        """
        Validate LLM response contains all required fields.

        Args:
            result: Parsed response dictionary

        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ["risk_score", "severity", "recommendations", "confidence"]
        missing_fields = [f for f in required_fields if f not in result]

        if missing_fields:
            raise ValueError(
                f"LLM response missing required fields: {missing_fields}\nGot fields: {list(result.keys())}"
            )

    def _format_assessment_response(self, result: RiskAssessment) -> str:
        """
        Format risk assessment for AgentResponse output.

        Args:
            result: RiskAssessment object

        Returns:
            Formatted response text
        """
        response_text = (
            f"Risk Assessment Complete:\n"
            f"- Risk Score: {result.risk_score:.1f}/10.0\n"
            f"- Severity: {result.severity.upper()}\n"
            f"- Vulnerabilities: {result.vulnerabilities_count}\n"
            f"- Confidence: {result.confidence:.0%}\n"
            f"\nTop Recommendations:\n"
        )

        for i, rec in enumerate(result.recommendations[:3], 1):
            response_text += f"{i}. {rec}\n"

        return response_text
