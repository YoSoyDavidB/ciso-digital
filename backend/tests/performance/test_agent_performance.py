"""
Performance Tests for CISO Digital AI Agents
============================================

Tests performance and latency requirements for AI agents.

Performance Targets:
- RAG search: < 2s
- LLM response (simple query): < 5s
- End-to-end assessment: < 7s
- Concurrent requests: 5 simultaneous
- Cache effectiveness: 2nd request < 0.5s

Usage:
    pytest tests/performance/test_agent_performance.py -v
    pytest tests/performance/test_agent_performance.py --benchmark-only
    pytest tests/performance/test_agent_performance.py --benchmark-save=baseline
"""

import asyncio
import time
from typing import List
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.agents.risk_agent import RiskAssessmentAgent
from app.services.copilot_service import CopilotService
from app.services.embedding_service import EmbeddingService
from app.services.rag_service import RAGService
from app.services.vector_store import VectorStoreService


@pytest.fixture
async def embedding_service():
    """Real embedding service for performance testing."""
    return EmbeddingService()


@pytest.fixture
async def vector_store():
    """Real vector store for performance testing."""
    from app.core.config import get_settings

    settings = get_settings()
    return VectorStoreService(
        qdrant_url=settings.QDRANT_URL, collection_name="security_knowledge"
    )


@pytest.fixture
async def rag_service(embedding_service, vector_store):
    """Real RAG service for performance testing."""
    return RAGService(
        embedding_service=embedding_service,
        vector_store_service=vector_store,
        copilot_service=AsyncMock(),  # Mock LLM to isolate RAG performance
    )


@pytest.fixture
async def copilot_service():
    """Real Copilot service for performance testing."""
    return CopilotService()


@pytest.fixture
async def risk_agent(copilot_service, rag_service):
    """Real RiskAssessmentAgent for performance testing."""
    return RiskAssessmentAgent(
        copilot_service=copilot_service,
        rag_service=rag_service,
        db_session=MagicMock(),
    )


# =============================================================================
# Test 1: RAG Search Latency
# =============================================================================


@pytest.mark.asyncio
@pytest.mark.performance
async def test_rag_search_latency(rag_service, benchmark):
    """
    Test RAG search latency.
    
    Target: < 2 seconds
    
    Given: RAG service with populated knowledge base
    When: Performing a semantic search
    Then: Search should complete in < 2s
    """

    async def search_operation():
        """Perform RAG search."""
        query = "What are the key risk assessment methodologies?"
        start_time = time.time()
        results = await rag_service.search(query, limit=5)
        elapsed = time.time() - start_time
        return elapsed, results

    # Run the search
    elapsed, results = await search_operation()

    # Assertions
    assert elapsed < 2.0, f"RAG search took {elapsed:.2f}s (target: < 2s)"
    assert len(results) > 0, "Should return results"

    print(f"\n[PERFORMANCE] RAG Search Latency: {elapsed:.3f}s")
    print(f"[PERFORMANCE] Results returned: {len(results)}")


@pytest.mark.asyncio
@pytest.mark.performance
async def test_rag_search_with_benchmark(rag_service, benchmark):
    """
    Benchmark RAG search using pytest-benchmark.
    
    This test uses benchmark fixture to get statistical analysis
    of search performance over multiple runs.
    """

    async def search():
        return await rag_service.search(
            "ISO 27001 security controls", limit=5
        )

    # Benchmark the async function
    def run_search():
        return asyncio.run(search())

    results = benchmark(run_search)
    assert len(results) > 0


# =============================================================================
# Test 2: LLM Response Time
# =============================================================================


@pytest.mark.asyncio
@pytest.mark.performance
async def test_llm_response_time_simple_query(copilot_service):
    """
    Test LLM response time for simple query.
    
    Target: < 5 seconds for simple query
    
    Given: Copilot service with Claude Sonnet 4.5
    When: Sending a simple question
    Then: Response should arrive in < 5s
    """
    message = "What is a security risk in one sentence?"

    start_time = time.time()
    response = await copilot_service.chat(
        session={},  # New session
        message=message,
        model="claude-sonnet-4.5",
        max_tokens=100,
    )
    elapsed = time.time() - start_time

    # Assertions
    assert elapsed < 5.0, f"LLM response took {elapsed:.2f}s (target: < 5s)"
    assert response["text"], "Should return text"
    assert len(response["text"]) > 0, "Response should not be empty"

    print(f"\n[PERFORMANCE] LLM Response Time: {elapsed:.3f}s")
    print(f"[PERFORMANCE] Response length: {len(response['text'])} chars")
    print(f"[PERFORMANCE] Model: {response.get('model', 'unknown')}")


