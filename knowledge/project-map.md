---
type: Reference
title: Project map
description: Where scripts, user documentation, configuration, and local-only files live.
tags: [architecture, scripts, documentation, layout]
sources:
  - id: readme
    resource: ../README.md
  - id: project
    resource: ../pyproject.toml
  - id: ignore
    resource: ../.gitignore
generated:
  by: codex/gpt-6
  at: 2026-11-09T12:38:36Z
---

# Scope

Tools is a collection of independently invoked scripts, with Python, Bash,
Perl, PowerShell, batch, and CoffeeScript files at the repository root.
The user-facing tool inventory and execution examples belong in
[README.md](../README.md); follow its relevant section instead of duplicating
that inventory here.[^readme]

# Navigation

- For tool usage, external commands, fixed paths, and operational effects, read
  the relevant README section and the named script.[^readme]
- For Python configuration and known documentation drift, read
  [Python environment and constraints](python-environment.md).[^project]
- For the rename generator's shared result type, read
  [Scraper result contract](scraper-contract.md).
- For knowledge changes, read [Maintaining project knowledge](maintaining-knowledge.md).

# Repository boundaries

`pyproject.toml` declares a `tools = "tools:main"` entry point. The ignore rules
exclude `src/`, so local package files are not necessarily available in a fresh
clone. Do not assume the entry point is the interface to every script.[^project][^ignore]

The ignore rules also exclude `test/`, `test_*`, `.venv/`, `.vscode/`, caches,
and `.mix_feed_state.json`. Check whether a local test or environment file is
tracked before relying on its presence elsewhere.[^ignore]

These are source-backed observations made on 2026-11-09, not an inferred
architecture rationale or a claim that all legacy tools run on this machine.
No independent verification event is asserted in the frontmatter.

[^readme]: [User documentation](../README.md).
[^project]: [Project metadata](../pyproject.toml).
[^ignore]: [Ignore rules](../.gitignore).
