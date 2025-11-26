#!/usr/bin/env python3
"""
Smart Dependency Updater Agent

Intelligently updates dependencies with automatic testing and rollback capabilities.
Tests updates, identifies breaking changes, and creates PRs or Issues accordingly.
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent

# Load environment variables
load_dotenv()

# Import dependency operation tools
from dependency_operations import (
    apply_all_updates,
    rollback_major_update,
    parse_error_for_dependency,
    categorize_updates,
    get_latest_version_for_major
)


@tool
def detect_build_command(repo_path: str) -> str:
    """
    Auto-detect build, test, and verification commands for the repository.

    Args:
        repo_path: Path to the repository

    Returns:
        JSON with detected commands for build, test, and verification
    """
    try:
        commands = {
            "package_manager": None,
            "install": None,
            "build": None,
            "test": None,
            "lint": None,
            "type_check": None
        }

        # JavaScript/TypeScript - npm/yarn/pnpm
        if os.path.exists(os.path.join(repo_path, "package.json")):
            with open(os.path.join(repo_path, "package.json"), 'r') as f:
                package_json = json.load(f)
                scripts = package_json.get("scripts", {})

            # Detect package manager
            if os.path.exists(os.path.join(repo_path, "pnpm-lock.yaml")):
                pm = "pnpm"
            elif os.path.exists(os.path.join(repo_path, "yarn.lock")):
                pm = "yarn"
            else:
                pm = "npm"

            commands["package_manager"] = pm
            commands["install"] = f"{pm} install"

            # Detect available scripts
            if "build" in scripts:
                commands["build"] = f"{pm} run build"
            if "test" in scripts:
                commands["test"] = f"{pm} test"
            if "lint" in scripts:
                commands["lint"] = f"{pm} run lint"
            if "type-check" in scripts or "typecheck" in scripts:
                commands["type_check"] = f"{pm} run type-check"

        # Python - pip/poetry/pipenv
        elif os.path.exists(os.path.join(repo_path, "pyproject.toml")):
            with open(os.path.join(repo_path, "pyproject.toml"), 'r') as f:
                content = f.read()
                if '[tool.poetry]' in content:
                    commands["package_manager"] = "poetry"
                    commands["install"] = "poetry install"
                    commands["test"] = "poetry run pytest"
                    commands["build"] = "poetry build"

        elif os.path.exists(os.path.join(repo_path, "Pipfile")):
            commands["package_manager"] = "pipenv"
            commands["install"] = "pipenv install"
            commands["test"] = "pipenv run pytest"

        elif os.path.exists(os.path.join(repo_path, "requirements.txt")):
            commands["package_manager"] = "pip"
            commands["install"] = "pip install -r requirements.txt"
            commands["test"] = "pytest"

            # Check for setup.py
            if os.path.exists(os.path.join(repo_path, "setup.py")):
                commands["build"] = "python setup.py build"

        # Rust - Cargo
        elif os.path.exists(os.path.join(repo_path, "Cargo.toml")):
            commands["package_manager"] = "cargo"
            commands["build"] = "cargo build"
            commands["test"] = "cargo test"
            commands["lint"] = "cargo clippy"

        # Go
        elif os.path.exists(os.path.join(repo_path, "go.mod")):
            commands["package_manager"] = "go"
            commands["build"] = "go build ./..."
            commands["test"] = "go test ./..."
            commands["lint"] = "go vet ./..."

        # Ruby
        elif os.path.exists(os.path.join(repo_path, "Gemfile")):
            commands["package_manager"] = "bundler"
            commands["install"] = "bundle install"
            commands["test"] = "bundle exec rspec"

        # PHP
        elif os.path.exists(os.path.join(repo_path, "composer.json")):
            commands["package_manager"] = "composer"
            commands["install"] = "composer install"
            commands["test"] = "composer test"

        return json.dumps({
            "status": "success",
            "commands": commands
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error detecting build commands: {str(e)}"
        })


@tool
def run_build_test(repo_path: str, command: str, timeout: int = 300) -> str:
    """
    Execute a build or test command in the repository.

    Args:
        repo_path: Path to the repository
        command: Command to execute
        timeout: Timeout in seconds (default 300)

    Returns:
        JSON with execution results (success/failure, stdout, stderr)
    """
    try:
        original_dir = os.getcwd()
        os.chdir(repo_path)

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        os.chdir(original_dir)

        return json.dumps({
            "status": "success",
            "command": command,
            "exit_code": result.returncode,
            "succeeded": result.returncode == 0,
            "stdout": result.stdout[-5000:] if result.stdout else "",  # Last 5000 chars
            "stderr": result.stderr[-5000:] if result.stderr else ""
        }, indent=2)

    except subprocess.TimeoutExpired:
        os.chdir(original_dir)
        return json.dumps({
            "status": "error",
            "command": command,
            "message": f"Command timed out after {timeout} seconds"
        })
    except Exception as e:
        os.chdir(original_dir)
        return json.dumps({
            "status": "error",
            "command": command,
            "message": f"Error running command: {str(e)}"
        })


@tool
def write_dependency_file(repo_path: str, file_name: str, content: str) -> str:
    """
    Write updated dependency file to the repository.

    Args:
        repo_path: Path to the repository
        file_name: Name of the file (e.g., package.json, requirements.txt)
        content: New file content

    Returns:
        Confirmation message
    """
    try:
        file_path = os.path.join(repo_path, file_name)
        with open(file_path, 'w') as f:
            f.write(content)

        return json.dumps({
            "status": "success",
            "file": file_name,
            "path": file_path,
            "message": f"Successfully wrote {file_name}"
        })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error writing file: {str(e)}"
        })


@tool
def git_operations(repo_path: str, operation: str, **kwargs) -> str:
    """
    Perform git operations (branch, commit, push).

    Args:
        repo_path: Path to the repository
        operation: Operation to perform (create_branch, commit, push, get_remote_url)
        **kwargs: Additional arguments based on operation

    Returns:
        JSON with operation results
    """
    try:
        original_dir = os.getcwd()
        os.chdir(repo_path)

        if operation == "create_branch":
            branch_name = kwargs.get("branch_name", f"deps/auto-update-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                capture_output=True,
                text=True
            )
            os.chdir(original_dir)

            if result.returncode == 0:
                return json.dumps({
                    "status": "success",
                    "operation": "create_branch",
                    "branch_name": branch_name
                })
            else:
                return json.dumps({
                    "status": "error",
                    "operation": "create_branch",
                    "message": result.stderr
                })

        elif operation == "commit":
            message = kwargs.get("message", "chore: update dependencies")

            # Add all changes
            subprocess.run(["git", "add", "."], capture_output=True)

            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True
            )
            os.chdir(original_dir)

            if result.returncode == 0:
                return json.dumps({
                    "status": "success",
                    "operation": "commit",
                    "message": message
                })
            else:
                return json.dumps({
                    "status": "error",
                    "operation": "commit",
                    "message": result.stderr
                })

        elif operation == "push":
            branch_name = kwargs.get("branch_name")
            result = subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                capture_output=True,
                text=True
            )
            os.chdir(original_dir)

            if result.returncode == 0:
                return json.dumps({
                    "status": "success",
                    "operation": "push",
                    "branch_name": branch_name
                })
            else:
                return json.dumps({
                    "status": "error",
                    "operation": "push",
                    "message": result.stderr
                })

        elif operation == "get_remote_url":
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True
            )
            os.chdir(original_dir)

            if result.returncode == 0:
                url = result.stdout.strip()
                # Extract owner/repo from URL
                if "github.com" in url:
                    parts = url.replace(".git", "").split("/")
                    repo_name = f"{parts[-2]}/{parts[-1]}"
                else:
                    repo_name = url

                return json.dumps({
                    "status": "success",
                    "operation": "get_remote_url",
                    "url": url,
                    "repo_name": repo_name
                })
            else:
                return json.dumps({
                    "status": "error",
                    "operation": "get_remote_url",
                    "message": result.stderr
                })

        else:
            os.chdir(original_dir)
            return json.dumps({
                "status": "error",
                "message": f"Unknown operation: {operation}"
            })

    except Exception as e:
        os.chdir(original_dir)
        return json.dumps({
            "status": "error",
            "operation": operation,
            "message": f"Error performing git operation: {str(e)}"
        })


@tool
def create_github_pr(repo_name: str, branch_name: str, title: str, body: str, base_branch: str = "main") -> str:
    """
    Create a GitHub Pull Request using GitHub MCP.

    Args:
        repo_name: Repository in owner/repo format
        branch_name: Source branch for the PR
        title: PR title
        body: PR description
        base_branch: Target branch (default: main)

    Returns:
        JSON with PR URL or error
    """
    try:
        from github_mcp_client import create_pr_sync

        result = create_pr_sync(
            repo_name=repo_name,
            branch_name=branch_name,
            title=title,
            body=body,
            base_branch=base_branch
        )

        if result["status"] == "success":
            return json.dumps({
                "status": "success",
                "pr_url": result["pr_url"],
                "message": result["message"]
            })
        else:
            return json.dumps({
                "status": "error",
                "message": result["message"]
            })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error creating PR via MCP: {str(e)}"
        })


@tool
def create_github_issue(repo_name: str, title: str, body: str, labels: str = "dependencies") -> str:
    """
    Create a GitHub Issue using GitHub MCP.

    Args:
        repo_name: Repository in owner/repo format
        title: Issue title
        body: Issue description
        labels: Comma-separated labels (default: dependencies)

    Returns:
        JSON with Issue URL or error
    """
    try:
        from github_mcp_client import create_issue_sync

        result = create_issue_sync(
            repo_name=repo_name,
            title=title,
            body=body,
            labels=labels
        )

        if result["status"] == "success":
            return json.dumps({
                "status": "success",
                "issue_url": result["issue_url"],
                "message": result["message"]
            })
        else:
            return json.dumps({
                "status": "error",
                "message": result["message"]
            })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error creating issue via MCP: {str(e)}"
        })


def create_smart_updater_agent():
    """
    Create the smart dependency updater agent with testing and rollback capabilities.
    """
    tools = [
        detect_build_command,
        run_build_test,
        write_dependency_file,
        git_operations,
        create_github_pr,
        create_github_issue,
        apply_all_updates,
        rollback_major_update,
        parse_error_for_dependency,
        categorize_updates,
        get_latest_version_for_major
    ]

    system_message = """You are an intelligent dependency update automation agent with testing and rollback capabilities.