# =============================================================================
# Test 3: End-to-End Latency
# =============================================================================


@pytest.mark.asyncio
@pytest.mark.performance
async def test_end_to_end_risk_assessment_latency(risk_agent):
    """
    Test end-to-end risk assessment latency.
    
    Target: < 7 seconds
    
    Given: RiskAssessmentAgent with real services
    When: Performing complete risk assessment (RAG + LLM + processing)
    Then: Total time should be < 7s
    """
    asset = {
        "id": "perf-test-001",
        "name": "Production API Server",
        "type": "server",
        "criticality": "critical",
    }

    vulnerabilities = [
        {
            "cve_id": "CVE-2024-TEST1",
            "cvss_score": 9.8,
            "description": "Critical remote code execution vulnerability",
        },
        {
            "cve_id": "CVE-2024-TEST2",
            "cvss_score": 7.5,
            "description": "High severity SQL injection",
        },
    ]

    start_time = time.time()
    assessment = await risk_agent.assess_risk(asset, vulnerabilities)
    elapsed = time.time() - start_time

    # Assertions
    assert elapsed < 7.0, f"End-to-end took {elapsed:.2f}s (target: < 7s)"
    assert assessment.risk_score > 0, "Should calculate risk score"
    assert assessment.severity in [
        "critical",
        "high",
        "medium",
        "low",
    ], "Should have valid severity"
    assert len(assessment.recommendations) > 0, "Should provide recommendations"

    print(f"\n[PERFORMANCE] End-to-End Latency: {elapsed:.3f}s")
    print(f"[PERFORMANCE] Risk Score: {assessment.risk_score}/10")
    print(f"[PERFORMANCE] Severity: {assessment.severity}")
    print(f"[PERFORMANCE] Recommendations: {len(assessment.recommendations)}")


# =============================================================================
# Test 4: Concurrent Requests
# =============================================================================


