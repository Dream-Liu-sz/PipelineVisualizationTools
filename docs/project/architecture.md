# Architecture - Pipeline Visualization Tools

<!-- SCOPE: Architecture Document -->
<!-- OWNER: Engineering -->

## Overview

This document describes the system architecture of the Pipeline Visualization Tools application, following the arc42 architecture documentation template adapted for a desktop application.

## Architecture Context

### Stakeholders

| Stakeholder | Role | Interest |
|-------------|------|----------|
| Camera Engineers | End Users | Visualize pipeline topology for development and debugging |
| Developers | Maintainers | Understand codebase for feature development |
| QA Team | Testers | Verify pipeline configurations |

### Technical Constraints

- Desktop application (Windows only)
- Python 3.x runtime
- PyQt5 GUI framework
- No server or cloud dependencies

## System Decomposition

The application follows a **Model-View-Controller (MVC)** inspired architecture with clear separation between data parsing, visualization, and user interaction.

### Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    Presentation Layer                         │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐      │
│  │  MainWindow  │  │ CanvasWidget │  │  NodePainter   │      │
│  │  (Controller)│  │   (View)     │  │   (Renderer)   │      │
│  └──────┬──────┘  └──────┬───────┘  └───────┬────────┘      │
│         │                │                   │               │
│  ┌──────┴──────┐  ┌──────┴───────┐  ┌───────┴────────┐      │
│  │ TreeWidget  │  │ BezierLine   │  │ Link Painter   │      │
│  │ (Navigation)│  │ (Connections)│  │ (Edges)        │      │
│  └─────────────┘  └──────────────┘  └────────────────┘      │
└─────────────────────────┬────────────────────────────────────┘
                          │
┌─────────────────────────┴────────────────────────────────────┐
│                     Business Logic Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐     │
│  │  UseCaseDes   │  │ PipelineDes  │  │   NodeDes      │     │
│  │  (Parser)     │  │ (Model)      │  │   (Model)      │     │
│  └──────────────┘  └──────────────┘  └────────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐     │
│  │  PortDes      │  │LayoutEngine  │  │   Utils        │     │
│  │  (Model)      │  │ (Layout)     │  │  (Helpers)     │     │
│  └──────────────┘  └──────────────┘  └────────────────┘     │
└─────────────────────────┬────────────────────────────────────┘
                          │
┌─────────────────────────┴────────────────────────────────────┐
│                      Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐                          │
│  │  XML Parser   │  │  JSON Parser │                          │
│  │(ElementTree)  │  │  (json5)     │                          │
│  └──────────────┘  └──────────────┘                          │
└──────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | File | Responsibility |
|-----------|------|----------------|
| **MainWindow** | `MainWindow.py` | Application window, menu bar, tree navigation, canvas management, event handling, dynamic canvas sizing |
| **CanvasWidget** | `CanvasWidget.py` | Drawing canvas, delegates port-to-port connection rendering to BezierLineRenderer |
| **NodePainter** | `NodePainter.py` | Individual node rendering, property display, mouse interaction |
| **UseCaseDes** | `UseCase.py` | XML/JSON file parsing, UseCase and Pipeline extraction |
| **PipelineDes** | `Pipeline.py` | Pipeline data model, level assignment, delegates layout to LayoutEngine |
| **LayoutEngine** | `LayoutEngine.py` | Graph-based Sugiyama hierarchical layout, barycenter crossing minimization, port ordering |
| **BezierLineRenderer** | `BezierLine.py` | Cubic Bezier curve rendering for port connections, port dot rendering |
| **NodeDes** | `Node.py` | Node data model, port management, size calculation, position |
| **PortDes** | `Port.py` | Port data model, port name/ID, position tracking |
| **Link** | `Link.py` | Link data representation |
| **Utils** | `Utils.py` | Logging utilities, message types, common helpers |
| **Resource** | `resource.py` | Compiled Qt resources (icons, etc.) |

## Runtime View

### File Loading Sequence

```
User Action          MainWindow         UseCaseDes        PipelineDes        NodeDes/Pipeline
    │                    │                   │                  │                  │
    │─ Ctrl+O/Alt+O ───>│                   │                  │                  │
    │                    │─ File Dialog ────>│                  │                  │
    │                    │<─ File Path ──────│                  │                  │
    │                    │                   │                  │                  │
    │                    │─ useCaseTranslation() ──────────────>│                  │
    │                    │                   │─ Parse XML/JSON  │                  │
    │                    │                   │─ pipelineTranslation() ────────────>│
    │                    │                   │                  │─ nodesTranslation()│
    │                    │                   │                  │─ portTranslation() │
    │                    │                   │<─────────────────│                  │
    │                    │<──────────────────│                  │                  │
    │                    │─ updateTreeWidget()                  │                  │
    │                    │ (Display tree)    │                  │                  │
```

