#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
YouTube Transcript MCP Server

A reliable Model Context Protocol server for extracting YouTube video transcripts.
Built using the proven youtube-transcript-api library.
"""

import asyncio
import re
import sys
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

from mcp.server.stdio import stdio_server
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    CallToolRequest,
    CallToolResult,
)
from pydantic import BaseModel

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    VideoUnavailable, 
    NoTranscriptFound,
    NotTranslatable,
    CookiePathInvalid,
    TranslationLanguageNotAvailable
)


def extract_video_id(url: str) -> str:
    """
    Extract YouTube video ID from various URL formats.
    
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - VIDEO_ID (direct ID)
    """
    # If it's already just a video ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
    
    # Parse various YouTube URL formats
    parsed = urlparse(url)
    
    if parsed.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed.path == '/watch':
            return parse_qs(parsed.query).get('v', [None])[0]
    elif parsed.hostname in ['youtu.be']:
        return parsed.path.lstrip('/')
    
    # If we can't parse it, try to extract anything that looks like a video ID
    match = re.search(r'[a-zA-Z0-9_-]{11}', url)
    if match:
        return match.group(0)
    
    raise ValueError(f"Could not extract video ID from: {url}")


class TranscriptInfo(BaseModel):
    """Information about an available transcript."""
    language_code: str
    language: str
    is_generated: bool
    is_translatable: bool
    translation_languages: List[str]


class TranscriptSegment(BaseModel):
    """A single transcript segment with text and timing."""
    text: str
    start: float
    duration: float


# Create the MCP server
server = Server("youtube-transcript-reliable")


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_transcript",
            description="Extract transcript from a YouTube video. Handles various URL formats and provides detailed error messages.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "YouTube video URL or video ID (e.g., 'https://youtube.com/watch?v=abc123' or 'abc123')"
                    },
                    "lang": {
                        "type": "string", 
                        "description": "Preferred language code (e.g., 'en', 'de', 'fr'). Defaults to 'en'.",
                        "default": "en"
                    },
                    "preserve_formatting": {
                        "type": "boolean",
                        "description": "Keep HTML formatting tags like <i>, <b>. Defaults to false.",
                        "default": False
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="list_transcripts", 
            description="List all available transcript languages for a YouTube video. Useful for debugging transcript availability.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "YouTube video URL or video ID"
                    }
                },
                "required": ["url"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls."""
    
    if request.name == "get_transcript":
        return await get_transcript(request.arguments)
    elif request.name == "list_transcripts":
        return await list_transcripts(request.arguments)
    else:
        raise ValueError(f"Unknown tool: {request.name}")


async def get_transcript(arguments: Dict[str, Any]) -> CallToolResult:
    """Extract transcript from YouTube video."""
    
    try:
        # Parse arguments
        url = arguments.get("url")
        lang = arguments.get("lang", "en")
        preserve_formatting = arguments.get("preserve_formatting", False)
        
        if not url:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: URL is required")]
            )
        
        # Extract video ID
        try:
            video_id = extract_video_id(url)
        except ValueError as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")]
            )
        
        # Fetch transcript
        try:
            fetched = YouTubeTranscriptApi().fetch(
                video_id, 
                languages=[lang, 'en'],  # Fallback to English if preferred not available
                preserve_formatting=preserve_formatting
            )
            
            # Convert to our format
            segments = []
            total_chars = 0
            
            for segment in fetched:
                segments.append({
                    "text": segment.text,
                    "start": segment.start,
                    "duration": segment.duration
                })
                total_chars += len(segment.text)
            
            # Create response
            response = {
                "video_id": video_id,
                "language": fetched.language,
                "language_code": fetched.language_code,
                "is_generated": fetched.is_generated,
                "segment_count": len(segments),
                "total_characters": total_chars,
                "segments": segments
            }
            
            result_text = f"Successfully extracted transcript for video {video_id}\n"
            result_text += f"Language: {fetched.language} ({fetched.language_code})\n"
            result_text += f"Generated: {fetched.is_generated}\n"
            result_text += f"Segments: {len(segments)}\n"
            result_text += f"Characters: {total_chars:,}\n\n"
            
            # Add first few segments as preview
            result_text += "Preview (first 3 segments):\n"
            for i, segment in enumerate(segments[:3]):
                result_text += f"{i+1}. [{segment['start']:.1f}s] {segment['text']}\n"
            
            if len(segments) > 3:
                result_text += f"... ({len(segments) - 3} more segments)\n"
            
            result_text += f"\nFull transcript JSON:\n{response}"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except TranscriptsDisabled:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: Transcripts are disabled for video {video_id}")]
            )
        except VideoUnavailable:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: Video {video_id} is unavailable")]
            )
        except NoTranscriptFound as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: No transcript found for video {video_id} in language '{lang}' or English fallback: {str(e)}")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unexpected error: {str(e)}")]
            )
    
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Server error: {str(e)}")]
        )


async def list_transcripts(arguments: Dict[str, Any]) -> CallToolResult:
    """List available transcripts for a YouTube video."""
    
    try:
        # Parse arguments
        url = arguments.get("url")
        
        if not url:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: URL is required")]
            )
        
        # Extract video ID
        try:
            video_id = extract_video_id(url)
        except ValueError as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")]
            )
        
        # List available transcripts
        try:
            transcript_list = YouTubeTranscriptApi().list(video_id)
            
            result_text = f"Available transcripts for video {video_id}:\n\n"
            
            manual_transcripts = []
            generated_transcripts = []
            
            for transcript in transcript_list:
                info = {
                    "language_code": transcript.language_code,
                    "language": transcript.language,
                    "is_generated": transcript.is_generated,
                    "is_translatable": transcript.is_translatable,
                    "translation_languages": [lang.language_code for lang in transcript.translation_languages[:5]]  # Get language codes and limit
                }
                
                if transcript.is_generated:
                    generated_transcripts.append(info)
                else:
                    manual_transcripts.append(info)
            
            if manual_transcripts:
                result_text += "Manual/Human-created transcripts:\n"
                for t in manual_transcripts:
                    result_text += f"- {t['language_code']} ({t['language']})\n"
                    if t['is_translatable'] and t['translation_languages']:
                        result_text += f"  Can translate to: {', '.join(t['translation_languages'])}\n"
                result_text += "\n"
            
            if generated_transcripts:
                result_text += "Auto-generated transcripts:\n"
                for t in generated_transcripts:
                    result_text += f"- {t['language_code']} ({t['language']})\n"
                    if t['is_translatable'] and t['translation_languages']:
                        result_text += f"  Can translate to: {', '.join(t['translation_languages'])}\n"
                result_text += "\n"
            
            if not manual_transcripts and not generated_transcripts:
                result_text += "No transcripts found.\n"
            
            result_text += f"\nTotal: {len(manual_transcripts)} manual, {len(generated_transcripts)} generated"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except TranscriptsDisabled:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: Transcripts are disabled for video {video_id}")]
            )
        except VideoUnavailable:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: Video {video_id} is unavailable")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unexpected error: {str(e)}")]
            )
    
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Server error: {str(e)}")]
        )


async def async_main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, 
            write_stream, 
            server.create_initialization_options()
        )


def main():
    """Entry point for pipx/pip installations."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()