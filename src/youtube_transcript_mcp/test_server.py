#!/usr/bin/env python3
"""Test the MCP server startup"""

import asyncio
import sys
import traceback

try:
    from server import main
    print("Successfully imported server module", file=sys.stderr)
    
    async def test_startup():
        print("Starting MCP server test...", file=sys.stderr)
        await main()
    
    if __name__ == "__main__":
        asyncio.run(test_startup())
        
except Exception as e:
    print(f"Error starting server: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)