# Tech Stack - Pipeline Visualization Tools

<!-- SCOPE: Technology Document -->
<!-- OWNER: Engineering -->

## Overview

This document describes the technology stack, dependencies, and development tools used in the Pipeline Visualization Tools project.

## Core Technologies

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| **Language** | Python | 3.9+ | Application programming language |
| **GUI Framework** | PyQt5 | 5.x | Desktop UI framework (QMainWindow, QTreeWidget, QWidget, etc.) |
| **Graph Library** | networkx | 2.6+ | Directed graph construction and Sugiyama hierarchical layout |
| **JSON Parser** | json5 | Latest | Parse JSON5 format pipeline configurations |
| **XML Parser** | xml.etree.ElementTree | Built-in | Parse XML format pipeline configurations |
| **Build Tool** | PyInstaller | Latest | Package application into standalone executable |

## PyQt5 Components Used

| Component | Module | Usage |
|-----------|--------|-------|
| QApplication | PyQt5.Qt | Application entry point |
| QMainWindow | PyQt5.Qt | Main window container |
| QTreeWidget | PyQt5.QtWidgets | Left-side pipeline navigation tree |
| QWidget | PyQt5.QtWidgets | Canvas container and UI elements |
| QLabel | PyQt5.QtWidgets | Node property tooltip display |
| QAction | PyQt5.Qt | Menu bar actions |
| QMenu | PyQt5.Qt | File and Help menus |
| QFileDialog | PyQt5.QtWidgets | File open dialog |
| QMessageBox | PyQt5.Qt | About and Tips dialogs |
| QTimer | PyQt5.QtCore | Delayed tooltip display |
| pyqtSignal | PyQt5.QtCore | Inter-component communication |
| Qt | PyQt5.QtCore | Widget attributes and event types |
| QEvent | PyQt5.QtCore | Hover move event handling |
| QColor | PyQt5.QtGui | Node coloring |
| QCursor | PyQt5.QtGui | Cursor changes during drag |
| QFont | PyQt5.QtGui | Font configuration for labels |
| QFontMetrics | PyQt5.QtGui | Text measurement for layout |
| QPainterPath | PyQt5.QtGui | Bezier curve path rendering |
| QPalette | PyQt5.Qt | Color palette management |
| QIcon | PyQt5.Qt | Window and action icons |
| QPoint | PyQt5.Qt | 2D position coordinates |
| QSize | PyQt5.Qt | 2D size dimensions |
| QRect | PyQt5.Qt | Rectangle for overlap calculation |

## networkx Components Used

| Component | Usage |
|-----------|-------|
| `nx.DiGraph` | Directed graph representation of pipeline topology |
| `nx.topological_sort` | Layer assignment via topological ordering |
| `nx.is_directed_acyclic_graph` | Cycle detection for layout algorithm selection |
| `nx.has_edge` | Edge existence checking during graph construction |
| Graph attributes | `src_ports`, `dst_ports` stored on edges for port-level tracking |

## Project Structure

```
Pipeline-visualization-tools/
├── main.py                 # Application entry point
├── MainWindow.py           # Main window (controller + view)
├── CanvasWidget.py         # Drawing canvas (delegates to BezierLineRenderer)
├── NodePainter.py          # Node renderer
├── LayoutEngine.py         # Sugiyama layout engine (networkx-based)
├── BezierLine.py           # Bezier curve connection renderer
├── Pipeline.py             # Pipeline model + level assignment
├── Node.py                 # Node data model
├── Port.py                 # Port data model
├── UseCase.py              # XML/JSON parser
├── DrawLine.py             # Legacy connection line drawing (unused)
├── Link.py                 # Link data structure
├── Utils.py                # Logging and utilities
├── resource.py             # Compiled Qt resources
├── resource.qrc            # Qt resource file
├── requirements.txt        # Python dependencies
├── main.spec               # PyInstaller spec file
├── res/
│   └── logo.ico            # Application icon
├── example/                # Sample pipeline files
│   ├── *.xml               # XML pipeline configs
│   └── *.json              # JSON pipeline configs
├── build/                  # PyInstaller build output
├── dist/                   # Distribution executables
└── venv/                   # Python virtual environment
```

## Development Environment

| Tool | Purpose |
|------|---------|
| Python 3.9+ | Runtime environment |
| pip | Package management |
| venv | Virtual environment isolation |
| PyInstaller | Application packaging |
| Qt Designer (optional) | UI design (if used) |

## Build & Distribution

### Development Setup

```
1. Create virtual environment: python -m venv venv
2. Activate: venv\Scripts\activate
3. Install dependencies: pip install -r requirements.txt
4. Run: python main.py
```

### Packaging

```
pyinstaller main.spec
```

Output: `dist/pipelineVisualization.exe`

## Dependencies

| Dependency | Required | Version | Notes |
|------------|----------|---------|-------|
| PyQt5 | Yes | >=5.15 | Core GUI framework |
| networkx | Yes | >=2.6 | Graph construction and Sugiyama layout algorithm |
| json5 | Yes | Latest | JSON parsing |
| PyInstaller | Build time only | Latest | Packaging tool |

## Maintenance

- Update when dependencies are upgraded
- Update when new libraries are added
- Document any version-specific requirements

<!-- Metadata: Generated 2026-05-19 | Version 2.0.0 -->
