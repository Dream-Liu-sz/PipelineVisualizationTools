# Pipeline Visualization Tools - Documentation Hub

Welcome to the documentation for **Pipeline Visualization Tools**, a PyQt5-based desktop application for visualizing Qualcomm Camera Pipeline configurations.

## Quick Navigation

| Category | Document | Description |
|----------|----------|-------------|
| **Project** | [Requirements](project/requirements.md) | Functional requirements and user stories |
| | [Architecture](project/architecture.md) | System architecture and design patterns |
| | [Tech Stack](project/tech_stack.md) | Technologies, libraries, and tools |
| | [API Specification](project/api_spec.md) | File format specifications (XML/JSON) |
| | [Data Schema](project/database_schema.md) | Data models and structures |
| | [Design Guidelines](project/design_guidelines.md) | UI/UX design patterns |
| | [Runbook](project/runbook.md) | Installation, configuration, and operations |
| **Reference** | [ADRs](reference/adrs/) | Architecture Decision Records |
| | [Guides](reference/guides/) | Technical guides and how-tos |
| | [Manuals](reference/manuals/) | User and operator manuals |
| | [Research](reference/research/) | Research notes and explorations |
| **Tasks** | [Task Management](tasks/README.md) | Task tracking and planning |

## Document Dependency Graph

```
README.md (root)
├── project/
│   ├── requirements.md      ← Functional scope
│   ├── architecture.md      ← Depends on requirements.md
│   ├── tech_stack.md        ← Supports architecture.md
│   ├── api_spec.md          ← Depends on architecture.md
│   ├── database_schema.md   ← Depends on architecture.md
│   ├── design_guidelines.md ← Depends on requirements.md
│   └── runbook.md           ← Depends on tech_stack.md, architecture.md
├── reference/
│   ├── adrs/                ← Depends on architecture.md
│   ├── guides/              ← Independent, topic-specific
│   ├── manuals/             ← Depends on runbook.md
│   └── research/            ← Independent, exploratory
└── tasks/
    └── README.md            ← Independent
```

## Documentation Standards

- All documents follow the [Documentation Standards](documentation_standards.md) (if available)
- Use Markdown format with clear headings and tables
- Keep documents up-to-date with code changes
- No code blocks exceeding 5 lines (implementation details go in source code)

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-05-19 | Initial documentation creation |
