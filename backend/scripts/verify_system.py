"""
System Verification Script
==========================

Verifies that all CISO Digital components are working correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def verify_system():
    """Run comprehensive system verification"""
    print("=" * 60)
    print("CISO Digital - System Verification")
    print("=" * 60)
    print()

    # 1. Configuration
    print("[1/7] Verifying Configuration...")
    try:
        from app.core.config import get_settings

        settings = get_settings()
        print(f"   [OK] Environment: {settings.ENVIRONMENT}")
        print(f"   [OK] Azure OpenAI Endpoint: {settings.AZURE_OPENAI_ENDPOINT}")
        print(f"   [OK] Qdrant URL: {settings.QDRANT_URL}")
        print(f"   [OK] Default Model: {settings.COPILOT_DEFAULT_MODEL}")
    except Exception as e:
        print(f"   [ERROR] Configuration error: {e}")
        return False

    print()

    # 2. Database
    print("[2/7] Verifying Database...")
    try:
        from app.core.database import get_db

        async with get_db() as db:
            print("   [OK] Database connection successful")
    except Exception as e:
        print(f"   [ERROR] Database error: {e}")
        return False

    print()

    # 3. Vector Store (Qdrant)
    print("[3/7] Verifying Vector Store (Qdrant)...")
    try:
        from app.services.vector_store import VectorStore

        vector_store = VectorStore()
        collection_name = "security_knowledge"

        # Check collection exists
        exists = await vector_store.collection_exists(collection_name)
        if exists:
            print(f"   [OK] Collection '{collection_name}' exists")

            # Get collection info
            info = await vector_store.get_collection_info(collection_name)
            points_count = info.get("points_count", 0)
            print(f"   [OK] Points count: {points_count}")
        else:
            print(f"   [WARNING] Collection '{collection_name}' does not exist")
            print("   [TIP] Run: python scripts/seed_knowledge_base.py")

    except Exception as e:
        print(f"   [ERROR] Vector store error: {e}")
        print("   [TIP] Make sure Qdrant is running: docker-compose up -d qdrant")
        return False

    print()

    # 4. Embedding Service
    print("[4/7] Verifying Embedding Service...")
    try:
        from app.services.embedding_service import EmbeddingService

        embedding_service = EmbeddingService()
        test_text = "This is a test for risk assessment"

        embedding = await embedding_service.generate_embedding(test_text)
        print(f"   [OK] Generated embedding with {len(embedding)} dimensions")
    except Exception as e:
        print(f"   [ERROR] Embedding service error: {e}")
        print(
            "   [TIP] Check Azure OpenAI credentials in .env: AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT"
        )
        return False

    print()

    # 5. RAG Service
    print("[5/7] Verifying RAG Service...")
    try:
        from app.services.rag_service import RAGService

        rag_service = RAGService()
        query = "What is risk management?"

        results = await rag_service.search(query, limit=3)
        print(f"   [OK] RAG search returned {len(results)} documents")

        if results:
            print(f"   [OK] Top result: {results[0]['text'][:80]}...")
    except Exception as e:
        print(f"   [ERROR] RAG service error: {e}")
        return False

    print()

    # 6. Copilot Service
    print("[6/7] Verifying GitHub Copilot Service...")
    try:
        from app.services.copilot_service import CopilotService

        copilot = CopilotService()
        test_messages = [{"role": "user", "content": "Say 'Hello from CISO Digital!'"}]

        response = await copilot.chat(
            messages=test_messages, model="claude-sonnet-4.5", max_tokens=50
        )

        print(f"   [OK] Copilot response: {response['text'][:80]}...")
        print(f"   [OK] Model: {response['model']}")
        print(f"   [OK] Provider: {response['provider']}")
    except Exception as e:
        print(f"   [ERROR] Copilot service error: {e}")
        print("   [TIP] Make sure GITHUB_TOKEN is configured")
        return False

    print()

    # 7. Risk Assessment Agent
    print("[7/7] Verifying Risk Assessment Agent...")
    try:
        from unittest.mock import MagicMock

        from app.agents.risk_agent import RiskAssessmentAgent
        from app.services.copilot_service import CopilotService
        from app.services.rag_service import RAGService

        copilot = CopilotService()
        rag = RAGService()

        agent = RiskAssessmentAgent(
            copilot_service=copilot, rag_service=rag, db_session=MagicMock()
        )

        # Test with minimal asset
        asset = {
            "id": "test-001",
            "name": "Test Server",
            "type": "server",
            "criticality": "high",
        }

        vulnerabilities = [
            {
                "cve_id": "CVE-2024-TEST",
                "cvss_score": 8.5,
                "description": "Test vulnerability",
            }
        ]

        assessment = await agent.assess_risk(asset, vulnerabilities)

        print(f"   [OK] Risk Assessment completed")
        print(f"   Risk Score: {assessment.risk_score}/10")
        print(f"   Severity: {assessment.severity}")
        print(f"   Recommendations: {len(assessment.recommendations)}")
        print(f"   Confidence: {assessment.confidence:.2f}")

    except Exception as e:
        print(f"   [ERROR] Risk agent error: {e}")
        import traceback

        traceback.print_exc()
        return False

    print()
    print("=" * 60)
    print("SUCCESS - All System Checks Passed!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("   1. Start API: uvicorn app.main:app --reload")
    print("   2. Visit: http://localhost:8000/docs")
    print("   3. Test: POST /api/v1/chat/message")
    print()

    return True


if __name__ == "__main__":
    success = asyncio.run(verify_system())
    sys.exit(0 if success else 1)
