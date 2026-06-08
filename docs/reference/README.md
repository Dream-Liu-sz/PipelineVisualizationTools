# Reference Documentation - Pipeline Visualization Tools

<!-- SCOPE: Reference Hub Document -->
<!-- OWNER: Engineering -->

## Overview

This directory contains reference documentation including Architecture Decision Records (ADRs), technical guides, operator manuals, and research notes.

## Directory Structure

| Directory | Purpose | Content Guidelines |
|-----------|---------|-------------------|
| `adrs/` | Architecture Decision Records | Document significant architectural decisions with context, consequences, and status |
| `guides/` | Technical Guides | Step-by-step guides for specific technical tasks |
| `manuals/` | Operator Manuals | Detailed user instructions and operational procedures |
| `research/` | Research Notes | Exploratory research, technology evaluations, and spike results |

## Architecture Decision Records (adrs/)

### Template

New ADRs should follow this format:

```markdown
# ADR-NNN: Title

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue that we're seeing that is motivating this decision or change?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult to do because of this change?
```

### Existing ADRs

| ADR | Title | Status |
|-----|-------|--------|
| *(None yet)* | | |

## Technical Guides (guides/)

### Suggested Guides

| Guide | Description | Priority |
|-------|-------------|----------|
| Adding a New File Format | How to add support for new pipeline file formats | Medium |
| Customizing Node Colors | How to modify the node color palette | Low |
| Building for Distribution | Complete PyInstaller build guide | Medium |
| Extending the Layout Algorithm | How to modify the node positioning logic | Low |

### Existing Guides

| Guide | Description |
|-------|-------------|
| *(None yet)* | |

## Operator Manuals (manuals/)

### Suggested Manuals

| Manual | Description | Priority |
|--------|-------------|----------|
| User Manual | End-user guide for using the application | High |
| Troubleshooting Manual | Comprehensive troubleshooting procedures | Medium |

### Existing Manuals

| Manual | Description |
|--------|-------------|
| *(None yet)* | |

## Research Notes (research/)

### Suggested Research Topics

| Topic | Description |
|-------|-------------|
| PyQt6 Migration | Feasibility of upgrading from PyQt5 to PyQt6 |
| Web-based Visualization | Exploring browser-based pipeline visualization |
| GPU-Accelerated Rendering | Using OpenGL for large pipeline rendering |

### Existing Research

| Topic | Notes |
|-------|-------|
| *(None yet)* | |

## Maintenance

- Create new reference documents as needed
- Archive outdated documents with clear deprecation notices
- Link reference documents from the main [docs/README.md](../README.md)

<!-- Metadata: Generated 2026-05-19 | Version 1.0.0 -->
