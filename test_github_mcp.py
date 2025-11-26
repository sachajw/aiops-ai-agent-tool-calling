#!/usr/bin/env python3
"""
Test script for GitHub MCP integration.

This script tests the GitHub MCP client connection and basic functionality.
"""

import os
import asyncio
from github_mcp_client import GitHubMCPClient


async def test_basic_connection():
    """Test basic connection to GitHub MCP server."""
    print("🧪 Testing GitHub MCP connection...")
    print()

    # Check for token
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        print("❌ GITHUB_PERSONAL_ACCESS_TOKEN not set")
        print("   Set it with: export GITHUB_PERSONAL_ACCESS_TOKEN='your_token'")
        return False

    print("✅ Token found")

    try:
        async with GitHubMCPClient(token) as client:
            print("✅ Connected to GitHub MCP server")

            # List available tools
            print("\n📋 Available GitHub MCP tools:")
            tools = await client.list_available_tools()
            for tool in tools:
                print(f"   - {tool}")

            print(f"\n✅ Found {len(tools)} GitHub tools")
            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test entry point."""
    print("=" * 60)
    print("GitHub MCP Integration Test")
    print("=" * 60)
    print()

    success = asyncio.run(test_basic_connection())

    print()
    print("=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
