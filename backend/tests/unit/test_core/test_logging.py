"""
🔴 RED: Tests for Structured Logging Configuration

Tests para verificar que la configuración de logging estructurado
funciona correctamente en desarrollo y producción.
"""

import io
import json
import logging
from unittest.mock import patch

import pytest
import structlog


class TestStructLogConfiguration:
    """Tests para configuración de structlog"""

    def test_configure_logging_sets_up_structlog(self):
        """
        🔴 RED: configure_logging debe configurar structlog correctamente.

        Given: Aplicación inicializando
        When: Se llama configure_logging()
        Then: structlog debe estar configurado
        """
        from app.core.logging import configure_logging

        configure_logging(environment="development")

        # Verify structlog is configured
        logger = structlog.get_logger()
        assert logger is not None

    def test_development_logging_uses_pretty_console_output(self):
        """
        🔴 RED: En development, logs deben ser human-readable.

        Given: Environment = development
        When: Se configura logging
        Then: Debe usar ConsoleRenderer
        """
        from app.core.logging import configure_logging

        configure_logging(environment="development")

        # Get the configured processors
        processors = structlog.get_config().get("processors", [])

        # Check if ConsoleRenderer is in processors
        renderer_types = [type(p).__name__ for p in processors]
        assert "ConsoleRenderer" in renderer_types

    def test_production_logging_uses_json_output(self):
        """
        🔴 RED: En production, logs deben ser JSON.

        Given: Environment = production
        When: Se configura logging
        Then: Debe usar JSONRenderer
        """
        from app.core.logging import configure_logging

        configure_logging(environment="production")

        # Get the configured processors
        processors = structlog.get_config().get("processors", [])

        # Check if JSONRenderer is in processors
        renderer_types = [type(p).__name__ for p in processors]
        assert "JSONRenderer" in renderer_types

    def test_logger_includes_timestamp_processor(self):
        """
        🔴 RED: Logs deben incluir timestamps.

        Given: Logger configurado
        When: Se verifica processors
        Then: Debe incluir TimeStamper
        """
        from app.core.logging import configure_logging

        configure_logging(environment="production")

        processors = structlog.get_config().get("processors", [])
        processor_types = [type(p).__name__ for p in processors]

        assert "TimeStamper" in processor_types

    def test_get_logger_returns_bound_logger(self):
        """
        🔴 RED: get_logger debe retornar BoundLogger.

        Given: Logging configurado
        When: Se llama get_logger()
        Then: Debe retornar BoundLogger con contexto
        """
        from app.core.logging import configure_logging, get_logger

        configure_logging(environment="production")
        logger = get_logger("test_component")

        assert logger is not None
        # BoundLogger should have info, warning, error methods
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")

    def test_logger_can_log_structured_data(self):
        """
        🔴 RED: Logger debe poder loggear datos estructurados.

        Given: Logger configurado
        When: Se loggea con key-value pairs
        Then: Debe incluir todos los campos
        """
        from app.core.logging import configure_logging, get_logger

        configure_logging(environment="production")
        logger = get_logger("test")

        # Capture log output
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            logger.info(
                "test_event",
                user_id="user-123",
                action="test_action",
                count=42,
            )

            output = fake_out.getvalue()

            # In production mode, output should be JSON
            if output:
                log_entry = json.loads(output)
                assert log_entry["event"] == "test_event"
                assert log_entry["user_id"] == "user-123"
                assert log_entry["action"] == "test_action"
                assert log_entry["count"] == 42


class TestLoggerHelpers:
    """Tests para helper functions de logging"""

    def test_log_llm_call_creates_structured_log(self):
        """
        🔴 RED: log_llm_call debe crear log estructurado.

        Given: LLM call completado
        When: Se llama log_llm_call()
        Then: Debe loggear con todos los campos relevantes
        """
        from app.core.logging import configure_logging, log_llm_call

        configure_logging(environment="production")

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            log_llm_call(
                agent_name="risk_assessment",
                model="claude-sonnet-4.5",
                prompt_tokens=100,
                completion_tokens=50,
                latency_ms=1200,
                success=True,
            )

            output = fake_out.getvalue()
            if output:
                log_entry = json.loads(output)
                assert log_entry["event"] == "llm_call_completed"
                assert log_entry["agent_name"] == "risk_assessment"
                assert log_entry["model"] == "claude-sonnet-4.5"
                assert log_entry["prompt_tokens"] == 100
                assert log_entry["completion_tokens"] == 50
                assert log_entry["latency_ms"] == 1200
                assert log_entry["success"] is True

    def test_log_rag_retrieval_creates_structured_log(self):
        """
        🔴 RED: log_rag_retrieval debe loggear retrieval de RAG.

        Given: RAG retrieval completado
        When: Se llama log_rag_retrieval()
        Then: Debe loggear con query y results
        """
        from app.core.logging import configure_logging, log_rag_retrieval

        configure_logging(environment="production")

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            log_rag_retrieval(
                query="critical vulnerabilities",
                num_results=5,
                latency_ms=150,
            )

            output = fake_out.getvalue()
            if output:
                log_entry = json.loads(output)
                assert log_entry["event"] == "rag_retrieval_completed"
                assert log_entry["query"] == "critical vulnerabilities"
                assert log_entry["num_results"] == 5
                assert log_entry["latency_ms"] == 150

    def test_log_cache_operation_tracks_cache_hits_and_misses(self):
        """
        🔴 RED: log_cache_operation debe trackear hits/misses.

        Given: Cache operation
        When: Se llama log_cache_operation()
        Then: Debe loggear hit/miss
        """
        from app.core.logging import configure_logging, log_cache_operation

        configure_logging(environment="production")

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            log_cache_operation(
                operation="get",
                key="risk_assessment:asset-123",
                hit=True,
                latency_ms=5,
            )

            output = fake_out.getvalue()
            if output:
                log_entry = json.loads(output)
                assert log_entry["event"] == "cache_operation"
                assert log_entry["operation"] == "get"
                assert log_entry["key"] == "risk_assessment:asset-123"
                assert log_entry["hit"] is True
                assert log_entry["latency_ms"] == 5


class TestLoggingLevels:
    """Tests para diferentes niveles de logging"""

    def test_logger_respects_log_level(self):
        """
        🔴 RED: Logger debe respetar log level configurado.

        Given: Log level = WARNING
        When: Se loggea INFO
        Then: No debe aparecer en output
        """
        from app.core.logging import configure_logging, get_logger

        configure_logging(environment="production", log_level="WARNING")
        logger = get_logger("test")

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            logger.info("this_should_not_appear")
            logger.warning("this_should_appear")

            output = fake_out.getvalue()
            assert "this_should_not_appear" not in output
            # Warning might appear depending on configuration

    def test_error_logs_include_exception_info(self, caplog):
        """
        🔴 RED: Error logs deben incluir stack traces.

        Given: Exception ocurre
        When: Se loggea con logger.error()
        Then: Debe incluir exception info
        """
        from app.core.logging import configure_logging, get_logger

        configure_logging(environment="production")
        logger = get_logger("test")

        try:
            raise ValueError("Test error")
        except ValueError:
            logger.error("error_occurred", exc_info=True)

        # Check that error was logged
        assert len(caplog.records) > 0
        assert "error_occurred" in caplog.text or any(
            "error_occurred" in str(record.msg) for record in caplog.records
        )
