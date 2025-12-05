# Temp File Output Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Save transcript JSON to temp file instead of returning inline, reducing model context consumption.

**Architecture:** Modify `get_transcript` to write the response dict to a temp file and return the file path in the output text instead of the full JSON.

**Tech Stack:** Python stdlib (tempfile, json, pathlib)

---

### Task 1: Add Test for Temp File Creation

**Files:**
- Create: `tests/test_temp_file_output.py`

**Step 1: Write the failing test**

```python
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

        result = await get_transcript({"url": "test123video"})

        # Check temp file exists
        temp_dir = Path(tempfile.gettempdir())
        temp_file = temp_dir / "youtube-transcript-test123video.json"
        assert temp_file.exists(), f"Expected temp file at {temp_file}"

        # Check file contains valid JSON with expected structure
        content = json.loads(temp_file.read_text())
        assert content["video_id"] == "test123video"
        assert content["language"] == "English"
        assert "segments" in content

        # Cleanup
        temp_file.unlink()
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/jsnitsel/devel/youtube-transcript-mcp && source venv/bin/activate && pytest tests/test_temp_file_output.py -v`

Expected: FAIL - temp file not created (current implementation doesn't write files)

**Step 3: Commit failing test**

```bash
git add tests/test_temp_file_output.py
git commit -s -m "test: add failing test for temp file output"
```

---

### Task 2: Add Test for Response Text Contains File Path

**Files:**
- Modify: `tests/test_temp_file_output.py`

**Step 1: Add second test**

Add to `tests/test_temp_file_output.py`:

```python
@pytest.mark.asyncio
async def test_response_contains_file_path_not_json(mock_transcript):
    """Verify response text includes file path, not full JSON."""
    from youtube_transcript_mcp.server import get_transcript

    with patch("youtube_transcript_mcp.server.YouTubeTranscriptApi") as mock_api:
        mock_api.return_value.fetch.return_value = mock_transcript

        result = await get_transcript({"url": "test123video"})

        response_text = result[0].text

        # Should contain file path
        assert "Full transcript saved to:" in response_text
        assert "youtube-transcript-test123video.json" in response_text

        # Should NOT contain the full segments array inline
        assert '"segments":' not in response_text

        # Cleanup
        temp_file = Path(tempfile.gettempdir()) / "youtube-transcript-test123video.json"
        if temp_file.exists():
            temp_file.unlink()
```

**Step 2: Run tests to verify both fail**

Run: `cd /Users/jsnitsel/devel/youtube-transcript-mcp && source venv/bin/activate && pytest tests/test_temp_file_output.py -v`

Expected: Both tests FAIL

**Step 3: Commit**

```bash
git add tests/test_temp_file_output.py
git commit -s -m "test: add test for file path in response text"
```

---

### Task 3: Implement Temp File Output

**Files:**
- Modify: `src/youtube_transcript_mcp/server.py:10-14` (imports)
- Modify: `src/youtube_transcript_mcp/server.py:197-213` (file writing)

**Step 1: Add imports**

At top of `server.py`, add to existing imports (around line 10):

```python
import json
import tempfile
from pathlib import Path
```

**Step 2: Modify get_transcript to write temp file**

Replace lines 197-213 (after building segments, before return) with:

```python
            # Create response
            response = {
                "video_id": video_id,
                "language": fetched.language,
                "language_code": fetched.language_code,
                "is_generated": fetched.is_generated,
                "segment_count": len(segments),
                "total_characters": total_chars,
                "segments": segments,
            }

            # Write to temp file
            temp_path = Path(tempfile.gettempdir()) / f"youtube-transcript-{video_id}.json"
            temp_path.write_text(json.dumps(response, indent=2))

            result_text = f"Successfully extracted transcript for video {video_id}\n"
            result_text += f"Language: {fetched.language} ({fetched.language_code})\n"
            result_text += f"Generated: {fetched.is_generated}\n"
            result_text += f"Segments: {len(segments)}\n"
            result_text += f"Characters: {total_chars:,}\n\n"

            # Add first few segments as preview
            result_text += "Preview (first 3 segments):\n"
            for i, segment in enumerate(segments[:3]):
                result_text += f"{i + 1}. [{segment['start']:.1f}s] {segment['text']}\n"

            if len(segments) > 3:
                result_text += f"... ({len(segments) - 3} more segments)\n"

            result_text += f"\nFull transcript saved to: {temp_path}"

            return [TextContent(type="text", text=result_text)]
```

**Step 3: Run tests to verify they pass**

Run: `cd /Users/jsnitsel/devel/youtube-transcript-mcp && source venv/bin/activate && pytest tests/test_temp_file_output.py -v`

Expected: Both tests PASS

**Step 4: Run full test suite**

Run: `cd /Users/jsnitsel/devel/youtube-transcript-mcp && source venv/bin/activate && pytest -v`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/youtube_transcript_mcp/server.py
git commit -s -m "feat: save transcript to temp file instead of inline output

Reduces model context consumption for large transcripts.
Models can read the temp file when full content is needed."
```

---

### Task 4: Update Tool Description

**Files:**
- Modify: `src/youtube_transcript_mcp/server.py:93-94` (tool description)

**Step 1: Update description**

Change the `get_transcript` tool description (around line 93) from:

```python
            description="Extract transcript from a YouTube video. Handles various URL formats and provides detailed error messages.",
```

to:

```python
            description="Extract transcript from a YouTube video. Handles various URL formats and provides detailed error messages. Full transcript is saved to a temp file to reduce context usage.",
```

**Step 2: Run tests to verify nothing broke**

Run: `cd /Users/jsnitsel/devel/youtube-transcript-mcp && source venv/bin/activate && pytest -v`

Expected: All tests PASS

**Step 3: Commit**

```bash
git add src/youtube_transcript_mcp/server.py
git commit -s -m "docs: update tool description to mention temp file output"
```

---

### Task 5: Manual Integration Test

**Step 1: Test with real video**

Run: `cd /Users/jsnitsel/devel/youtube-transcript-mcp && source venv/bin/activate && python src/youtube_transcript_mcp/test_server.py`

Or test via Claude Code MCP integration if configured.

**Step 2: Verify output format**

Expected output should show:
- Metadata (language, segments, characters)
- Preview of first 3 segments
- File path (not inline JSON)

**Step 3: Verify temp file**

```bash
cat /tmp/youtube-transcript-*.json | head -20
```

Should show valid JSON with video_id, segments, etc.
