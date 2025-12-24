#!/usr/bin/env python3
"""Test script for MCP server validation."""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.server import mcp

async def test_server():
    """Test the MCP server functionality."""
    print("=== MCP Server Pre-flight Tests ===\n")

    print("1. Testing tool listing...")
    try:
        tools = await mcp.get_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            if hasattr(tool, 'name'):
                name = tool.name
                desc = getattr(tool, 'description', 'No description')
                if desc and isinstance(desc, str):
                    desc = desc.split('.')[0]
            else:
                # Handle if tools are returned as strings
                name = str(tool)
                desc = 'Tool available'
            print(f"   - {name}: {desc}")
    except Exception as e:
        print(f"❌ Tool listing failed: {e}")
        return False

    print("\n2. Testing server info tool...")
    try:
        # Import the function directly since we can't easily call tools in this context
        from server import get_server_info
        info = get_server_info()
        print(f"✅ Server info: {info['server_info']['name']}")
    except Exception as e:
        print(f"❌ Server info failed: {e}")

    print("\n3. Testing job manager...")
    try:
        from jobs.manager import job_manager
        jobs = job_manager.list_jobs()
        print(f"✅ Job manager working, found {len(jobs.get('jobs', []))} existing jobs")
    except Exception as e:
        print(f"❌ Job manager failed: {e}")

    print("\n=== Pre-flight tests completed ===")
    return True

if __name__ == "__main__":
    asyncio.run(test_server())