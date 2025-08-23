# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About This Project

This is a Model Context Protocol (MCP) server that provides reliable YouTube transcript extraction. Built to replace a broken third-party MCP server that failed to extract accessible transcripts. Uses the proven `youtube-transcript-api` library as the backend.

## Development Commands

### Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Testing
```bash
# Test server startup
python src/youtube_transcript_mcp/test_server.py

# Manual testing with MCP integration
claude mcp add youtube-transcript-reliable "/path/to/venv/bin/python /path/to/server.py" -s user
```

### Installation as Package
```bash
pip install -e .
youtube-transcript-mcp  # runs the server
```

## Architecture

### Core Components

**`src/youtube_transcript_mcp/server.py`** - Main MCP server implementation
- `extract_video_id()` - Parses YouTube URLs to extract video IDs
- `get_transcript()` - Core transcript extraction with error handling
- `list_transcripts()` - Debug tool to show available transcript languages
- MCP server framework integration with stdio communication

### Key Architecture Decisions

**URL Flexibility**: Handles multiple YouTube URL formats (youtube.com, youtu.be, direct video IDs)

**Error Handling Strategy**: Comprehensive exception handling for all YouTube API failure modes:
- TranscriptsDisabled, VideoUnavailable, NoTranscriptFound
- Language fallback (user preference → English → error)

**Output Format**: Structured JSON with metadata for downstream processing:
- Video metadata (language, generation status)
- Segment-level timing data (start, duration)
- Statistics (segment count, character count)
- Preview format for large responses

### Dependencies Architecture

- `youtube-transcript-api==1.2.2` - Proven transcript extraction backend (trust score 8.9)
- `mcp==1.1.2` - Model Context Protocol framework for LLM integration  
- `pydantic==2.8.2` - Data validation and serialization

### MCP Integration Pattern

The server implements two MCP tools:
- `get_transcript(url, lang="en", preserve_formatting=False)` - Extract transcript
- `list_transcripts(url)` - Debug available languages

Both tools use consistent error handling and return detailed diagnostic information to help with troubleshooting YouTube transcript access issues.

## Key Design Patterns

**Defensive URL Parsing**: Multiple fallback strategies for extracting video IDs from various URL formats

**Language Prioritization**: Attempts user-specified language first, falls back to English, provides clear error messages

**Rich Error Context**: Each failure mode provides specific diagnostic information rather than generic errors

**Preview-First Output**: Large transcript responses include metadata preview before full JSON dump for better UX

## Integration Notes

This server was built specifically for Alexandria knowledge base integration. The structured JSON output format includes timing metadata and video context needed for downstream knowledge processing pipelines.