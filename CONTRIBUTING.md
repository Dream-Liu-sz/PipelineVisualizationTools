# Contributing to Pipeline Visualization Tools

Thank you for your interest in contributing! This document explains how to set up a development environment, propose changes, and submit a pull request.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Submitting Pull Requests](#submitting-pull-requests)
- [Coding Style](#coding-style)
- [Commit Messages](#commit-messages)

## Code of Conduct

This project follows the principles of open, respectful collaboration. Be kind, assume good intent, and focus on the work. Harassment or abusive behavior will not be tolerated.

## Getting Started

### Prerequisites

- **Python**: 3.9 or newer
- **OS**: Windows 10/11, macOS, or Linux (the app is built and shipped as a Windows executable, but the Python source runs cross-platform wherever PyQt5 is available)
- **Git**

### Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/Dream-Liu-sz/PipelineVisualizationTools.git
cd PipelineVisualizationTools

# 2. Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install runtime dependencies
pip install -r requirements.txt

# 4. (Optional) Install PyInstaller for building the executable
pip install pyinstaller

# 5. Run the application
python main.py
```

### Project Layout

| Module | Responsibility |
|--------|----------------|
| `main.py` | Application entry point |
| `MainWindow.py` | Main window and UI orchestration |
| `PipelineEditor.py` | JSON edit controller, command stack, save logic |
| `CanvasWidget.py` | Drawing canvas, hit testing, selection rendering |
| `NodePainter.py` | Node renderer |
| `Pipeline.py` | Pipeline model and hierarchical layout |
| `Node.py` / `Port.py` / `Link.py` | Data models |
| `UseCase.py` | XML / JSON parsers |
| `DrawLine.py` / `BezierLine.py` | Connection line drawing |
| `Utils.py` | Logging and shared utilities |
| `ui_theme.py` | Shared dark UI theme |
| `resource.py` | Compiled Qt resources |

The `example/` directory contains sample XML and JSON pipeline files you can use to verify your changes visually.

## Reporting Bugs

Before opening a bug report, please search existing issues to avoid duplicates.

When filing a bug, include:

1. **Summary** — a clear, one-sentence description.
2. **Steps to reproduce** — minimal steps that reliably trigger the bug.
3. **Expected vs. actual behavior**.
4. **Environment** — OS, Python version, PyQt5 version, app version.
5. **Logs / screenshots** — attach the application log and a screenshot if applicable.
6. **Sample file** — if the bug only reproduces with a specific XML/JSON pipeline, attach a redacted sample.

## Suggesting Features

Open an issue with the `enhancement` label and describe:

- The problem you are trying to solve.
- Your proposed solution and any alternatives you considered.
- Whether you are willing to submit a pull request.

## Submitting Pull Requests

1. **Branch** — create a topic branch from `main`:
   ```bash
   git checkout -b feat/short-description
   ```
2. **Keep changes focused** — one logical change per pull request. Large refactors should be discussed in an issue first.
3. **Verify locally** before pushing:
   - The app launches without errors: `python main.py`
   - You can open a sample file from `example/` and the affected flow still works.
   - No new Python warnings are emitted on startup.
4. **Write a clear PR description**:
   - What changed and why.
   - How you tested it (commands run, screenshots).
   - Link the related issue with `Closes #123` or `Refs #123`.
5. **Be responsive** to review feedback.

## Coding Style

- **PEP 8** with a maximum line length of **120** characters.
- **Type hints** are encouraged for new public functions and methods.
- **Docstrings** in the Google or NumPy style for non-trivial functions.
- **Naming**:
  - Classes: `PascalCase`
  - Functions / variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
- **Qt UI code** lives in the same module as the orchestration code in this repo (no separate `.ui` files) — keep this convention when adding new widgets.
- **Logging** — use the project logger from `Utils.py` rather than `print()` for non-interactive output.
- **No new top-level dependencies** without prior discussion. Update `requirements.txt` if you must add one.

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) style:

```
<type>(<scope>): <short summary>

<body explaining the why, not the what>

<footer with issue refs>
```

Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `build`, `ci`.

Examples:

```
feat(editor): support multi-select node deletion
fix(canvas): prevent crash when link references missing port
docs(readme): clarify Ctrl+Alt+O shortcut for JSON files
```

## Release Process

Maintainers will:

1. Update the version in `README.md` ("Version Information" table).
2. Add a new entry at the top of `CHANGELOG.md`.
3. Cut a Git tag matching the version (e.g. `v3.2.0`).
4. Attach a Windows build artifact to the GitHub Release.

## Questions?

Open an issue with the `question` label — there are no stupid questions.

Thank you for helping improve Pipeline Visualization Tools.
