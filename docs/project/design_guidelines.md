# Design Guidelines - Pipeline Visualization Tools

<!-- SCOPE: UI/UX Design Document -->
<!-- OWNER: Design/Engineering -->

## Overview

This document describes the UI/UX design patterns, visual conventions, and interaction guidelines for the Pipeline Visualization Tools application.

## Visual Design System

### Color Palette

| Usage | RGB | Hex | Purpose |
|-------|-----|-----|---------|
| Background Dark | (50, 50, 50) | #323232 | Main window, tree panel, canvas background |
| Text Light | (200, 200, 200) | #C8C8C8 | Tree item text, general labels |
| Text White | (255, 255, 255) | #FFFFFF | Tooltip text, dialog text |
| Tooltip Background | (50, 50, 50) | #323232 | Node property tooltip |
| Window Background | (255, 255, 255) | #FFFFFF | Default window background (unused) |

### Node Colors

Nodes are assigned colors from a predefined palette (20 colors) to visually distinguish different nodes in the pipeline:

| Index | RGB | Index | RGB |
|-------|-----|-------|-----|
| 0 | (252, 230, 202) | 10 | (0, 199, 104) |
| 1 | (200, 0, 0) | 11 | (199, 97, 20) |
| 2 | (255, 255, 0) | 12 | (153, 51, 250) |
| 3 | (64, 224, 205) | 13 | (128, 42, 42) |
| 4 | (255, 0, 255) | 14 | (255, 125, 64) |
| 5 | (0, 255, 255) | 15 | (107, 142, 35) |
| 6 | (255, 153, 18) | 16 | (85, 102, 0) |
| 7 | (156, 102, 31) | 17 | (0, 0, 255) |
| 8 | (202, 235, 216) | 18 | (250, 240, 230) |
| 9 | (3, 168, 158) | 19 | (150, 100, 0) |

Colors cycle through the list when more than 20 nodes are present.

### Typography

| Element | Font | Size | Style |
|---------|------|------|-------|
| Node Label | System default | 24px (configurable) | Normal |
| Tooltip | KaiTi (楷体) | 18px | Italic |
| Tree Items | System default | Default | Normal |
| Dialog Text | System default | Default | Normal |

## Layout Conventions

### Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Menu Bar: [File]                    [Help]                 │
├────────────┬────────────────────────────────────────────────┤
│            │                                                │
│  Tree      │              Canvas Area                       │
│  Panel     │              (8000 x 8000 virtual)             │
│  (200px)   │                                                │
│            │              ┌───────────┐                     │
│  UseCase1  │              │  Node1    │────┐                │
│    Pipeline│              └───────────┘    │                │
│    A       │                               ▼                │
│    B       │                        ┌───────────┐           │
│            │                        │  Node2    │           │
│  UseCase2  │                        └───────────┘           │
│    Pipeline│                                                │
│    C       │              [Tooltip Label (floating)]        │
│            │                                                │
├────────────┴────────────────────────────────────────────────┤
│  Status: 1280 x 720 (default window size)                  │
└─────────────────────────────────────────────────────────────┘
```

### Node Visual Design

```
┌──────────────────────────────────┐
│                                  │  ← Input Ports (left side)
│  ┌──────────────────────────┐    │     - Port names displayed
│  │       NODE NAME          │    │     - Vertically distributed
│  │                          │    │
│  │                          │────┼── → Output Ports (right side)
│  │                          │    │     - Port names displayed
│  │                          │    │     - Vertically distributed
│  └──────────────────────────┘    │
│                                  │
└──────────────────────────────────┘
```

### Connection Lines

- Drawn from source node output port to destination node input port
- Color matches the source node's assigned color
- Straight line connections (no curved routing)

## Interaction Patterns

### Mouse Interactions

| Action | Effect |
|--------|--------|
| Left-click + drag on canvas | Pan the canvas |
| Scroll wheel | Vertical pan |
| Scroll wheel + Shift | Horizontal pan |
| Scroll wheel + Ctrl | Zoom (if implemented) |
| Hover on node | Display tooltip with node properties (after 800ms delay) |
| Double-click tree item | Render selected pipeline |
| Resize window | Tree panel width stays fixed at 200px |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open XML file |
| Ctrl+Alt+O | Open JSON file(s) |

### Menu Structure

| Menu | Item | Action |
|------|------|--------|
| File | open xml file | Open file dialog for XML |
| File | open json file | Open file dialog for JSON |
| Help | about | Show version and author info |
| Help | tips | Show troubleshooting tips |

## Responsive Behavior

### Canvas Size

- Virtual canvas: 8000 x 8000 pixels
- Canvas positioned at center offset (1000, 2000)
- Window resizes do not affect canvas size

### Tree Panel

- Fixed width: 200px minimum
- Full height: window height - 15px
- Auto-resizes column to fit content
- Dark background (#323232)

### Tooltip

- Appears after 800ms hover delay
- Displays near the hovered node
- Shows all node properties with separators
- Auto-hides when cursor moves away

## Design Principles

| Principle | Application |
|-----------|-------------|
| **Visual Hierarchy** | Source nodes on left, flowing to sink nodes on right |
| **Color Coding** | Each node has a unique color for easy identification |
| **Information Density** | Show essential info (node name, ports) by default; details on hover |
| **Consistency** | Same color scheme across tree panel and canvas |
| **Feedback** | Cursor changes during drag, tooltips on hover |

## Accessibility Considerations

- High contrast text (light text on dark background)
- Readable font sizes (18px+ for tooltips, 24px for node labels)
- Clear visual distinction between nodes (color + position)
- Keyboard shortcuts for primary actions

## Maintenance

- Update when UI components are redesigned
- Update when new interaction patterns are added
- Review for consistency with actual implementation

<!-- Metadata: Generated 2026-05-19 | Version 1.0.0 -->
