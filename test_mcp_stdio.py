#!/usr/bin/env python3
"""
Test GitHub MCP Server stdio mode communication.

This script tests if the GitHub MCP server properly responds in stdio mode,
which is required for MCP protocol communication.
"""

import os
import sys
import subprocess
import asyncio
import json
from typing import Optional


def test_docker_stdio_manually():
    """Test Docker stdio communication manually."""
    print("🧪 Testing Docker stdio mode manually...")
    print("=" * 60)

    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        print("❌ GITHUB_PERSONAL_ACCESS_TOKEN not set")
        return False

    # Build the exact Docker command
    docker_cmd = [
        "docker", "run", "-i", "--rm",
        "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={token}",
        "ghcr.io/github/github-mcp-server",
        "stdio"
    ]

    print(f"📝 Running command:")
    print(f"   {' '.join(docker_cmd)}")
    print()

    # Create a simple MCP initialize message
    initialize_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }

    try:
        print("📤 Sending initialize request...")
        print(f"   {json.dumps(initialize_msg)[:80]}...")
        print()

        # Run Docker with the initialize message
        process = subprocess.Popen(
            docker_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Send the message
        stdout, stderr = process.communicate(
            input=json.dumps(initialize_msg) + "\n",
            timeout=10
        )

        print("📥 Response received:")
        if stdout:
            print(f"✅ STDOUT:")
            for line in stdout.strip().split('\n')[:10]:
                print(f"   {line[:120]}")
            if len(stdout.strip().split('\n')) > 10:
                print("   ... (truncated)")

        if stderr:
            print(f"⚠️  STDERR:")
            for line in stderr.strip().split('\n')[:10]:
                print(f"   {line}")

        # Check if we got a valid response
        if stdout and ("result" in stdout or "serverInfo" in stdout):
            print("\n✅ Server responded correctly in stdio mode!")
            return True
        else:
            print("\n❌ Server did not respond as expected")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Timeout waiting for server response")
        process.kill()
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_mcp_client_with_stdio():
    """Test MCP client with stdio mode."""
    print("\n" + "=" * 60)
    print("🧪 Testing MCP Client with stdio mode...")
    print("=" * 60)

    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        print("❌ GITHUB_PERSONAL_ACCESS_TOKEN not set")
        return False

    try:
        from github_mcp_client import GitHubMCPClient

        print("📦 GitHubMCPClient loaded")
        print("🔌 Connecting to GitHub MCP server...")

        async with GitHubMCPClient(token) as client:
            print("✅ Connected successfully!")

            # List tools
            print("\n📋 Listing available tools...")
            tools = await client.list_available_tools()

            print(f"✅ Found {len(tools)} tools:")
            for i, tool in enumerate(tools[:10], 1):
                print(f"   {i}. {tool}")
            if len(tools) > 10:
                print(f"   ... and {len(tools) - 10} more")

            # Try a simple operation
            print("\n🧪 Testing tool call (get_repository)...")
            result = await client.get_repository_info("github", "docs")

            if result.get("status") == "success":
                print("✅ Tool call successful!")
                repo_data = result.get("data", {})
                print(f"   Repository: {repo_data.get('full_name', 'N/A')}")
                print(f"   Stars: {repo_data.get('stargazers_count', 'N/A')}")
                return True
            else:
                print(f"❌ Tool call failed: {result.get('message')}")
                return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test runner."""
    print("=" * 60)
    print("GitHub MCP stdio Mode Test")
    print("=" * 60)
    print()

    # Test 1: Manual Docker stdio test
    manual_success = test_docker_stdio_manually()

    # Test 2: MCP client test
    client_success = await test_mcp_client_with_stdio()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Manual Docker stdio test: {'✅ PASS' if manual_success else '❌ FAIL'}")
    print(f"MCP Client test: {'✅ PASS' if client_success else '❌ FAIL'}")

    if manual_success and client_success:
        print("\n✅ All tests passed! GitHub MCP is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