### Pipeline Rendering Sequence

```
User Double-Click    MainWindow     UseCaseDes    PipelineDes    LayoutEngine    Canvas/NodePainter
    │                    │               │              │              │                │
    │── Double Click ──>│               │              │              │                │
    │                    │─ buildPipeline() ──────────>│              │                │
    │                    │               │              │─ buildNode() │                │
    │                    │               │              │─ createLevel()│               │
    │                    │               │              │─ createNodePos()              │
    │                    │               │              │              │<──compute_layout()
    │                    │               │              │              │─ build_graph()
    │                    │               │              │              │─ assign_layers()
    │                    │               │              │              │─ minimize_crossings()
    │                    │               │              │              │─ position_nodes()
    │                    │               │              │              │─ order_ports()
    │                    │               │              │<─────────────│                │
    │                    │               │<─────────────│              │                │
    │                    │<──────────────│              │              │                │
    │                    │─ initCanvas() ─────────────────────────────────────────────>│
    │                    │               │              │              │                │─ Render Nodes
    │                    │               │              │              │                │─ Draw Bezier Links
```

## Node Layout Algorithm

The application implements a **Sugiyama-style hierarchical graph layout** algorithm powered by networkx:

### Algorithm Steps

1. **Graph Construction**: Build a `networkx.DiGraph` from pipeline data, using `matchNodePort` for robust port-to-node mapping that handles name mismatches between ports and nodes
2. **Layer Assignment**: Assign layers via topological sort (longest path), with BFS fallback for cyclic graphs
3. **Crossing Minimization**: Barycenter heuristic with 24 alternating up/down sweeps to minimize edge crossings
4. **Node Positioning**: Layer-by-layer left-to-right layout with vertical centering, automatic spacing (250px between layers, 50px between nodes)
5. **Port Ordering**: Barycenter-based output/input port ordering to reduce intra-node connection crossings
6. **Duplicate Node Handling**: Canonical node positions propagated to duplicate entries in the node list

### Layout Strategy

```
Layer 0 (Source)     Layer 1            Layer 2            Layer 3
┌─────────┐         ┌─────────┐        ┌─────────┐        ┌─────────┐
│ Sensor0 │────────>│ IFE0    │───────>│ IPE0    │───────>│ Sink0   │
└─────────┘         └─────────┘        └─────────┘        └─────────┘
                         │
                    ┌────┴────┐
                    │ BPS0    │
                    └─────────┘
```

### Connection Rendering

Connections between ports are rendered as **cubic Bezier curves** using `QPainterPath.cubicTo()`:

- Control points extend horizontally from source/end points
- Offset = `max(50, horizontal_distance * 0.4)` ensures smooth curves for both short and long connections
- Port endpoints rendered as filled circles via `drawEllipse()` (replacing the previous per-pixel trigonometric approach)

### Edge Cases Handled

| Case | Handling |
|------|----------|
| Empty pipeline | Early return, mark as built |
| Single node | Place at center position |
| Cyclic graph | BFS-based layering fallback |
| Port name ≠ Node name | `matchNodePort` uses NodeId+NodeInstanceId matching |
| Duplicate nodes in list | Canonical position propagation |
| Orphan nodes (no connections) | Added to graph as isolated nodes |
| Canvas overflow | Dynamic canvas resize based on max node extent |

## Key Design Decisions

| Decision | Rationale | Impact |
|----------|-----------|--------|
| PyQt5 for GUI | Mature Python GUI framework with rich widget set | Desktop-only, Windows-focused |
| XML + JSON support | Legacy XML format + modern NCF JSON format | Dual parsing logic in UseCaseDes |
| Sugiyama layout via networkx | Industry-standard algorithm for directed graph layout | Optimal crossing reduction, deterministic output |
| Bezier curve connections | Smooth visual flow between nodes | Better readability than straight lines |
| matchNodePort for graph building | Port names may differ from node names in JSON configs | Robust port-to-node mapping |
| Dynamic canvas sizing | Large pipelines may exceed fixed 8000x8000 canvas | All nodes always visible |
| Canvas-based rendering | Large pipelines need scrollable/pannable area | Custom drawing instead of standard widgets |

## Maintenance

- Update when new components are added
- Update when architecture patterns change
- Review when adding support for new file formats

<!-- Metadata: Generated 2026-05-19 | Version 2.0.0 -->
