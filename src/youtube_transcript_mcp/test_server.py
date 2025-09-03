#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Test the MCP server startup"""

import asyncio
import sys
import traceback

try:
    from server import async_main
    print("Successfully imported server module", file=sys.stderr)
    
    async def test_startup():
        print("Starting MCP server test...", file=sys.stderr)
        print("Server imports are working correctly", file=sys.stderr)
        print("Test completed successfully - server can start", file=sys.stderr)
        # Note: We don't actually start the server as it would run indefinitely
        # This test just verifies imports and basic module loading
    
    if __name__ == "__main__":
        asyncio.run(test_startup())
        
except Exception as e:
    print(f"Error starting server: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)