---
type: Playbook
title: Maintaining project knowledge
description: How to retrieve, update, and check this OKF v0.2 bundle without mandatory tooling.
tags: [okf, knowledge, retrieval, maintenance, validation]
sources:
  - id: okf-spec
    resource: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md
    title: Open Knowledge Format v0.2
  - id: project-rules
    resource: ../AGENTS.md
generated:
  by: codex/gpt-6
  at: 2026-11-09T12:38:36Z
---

# Scope and format

`knowledge/` is the bundle root. [AGENTS.md](../AGENTS.md) holds behavior rules;
the existing README remains the user-facing tool reference. This playbook
implements the requested knowledge workflow, not historical design rationale.
The official v0.2 specification was checked on 2026-11-09.[^okf-spec][^project-rules]

Every non-reserved Markdown file represents one concept with UTF-8 YAML
frontmatter. Only a non-empty string `type` is always required. Titles,
descriptions, tags, sources, trust, and lifecycle fields are optional in OKF;
this project uses a small subset for discoverability and provenance.[^okf-spec]

`index.md` and `log.md` are reserved. The root index declares
`okf_version: "0.2"`; its body groups link lists under headings. Other indexes
have no frontmatter. The log has newest-first `YYYY-MM-DD` date headings and
no concept metadata. Concept IDs are paths without `.md`.[^okf-spec]

# Retrieve only what the task needs

1. Search an already available OKF CLI/MCP scoped to this bundle, or inspect
   [index.md](index.md). No particular CLI or MCP is required.
2. Match the task to index descriptions or frontmatter before reading bodies.
3. Read only matching concepts, then only the sources needed for the change.
   Read the log only for history and this playbook only for maintenance.
4. If the index is missing, list filenames and inspect metadata. If tooling or
   knowledge is unavailable, report the gap and continue from project sources.

PowerShell examples from the repository root; these produce bounded output:

```powershell
rg -n -i 'python|dependencies' knowledge/index.md
Get-Content -LiteralPath knowledge/python-environment.md
# Metadata discovery when the index does not identify a useful concept:
rg -n '^(type|title|description|tags):' knowledge -g '*.md'
```

Use file-relative links such as `scraper-contract.md` within this flat bundle.
OKF also permits `/path.md` relative to the bundle root, not the repository
root. Sources outside the bundle use paths such as `../pyproject.toml`;
distribute the enclosing repository to keep these resolvable.[^okf-spec]

# Update confirmed knowledge

1. Search the index and metadata for duplicates. Update the existing concept
   whenever it already owns the subject; link to README instead of copying it.
2. Check the relevant implementation, configuration, or confirmed decision.
   Report disagreements; do not silently decide which intended behavior wins.
3. Keep one subject per concept. Record evidence in `sources`, with stable `id`
   values and matching footnotes for claims. Say what was observed, when, and
   what remains unconfirmed. Do not persist transient notes or guesses as facts.
4. Update `generated` for a meaningful content change using the actual actor
   and an ISO 8601 datetime with an explicit offset. Never invent a human review.
   `verified` records an actual independent content check, not a YAML check.
   Without it the OKF trust tier is unverified, even for source-backed text.
   If content changes, make clear which previous checks still apply.
5. `status: draft`, `stable`, and `deprecated` are lifecycle signals, not trust
   tiers. Optional `stale_after` is an offset-aware datetime. Recheck stale
   material against sources; do not turn staleness into a development blocker.
6. Update index descriptions and the dated log as needed. Preserve incoming
   links when changing paths. Ask before large restructures or deletions.
7. Validate and report the scope and limitations of the checks.[^project-rules][^okf-spec]

# Validation without installing dependencies

Use a compatible OKF validator if one is already available. Otherwise use an
existing YAML parser for frontmatter and review the index/log structure and
links separately. A YAML parser alone is not a full OKF validator. Do not
require optional fields, reject unknown types/keys, or treat a missing index
or broken link as grounds to reject the entire bundle. Fix broken local links
as a maintenance issue.[^okf-spec]

The following checks concept frontmatter with an interpreter that already has
PyYAML. Run it from the repository root, replacing `python` with that
interpreter's path if needed. It does not install anything:

```powershell
@'
from pathlib import Path
import yaml

count = 0
for path in Path("knowledge").rglob("*.md"):
    if path.name in {"index.md", "log.md"}:
        continue
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{path}: missing frontmatter")
    end = lines.index("---", 1)
    data = yaml.safe_load("\n".join(lines[1:end]))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: metadata is not a mapping")
    kind = data.get("type")
    if not isinstance(kind, str) or not kind.strip():
        raise ValueError(f"{path}: type must be a non-empty string")
    count += 1
if not count:
    raise ValueError("No concepts found; check the working directory")
print(f"Frontmatter OK: {count} concepts; review indexes, logs and links separately")
'@ | python -
```

Check index entries against filenames and descriptions, log dates/order,
Markdown links, source paths, and footnote IDs. Search a representative task
in the index and confirm it leads to the intended concept without reading the
whole bundle. Review `git diff --check` and ensure unrelated source and
configuration files are untouched. Do not execute operational scripts merely
to validate documentation. If a check is unavailable, state that limitation.

[^okf-spec]: [Official specification, sections 3-9 and 11-12](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md).
[^project-rules]: [Project knowledge rules](../AGENTS.md).
