# YouTube Transcript MCP Server

A reliable Model Context Protocol server for extracting YouTube video transcripts using the proven `youtube-transcript-api` library.

## Features

- Extract transcripts from YouTube videos
- List available transcript languages  
- Support for auto-generated and manual transcripts
- Proper error handling and debugging
- Multiple output formats (JSON, plain text)

## Installation

### Using pipx (recommended)
```bash
pipx install .
```

### Using pip
```bash
pip install .
```

### Development Installation
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Usage

### As MCP Server
Add to your Claude Code configuration:

```json
{
  "youtube-transcript-reliable": {
    "command": "youtube-transcript-mcp"
  }
}
```

### Available Tools

- **`get_transcript(url, lang="en", preserve_formatting=false)`** - Extract transcript from a YouTube video
  - `url`: YouTube video URL or video ID (e.g., 'https://youtube.com/watch?v=abc123' or 'abc123') 
  - `lang`: Preferred language code (e.g., 'en', 'de', 'fr'). Defaults to 'en'
  - `preserve_formatting`: Keep HTML formatting tags like `<i>`, `<b>`. Defaults to false
  
- **`list_transcripts(url)`** - List all available transcript languages for a YouTube video
  - `url`: YouTube video URL or video ID
  - Useful for debugging transcript availability

## Development

Built using:
- `youtube-transcript-api` - Proven transcript extraction
- `mcp` - Model Context Protocol framework

## Acknowledgments

Thanks to **Johannes Depoix** and contributors to [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) for providing the reliable transcript extraction backend that powers this MCP server.

Special recognition to open source software developers everywhere, whose collective work forms the foundation of modern software development and whose source code contributed to the training data that enables AI assistance in projects like this.