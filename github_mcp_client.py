#!/usr/bin/env python3
"""
GitHub MCP Client - Integration with GitHub MCP Server

This module provides integration with the GitHub MCP (Model Context Protocol) server
to perform GitHub operations like creating PRs and issues without requiring the gh CLI.
"""

import os
import json
import subprocess
from typing import Dict, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class GitHubMCPClient:
    """Client for interacting with GitHub via MCP server."""

    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub MCP client.

        Args:
            github_token: GitHub Personal Access Token (falls back to env var)
        """
        self.github_token = github_token or os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        if not self.github_token:
            raise ValueError(
                "GitHub token not provided. Set GITHUB_PERSONAL_ACCESS_TOKEN "
                "environment variable or pass token to constructor."
            )

        self.server_params = StdioServerParameters(
            command="/usr/local/bin/github-mcp-server",
            args=["stdio"],
            env={
                "GITHUB_PERSONAL_ACCESS_TOKEN": self.github_token
            }
        )
        self.session: Optional[ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        # Start MCP server connection
        self.stdio_transport = await stdio_client(self.server_params).__aenter__()
        self.stdio, self.write = self.stdio_transport

        # Initialize session
        self.session = ClientSession(self.stdio, self.write)
        await self.session.__aenter__()

        # Initialize the session
        await self.session.initialize()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        if hasattr(self, 'stdio_transport'):
            await self.stdio_transport.__aexit__(exc_type, exc_val, exc_tb)

    async def list_available_tools(self) -> list:
        """
        List all available tools from the GitHub MCP server.

        Returns:
            List of available tool names
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")

        tools_result = await self.session.list_tools()
        return [tool.name for tool in tools_result.tools]

    async def create_pull_request(
        self,
        repo_owner: str,
        repo_name: str,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> Dict:
        """
        Create a GitHub Pull Request using MCP.

        Args:
            repo_owner: Repository owner (username or organization)
            repo_name: Repository name
            title: PR title
            body: PR description
            head: Source branch
            base: Target branch (default: main)

        Returns:
            Dictionary with PR details or error
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")

        try:
            result = await self.session.call_tool(
                "create_pull_request",
                arguments={
                    "owner": repo_owner,
                    "repo": repo_name,
                    "title": title,
                    "body": body,
                    "head": head,
                    "base": base
                }
            )

            # Parse the result
            if result.content and len(result.content) > 0:
                response = result.content[0].text
                pr_data = json.loads(response) if isinstance(response, str) else response

                return {
                    "status": "success",
                    "pr_url": pr_data.get("html_url", ""),
                    "pr_number": pr_data.get("number", ""),
                    "message": f"Successfully created PR #{pr_data.get('number', '')}"
                }
            else:
                return {
                    "status": "error",
                    "message": "No response from MCP server"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error creating PR via MCP: {str(e)}"
            }

    async def create_issue(
        self,
        repo_owner: str,
        repo_name: str,
        title: str,
        body: str,
        labels: Optional[list] = None
    ) -> Dict:
        """
        Create a GitHub Issue using MCP.

        Args:
            repo_owner: Repository owner (username or organization)
            repo_name: Repository name
            title: Issue title
            body: Issue description
            labels: List of label names (default: ["dependencies"])

        Returns:
            Dictionary with Issue details or error
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")

        if labels is None:
            labels = ["dependencies"]

        try:
            result = await self.session.call_tool(
                "create_issue",
                arguments={
                    "owner": repo_owner,
                    "repo": repo_name,
                    "title": title,
                    "body": body,
                    "labels": labels
                }
            )

            # Parse the result
            if result.content and len(result.content) > 0:
                response = result.content[0].text
                issue_data = json.loads(response) if isinstance(response, str) else response

                return {
                    "status": "success",
                    "issue_url": issue_data.get("html_url", ""),
                    "issue_number": issue_data.get("number", ""),
                    "message": f"Successfully created issue #{issue_data.get('number', '')}"
                }
            else:
                return {
                    "status": "error",
                    "message": "No response from MCP server"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error creating issue via MCP: {str(e)}"
            }

    async def get_repository_info(self, repo_owner: str, repo_name: str) -> Dict:
        """
        Get repository information using MCP.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name

        Returns:
            Dictionary with repository details or error
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")

        try:
            result = await self.session.call_tool(
                "get_repository",
                arguments={
                    "owner": repo_owner,
                    "repo": repo_name
                }
            )

            if result.content and len(result.content) > 0:
                response = result.content[0].text
                repo_data = json.loads(response) if isinstance(response, str) else response

                return {
                    "status": "success",
                    "data": repo_data
                }
            else:
                return {
                    "status": "error",
                    "message": "No response from MCP server"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error getting repository info: {str(e)}"
            }


# Synchronous wrapper functions for compatibility with existing code
def create_pr_sync(
    repo_name: str,
    branch_name: str,
    title: str,
    body: str,
    base_branch: str = "main",
    github_token: Optional[str] = None
) -> Dict:
    """
    Synchronous wrapper for creating a PR via GitHub MCP.

    Args:
        repo_name: Repository in owner/repo format
        branch_name: Source branch for the PR
        title: PR title
        body: PR description
        base_branch: Target branch (default: main)
        github_token: GitHub token (optional, uses env var if not provided)

    Returns:
        Dictionary with PR URL or error
    """
    import asyncio

    # Parse repo_name
    parts = repo_name.split("/")
    if len(parts) != 2:
        return {
            "status": "error",
            "message": f"Invalid repo_name format. Expected 'owner/repo', got '{repo_name}'"
        }

    owner, repo = parts

    async def _create_pr():
        async with GitHubMCPClient(github_token) as client:
            return await client.create_pull_request(
                repo_owner=owner,
                repo_name=repo,
                title=title,
                body=body,
                head=branch_name,
                base=base_branch
            )

    try:
        return asyncio.run(_create_pr())
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in MCP client: {str(e)}"
        }


def create_issue_sync(
    repo_name: str,
    title: str,
    body: str,
    labels: Optional[str] = "dependencies",
    github_token: Optional[str] = None
) -> Dict:
    """
    Synchronous wrapper for creating an issue via GitHub MCP.

    Args:
        repo_name: Repository in owner/repo format
        title: Issue title
        body: Issue description
        labels: Comma-separated labels or single label (default: dependencies)
        github_token: GitHub token (optional, uses env var if not provided)

    Returns:
        Dictionary with Issue URL or error
    """
    import asyncio

    # Parse repo_name
    parts = repo_name.split("/")
    if len(parts) != 2:
        return {
            "status": "error",
            "message": f"Invalid repo_name format. Expected 'owner/repo', got '{repo_name}'"
        }

    owner, repo = parts

    # Parse labels
    label_list = labels.split(",") if labels else ["dependencies"]
    label_list = [label.strip() for label in label_list]

    async def _create_issue():
        async with GitHubMCPClient(github_token) as client:
            return await client.create_issue(
                repo_owner=owner,
                repo_name=repo,
                title=title,
                body=body,
                labels=label_list
            )

    try:
        return asyncio.run(_create_issue())
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in MCP client: {str(e)}"
        }


# CLI testing
if __name__ == "__main__":
    import asyncio

    async def test_connection():
        """Test GitHub MCP connection and list available tools."""
        try:
            async with GitHubMCPClient() as client:
                print("✅ Successfully connected to GitHub MCP server")
                print("\n📋 Available tools:")
                tools = await client.list_available_tools()
                for tool in tools:
                    print(f"  - {tool}")
        except Exception as e:
            print(f"❌ Error connecting to GitHub MCP: {e}")

    print("Testing GitHub MCP connection...")
    asyncio.run(test_connection())
