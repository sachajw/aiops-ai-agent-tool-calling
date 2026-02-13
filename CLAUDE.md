# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-agent AI system for automated dependency management. Uses LangChain tool calling with Claude AI to analyze repositories, update dependencies, run tests, and create PRs (success) or Issues (failure).

## Common Commands

```bash
# Install dependencies
pip install -e .

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_dependency_analyzer.py -v

# CLI entry points (after install)
dep-updater owner/repo      # Run dependency updater
dep-server                  # Start API server (port 8000)
dep-diagnose                # Run diagnostic tools

# Docker deployment
docker-compose up -d
```

## Architecture

Three-tier agent hierarchy:

```
Orchestrator Agent (src/agents/orchestrator.py)
├── Analyzer Agent (src/agents/analyzer.py)
│   └── Tools: clone, detect, check outdated
└── Updater Agent (src/agents/updater.py)
    └── Tools: detect build, test, write files, git ops, create PR/Issue
```

### Key Directories

- `src/agents/` - Core AI agents (orchestrator, analyzer, updater)
- `src/tools/` - Dependency operation tools
- `src/integrations/` - GitHub MCP client and server management
- `src/api/` - FastAPI REST API with background job processing
- `src/config/` - Language/package manager configurations
- `tests/` - Test suite

### Critical Patterns

- **GitHub MCP Integration**: All Git operations go through the MCP server running in Docker (`ghcr.io/github/github-mcp-server`). See `GITHUB_MCP_SETUP.md` for setup.
- **Caching**: Repository clones and analysis cached in `~/.cache/ai-dependency-updater/` (24h TTL)
- **Model**: Uses `claude-sonnet-4-5-20250929` with temperature 0
- **Language Support**: 11+ languages configured in `src/config/language_map.py`

### Environment Variables

Required in `.env`:
- `ANTHROPIC_API_KEY` - Claude API key
- `GITHUB_PERSONAL_ACCESS_TOKEN` - GitHub token with `repo` and `workflow` scopes
