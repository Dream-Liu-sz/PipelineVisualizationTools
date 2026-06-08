# Runbook - Pipeline Visualization Tools

<!-- SCOPE: Operations and Deployment Document -->
<!-- OWNER: Engineering -->

## Overview

This document provides installation, configuration, troubleshooting, and operational guidance for the Pipeline Visualization Tools application.

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Operating System | Windows 10+ | 64-bit recommended |
| Python | 3.9+ | Required for development mode |
| RAM | 2 GB+ | For loading large pipeline files |
| Disk Space | 500 MB+ | Including Python environment and dependencies |

## Installation

### Option 1: Using Pre-built Executable

1. Obtain `pipelineVisualization.exe` from `dist/` directory
2. Double-click to run
3. No additional installation required

### Option 2: Development Setup

```powershell
# Step 1: Navigate to project directory
cd Pipeline-visualization-tools

# Step 2: Create virtual environment
python -m venv venv

# Step 3: Activate virtual environment
venv\Scripts\activate

# Step 4: Install dependencies
pip install PyQt5 json5

# Step 5: Run the application
python main.py
```

### Option 3: Build from Source

```powershell
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller main.spec

# Output will be in dist/pipelineVisualization.exe
```

## Configuration

### File Paths

The application uses hardcoded default paths for file dialogs:

| File Type | Default Path | Location in Code |
|-----------|--------------|------------------|
| XML files | `D:\workspace\tools\PipelineTools` | `MainWindow.py:triggerOpenFile()` |
| JSON files | `Y:\workspace\code\aero_vendor_do\vendor\noth\hardware\camera\src\extened\config\aero\pipelinedescription` | `MainWindow.py:triggerOpenFiles()` |

**Note**: Update these paths in the source code to match your environment.

### Log Level

Adjust the log level in `Utils.py`:

| Level | Value | Output |
|-------|-------|--------|
| ERROR | 0 | Error messages only |
| INFO | 1 | Error + Info messages |
| DEBUG | 2 | Error + Info + Debug messages |
| VERBOSE | 3 | All messages (default) |

```python
# In Utils.py
gLogLevel = 3  # Change to 0-3 as needed
```

## Usage Guide

### Loading XML Pipeline Files

1. Press `Ctrl+O` or click File > "open xml file"
2. Navigate to your XML pipeline file (e.g., `g_xxx_usecase.xml`)
3. Select the file and click Open
4. Pipeline structure appears in the left tree panel
5. Double-click a pipeline name to visualize

### Loading JSON Pipeline Files

1. Press `Ctrl+Alt+O` or click File > "open json file"
2. Navigate to your JSON pipeline files
3. Select one or more files and click Open
4. Pipeline structure appears in the left tree panel
5. Double-click a pipeline name to visualize

### Navigating the Visualization

| Action | Method |
|--------|--------|
| Pan vertically | Mouse scroll wheel |
| Pan horizontally | Shift + Mouse scroll wheel |
| Pan freely | Left-click and drag on canvas |
| View node properties | Hover mouse over a node |

### Viewing Node Properties

1. Hover your mouse over any node in the visualization
2. After a brief delay (800ms), a tooltip will appear showing:
   - NodePropertyName
   - NodePropertyId
   - NodePropertyDataType
   - NodePropertyValue

## Troubleshooting

### Issue: No visualization after loading file

**Possible causes and solutions:**

| Cause | Solution |
|-------|----------|
| File format incorrect | Ensure file is valid XML or JSON pipeline format |
| Missing compiled XML | Use the compiled XML file (e.g., `g_xxx_usecase.xml`) instead of source |
| Path not set correctly | Update default path in `MainWindow.py` |

### Issue: Application crashes on startup

**Possible causes and solutions:**

| Cause | Solution |
|-------|----------|
| PyQt5 not installed | Run `pip install PyQt5` |
| Python version incompatible | Use Python 3.9+ |
| Missing resource file | Ensure `resource.py` is compiled from `resource.qrc` |

### Issue: Node position errors

**Symptom**: Error message about node position being None

**Solution**: This indicates a data parsing issue. Check the pipeline file for completeness.

### Issue: Port names overlap with node name

**Solution**: The application automatically prunes (shortens) port names when overlap is detected. If pruning is insufficient, consider adjusting font size.

## Environment Variables

No environment variables are currently required or used by the application.

## Build Output

| File/Directory | Description |
|----------------|-------------|
| `build/` | PyInstaller intermediate build files |
| `dist/pipelineVisualization.exe` | Final standalone executable |
| `dist/pipelineVisualization.txt` | Build log/output listing |
| `dist/pipelineVisualization.7z` | Compressed distribution archive |

## Maintenance Schedule

| Task | Frequency | Description |
|------|-----------|-------------|
| Dependency updates | Quarterly | Check for PyQt5, json5 updates |
| Default path review | As needed | Update file dialog paths for new projects |
| Icon/asset updates | As needed | Update `res/logo.ico` if branding changes |

## Contact

| Role | Contact |
|------|---------|
| Author | Jianlin |
| Email | a185531353@qq.com |
| Version | V2.0 |
| Last Updated | 2024-03-28 |

## Maintenance

- Update when installation procedures change
- Update when new configuration options are added
- Review when new troubleshooting scenarios are identified

<!-- Metadata: Generated 2026-05-19 | Version 1.0.0 -->
