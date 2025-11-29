# GitHub MCP stdio Mode Fix

## 🐛 The Problem

The GitHub MCP server was failing to connect with the error:
```
Mcp Connection: FAIL
Mcp Tool Call: FAIL
```

Even though all prerequisites were passing:
- ✅ Python Version
- ✅ Docker Installed
- ✅ Docker Running
- ✅ Python Packages
- ✅ GitHub Token
- ✅ Docker Run
- ✅ Docker Image

## 🔍 Root Cause

According to the [official GitHub MCP server documentation](https://github.com/github/github-mcp-server), the server must be run with the `stdio` argument to enable stdio mode for MCP protocol communication.

**Before (Incorrect):**
```python
docker_args = [
    "run", "-i", "--rm",
    "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
    "ghcr.io/github/github-mcp-server"
    # Missing: "stdio" argument!
]
```

**After (Correct):**
```python
docker_args = [
    "run", "-i", "--rm",
    "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={token}",
    "ghcr.io/github/github-mcp-server",
    "stdio"  # ← Required for MCP communication
]
```

## ✅ The Fix

### Changes Made to `github_mcp_client.py`

1. **Added `stdio` argument** to Docker command
2. **Fixed environment variable passing** (now uses `-e VAR=value` format)
3. **Added optional toolsets support** for enabling specific GitHub features

### Updated Constructor

```python
def __init__(self, github_token: Optional[str] = None, toolsets: Optional[str] = None):
    """
    Initialize GitHub MCP client.

    Args:
        github_token: GitHub Personal Access Token (falls back to env var)
        toolsets: Comma-separated list of toolsets to enable
                 (e.g., "repos,issues,pull_requests")
                 Use "all" to enable all toolsets. Defaults to basic toolsets.
    """
```

### Example Usage

**Basic connection:**
```python
async with GitHubMCPClient() as client:
    tools = await client.list_available_tools()
```

**With specific toolsets:**
```python
async with GitHubMCPClient(toolsets="repos,issues,pull_requests") as client:
    result = await client.create_pull_request(...)
```

**With all toolsets:**
```python
async with GitHubMCPClient(toolsets="all") as client:
    # Full access to all GitHub MCP features
```

## 🧪 Testing the Fix

### Option 1: Quick Test
```bash
python quick_test_mcp.py
```

### Option 2: Comprehensive Diagnostics
```bash
python diagnose_github_mcp.py
```

### Option 3: stdio Mode Verification
```bash
python test_mcp_stdio.py
```

This new test script specifically verifies:
1. Docker stdio communication works manually
2. MCP client properly initializes with stdio mode
3. Tools can be listed and called successfully

## 📋 Available Toolsets

According to the GitHub MCP server documentation, you can enable these toolset groups:

| Toolset | Description |
|---------|-------------|
| `repos` | Repository operations (get files, search code, etc.) |
| `issues` | Issue management (create, read, update) |
| `pull_requests` | Pull request operations |
| `actions` | GitHub Actions workflow monitoring |
| `code_security` | Security vulnerability scanning |
| `all` | Enable all available toolsets |

**Example with toolsets:**
```python
from github_mcp_client import GitHubMCPClient

async with GitHubMCPClient(
    toolsets="repos,issues,pull_requests,actions"
) as client:
    tools = await client.list_available_tools()
    print(f"Available tools: {len(tools)}")
```

## 🔧 Troubleshooting

### If connection still fails after the fix:

1. **Verify stdio mode is being used:**
   ```bash
   python test_mcp_stdio.py
   ```

2. **Check Docker command manually:**
   ```bash
   docker run -i --rm \
     -e GITHUB_PERSONAL_ACCESS_TOKEN='your_token' \
     ghcr.io/github/github-mcp-server \
     stdio
   ```

   This should wait for input (not exit immediately).

3. **Verify token has correct permissions:**
   - Required scopes: `repo`, `workflow`
   - Check at: https://github.com/settings/tokens

4. **Check Docker logs:**
   ```bash
   docker logs $(docker ps -a | grep github-mcp-server | awk '{print $1}' | head -1)
   ```

5. **Test with verbose output:**
   Add debug logging to `github_mcp_client.py`:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

## 📚 References

- **GitHub MCP Server Repository:** https://github.com/github/github-mcp-server
- **MCP Protocol Specification:** https://modelcontextprotocol.io/
- **GitHub API Documentation:** https://docs.github.com/en/rest

## 🔐 Security Notes

When using toolsets and tokens:

1. **Use minimal required scopes** - Only enable toolsets you need
2. **Rotate tokens regularly** - Create new tokens periodically
3. **Never commit tokens** - Always use environment variables
4. **Review token usage** - Check GitHub settings for active tokens
5. **Use fine-grained tokens** - Consider fine-grained PATs for better security

## ✨ What Changed

### Before
```python
# ❌ Missing stdio mode
StdioServerParameters(
    command="docker",
    args=["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", ...]
)
```

### After
```python
# ✅ Correct stdio mode
StdioServerParameters(
    command="docker",
    args=["run", "-i", "--rm",
          "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={token}",
          "ghcr.io/github/github-mcp-server",
          "stdio"]  # ← This was missing!
)
```

## 🎯 Expected Results After Fix

Running `diagnose_github_mcp.py` should now show:

```
Test Results Summary
======================================================================
Python Version: PASS
Docker Installed: PASS
Docker Running: PASS
Python Packages: PASS
Github Token: PASS
Docker Run: PASS
Docker Image: PASS
Mcp Connection: PASS  ← Now passing!
Mcp Tool Call: PASS   ← Now passing!

Overall: 9/9 tests passed

✅ All Tests Passed!
✅ GitHub MCP integration is working correctly!
```

---

**Issue resolved by:** Adding `stdio` argument to Docker command as specified in the official GitHub MCP server documentation.
