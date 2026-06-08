# API/Interface Specification - Pipeline Visualization Tools

<!-- SCOPE: Interface Specification Document -->
<!-- OWNER: Engineering -->

## Overview

This document specifies the file format interfaces (XML and JSON) that the application parses, as well as the internal data model contracts.

## External Interfaces

### XML Pipeline Configuration Format

The application parses Qualcomm XML pipeline configuration files with the following structure:

#### Root Structure

| Element | Cardinality | Description |
|---------|-------------|-------------|
| `<Root>` | 1 | Root element containing all use cases |
| `<Usecase>` | 1..N | Individual use case definition |
| `<UsecaseName>` | 1 | Name of the use case |
| `<Pipeline>` | 1..N | Pipeline definition within a use case |

#### Pipeline Structure

| Element | Cardinality | Description |
|---------|-------------|-------------|
| `<PipelineName>` | 1 | Name of the pipeline |
| `<NodesList>` | 1..N | Container for node definitions |
| `<PortLinkages>` | 1..N | Container for port connection definitions |

#### Node Structure

| Element | Cardinality | Description |
|---------|-------------|-------------|
| `<Node>` | 1..N | Individual node definition |
| `<NodeName>` | 1 | Node type name (e.g., "Sensor", "IFE") |
| `<NodeId>` | 1 | Unique node identifier |
| `<NodeInstance>` | 1 | Node instance name |
| `<NodeInstanceId>` | 1 | Unique instance identifier |
| `<NodeProperty>` | 0..N | Node property definition |
| `<NodePropertyName>` | 1 | Property name |
| `<NodePropertyId>` | 1 | Property identifier |
| `<NodePropertyDataType>` | 1 | Property data type |
| `<NodePropertyValue>` | 1 | Property value |

#### Port Linkage Structure

| Element | Cardinality | Description |
|---------|-------------|-------------|
| `<SourceNode>` | 0..N | Source node name reference |
| `<TargetName>` | 0..N | Target node name reference |
| `<Link>` | 1..N | Port connection definition |
| `<SrcPort>` | 1 | Source port definition |
| `<DstPort>` | 1..N | Destination port definition(s) |

#### Port Definition (SrcPort/DstPort)

| Element | Description |
|---------|-------------|
| `<PortName>` | Port name (e.g., "TARGET_BUFFER0") |
| `<PortId>` | Port identifier |
| `<NodeName>` | Owning node name |
| `<NodeId>` | Owning node ID |
| `<NodeInstance>` | Owning node instance |
| `<NodeInstanceId>` | Owning node instance ID |

### JSON Pipeline Configuration Format (NCF)

The application also supports JSON format pipeline configurations:

#### Root Structure

| Field | Type | Description |
|-------|------|-------------|
| `PipelineName` | string | Name of the pipeline |
| `Nodes` | object | Container for node definitions |
| `PortLinks` | array | Array of port link definitions |

#### Nodes Structure

| Field | Type | Description |
|-------|------|-------------|
| `Nodes.Node` | array | Array of node objects |
| `NodeName` | string | Node type name |
| `NodeId` | string/number | Node identifier |
| `NodeInstance` | string | Node instance name |
| `NodeProperties` | array | Array of property objects |

#### Node Property Structure

| Field | Type | Description |
|-------|------|-------------|
| `NodePropertyName` | string | Property name |
| `Id` | string | Property identifier |
| `NodePropertyDataType` | string | Data type |
| `Value` | string | Property value |

#### Port Link Structure

| Field | Type | Description |
|-------|------|-------------|
| `PortLinks` | array | Array of link objects |
| `Link` | array | Links within a port linkage |
| `SrcPort` | object | Source port definition |
| `DstPort` | object | Destination port definition |

#### Port Object Structure

| Field | Type | Description |
|-------|------|-------------|
| `PortId` | string/number | Port identifier |
| `NodeName` | string | Owning node name |
| `NodeId` | string/number | Owning node ID |
| `NodeInstance` | string | Owning node instance |

## Internal Data Model Contracts

