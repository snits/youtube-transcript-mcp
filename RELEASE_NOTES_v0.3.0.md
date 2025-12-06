# Release Notes - Version 0.3.0

**Release Date**: 2025-12-05
**Version**: 0.3.0
**Previous Version**: 0.2.0

## ⚠️ BEHAVIOR CHANGE ⚠️

This release changes how transcript data is returned to reduce context usage.

### Temp File Output (BEHAVIOR CHANGE)

**Impact**: Clients expecting inline JSON transcript data will now receive a file path instead.

- **Change**: Full transcript JSON is now saved to a temp file instead of returned inline
- **What changes**: The `get_transcript` tool now returns:
  - Summary metadata (video ID, language, segment count, character count)
  - Preview of first 3 segments
  - File path to full transcript JSON
- **Rationale**: Large transcripts were consuming significant context window space. Saving to a temp file allows models to selectively read the full transcript when needed.
- **File location**: `/tmp/youtube-transcript-{video_id}.json`

## Migration Guide

### For MCP Clients

The tool response format has changed:

**Before (v0.2.x):**
```
{
  "video_id": "abc123",
  "language": "English",
  "segments": [...]  // Full transcript inline
}
```

**After (v0.3.0):**
```
Successfully extracted transcript for video abc123
Language: English (en)
Generated: True
Segments: 150
Characters: 25,000

Preview (first 3 segments):
1. [0.0s] Hello and welcome...
2. [3.5s] Today we'll be...
3. [7.2s] Let's get started...
... (147 more segments)

Full transcript saved to: /tmp/youtube-transcript-abc123.json
```

**Recommended Actions:**

1. Update any code that parses the inline JSON response
2. If you need the full transcript, read from the temp file path provided
3. The temp file contains the same JSON structure as before (video_id, language, segments array)

### For End Users

No action required. The tool now outputs a summary and saves the full transcript to a temp file, which reduces context usage for LLM conversations.

## What's New

### Features

- **Temp file output**: Full transcript saved to temp file to reduce context usage
- **Summary response**: Concise metadata and preview returned instead of full JSON
- **Preview segments**: First 3 segments shown inline for quick verification

### Improvements

- Significantly reduced context window consumption for long videos
- Faster response display since only summary is rendered
- Full data still available in structured JSON format

## Compatibility

- **Python**: 3.10+ (unchanged)
- **MCP Protocol**: v1.1.2 (unchanged)
- **Dependencies**: All unchanged
  - `youtube-transcript-api==1.2.2`
  - `mcp==1.1.2`
  - `pydantic==2.8.2`

## Installation

```bash
# Ensure Python 3.10+
python --version

# Install/upgrade
pip install youtube-transcript-mcp==0.3.0
```

## Rollback Instructions

If you need the previous inline JSON behavior:

```bash
pip install youtube-transcript-mcp==0.2.0
```

## Getting Help

If you encounter issues:

1. **Check temp file**: Verify the file exists at the path shown
2. **File permissions**: Ensure `/tmp` is writable
3. **Parse the JSON**: Use the temp file for full transcript access
4. **File an issue**: Report problems at https://github.com/jsnitsel/youtube-transcript-mcp

---

**Note**: This change optimizes for LLM context usage. The full transcript data is preserved in the temp file with the same structure as before.
