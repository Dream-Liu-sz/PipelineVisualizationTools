# Design Guidelines - Pipeline Visualization Tools

<!-- SCOPE: UI/UX Design Document -->
<!-- OWNER: Design/Engineering -->

## Overview

Pipeline Visualization Tools uses a professional dark engineering workspace optimized for long-running pipeline debugging. The UI should keep visual noise low, emphasize topology flow, and make node and property inspection feel immediate.

## Visual System

| Usage | Hex | Purpose |
|-------|-----|---------|
| Background | `#0F172A` | Main window and canvas |
| Panel | `#111827` | Navigation and empty-state surfaces |
| Card | `#1F2937` | Nodes, toolbar pills, contextual controls |
| Border | `#334155` | Separators and low-emphasis outlines |
| Strong border | `#475569` | Node borders and hover structure |
| Primary accent | `#38BDF8` | Focus states, selected states, active highlights |
| Success accent | `#34D399` | Secondary node color and positive flow color |
| Warning accent | `#F59E0B` | Attention state |
| Text | `#E5EDF7` | Primary labels |
| Muted text | `#94A3B8` | Metadata, hints, port labels |

Node colors are selected from a color-blind-aware accent palette in `ui_theme.py`. Avoid large saturated fills; use node colors as accent stripes, ports, and link colors so dense graphs stay readable.

## Typography

| Element | Font | Style |
|---------|------|-------|
| App chrome, menus, tree | `Microsoft YaHei UI` | 9-11pt regular |
| Panel titles and current pipeline | `Microsoft YaHei UI` | 15-17px bold |
| Node title | `Microsoft YaHei UI` | Bold, scaled with zoom |
| Port labels and properties | `Cascadia Mono` | Compact technical text |

Text should be left-aligned except for compact pills. Keep line height generous in tooltips and documentation-like content.

## Layout

The main window is split into a navigation panel and a canvas workspace with `QSplitter`.

```text
Menu bar
┌───────────────────────┬──────────────────────────────────────────────┐
│ Searchable tree panel │ Context bar: file, pipeline, metrics, action │
│ UseCase/Pipeline nav  │ Canvas viewport with grid and graph           │
└───────────────────────┴──────────────────────────────────────────────┘
Status bar: interaction hints
```

Guidelines:

- Navigation defaults to 280px wide and should remain usable down to 220px.
- The canvas owns most horizontal space and should remain the dominant visual area.
- The context bar summarizes state: current pipeline, loaded file(s), node count, link count, and zoom.
- Empty states should tell users the next action instead of showing a blank panel.

## Canvas And Nodes

- Canvas background uses a subtle grid to support spatial orientation while panning large graphs.
- Nodes render as rounded dark cards with an accent stripe, clear title, and muted port labels.
- Links use antialiased Bezier curves, rounded caps, alpha, and endpoint dots.
- Node hover and drag states increase border emphasis instead of changing layout.
- Tooltip cards show the selected node and property fields with monospace text.

## Interaction Patterns

| Action | Behavior |
|--------|----------|
| `Ctrl+O` | Open XML file |
| `Ctrl+Alt+O` | Open JSON files |
| Tree filter input | Filter UseCase and Pipeline names |
| Double-click pipeline | Build and render selected pipeline |
| Drag canvas | Free pan |
| Wheel | Vertical pan |
| `Shift+Wheel` | Horizontal pan |
| `Ctrl+Wheel` | Zoom whole topology |
| Hover node | Show delayed property card |
| Center View | Recenter canvas around the layout origin |

## Responsiveness

- Use Qt layouts for application chrome and splitter-managed panels.
- Keep the custom canvas oversized so large graphs remain pannable.
- On narrow windows, preserve pipeline title and zoom first; secondary metric labels may compress.
- Enable High DPI scaling in the app entrypoint.

## Accessibility And Readability

- Maintain strong contrast between text and surface colors.
- Do not use color alone to encode meaning; position, labels, and topology direction remain primary.
- Keep hover and selected states visually distinct.
- Avoid decorative effects that obscure link direction or port labels.

## Related Documents

- `docs/project/ui_ux_redesign.md` records the design comparison and selected direction.
- `docs/project/ui_prototypes.md` contains key Markdown wireframes.

<!-- Metadata: Updated 2026-05-19 | Version 3.0.0 -->