Your mission: Update dependencies safely by testing changes and automatically rolling back breaking updates.

Core Workflow:

1. ANALYZE REPOSITORY
   - Detect package manager and build commands
   - Identify all outdated dependencies
   - Categorize updates: major, minor, patch

2. APPLY ALL UPDATES
   - Update ALL dependencies to their latest versions
   - This includes major version updates
   - Write updated dependency files to disk

3. TEST THE UPDATES
   - Run install command
   - Run build command (if exists)
   - Run test command (if exists)
   - Capture all output

4. HANDLE RESULTS

   IF ALL TESTS PASS:
   - Create git branch
   - Commit changes
   - Push to remote
   - Create Pull Request with comprehensive report
   - Include: what was updated, test results, instructions

   IF TESTS FAIL:
   - Analyze error output to identify problematic dependency
   - Rollback MAJOR updates for that dependency (keep minor/patch)
   - Test again
   - Repeat up to 3 times

   IF STILL FAILING AFTER ROLLBACKS:
   - Create GitHub Issue (not PR)
   - Detail: what was attempted, what failed, error logs
   - Tag with 'dependencies' and 'automated-update-failed'

5. REPORT RESULTS
   - For PR: provide URL and summary of updates
   - For Issue: explain what went wrong and next steps

Key Principles:
- Always try the most aggressive updates first (all latest)
- Use testing to validate changes
- Be surgical with rollbacks (only the breaking package)
- Create PRs for successes, Issues for failures
- Provide detailed, actionable reports

