"""
Pytest configuration for performance tests.
"""

import pytest


def pytest_configure(config):
    """Configure pytest for performance tests."""
    config.addinivalue_line(
        "markers", "performance: Performance and benchmark tests"
    )


@pytest.fixture(scope="session")
def performance_report():
    """Fixture to collect performance metrics across tests."""
    metrics = {
        "rag_search_latency": [],
        "llm_response_time": [],
        "end_to_end_latency": [],
        "concurrent_latency": [],
        "cache_effectiveness": {},
        "memory_usage": {},
    }
    return metrics