### PipelineDes Contract

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `addNode()` | NodeDes | void | Add node to pipeline (deduplicated) |
| `getNodeList()` | - | list[NodeDes] | Get all nodes in pipeline |
| `getPortLink()` | - | dict[PortDes, list[PortDes]] | Get port linkage map |
| `buildNode()` | - | void | Assign ports to nodes, identify source nodes |
| `createLevel()` | - | void | Assign hierarchy levels to nodes |
| `createNodePos()` | QPoint, int | void | Delegate layout computation to LayoutEngine |
| `matchNodePort()` | NodeDes, PortDes | bool | Match node to port by NodeId+NodeInstanceId |
| `getPipelineName()` | - | string | Get pipeline name |
| `isBuild()` | - | bool | Check if pipeline has been built |

### NodeDes Contract

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `getNodeName()` | - | string | Get node type name |
| `getNodeId()` | - | string | Get node ID |
| `getNodePos()` | - | QPoint | Get node position |
| `setNodePos()` | QPoint | void | Set node position |
| `getNodeSize()` | - | QSize | Get calculated node size |
| `getNodeProp()` | - | list[tuple] | Get node properties |
| `getInputPort()` | - | list[PortDes] | Get input ports |
| `getOutputPort()` | - | list[PortDes] | Get output ports |
| `getLink()` | - | dict | Get node link map |
| `sortOutputPort()` | - | void | Reorder output ports by mChildNodeToOutputPortMap |
| `calOutputPortPosNew()` | QFont | void | Calculate output port positions |
| `calInputPortPos()` | QFont | void | Calculate input port positions |
| `match()` | NodeDes | bool | Check if two nodes are the same |

### LayoutEngine Contract

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `compute_layout()` | QPoint center_pos, int font_size | void | Execute full layout pipeline (graph build → layers → crossings → positions → ports) |
| `build_graph()` | - | void | Build networkx DiGraph from pipeline data using matchNodePort |
| `assign_layers()` | - | void | Assign layers via topological sort (longest path), BFS fallback for cycles |
| `minimize_crossings()` | int iterations=24 | void | Barycenter heuristic with alternating up/down sweeps |
| `position_nodes()` | QPoint center_pos | void | Layer-by-layer left-to-right positioning with vertical centering |
| `order_ports()` | - | void | Barycenter-based output/input port ordering |

#### LayoutEngine Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `mPipeline` | PipelineDes | Reference to pipeline being laid out |
| `mGraph` | nx.DiGraph | NetworkX directed graph |
| `mLayers` | dict[str, int] | Node ID to layer number mapping |
| `mLayerList` | list[list[str]] | Nodes organized by layer |
| `mNodeOrder` | dict[str, int] | Node ID to position within layer |
| `mFont` | QFont | Font for port size calculation |

#### LayoutEngine Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `LAYER_SPACING` | 250 | Horizontal spacing between layers |
| `NODE_SPACING` | 50 | Vertical spacing between nodes in same layer |
| `MIN_NODE_WIDTH` | 250 | Minimum node width |
| `MIN_NODE_HEIGHT` | 100 | Minimum node height |

### BezierLineRenderer Contract

All methods are static.

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `draw_bezier_link()` | QPainter, PortDes src, PortDes dst, QPen, int radius=5 | void | Draw complete Bezier connection between two ports |
| `create_bezier_path()` | QPoint start, QPoint end | QPainterPath | Create cubic Bezier path with horizontal control points |
| `draw_port_dot()` | QPainter, QPoint, QColor, int radius=5 | void | Draw filled circle at port endpoint |

#### Bezier Curve Parameters

| Parameter | Formula | Description |
|-----------|---------|-------------|
| Control point offset | `max(50, abs(dx) * 0.4)` | Horizontal distance of control points from endpoints |
| Control point 1 | `(start.x + offset, start.y)` | Extends rightward from source |
| Control point 2 | `(end.x - offset, end.y)` | Extends leftward from destination |

### UseCaseDes Contract

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `useCaseTranslation()` | - | void | Parse XML file |
| `useCaseTranslationJson()` | - | void | Parse JSON files |
| `buildPipeline()` | useCase, pipelineName, point, fontSize, parent | PipelineDes | Build and return a pipeline |
| `getPipelineMap()` | - | dict[str, list[PipelineDes]] | Get use case to pipeline map |

## Maintenance

- Update when XML/JSON schema changes
- Update when new internal interfaces are added
- Document breaking changes with version notes

<!-- Metadata: Generated 2026-05-19 | Version 2.0.0 -->