Error Analysis:
When a build/test fails, analyze the error output to identify:
- Which package is mentioned in the error
- What kind of error (compile, runtime, test failure)
- Whether it's likely a breaking change

Rollback Strategy:
- Only rollback MAJOR version updates
- Keep minor and patch updates
- Example: If react 17→18 breaks, rollback to latest 17.x
- Test after each rollback

Output Format:
Always provide clear status updates about:
- What you're testing
- Whether tests passed/failed
- What you're rolling back
- Final outcome (PR URL or Issue URL)"""

    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        temperature=0
    )

    agent_executor = create_agent(llm, tools, system_prompt=system_message)

    return agent_executor


def main():
    """
    Main entry point for testing the smart updater.
    """
    if len(sys.argv) < 2:
        print("Usage: python smart_dependency_updater.py <repo_path>")
        print("\nExample:")
        print("  python smart_dependency_updater.py /tmp/cloned_repo")
        sys.exit(1)

    repo_path = sys.argv[1]

    print("="*80)
    print("🧠 Smart Dependency Updater Agent")
    print("="*80)
    print(f"\n📦 Repository: {repo_path}\n")

    agent = create_smart_updater_agent()

    try:
        result = agent.invoke({
            "messages": [("user", f"Update dependencies for repository at {repo_path}. Test the updates and create a PR if successful, or an Issue if they break the build.")]
        })

        print("\n" + "="*80)
        print("✅ FINAL RESULT")
        print("="*80)
        final_message = result["messages"][-1]
        print(final_message.content)
        print("\n")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
