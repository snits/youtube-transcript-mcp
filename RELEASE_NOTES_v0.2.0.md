# Release Notes - Version 0.2.0

**Release Date**: [2025-09-03]  
**Version**: 0.2.0  
**Previous Version**: 0.1.0  

## ⚠️ BREAKING CHANGES ⚠️

This release contains **significant breaking changes** that require user action. Please read carefully before upgrading.

### 1. MCP Protocol Update (BREAKING)

**Impact**: All MCP clients must be updated to work with this version.

- **Change**: Updated to MCP protocol v1.1.2
- **What breaks**: Existing MCP client integrations will fail with protocol errors
- **Required action**: Update your MCP client implementations to use the new protocol
- **Technical details**:
  - Removed deprecated `CallToolRequest`/`CallToolResult` imports
  - Updated `handle_call_tool` method signature and return types
  - Protocol communication format has changed

### 2. Python Version Requirement (BREAKING)

**Impact**: Support for Python 3.8 and 3.9 has been dropped.

- **Change**: Minimum required Python version is now **3.10**
- **What breaks**: Installation will fail on Python 3.8 and 3.9
- **Required action**: Upgrade to Python 3.10 or later before installing this version
- **Driver**: MCP v1.1.2 dependency requires Python >=3.10

## Migration Guide

### For MCP Client Developers

If you're integrating with this MCP server, update your client code:

**Before (v0.1.x):**

```python
# Old MCP protocol - will no longer work
from mcp.types import CallToolRequest, CallToolResult
```

**After (v0.2.0):**

```python
# New MCP protocol - updated imports and handling
from mcp.types import TextContent
# Protocol handling updated internally - client-side changes may be required
```

**Recommended Actions:**

1. Review your MCP client implementation
2. Test connectivity with the new server version
3. Update error handling for protocol changes

### For End Users

1. **Check Python Version**: Run `python --version` - must be 3.10 or later
2. **Upgrade Python if needed**: Install Python 3.10+ before upgrading the MCP server
3. **Update Installation**:

   ```bash
   pip install --upgrade youtube-transcript-mcp
   ```

4. **Test Integration**: Verify your MCP client still works with the updated server

## What's New

### Features

- Updated to latest MCP protocol (v1.1.2) for improved compatibility and performance
- Enhanced error handling and protocol robustness

### Bug Fixes

- Fixed asyncio event loop conflict in test script
- Resolved dependency version compatibility issues

### Maintenance

- Updated third-party license information
- Added SPDX identifiers to source files
- Improved code formatting and consistency
- Enhanced documentation and license compliance

## Compatibility

- **Python**: 3.10+ (was 3.8+)
- **MCP Protocol**: v1.1.2 (was v1.0.x)
- **Dependencies**:
  - `youtube-transcript-api==1.2.2` (unchanged)
  - `mcp==1.1.2` (updated from 1.0.x)
  - `pydantic==2.8.2` (unchanged)

## Installation

```bash
# Ensure Python 3.10+
python --version

# Install/upgrade
pip install youtube-transcript-mcp==0.2.0
```

## Rollback Instructions

If you encounter issues and need to rollback:

```bash
pip install youtube-transcript-mcp==0.1.0
```

Note: Rollback requires downgrading any MCP clients that were updated for v0.2.0.

## Getting Help

If you encounter issues during migration:

1. **Check Python version**: Ensure Python 3.10+
2. **Review MCP client**: Verify client compatibility with new protocol
3. **Check logs**: Protocol errors will be logged during MCP communication
4. **File an issue**: Report problems at [project repository]

## Technical Details

For developers interested in the technical changes:

- **Commit**: [commit hash] - MCP protocol compatibility update
- **Commit**: [commit hash] - Python version requirement fix  
- **Files changed**: `src/youtube_transcript_mcp/server.py`, `pyproject.toml`
- **Protocol changes**: Internal MCP message handling updated for v1.1.2

---

**⚠️ Important**: This release requires coordination between server and client updates. Plan your deployment accordingly to minimize downtime.

