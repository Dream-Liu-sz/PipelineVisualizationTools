# UI Prototypes

<!-- SCOPE: Key UI Wireframes -->
<!-- OWNER: Design/Engineering -->

## 1. Empty Start State

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ File  Help                                                                    │
├───────────────────────┬──────────────────────────────────────────────────────┤
│ Pipeline Explorer     │ Ready to visualize                 Nodes 0 Links 0   │
│ Search and double...  │ No file loaded                       Zoom 100%       │
│ ┌───────────────────┐ │ ┌──────────────────────────────────────────────────┐ │
│ │ Filter use cases  │ │ │                                                  │ │
│ └───────────────────┘ │ │                 Pipeline canvas                  │ │
│ ┌───────────────────┐ │ │  Open an XML or JSON pipeline file, then         │ │
│ │ Empty tree         │ │ │  double-click a pipeline in the explorer.        │ │
│ │                    │ │ │                                                  │ │
│ └───────────────────┘ │ └──────────────────────────────────────────────────┘ │
├───────────────────────┴──────────────────────────────────────────────────────┤
│ Drag canvas to pan | Wheel: vertical | Shift+Wheel: horizontal | Ctrl+Wheel  │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 2. Loaded Pipeline Workspace

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ File  Help                                                                    │
├───────────────────────┬──────────────────────────────────────────────────────┤
│ Pipeline Explorer     │ tfesupernightjpegpipeline          Nodes 42 Links 58 │
│ Search and double...  │ 1 JSON files loaded                  Zoom 100%       │
│ ┌───────────────────┐ │ ┌──────────────────────────────────────────────────┐ │
│ │ ipe               │ │ │  ┌───────────┐     ╭──────╮     ┌───────────┐   │ │
│ └───────────────────┘ │ │  │ Sensor_0  │─────╯      ╰────▶│ IFE_0     │   │ │
│ ▾ UseCase             │ │  │ in/out... │                 │ ports...  │   │ │
│   tfesupernight...    │ │  └───────────┘                 └───────────┘   │ │
│   rawhdrjpeg...       │ │       │                              │          │ │
│ ▾ NCFJsonUses         │ │       ╰────────────▶┌───────────┐◀──╯          │ │
│   motioncapture...    │ │                     │ IPE_0     │              │ │
│                       │ │                     └───────────┘              │ │
├───────────────────────┴──────────────────────────────────────────────────────┤
│ Drag canvas to pan | Wheel: vertical | Shift+Wheel: horizontal | Ctrl+Wheel  │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 3. Node Property Hover

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Canvas                                                                       │
│                                                                              │
│       ┌──────────────────────┐                                               │
│       │ IFE_0                │◀──────────────╮                               │
│       │ input ports          │               │                               │
│       │ output ports         │               │                               │
│       └──────────────────────┘               │                               │
│              ┌────────────────────────────────────────────┐                  │
│              │ Node: IFE_0                                │                  │
│              │ Name: DisableSensorCrop                    │                  │
│              │ Id: 102                                    │                  │
│              │ Type: UINT                                 │                  │
│              │ Value: 0                                   │                  │
│              └────────────────────────────────────────────┘                  │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 4. Narrow Window Behavior

```text
┌────────────────────────────────────────────────────────┐
│ File  Help                                             │
├────────────────┬───────────────────────────────────────┤
│ Pipeline       │ Selected pipeline         Zoom 85%    │
│ Explorer       │ ┌───────────────────────────────────┐ │
│ ┌────────────┐ │ │ Grid canvas keeps panning and      │ │
│ │ Filter     │ │ │ topology visible. Secondary metric │ │
│ └────────────┘ │ │ text may compress first.           │ │
│ Tree           │ └───────────────────────────────────┘ │
└────────────────┴───────────────────────────────────────┘
```

## Interaction Map

| Interaction | Result |
|-------------|--------|
| `Ctrl+O` | Open XML pipeline file |
| `Ctrl+Alt+O` | Open one or more JSON pipeline files |
| Type in filter | Hide non-matching UseCase/Pipeline tree items |
| Double-click pipeline | Render the selected topology |
| Drag canvas | Pan freely |
| Mouse wheel | Pan vertically |
| `Shift+Wheel` | Pan horizontally |
| `Ctrl+Wheel` | Zoom the full topology |
| Hover node | Show delayed property card |
