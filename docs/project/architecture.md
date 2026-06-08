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
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  MainWindow  │  │ CanvasWidget │  │  NodePainter   │  │
│  │  (Controller)│  │   (View)     │  │   (Renderer)   │  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬────────┘  │
│         │                │                   │           │
│  ┌──────┴──────┐  ┌──────┴───────┐  ┌───────┴────────┐  │
│  │ TreeWidget  │  │ DrawLine     │  │ Link Painter   │  │
│  │ (Navigation)│  │ (Connections)│  │ (Edges)        │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────┐
│                     Business Logic Layer                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  UseCaseDes   │  │ PipelineDes  │  │   NodeDes      │  │
│  │  (Parser)     │  │ (Layout)     │  │   (Model)      │  │
│  └──────────────┘  └──────────────┘  └────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │  PortDes      │  │   Utils      │                       │
│  │  (Model)      │  │  (Helpers)   │                       │
│  └──────────────┘  └──────────────┘                       │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────┐
│                      Data Layer                          │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │  XML Parser   │  │  JSON Parser │                     │
│  │(ElementTree)  │  │  (json5)     │                     │
│  └──────────────┘  └──────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | File | Responsibility |
|-----------|------|----------------|
| **MainWindow** | `MainWindow.py` | Application window, menu bar, tree navigation, canvas management, event handling |
| **CanvasWidget** | `CanvasWidget.py` | Drawing canvas, port-to-port connection rendering |
| **NodePainter** | `NodePainter.py` | Individual node rendering, property display, mouse interaction |
| **UseCaseDes** | `UseCase.py` | XML/JSON file parsing, UseCase and Pipeline extraction |
| **PipelineDes** | `Pipeline.py` | Pipeline data model, node layout algorithm, level assignment |
| **NodeDes** | `Node.py` | Node data model, port management, size calculation, position |
| **PortDes** | `Port.py` | Port data model, port name/ID, position tracking |
| **DrawLine** | `DrawLine.py` | Connection line drawing between ports |
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
User Double-Click    MainWindow         UseCaseDes        PipelineDes        Canvas/NodePainter
    │                    │                   │                  │                  │
    │── Double Click ──>│                   │                  │                  │
    │                    │─ buildPipeline() ──────────────────>│                  │
    │                    │                   │                  │─ buildNode()      │
    │                    │                   │                  │─ createLevel()    │
    │                    │                   │                  │─ createNodePos()  │
    │                    │                   │<─────────────────│                  │
    │                    │<──────────────────│                  │                  │
    │                    │─ initCanvas() ──────────────────────────────────────────>│
    │                    │                   │                  │                  │─ Render Nodes
    │                    │                   │                  │                  │─ Draw Links
```

## Node Layout Algorithm

The application implements a **hierarchical graph layout** algorithm:

### Algorithm Steps

1. **Source Node Identification**: Find nodes with no input ports or marked as TARGET nodes
2. **Level Assignment**: Assign levels to nodes based on topological distance from source nodes
3. **Position Calculation**: 
   - Source nodes placed at reference point
   - Child nodes positioned relative to parent's output port positions
4. **Overlap Resolution**: Adjust node positions to prevent overlaps within the same level
5. **Port Positioning**: Calculate input/output port positions based on node size

### Layout Strategy

```
Level 0 (Source)     Level 1            Level 2            Level 3
┌─────────┐         ┌─────────┐        ┌─────────┐        ┌─────────┐
│ Sensor0 │────────>│ IFE0    │───────>│ IPE0    │───────>│ Sink0   │
└─────────┘         └─────────┘        └─────────┘        └─────────┘
                         │
                    ┌────┴────┐
                    │ BPS0    │
                    └─────────┘
```

## Key Design Decisions

| Decision | Rationale | Impact |
|----------|-----------|--------|
| PyQt5 for GUI | Mature Python GUI framework with rich widget set | Desktop-only, Windows-focused |
| XML + JSON support | Legacy XML format + modern NCF JSON format | Dual parsing logic in UseCaseDes |
| Hierarchical layout | Pipeline topology is naturally directional | Clear visualization, minimizes crossings |
| Canvas-based rendering | Large pipelines need scrollable/pannable area | Custom drawing instead of standard widgets |

## Maintenance

- Update when new components are added
- Update when architecture patterns change
- Review when adding support for new file formats

<!-- Metadata: Generated 2026-05-19 | Version 1.0.0 -->
