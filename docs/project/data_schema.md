# Data Schema - Pipeline Visualization Tools

<!-- SCOPE: Data Model Document -->
<!-- OWNER: Engineering -->

## Overview

This document describes the core data models and their relationships used within the Pipeline Visualization Tools application. The application uses in-memory data structures (no database).

## Core Data Models

### UseCaseDes

Represents a complete use case containing multiple pipelines.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mFileName` | str / list | Input file path(s) - single XML or list of JSON files |
| `mUseCasePipelineMap` | dict[str, list[PipelineDes]] | Map from UseCase name to list of Pipelines |
| `mJsonDataList` | list[dict] | Parsed JSON data list |
| `mjsonName` | str | Use case name for JSON parsing |
| `mRoot` | ElementTree.Element | XML root element (XML mode only) |

### PipelineDes

Represents a single pipeline with nodes and port connections. Layout computation is delegated to LayoutEngine.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mNodeList` | list[NodeDes] | All nodes in the pipeline |
| `mPortLinkDes` | dict[PortDes, list[PortDes]] | Port linkage: source port -> list of destination ports |
| `mSrcNodeList` | list[NodeDes] | Source nodes (no input ports or TARGET nodes) |
| `mSrcNodeNameList` | list[str] | Source node name references from XML |
| `mPipelineName` | str | Pipeline name |
| `mNodeLevelKeyMap` | dict[int, list[NodeDes]] | Map from level key to nodes at that level |
| `mNodeLevelKeyList` | list[int] | Sorted list of level keys |
| `mMaxLevel` | int | Maximum hierarchy level in pipeline |
| `mBuild` | bool | Whether pipeline has been built (positions calculated) |
| `mParentWidget` | QWidget | Parent widget for node rendering |

### LayoutEngine

Handles graph-based Sugiyama hierarchical layout computation.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mPipeline` | PipelineDes | Reference to pipeline being laid out |
| `mGraph` | nx.DiGraph | NetworkX directed graph representation |
| `mLayers` | dict[str, int] | Node ID to layer number mapping |
| `mLayerList` | list[list[str]] | Nodes organized by layer index |
| `mNodeOrder` | dict[str, int] | Node ID to position within its layer |
| `mFont` | QFont | Font for port size calculation |

### BezierLineRenderer

Static utility class for rendering cubic Bezier curve connections.

No instance attributes. All methods are static.

### NodeDes

Represents a single processing node in the pipeline.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mNodeName` | str | Node type name (e.g., "Sensor", "IFE", "IPE") |
| `mNodeId` | str | Node identifier |
| `mNodeInstance` | str | Node instance name |
| `mNodeInstanceId` | str | Unique instance identifier |
| `mTargetName` | str | Target buffer name (if applicable) |
| `mIsSourceNode` | bool | Whether this is a source node |
| `mTargetNode` | bool | Whether this is a target buffer node |
| `mOutputPortList` | list[PortDes] | Output ports of this node (ordered by barycenter) |
| `mInputPortList` | list[PortDes] | Input ports of this node (ordered by barycenter) |
| `mNodeLevelList` | list[int] | Hierarchy levels for this node |
| `mNodePropertyList` | list[tuple] | Properties: (name, id, dataType, value) |
| `mNodePos` | QPoint | Position on canvas |
| `mNodeSize` | QSize | Calculated size based on ports |
| `mNodeLevelKey` | int | Computed level key for layout |
| `mLinkDes` | dict | This node's output port -> child node's input port map |
| `mChildNodeToOutputPortMap` | dict[NodeDes, list[PortDes]] | Child nodes and their connecting output ports |
| `mParentNodeToInputPortMap` | dict[NodeDes, list[PortDes]] | Parent nodes and their connecting input ports |
| `mChildNodeSortList` | list[NodeDes] | Sorted child nodes (by barycenter position) |
| `mColor` | QColor | Display color |
| `mFontSize` | int | Font size for node label |
| `mMinWidth` | int | Minimum node width (250) |
| `mMinHeight` | int | Minimum node height (100) |

