# Temp File Output for Model-Friendly Transcripts

## Problem

Large YouTube transcripts consume significant model context when returned inline. A 50k character transcript uses context that could be better spent on reasoning.

## Solution

Save full transcript JSON to a temp file and return the file path. Model reads file only when it needs full content.

## Design

### Output Format

```
Successfully extracted transcript for video abc123
Language: English (en)
Generated: True
Segments: 847
Characters: 52,341

Preview (first 3 segments):
1. [0.0s] Welcome to today's video...
2. [3.2s] We're going to cover...
3. [7.8s] Let's start with...
... (844 more segments)

Full transcript saved to: /tmp/youtube-transcript-abc123.json
```

### File Location

- System temp directory (`tempfile.gettempdir()`)
- Naming: `youtube-transcript-{video_id}.json`
- Same video ID overwrites previous file (no duplicates)

### File Content

Full JSON response object (same structure as current inline output):

```json
{
  "video_id": "abc123",
  "language": "English",
  "language_code": "en",
  "is_generated": true,
  "segment_count": 847,
  "total_characters": 52341,
  "segments": [...]
}
```

## Implementation

Changes to `server.py`:

1. Add imports: `tempfile`, `json`, `pathlib.Path`
2. After building response dict, write to temp file
3. Replace inline JSON with file path in output text

No changes to `list_transcripts`, URL parsing, or error handling.

## Testing

1. Verify temp file created with correct content
2. Verify response text includes file path (not full JSON)
3. Verify file is valid JSON with expected schema
4. Verify same video ID overwrites previous file
