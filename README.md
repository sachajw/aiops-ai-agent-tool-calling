# AI Agent Tool Calling - Dependency Update System

A multi-agent Python system that uses LangChain's tool calling pattern to analyze repositories, identify outdated dependencies, and prepare comprehensive dependency update reports with testing strategies.

## 🌟 Features

- **Multi-Agent Architecture**: Orchestrator pattern with specialized sub-agents
- **AI-Powered Analysis**: Uses LangChain agents with Claude for intelligent dependency analysis
- **Multi-Language Support**: Detects and checks dependencies for:
  - JavaScript/Node.js (npm, yarn, pnpm)
  - Python (pip, pipenv, poetry)
  - Rust (cargo)
  - Ruby (bundler)
  - Java (Maven, Gradle)
  - PHP (Composer)
  - Go (go modules)
- **Automatic Detection**: Identifies which package managers are used
- **Testing Strategies**: Provides specific test commands for each package manager
- **PR-Ready Output**: Generates comprehensive pull request descriptions

## 🏗️ Architecture

This project implements a multi-agent system following the [LangChain Tool Calling](https://blog.langchain.com/tool-calling-with-langchain/) pattern:

### Agent Hierarchy

```
dependency_update_agent.py (Orchestrator)
├── dependency_analyzer.py (Worker Agent)
│   └── Tools: clone, detect, check outdated
└── dependency_updater.py (Worker Agent)
    └── Tools: update files, generate PR descriptions
```

### 1. **Dependency Update Agent** (Orchestrator)

Main coordinator that manages the overall workflow:
- Receives repository URL or name
- Delegates analysis to the analyzer agent
- Delegates updates to the updater agent
- Generates final PR descriptions and reports

**Tools:**
- `run_dependency_analyzer` - Invokes the analyzer sub-agent
- `run_dependency_updater` - Invokes the updater sub-agent
- `create_github_pr_description` - Formats PR descriptions
- `format_testing_commands` - Generates testing instructions

### 2. **Dependency Analyzer Agent** (Worker)

Specialized in finding outdated dependencies:
- Clones repositories
- Detects package managers
- Identifies outdated packages
- Returns structured analysis reports

**Tools:**
- `clone_repository` - Clones git repos to temp directories
- `detect_package_manager` - Identifies package managers and config files
- `read_dependency_file` - Reads dependency configuration files
- `check_npm_outdated` - Checks outdated npm packages
- `check_pip_outdated` - Checks outdated Python packages
- `cleanup_repository` - Removes temporary files

### 3. **Dependency Updater Agent** (Worker)

Specialized in updating dependency files:
- Reads current dependency files
- Updates version numbers
- Preserves file formatting
- Determines testing strategies
- Generates PR descriptions

**Tools:**
- `read_file_content` - Reads file contents
- `update_package_json` - Updates npm package.json files
- `update_requirements_txt` - Updates Python requirements.txt files
- `determine_testing_strategy` - Identifies appropriate test commands
- `generate_pr_description` - Creates detailed PR descriptions

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Git
- Node.js and npm (for checking npm packages)
- pip (for checking Python packages)
- Other package managers as needed (cargo, go, etc.)

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

Or create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
# Edit .env and add your API key
```

## 🚀 Usage

### Main Orchestrator Agent (Recommended)

Run the main orchestrator which coordinates all sub-agents:

```bash
python dependency_update_agent.py <repository>
```

**Examples:**

```bash
# Using full URL
python dependency_update_agent.py https://github.com/expressjs/express

# Using owner/repo format
python dependency_update_agent.py expressjs/express
```

### Individual Agent Usage

You can also run sub-agents independently for specific tasks:

#### Dependency Analyzer Only

```bash
python dependency_analyzer.py https://github.com/owner/repo
```

#### Dependency Updater Only

```bash
python dependency_updater.py npm '[{"name":"express","current":"4.17.1","latest":"4.18.2"}]'
```

## 📊 Sample Output

### Orchestrator Agent Output

```
================================================================================
🤖 Dependency Update Agent
================================================================================

📦 Repository: expressjs/express
🔗 URL: https://github.com/expressjs/express

📊 Running dependency analyzer on https://github.com/expressjs/express...

> Entering new AgentExecutor chain...
Cloning repository...
Repository cloned successfully

Detecting package managers...
Found: npm (package.json)

Checking outdated packages...
Found 8 outdated npm packages

================================================================================
✅ FINAL REPORT
================================================================================

# 🔄 Dependency Updates for expressjs/express

## 📦 Updated Dependencies

### ⚠️ Major Updates
- 🔴 **body-parser**: `1.19.0` → `2.0.0` (MAJOR - may have breaking changes)

### Minor Updates
- 🟡 **cookie**: `0.4.1` → `0.5.0` (minor)
- 🟡 **debug**: `2.6.9` → `2.7.0` (minor)

### Patch Updates
- 🟢 **accepts**: `1.3.7` → `1.3.8` (patch)
- 🟢 **etag**: `1.8.1` → `1.8.2` (patch)

## 🧪 Testing Instructions

Please run the following commands to verify the updates:

```bash
# Install dependencies
npm install

# Run tests
npm test

# Run build
npm run build

# Check for issues
npm run lint
```

## ⚠️ Important Notes

- ⚠️ This PR includes **MAJOR version updates**
- Review changelogs for breaking changes
- Run the full test suite before merging
- Check for deprecation warnings
- Verify build succeeds
- Review any peer dependency warnings

---

📊 Total dependencies updated: 8
🤖 This PR was generated by the Dependency Update Agent
```

## 🔄 Workflow

The orchestrator agent follows this workflow:

1. **Analyze Dependencies**
   - Clone the repository
   - Detect package managers
   - Identify outdated dependencies
   - Generate analysis report

2. **Update Dependency Files**
   - Read current dependency files
   - Update version numbers
   - Preserve file formatting
   - Determine testing strategy

3. **Create PR Description**
   - Categorize updates (major/minor/patch)
   - Add testing instructions
   - Include warnings for breaking changes
   - Provide checklist

4. **Report Results**
   - Summary of updates
   - PR description ready to use
   - Next steps for the user

## 🛠️ Extending the System

### Adding New Package Manager Support

1. **Update `dependency_analyzer.py`:**

Add detection in `detect_package_manager` tool:
```python
if os.path.exists(os.path.join(repo_path, "your-config-file")):
    package_managers["your-pm"] = {
        "files": ["your-config-file"],
        "lock_files": []
    }
```

Create a checking tool:
```python
@tool
def check_yourpm_outdated(repo_path: str) -> str:
    """Check for outdated packages in your package manager."""
    # Implementation here
    pass
```

2. **Update `dependency_updater.py`:**

Add update logic:
```python
@tool
def update_yourpm_file(current_content: str, updates: str) -> str:
    """Update your package manager config file."""
    # Implementation here
    pass
```

Add testing strategy:
```python
# In determine_testing_strategy tool
strategies["your-pm"] = {
    "install": "your-pm install",
    "build": "your-pm build",
    "test": "your-pm test"
}
```

## 🔍 Agent Communication Flow

```
User Input (repo URL)
    ↓
Orchestrator Agent
    ↓
    ├─→ Dependency Analyzer Agent
    │   ├─→ clone_repository
    │   ├─→ detect_package_manager
    │   ├─→ check_npm_outdated
    │   └─→ cleanup_repository
    │   ↓
    │   Returns: Analysis Report
    ↓
Orchestrator receives analysis
    ↓
    ├─→ Dependency Updater Agent
    │   ├─→ read_file_content
    │   ├─→ update_package_json
    │   ├─→ determine_testing_strategy
    │   └─→ generate_pr_description
    │   ↓
    │   Returns: Updated Files + Testing Strategy
    ↓
Orchestrator generates final PR description
    ↓
Returns to User: Complete Update Report
```

## 🔧 Using Different LLM Providers

The system currently uses Anthropic's Claude, but you can switch to OpenAI:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
```

Update all three agent files and set your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## ⚠️ Limitations

- Some package managers require additional tools (e.g., `cargo-outdated` for Rust)
- Large repositories may take time to clone and analyze
- Some checks require the package manager to be installed locally
- Network connectivity required for cloning and checking updates
- The agents generate PR descriptions but don't create actual GitHub PRs (you need to do that manually)

## 📝 Example Scenarios

### Scenario 1: Check a Node.js Project

```bash
python dependency_update_agent.py facebook/react
```

### Scenario 2: Check a Python Project

```bash
python dependency_update_agent.py https://github.com/pallets/flask
```

### Scenario 3: Analyze Only (No Updates)

```bash
python dependency_analyzer.py https://github.com/rust-lang/cargo
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Add more package manager support
- Implement actual GitHub PR creation
- Add support for monorepos
- Improve version parsing and semver handling
- Add caching for faster repeated analyses
- Create a web interface

Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 📚 References

- [LangChain Tool Calling Blog Post](https://blog.langchain.com/tool-calling-with-langchain/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Multi-Agent Systems](https://python.langchain.com/docs/use_cases/multi_agent/)

## 🆘 Troubleshooting

### "Module not found" errors

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### API Key errors

Ensure your Anthropic API key is set:
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

### npm/pip not found

Install the required package managers:
- npm: Install Node.js from https://nodejs.org/
- pip: Included with Python 3

### Repository cloning fails

- Check your internet connection
- Ensure you have git installed
- Verify the repository URL is correct and public

---

**Built with ❤️ using LangChain and Claude**