### PortDes

Represents a connection port on a node.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mPortName` | str | Port name |
| `mPortId` | str | Port identifier |
| `mNodeName` | str | Owning node name |
| `mNodeId` | str | Owning node ID |
| `mNodeInstance` | str | Owning node instance |
| `mNodeInstanceId` | str | Owning node instance ID |
| `mPortPos` | QPoint | Position relative to node |
| `mParentNodePos` | QPoint | Parent node position (for absolute positioning) |
| `mWidth` | int | Port name text width |
| `mHeight` | int | Port name text height |
| `mTargetPort` | bool | Whether this is a target buffer port |

### ComMsg

Communication message for inter-component signaling.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mType` | MsgType | Message type enum |
| `mValue` | any | Message value |

### MsgType Enum

| Value | Hex | Description |
|-------|-----|-------------|
| LeftButton | 0x8000 | Mouse left button state |
| WheelMouse | 0x8001 | Mouse wheel event |
| HoverMove | 0x8002 | Mouse hover move event |
| KeyShift | 0x8100 | Shift key state |
| KeyCtrl | 0x8101 | Ctrl key state |

## Model Relationships

```
UseCaseDes
└── mUseCasePipelineMap (dict)
    └── PipelineDes (values)
        ├── mNodeList (list)
        │   └── NodeDes
        │       ├── mOutputPortList (list)
        │       │   └── PortDes
        │       ├── mInputPortList (list)
        │       │   └── PortDes
        │       └── mChildNodeToOutputPortMap (dict)
        │           └── NodeDes -> list[PortDes]
        ├── mPortLinkDes (dict)
        │   └── PortDes -> list[PortDes]
        └── [LayoutEngine] (transient, created during createNodePos)
            ├── mGraph (nx.DiGraph)
            │   └── node_id -> {node: NodeDes}
            │   └── edge -> {src_ports: [PortDes], dst_ports: [PortDes]}
            ├── mLayers (dict)
            │   └── node_id -> layer_index
            └── mLayerList (list)
                └── layer_index -> [node_id, ...]
```

## Layout Data Flow

```
PipelineDes.createNodePos()
    │
    ├── Build mChildNodeToOutputPortMap / mParentNodeToInputPortMap
    │
    └── LayoutEngine.compute_layout()
        ├── build_graph()          → nx.DiGraph from PipelineDes data
        │   └── _find_node_key_for_port()  → matchNodePort for robust mapping
        ├── assign_layers()        → mLayers, mLayerList
        │   └── _assign_layers_simple()  → BFS fallback for cyclic graphs
        ├── minimize_crossings()   → Optimized mLayerList ordering
        │   ├── _sweep_down()     → Barycenter from upper layer
        │   ├── _sweep_up()       → Barycenter from lower layer
        │   └── _count_crossings() → Crossing count for best-order selection
        ├── position_nodes()       → NodeDes.setNodePos() for all nodes
        │   └── Canonical position propagation for duplicate nodes
        └── order_ports()          → Barycenter-based port reordering
            ├── _order_output_ports()
            └── _order_input_ports()
```

## Node Size Calculation Rules

| Node Type Pattern | Additional Height | Additional Width |
|-------------------|-------------------|------------------|
| IFE | 80 | - |
| Stats | 30 | - |
| Auto | 30 | - |
| BPS | 40 | 10 |
| IPE | - | 10 |
| Sink | 5 | - |
| Sensor | - | - (default) |
| Default | 20 | 0 |

Formula:
- Height = `mMinHeight + max(input_ports, output_ports) * length_step`
- Width = `mMinWidth + max(input_ports, output_ports) * width_step`

## Maintenance

- Update when new data models are added
- Update when model attributes change
- Document new node types or port conventions

<!-- Metadata: Generated 2026-05-19 | Version 2.0.0 -->
