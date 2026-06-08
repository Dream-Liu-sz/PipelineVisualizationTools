# Pipeline Visualization Tools

A PyQt5-based desktop application for visualizing and editing Qualcomm Camera Pipeline configurations from XML and JSON files.

## Features

- **Dual Format Support**: Parse both XML legacy files and JSON NCF pipeline configuration files.
- **Interactive Visualization**: Render pipeline nodes and port connections with color-coded display.
- **Tree Navigation**: Browse use cases and pipelines from the left explorer panel.
- **Node Properties**: Hover on nodes to inspect node properties.
- **Canvas Navigation**: Pan, scroll, zoom, center, reset, and snapshot large pipeline topologies.
- **Auto Layout**: Use hierarchical graph layout to organize pipeline topology.
- **JSON Edit Mode**: Edit JSON pipeline topology with node add/delete, link add/delete, node field editing, Undo/Redo, and save-back support.
- **View-Only XML Mode**: XML pipelines remain read-only for safe inspection.

## Quick Start

### Using Pre-built Executable

```text
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
| Open JSON | `Ctrl+Alt+O` | Load one or more JSON pipeline configurations |
| Enter Edit Mode | Edit button | Available after opening JSON and rendering a pipeline |
| Pan Canvas | Mouse drag | Drag to pan the visualization |
| Vertical Scroll | Scroll wheel | Pan canvas vertically |
| Horizontal Scroll | Shift + Scroll | Pan canvas horizontally |
| Zoom Canvas | Ctrl + Scroll | Zoom around the cursor position |
| Center View | Center button | Center the current pipeline on the canvas |
| Reset View | Reset button | Reset zoom and canvas position |
| Snapshot | Snapshot button | Save a JPEG snapshot of the rendered pipeline |
| View Properties | Hover on node | Display node property tooltip |
| Undo Edit | `Ctrl+Z` | Undo the last edit-mode command |
| Redo Edit | `Ctrl+Y` | Redo the last undone edit-mode command |
| Delete Selection | `Delete` | Delete the selected node or link in edit mode |

## JSON Edit Mode

JSON edit mode is available after opening JSON files and double-clicking a pipeline in the left explorer. XML remains read-only.

- Use the floating **Edit** button to enter or leave edit mode.
- Use the floating **+** button to add a node from a single-column, de-duplicated template list.
- Node templates are collected from all opened JSON pipelines and de-duplicated by `NodeName + NodeId + NodeInstanceId`; different `NodeId` or `NodeInstanceId` values remain separate templates.
- Choose **Blank node** or an existing node template, then edit `NodeName`, `NodeId`, `NodeInstance`, `NodeInstanceId`, input port count, output port count, and port fields.
- Click an output port, then click an input port to create a link. Click empty canvas space to cancel a pending link.
- Click an existing node to edit its fields in the right details panel. The details panel is read-only outside edit mode.
- Select a node or link and press `Delete`, or right-click a node/link and choose delete.
- Use the floating Undo/Redo buttons or `Ctrl+Z` / `Ctrl+Y`.
- Use the floating Save button to overwrite the current JSON file. JSON5 comments may be discarded and output is saved as formatted JSON.
- The right details panel can be explicitly collapsed from the menu bar. While collapsed, canvas clicks do not reopen it.

## Project Structure

```text
Pipeline-visualization-tools/
|-- main.py                 # Application entry point
|-- MainWindow.py           # Main window, UI orchestration, edit-mode routing
|-- PipelineEditor.py       # JSON edit controller, command stack, validation, save logic
|-- CanvasWidget.py         # Drawing canvas, link/port hit testing, hover/selection rendering
|-- NodePainter.py          # Node renderer
|-- Pipeline.py             # Pipeline model + layout algorithm
|-- Node.py                 # Node data model
|-- Port.py                 # Port data model
|-- UseCase.py              # XML/JSON parser
|-- DrawLine.py             # Connection line drawing
|-- Link.py                 # Link data structure
|-- Utils.py                # Logging and utilities
|-- ui_theme.py             # Shared dark UI theme and scrollbar styles
|-- resource.py             # Compiled Qt resources
|-- docs/                   # Project documentation
|   |-- README.md           # Documentation hub
|   |-- project/            # Core project documents
|   |-- reference/          # Reference materials
|   `-- tasks/              # Task management
|-- example/                # Sample pipeline files
|-- res/                    # Application assets
|-- build/                  # PyInstaller build output
`-- dist/                   # Distribution executables
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
| Version | V3.1 |
| Last Updated | 2026-06-02 |
| Author | Jianlin(Jaylen) |
| Contact | a185531353@qq.com |

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

You may use, study, modify, and redistribute this software under the terms of GPLv3. If you distribute modified versions, you must provide the corresponding source code under the same license.

For hosted or network-service distribution requirements, consider switching to GNU Affero General Public License v3.0.