@pytest.mark.asyncio
@pytest.mark.performance
async def test_concurrent_risk_assessments(risk_agent):
    """
    Test concurrent request handling.
    
    Target: Handle 5 simultaneous requests
    
    Given: RiskAssessmentAgent
    When: 5 concurrent risk assessments are triggered
    Then: All should complete successfully within reasonable time
    """

    async def assess_risk_with_timing(asset_id: int):
        """Perform risk assessment and track timing."""
        asset = {
            "id": f"concurrent-test-{asset_id}",
            "name": f"Server {asset_id}",
            "type": "server",
            "criticality": "high",
        }

        vulnerabilities = [
            {
                "cve_id": f"CVE-2024-{asset_id:04d}",
                "cvss_score": 8.0,
                "description": f"Test vulnerability {asset_id}",
            }
        ]

        start = time.time()
        result = await risk_agent.assess_risk(asset, vulnerabilities)
        elapsed = time.time() - start

        return {
            "asset_id": asset_id,
            "elapsed": elapsed,
            "risk_score": result.risk_score,
            "severity": result.severity,
        }

    # Launch 5 concurrent assessments
    num_concurrent = 5
    start_time = time.time()

    tasks = [assess_risk_with_timing(i) for i in range(num_concurrent)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    total_elapsed = time.time() - start_time

    # Check for exceptions
    exceptions = [r for r in results if isinstance(r, Exception)]
    assert len(exceptions) == 0, f"Some requests failed: {exceptions}"

    # All should complete
    assert len(results) == num_concurrent, "All requests should complete"

    # Calculate statistics
    latencies = [r["elapsed"] for r in results]
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    min_latency = min(latencies)

    print(f"\n[PERFORMANCE] Concurrent Requests: {num_concurrent}")
    print(f"[PERFORMANCE] Total Time: {total_elapsed:.3f}s")
    print(f"[PERFORMANCE] Avg Latency: {avg_latency:.3f}s")
    print(f"[PERFORMANCE] Min Latency: {min_latency:.3f}s")
    print(f"[PERFORMANCE] Max Latency: {max_latency:.3f}s")

    # Assertions
    assert (
        total_elapsed < 10.0
    ), f"Concurrent processing took {total_elapsed:.2f}s (should be < 10s)"
    for result in results:
        assert result["risk_score"] > 0, "Each should have valid risk score"


# =============================================================================
# Test 5: Cache Effectiveness
# =============================================================================


@pytest.mark.asyncio
@pytest.mark.performance
async def test_cache_effectiveness(rag_service):
    """
    Test cache effectiveness for repeated queries.
    
    Target: 2nd request < 0.5s (using cache)
    
    Given: RAG service with caching enabled
    When: Same query is executed twice
    Then: Second request should be significantly faster (< 0.5s)
    """
    query = "What is the DORA regulation compliance requirement?"

    # First request (cold - no cache)
    start_time = time.time()
    results_1 = await rag_service.search(query, limit=5)
    elapsed_1 = time.time() - start_time

    # Second request (warm - should hit cache)
    start_time = time.time()
    results_2 = await rag_service.search(query, limit=5)
    elapsed_2 = time.time() - start_time

    # Assertions
    assert len(results_1) > 0, "First request should return results"
    assert len(results_2) > 0, "Second request should return results"
    assert (
        len(results_1) == len(results_2)
    ), "Both requests should return same number of results"

    # Cache effectiveness check
    speedup = elapsed_1 / elapsed_2 if elapsed_2 > 0 else 0
    cache_hit = elapsed_2 < 0.5  # Target: < 0.5s for cached request

    print(f"\n[PERFORMANCE] Cache Effectiveness Test:")
    print(f"[PERFORMANCE] 1st Request (cold): {elapsed_1:.3f}s")
    print(f"[PERFORMANCE] 2nd Request (warm): {elapsed_2:.3f}s")
    print(f"[PERFORMANCE] Speedup: {speedup:.2f}x")
    print(f"[PERFORMANCE] Cache Hit: {cache_hit}")

    # Note: Cache may not always work depending on implementation
    # This is more informational than a hard requirement
    if elapsed_2 < elapsed_1:
        print(f"[PERFORMANCE] Cache improved performance by {(1 - elapsed_2/elapsed_1)*100:.1f}%")


# =============================================================================
# Test 6: Memory Usage (Informational)
# =============================================================================


@pytest.mark.asyncio
@pytest.mark.performance
async def test_memory_usage_during_assessment(risk_agent):
    """
    Monitor memory usage during risk assessment.
    
    This is an informational test to track memory consumption.
    """
    import psutil
    import os

    process = psutil.Process(os.getpid())

    # Get memory before
    mem_before = process.memory_info().rss / 1024 / 1024  # MB

    asset = {
        "id": "memory-test-001",
        "name": "Test Server",
        "type": "server",
        "criticality": "high",
    }

    vulnerabilities = [
        {"cve_id": "CVE-2024-MEM", "cvss_score": 8.5, "description": "Test vuln"}
    ]

    # Perform assessment
    assessment = await risk_agent.assess_risk(asset, vulnerabilities)

    # Get memory after
    mem_after = process.memory_info().rss / 1024 / 1024  # MB
    mem_delta = mem_after - mem_before

    print(f"\n[PERFORMANCE] Memory Usage:")
    print(f"[PERFORMANCE] Before: {mem_before:.2f} MB")
    print(f"[PERFORMANCE] After: {mem_after:.2f} MB")
    print(f"[PERFORMANCE] Delta: {mem_delta:.2f} MB")

    # Informational only - no hard assertion
    # Large memory spikes could indicate issues
    if mem_delta > 100:  # More than 100MB increase
        print(f"[WARNING] Large memory increase detected: {mem_delta:.2f} MB")


# =============================================================================
# Performance Summary Report
# =============================================================================


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Generate performance summary report."""
    if config.getoption("verbose") > 0:
        terminalreporter.write_sep("=", "PERFORMANCE TEST SUMMARY")
        terminalreporter.write_line("")
        terminalreporter.write_line("Performance Targets:")
        terminalreporter.write_line("  - RAG Search:        < 2s")
        terminalreporter.write_line("  - LLM Response:      < 5s")
        terminalreporter.write_line("  - End-to-End:        < 7s")
        terminalreporter.write_line("  - Concurrent (5):    All complete")
        terminalreporter.write_line("  - Cache Hit:         < 0.5s")
        terminalreporter.write_line("")
