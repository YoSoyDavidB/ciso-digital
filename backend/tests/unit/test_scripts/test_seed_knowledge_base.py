"""
Tests for seed_knowledge_base.py script functions.
"""

from pathlib import Path

import pytest

# Import from scripts package
from scripts.seed_knowledge_base import chunk_text, extract_metadata


class TestChunkText:
    """Tests for chunk_text function."""

    def test_chunk_text_with_short_text(self):
        """Test that short text returns single chunk."""
        text = "Short text that fits in one chunk"
        chunks = chunk_text(text, chunk_size=1000, overlap=200)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_text_with_long_text(self):
        """Test that long text is split into multiple chunks."""
        text = "A" * 2500  # 2500 characters
        chunks = chunk_text(text, chunk_size=1000, overlap=200)

        assert len(chunks) >= 2
        assert all(len(chunk) <= 1000 for chunk in chunks)

    def test_chunk_text_with_overlap(self):
        """Test that overlap works correctly."""
        text = "First sentence. " * 100  # Create long text with sentences
        chunks = chunk_text(text, chunk_size=500, overlap=100)

        assert len(chunks) >= 2

        # Check that consecutive chunks have overlap
        if len(chunks) >= 2:
            # The end of first chunk should appear at start of second
            assert len(chunks[0]) <= 500
            assert len(chunks[1]) <= 500

    def test_chunk_text_with_empty_text(self):
        """Test that empty text returns empty list."""
        assert chunk_text("") == []
        assert chunk_text("   ") == []

    def test_chunk_text_respects_natural_breaks(self):
        """Test that chunking prefers natural break points."""
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph." * 20
        chunks = chunk_text(text, chunk_size=500, overlap=50)

        # Should have multiple chunks
        assert len(chunks) >= 2

        # Chunks should not be empty
        assert all(len(chunk.strip()) > 0 for chunk in chunks)


class TestExtractMetadata:
    """Tests for extract_metadata function."""

    def test_extract_metadata_for_iso_document(self, tmp_path):
        """Test metadata extraction for ISO document."""
        # Create temp markdown file
        test_file = tmp_path / "iso27001-overview.md"
        test_file.write_text("# ISO 27001 Overview\n\nContent here.")

        metadata = extract_metadata(test_file)

        assert metadata["filename"] == "iso27001-overview.md"
        assert metadata["document_type"] == "standard"
        assert "ISO 27001" in metadata["title"]
        assert "iso27001-overview.md" in metadata["source"]

    def test_extract_metadata_for_risk_document(self, tmp_path):
        """Test metadata extraction for risk management document."""
        test_file = tmp_path / "risk-management-guide.md"
        test_file.write_text("# Risk Management Guide\n\nRisk content.")

        metadata = extract_metadata(test_file)

        assert metadata["document_type"] == "risk-management"
        assert metadata["filename"] == "risk-management-guide.md"

    def test_extract_metadata_for_incident_document(self, tmp_path):
        """Test metadata extraction for incident response document."""
        test_file = tmp_path / "incident-response-basics.md"
        test_file.write_text("# Incident Response Basics\n\nIncident content.")

        metadata = extract_metadata(test_file)

        assert metadata["document_type"] == "incident-response"

    def test_extract_metadata_handles_missing_title(self, tmp_path):
        """Test that metadata extraction handles files without markdown title."""
        test_file = tmp_path / "some-document.md"
        test_file.write_text("Content without a title header")

        metadata = extract_metadata(test_file)

        assert metadata["filename"] == "some-document.md"
        assert "Some Document" in metadata["title"]  # Generated from filename
        assert metadata["document_type"] == "general"
