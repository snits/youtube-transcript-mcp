# ABOUTME: Tests for temp file transcript output functionality.
# ABOUTME: Verifies transcripts are saved to temp files instead of inline.

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture
def mock_transcript():
    """Mock YouTubeTranscriptApi response."""
    mock_fetched = MagicMock()
    mock_fetched.language = "English"
    mock_fetched.language_code = "en"
    mock_fetched.is_generated = True
    mock_fetched.__iter__ = lambda self: iter([
        MagicMock(text="Hello world", start=0.0, duration=2.5),
        MagicMock(text="Second segment", start=2.5, duration=3.0),
    ])
    return mock_fetched


@pytest.mark.asyncio
async def test_transcript_saved_to_temp_file(mock_transcript):
    """Verify transcript JSON is saved to temp file."""
    from youtube_transcript_mcp.server import get_transcript

    with patch("youtube_transcript_mcp.server.YouTubeTranscriptApi") as mock_api:
        mock_api.return_value.fetch.return_value = mock_transcript

        result = await get_transcript({"url": "test1234567"})

        # Check temp file exists
        temp_dir = Path(tempfile.gettempdir())
        temp_file = temp_dir / "youtube-transcript-test1234567.json"

        try:
            assert temp_file.exists(), f"Expected temp file at {temp_file}"

            # Check file contains valid JSON with expected structure
            content = json.loads(temp_file.read_text())
            assert content["video_id"] == "test1234567"
            assert content["language"] == "English"
            assert "segments" in content
        finally:
            # Cleanup even if assertions fail
            if temp_file.exists():
                temp_file.unlink()


@pytest.mark.asyncio
async def test_response_contains_file_path_not_json(mock_transcript):
    """Verify response text includes file path, not full JSON."""
    from youtube_transcript_mcp.server import get_transcript

    with patch("youtube_transcript_mcp.server.YouTubeTranscriptApi") as mock_api:
        mock_api.return_value.fetch.return_value = mock_transcript

        result = await get_transcript({"url": "test1234567"})

        response_text = result[0].text

        temp_file = Path(tempfile.gettempdir()) / "youtube-transcript-test1234567.json"

        try:
            # Should contain file path
            assert "Full transcript saved to:" in response_text
            assert "youtube-transcript-test1234567.json" in response_text

            # Should NOT contain the full segments array inline
            assert '"segments":' not in response_text
        finally:
            # Cleanup even if assertions fail
            if temp_file.exists():
                temp_file.unlink()
