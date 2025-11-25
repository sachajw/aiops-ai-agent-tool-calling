# AI Agent Tool Calling - Outdated Repository Finder

A Python script that uses LangChain's tool calling pattern to analyze repositories and find outdated dependencies across multiple package managers.

## Features

- **AI-Powered Analysis**: Uses LangChain agents with Claude to intelligently analyze repositories
- **Multi-Language Support**: Detects and checks dependencies for:
  - JavaScript/Node.js (npm)
  - Python (pip, pipenv, poetry)
  - Rust (cargo)
  - Ruby (bundler)
  - Java (Maven, Gradle)
  - PHP (Composer)
  - Go (go modules)
- **Automatic Detection**: Identifies which package managers are used in the repository
- **Tool Calling Pattern**: Implements LangChain's tool calling approach for modular, extensible functionality

## Architecture

This project follows the [LangChain Tool Calling](https://blog.langchain.com/tool-calling-with-langchain/) pattern:

1. **Tools Definition**: Each capability (clone repo, detect package managers, check outdated packages) is defined as a `@tool` decorated function
2. **Agent Creation**: A LangChain agent is created with access to these tools
3. **LLM Orchestration**: Claude (via Anthropic API) decides which tools to use and in what order
4. **Execution**: The agent executor runs the tools and aggregates results

### Available Tools

- `clone_repository`: Clones a git repository to a temporary directory
- `detect_package_managers`: Identifies which package managers are used
- `check_npm_outdated`: Checks for outdated npm packages
- `check_pip_outdated`: Checks for outdated pip packages
- `check_cargo_outdated`: Checks for outdated Rust packages
- `cleanup_repository`: Removes the cloned repository

## Installation

### Prerequisites

- Python 3.8 or higher
- Git
- Node.js and npm (for checking npm packages)
- pip (for checking Python packages)
- cargo (optional, for checking Rust packages)

### Setup

1. Clone this repository:
```bash
git clone https://github.com/codeWithUtkarsh/AiAgentToolCalling.git
cd AiAgentToolCalling
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Anthropic API key:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Alternatively, create a `.env` file:
```
ANTHROPIC_API_KEY=your-api-key-here
```

## Usage

### Basic Usage

Run the script with a repository URL:

```bash
python outdated_repo_finder.py <repository_url>
```

### Examples

Check a JavaScript/Node.js repository:
```bash
python outdated_repo_finder.py https://github.com/expressjs/express
```

Check a Python repository:
```bash
python outdated_repo_finder.py https://github.com/pallets/flask
```

Check a Rust repository:
```bash
python outdated_repo_finder.py https://github.com/rust-lang/cargo
```

### Sample Output

```
🔍 Analyzing repository: https://github.com/user/repo

> Entering new AgentExecutor chain...
Cloning repository...
Repository cloned successfully to: /tmp/repo_check_abc123

Detecting package managers...
{
  "npm": "package.json",
  "pip": "requirements.txt"
}

Checking npm packages...
Found 5 outdated npm packages:

- express: 4.17.1 → 4.18.2
- lodash: 4.17.19 → 4.17.21
- axios: 0.21.1 → 1.6.0

Checking pip packages...
All pip packages are up to date!

Cleaning up...
Successfully cleaned up repository at /tmp/repo_check_abc123

================================================================================
FINAL REPORT
================================================================================
Analysis complete! Found outdated dependencies in npm (5 packages).
All Python packages are up to date.
```

## How It Works

1. **Input**: You provide a repository URL
2. **Cloning**: The agent clones the repository to a temporary directory
3. **Detection**: It scans for package manager configuration files (package.json, requirements.txt, etc.)
4. **Analysis**: For each detected package manager, it runs the appropriate outdated check
5. **Reporting**: Results are aggregated and presented
6. **Cleanup**: The temporary repository is removed

## Extending the Script

To add support for more package managers:

1. Add a detection rule in `detect_package_managers`:
```python
if os.path.exists(os.path.join(repo_path, "your-config-file")):
    package_managers["your-pm"] = "your-config-file"
```

2. Create a new tool:
```python
@tool
def check_yourpm_outdated(repo_path: str) -> str:
    """Check for outdated packages in your package manager."""
    # Implementation here
    pass
```

3. Add the tool to the tools list in `create_outdated_finder_agent()`

## Using Different LLM Providers

The script currently uses Anthropic's Claude, but you can switch to OpenAI:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
```

Don't forget to set your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Limitations

- Some package managers require additional tools (e.g., `cargo-outdated` for Rust)
- Large repositories may take time to clone
- Some checks require the package manager to be installed locally
- Network connectivity required for cloning and checking updates

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## References

- [LangChain Tool Calling Blog Post](https://blog.langchain.com/tool-calling-with-langchain/)
- [LangChain Documentation](https://python.langchain.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
