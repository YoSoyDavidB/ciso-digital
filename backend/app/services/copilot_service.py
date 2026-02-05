"""
Copilot Service - Wrapper para GitHub Copilot SDK con fallback a Azure OpenAI.

🟢 GREEN PHASE: Código mínimo para pasar los tests.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from copilot import CopilotClient, CopilotSession
from copilot.types import SessionConfig, SystemMessageConfig, Tool
from openai import AsyncAzureOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class CopilotService:
    """Servicio wrapper para GitHub Copilot SDK con fallback a Azure OpenAI."""
    
    def __init__(self):
        """Inicializa el CopilotService."""
        self.copilot_client: Optional[CopilotClient] = None
        self.azure_client: Optional[AsyncAzureOpenAI] = None
        self.max_retries = settings.COPILOT_MAX_RETRIES
        self.using_copilot = False
        self.using_azure = False
        
        self._initialize()
    
    def _initialize(self) -> None:
        """Inicializa los clientes de IA disponibles."""
        # Intentar GitHub Copilot SDK primero
        try:
            github_token = self._get_github_token()
            if github_token:
                self.copilot_client = CopilotClient(
                    auto_start=settings.COPILOT_AUTO_RESTART,
                    log_level=settings.COPILOT_LOG_LEVEL,
                )
                self.using_copilot = True
                logger.info("CopilotService initialized with GitHub Copilot SDK")
        except Exception as e:
            logger.warning(f"Failed to initialize GitHub Copilot SDK: {e}")
        
        # Fallback a Azure OpenAI
        if not self.using_copilot:
            try:
                if all([
                    settings.AZURE_OPENAI_KEY,
                    settings.AZURE_OPENAI_ENDPOINT,
                    settings.AZURE_OPENAI_DEPLOYMENT
                ]):
                    self.azure_client = AsyncAzureOpenAI(
                        api_key=settings.AZURE_OPENAI_KEY,
                        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                        api_version="2024-02-15-preview"
                    )
                    self.using_azure = True
                    logger.info("CopilotService initialized with Azure OpenAI")
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI: {e}")
    
    def _get_github_token(self) -> Optional[str]:
        """Obtiene el GITHUB_TOKEN desde env."""
        return settings.GITHUB_TOKEN
    
    async def create_session(
        self,
        model: str = "claude-sonnet-4.5",
        system_prompt: str = "",
        tools: Optional[List[Tool]] = None
    ) -> CopilotSession | Dict[str, Any]:
        """Crea una nueva sesión de conversación."""
        if self.using_copilot:
            system_config: SystemMessageConfig = {
                "mode": "append",
                "content": system_prompt
            }
            
            session_config: SessionConfig = {
                "model": model,
                "system_message": system_config,
                "streaming": False,
            }
            
            if tools:
                session_config["tools"] = tools
            
            session = await self.copilot_client.create_session(session_config)
            return session
        else:
            # Azure session (dict)
            return {
                "provider": "azure",
                "deployment": settings.AZURE_OPENAI_DEPLOYMENT,
                "system_prompt": system_prompt,
                "tools": tools,
                "messages": []
            }
    
    async def chat(
        self,
        session: CopilotSession | Dict[str, Any],
        message: str
    ) -> Dict[str, Any]:
        """Envía un mensaje en la sesión."""
        for attempt in range(self.max_retries):
            try:
                # Detectar si es CopilotSession o dict de Azure
                if isinstance(session, CopilotSession) or (hasattr(session, 'chat') and callable(session.chat)):
                    response = await session.chat(message)
                    
                    result = {
                        "text": response.text if hasattr(response, 'text') else str(response),
                        "model": settings.COPILOT_DEFAULT_MODEL,
                        "provider": "github-copilot-sdk",
                        "tokens": getattr(response, 'usage', {}).get('total_tokens', 0) if hasattr(response, 'usage') else 0,
                        "tool_calls": []
                    }
                    
                    logger.info(f"Copilot response - Model: {result['model']}, Tokens: {result['tokens']}")
                    return result
                else:
                    # Azure OpenAI (dict)
                    if not self.azure_client:
                        raise RuntimeError("Azure client not initialized")
                    
                    session["messages"].append({"role": "user", "content": message})
                    
                    messages = []
                    if session.get("system_prompt"):
                        messages.append({"role": "system", "content": session["system_prompt"]})
                    messages.extend(session["messages"])
                    
                    response = await self.azure_client.chat.completions.create(
                        model=session["deployment"],
                        messages=messages
                    )
                    
                    assistant_message = response.choices[0].message.content
                    session["messages"].append({"role": "assistant", "content": assistant_message})
                    
                    result = {
                        "text": assistant_message,
                        "model": session["deployment"],
                        "provider": "azure-openai",
                        "tokens": response.usage.total_tokens,
                        "tool_calls": []
                    }
                    
                    logger.info(f"Azure response - Model: {result['model']}, Tokens: {result['tokens']}")
                    return result
                    
            except Exception as e:
                logger.warning(f"Chat attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    raise
    
    async def chat_with_tools(
        self,
        session: CopilotSession | Dict[str, Any],
        message: str
    ) -> Dict[str, Any]:
        """Chat con soporte para tool calling."""
        return await self.chat(session, message)


# Singleton instance
_copilot_service: Optional[CopilotService] = None


def get_copilot_service() -> CopilotService:
    """Retorna la instancia singleton del CopilotService."""
    global _copilot_service
    if _copilot_service is None:
        _copilot_service = CopilotService()
    return _copilot_service
