# UI/UX Redesign Proposal

<!-- SCOPE: UI/UX Redesign Decision Record -->
<!-- OWNER: Design/Engineering -->

## Goal

Upgrade Pipeline Visualization Tools from a basic topology renderer into a modern engineering visualization workspace. The redesign keeps the PyQt5 Widgets stack and the current custom canvas renderer, while improving visual hierarchy, readability, interaction feedback, and responsiveness.

## Design Direction Comparison

| Direction | Strengths | Tradeoffs | Decision |
|-----------|-----------|-----------|----------|
| Professional dark engineering workspace | Best long-session readability, low visual noise, strong contrast for nodes and links, familiar to debugging tools | Requires careful muted color use so the UI does not feel too flat | Selected |
| Bright dashboard | Clean and approachable, strong for forms and documentation | Complex topology lines compete with a bright background and increase eye fatigue | Not selected |
| Futuristic dark presentation | High visual impact for demos and screenshots | Decorative effects can distract from dense engineering analysis | Not selected |

## Selected Visual System

| Token | Hex | Usage |
|-------|-----|-------|
| Background | `#0F172A` | Main window and canvas base |
| Panel | `#111827` | Navigation and empty-state surfaces |
| Card | `#1F2937` | Nodes, pills, toolbar controls |
| Border | `#334155` | Panel and control separation |
| Primary accent | `#38BDF8` | Focus, selected states, primary highlights |
| Success accent | `#34D399` | Flow completion and secondary semantic color |
| Warning accent | `#F59E0B` | Attention without alarm |
| Text | `#E5EDF7` | Primary labels |
| Muted text | `#94A3B8` | Hints, metadata, secondary labels |

Typography uses `Microsoft YaHei UI` for interface text and `Cascadia Mono` for technical identifiers, node properties, and port labels.

## UX Improvements

| Area | Previous State | New State |
|------|----------------|-----------|
| Navigation | Fixed tree panel with no search and weak hierarchy | Resizable `QSplitter` panel with search, stronger UseCase/Pipeline typography, hover and selected states |
| Canvas | Flat dark background with high-saturation nodes | Grid-backed engineering canvas with empty-state guidance and calmer semantic node colors |
| Nodes | Solid color rectangles with centered text | Rounded dark cards, accent stripe, clear title, muted port labels, hover/drag feedback |
| Links | Basic Bezier paths | Antialiased rounded links with alpha and clear port dots |
| Context | No persistent pipeline summary | Top context bar with file/pipeline state, node count, link count, zoom, and center action |
| Responsiveness | Manual widget positioning | Layout-managed splitter and viewport resizing while retaining canvas panning |
| Accessibility | High contrast only | Improved focus/hover states, readable fonts, lower cognitive load, clearer status guidance |

## Implementation Notes

The redesign is intentionally incremental. It avoids replacing the rendering architecture with QML or web tech, because the existing PyQt5 canvas already carries parsing, layout, node dragging, and link drawing behavior. The new `ui_theme.py` centralizes color, typography, QSS, and node color selection so future UI changes are localized.

## Acceptance Criteria

- The application starts with a modern dark UI and an empty canvas guidance card.
- XML and JSON loading still populate the navigation tree.
- Tree search filters UseCase and Pipeline names without changing loaded data.
- Double-clicking a pipeline renders the graph with card-style nodes and antialiased links.
- Ctrl+wheel zooms the full topology, Shift+wheel pans horizontally, and regular wheel pans vertically.
- Window resizing preserves the left navigation and right canvas layout without overlap.
