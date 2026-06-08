# Changelog

All notable changes to **Pipeline Visualization Tools** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Linux / macOS packaging via PyInstaller.
- Plugin API for custom node renderers.
- Search and filter in the left explorer.

## [V3.1] - 2026-06-02

### Added
- JSON edit mode with node add/delete, link add/delete, and node field editing.
- Floating Edit / + / Undo / Redo / Save controls in the canvas overlay.
- Node template list collected from all opened JSON pipelines, de-duplicated by `NodeName + NodeId + NodeInstanceId` while preserving distinct `NodeId` / `NodeInstanceId` entries.
- Blank-node creation with editable `NodeName`, `NodeId`, `NodeInstance`, `NodeInstanceId`, and port counts.
- Pending-link workflow: click an output port, then an input port, to create a link; click empty canvas to cancel.
- Right-side details panel with read-only mode outside of edit mode, and a menu command to explicitly collapse it.
- JSON5 support via the `json5` parser.

### Changed
- Save behavior in edit mode: JSON5 comments are discarded and output is written as formatted JSON.
- Hover tooltips on nodes display node properties in a consistent tooltip.

### Notes
- XML pipeline files remain **read-only** for safe inspection.
- Tested with Python 3.9 and 3.12, PyQt5 ≥ 5.15, `json5` ≥ 0.9, `networkx` ≥ 2.6.

## [V3.0] - Earlier

### Added
- Dual-format parsing for legacy XML pipeline files and JSON NCF pipeline configuration files.
- Interactive canvas with color-coded nodes and port connections.
- Left-side tree navigator for use cases and pipelines.
- Canvas navigation: pan, scroll, zoom around cursor, center, reset, and JPEG snapshot.
- Hierarchical auto-layout for pipeline topology (powered by `networkx`).
- Dark UI theme and shared scrollbar styling (`ui_theme.py`).
- Pre-built Windows executable built with PyInstaller.

[Unreleased]: https://github.com/Dream-Liu-sz/PipelineVisualizationTools/compare/v3.1...HEAD
[V3.1]: https://github.com/Dream-Liu-sz/PipelineVisualizationTools/releases/tag/v3.1
[V3.0]: https://github.com/Dream-Liu-sz/PipelineVisualizationTools/releases/tag/v3.0
