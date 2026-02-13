# Dependency Management Tools Comparison

A comparison between our AI Dependency Updater and Renovate for keeping software dependencies up-to-date.

---

## The Problem We're Solving

Software is built from many pre-made components that get regular updates - security fixes, new features, and performance improvements. Someone needs to:

1. Check for available updates
2. Install them
3. Make sure nothing breaks

Both tools automate this process, but with very different approaches.

---

## At a Glance

|                      | **AI Dependency Updater**    | **Renovate**                                         |
| -------------------- | ---------------------------- | ---------------------------------------------------- |
| **Type**             | AI-powered experimental tool | Industry-standard automation                         |
| **Maintainer**       | Internal/Custom              | Mend.io (Open Source)                                |
| **Maturity**         | New/Experimental             | Mature, battle-tested                                |
| **Language Support** | ~11 languages                | 120+ package managers                                |
| **Platform Support** | GitHub only                  | GitHub, GitLab, Bitbucket, Azure DevOps, Gitea, more |

---

## How They Work

### Renovate: The Diligent Assistant

Think of Renovate like a **highly organized personal assistant** who:

- **Knows every catalog** - Works with 120+ different package sources
- **Follows your rules** - You configure what to update, when, and how
- **Prepares detailed paperwork** - Every update comes with a Pull Request containing:
  - What changed
  - Security notes
  - Confidence levels and adoption rates
- **Works on a schedule** - Configure "only update on Tuesdays" or "max 2 updates per hour"
- **Provides a dashboard** - See all pending updates in one place

**Limitation:** It follows rules blindly. If an update breaks something, it reports the failure but doesn't understand _why_.

### AI Dependency Updater: The Smart Problem-Solver

Think of this tool like a **consultant who diagnoses and fixes problems**:

1. **Updates everything** - Installs all available updates at once
2. **Tests the result** - Runs your build and test suite
3. **Investigates failures** - Uses AI to analyze error messages and identify the culprit
4. **Makes smart rollbacks** - "The new door broke the lock, but the windows are fine. Keep the windows, revert the door."
5. **Iterates** - Repeats until it finds a working combination

**Limitation:** Newer tool, smaller scope (GitHub only, fewer languages), AI decisions can be unpredictable.

---

## Feature Comparison

| Feature                           | AI Dependency Updater |     Renovate     |
| --------------------------------- | :-------------------: | :--------------: |
| AI-powered error analysis         |          ✅           |        ❌        |
| Smart partial rollbacks           |          ✅           |        ❌        |
| Language/package manager coverage |          ~11          |       120+       |
| Git platform coverage             |        GitHub         |   8+ platforms   |
| Vulnerability alerts              |          ❌           |        ✅        |
| Onboarding/configuration help     |          ❌           |        ✅        |
| Dependency dashboard              |          ❌           |        ✅        |
| Scheduled updates                 |          ❌           |        ✅        |
| Automerge with confidence data    |          ❌           |        ✅        |
| Grouping related updates          |          ❌           |        ✅        |
| REST API                          |          ✅           | ❌ (has webhook) |

---

## Technical Summary

| Aspect         | AI Dependency Updater        | Renovate                                      |
| -------------- | ---------------------------- | --------------------------------------------- |
| **Tech Stack** | Python, LangChain, Claude AI | TypeScript, Node.js                           |
| **License**    | Proprietary/Internal         | AGPL-3.0 (Open Source)                        |
| **Deployment** | CLI, FastAPI server, Docker  | Docker, npm CLI, GitHub Action, GitLab Runner |
| **Model**      | claude-sonnet-4-5            | N/A (rule-based)                              |

---

## When to Use Each

### Choose Renovate if you need:

- Maximum reliability and proven track record
- Support for many languages and platforms
- Fine-grained control over update schedules and policies
- Security vulnerability alerting
- Enterprise support options
- Industry-standard tooling your team already knows

### Choose AI Dependency Updater if you need:

- AI to handle the decision-making when things break
- Automatic identification of problematic updates from test failures
- A Python-based system you can customize
- Smart rollbacks that keep safe updates while reverting breaking ones

---

## The Bottom Line

|                  | **Renovate**                              | **AI Dependency Updater**              |
| ---------------- | ----------------------------------------- | -------------------------------------- |
| **Best analogy** | Experienced assistant who needs direction | Clever intern who figures things out   |
| **Philosophy**   | Predictable, controllable, comprehensive  | Experimental, intelligent, adaptive    |
| **Risk profile** | Conservative - you control everything     | Experimental - AI makes judgment calls |

---

## Questions?

For more details on each tool:

- **AI Dependency Updater**: See `CLAUDE.md` and `README.md` in this repository
- **Renovate**: See [docs.renovatebot.com](https://docs.renovatebot.com)
