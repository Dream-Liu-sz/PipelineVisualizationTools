# Pipeline Visualization Tools

A PyQt5-based desktop application for visualizing Qualcomm Camera Pipeline configurations from XML and JSON files.

## Features

- **Dual Format Support**: Parse both XML (legacy) and JSON (NCF) pipeline configuration files
- **Interactive Visualization**: Render pipeline nodes and port connections with color-coded display
- **Tree Navigation**: Hierarchical UseCase/Pipeline navigation panel
- **Node Properties**: Hover-based tooltip display of detailed node properties
- **Canvas Navigation**: Pan and scroll for exploring large pipeline topologies
- **Auto Layout**: Hierarchical graph layout algorithm minimizes connection crossings

## Quick Start

### Using Pre-built Executable

```
1. Run: dist/pipelineVisualization.exe
2. Press Ctrl+O to open XML files, or Ctrl+Alt+O for JSON files
3. Double-click a pipeline in the tree to visualize
```

### Development Setup

```powershell
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install PyQt5 json5

# Run application
python main.py
```

### Building Executable

```powershell
pip install pyinstaller
pyinstaller main.spec
```

Output: `dist/pipelineVisualization.exe`

## Usage

| Action | Shortcut | Description |
|--------|----------|-------------|
| Open XML | `Ctrl+O` | Load XML pipeline configuration |
| Open JSON | `Ctrl+Alt+O` | Load JSON pipeline configuration(s) |
| Pan Canvas | Mouse drag | Drag to pan the visualization |
| Vertical Scroll | Scroll wheel | Pan canvas vertically |
| Horizontal Scroll | Shift + Scroll | Pan canvas horizontally |
| View Properties | Hover on node | Display node property tooltip |

## Project Structure

```
Pipeline-visualization-tools/
├── main.py                 # Application entry point
├── MainWindow.py           # Main window (controller + view)
├── CanvasWidget.py         # Drawing canvas
├── NodePainter.py          # Node renderer
├── Pipeline.py             # Pipeline model + layout algorithm
├── Node.py                 # Node data model
├── Port.py                 # Port data model
├── UseCase.py              # XML/JSON parser
├── DrawLine.py             # Connection line drawing
├── Link.py                 # Link data structure
├── Utils.py                # Logging and utilities
├── resource.py             # Compiled Qt resources
├── docs/                   # Project documentation
│   ├── README.md           # Documentation hub
│   ├── project/            # Core project documents
│   ├── reference/          # Reference materials
│   └── tasks/              # Task management
├── example/                # Sample pipeline files
├── res/                    # Application assets
├── build/                  # PyInstaller build output
└── dist/                   # Distribution executables
```

## Documentation

Complete project documentation is available in the [docs/](docs/) directory:

| Document | Path | Description |
|----------|------|-------------|
| Requirements | [docs/project/requirements.md](docs/project/requirements.md) | Functional and non-functional requirements |
| Architecture | [docs/project/architecture.md](docs/project/architecture.md) | System architecture and design |
| Tech Stack | [docs/project/tech_stack.md](docs/project/tech_stack.md) | Technologies and dependencies |
| API Spec | [docs/project/api_spec.md](docs/project/api_spec.md) | File format specifications |
| Data Schema | [docs/project/data_schema.md](docs/project/data_schema.md) | Data models and structures |
| Design Guide | [docs/project/design_guidelines.md](docs/project/design_guidelines.md) | UI/UX design patterns |
| Runbook | [docs/project/runbook.md](docs/project/runbook.md) | Installation and operations |

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.9+ |
| GUI Framework | PyQt5 |
| JSON Parser | json5 |
| XML Parser | xml.etree.ElementTree |
| Packaging | PyInstaller |

## Version Information

| Field | Value |
|-------|-------|
| Version | V3.0 |
| Last Updated | 2026-05-20 |
| Author | Jianlin |
| Contact | a185531353@qq.com |

## License

Proprietary - internal tool.
