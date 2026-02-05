"""
Agents Package - AI Agents for CISO Digital.

This package contains the agent implementations using GitHub Copilot SDK
with tool calling capabilities for security automation.
"""

from app.agents.base_agent import AgentResponse, BaseAgent, Task
from app.agents.risk_agent import RiskAssessment, RiskAssessmentAgent

__version__ = "1.0.0"

__all__ = [
    "BaseAgent",
    "Task",
    "AgentResponse",
    "RiskAssessmentAgent",
    "RiskAssessment",
]
