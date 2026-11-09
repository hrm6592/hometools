---
type: Reference
title: Python environment and constraints
description: Python and dependency declarations, platform constraints, and known documentation discrepancies.
tags: [python, uv, dependencies, testing, windows, unix]
sources:
  - id: project
    resource: ../pyproject.toml
  - id: version
    resource: ../.python-version
  - id: lock
    resource: ../uv.lock
  - id: readme
    resource: ../README.md
  - id: attributes
    resource: ../.gitattributes
  - id: ignore
    resource: ../.gitignore
generated:
  by: codex/gpt-6
  at: 2026-11-09T12:47:36Z
---

# Declared environment

Observed in repository configuration on 2026-11-09:

- Python requirement: `==3.15.2`; interpreter pin: `3.15.2`.
  The project runtime is pinned to this exact patch version.[^project][^version]
- Direct dependencies: `beautifulsoup4>=4.15.0` and `requests>=2.34.2`.
  `uv.lock` contains the resolved dependencies.[^project][^lock]
- Build backend: `uv_build`, constrained to `>=0.12.12,<0.13.0`.[^project]
- Pyright targets Python `3.15`, uses `standard` checking, and looks for
  `.venv` under the project directory. Its language-version setting remains
  `3.15`; the runtime patch pin is specified separately.[^project]

When changing the runtime or dependencies, inspect the declarations and lockfile
together. The [scraper contract](scraper-contract.md) identifies the shared
Python consumers of requests and Beautiful Soup.

# Platform and validation boundaries

The README identifies `check_video.py` and `clear_torrent_files.py` as Unix
scripts because of `syslog`, and lists external dependencies for other tools.
Installing Python packages alone does not establish cross-platform support.[^readme]

The checked-in line-ending rule specifically sets `mem4screen.sh` to
`text eol=lf`. It is not a repository-wide rule for every script.[^attributes]

The existing user instruction requires test filenames to start with `test_`.
However, `.gitignore` excludes `test_*` as well as `test/`. A locally passing
test may therefore be absent from a clone. Report this conflict and inspect
`git check-ignore` and `git ls-files` before relying on shared test coverage;
do not silently rename tests or change the ignore policy.[^ignore]

# Known documentation discrepancies

The README's Python version now agrees with the `3.15.2` pin. It still says
dependencies are empty and requests is undeclared, contrary to the dependency
configuration above. This remaining discrepancy is not a resolved decision to
change dependencies or rewrite that README section. Recheck both sources when
working on setup and report the difference before resolving it.[^readme][^project][^version]

The README mentions a mail-search regression test, but `test_*` files are
ignored. Confirm its availability separately; the documented command alone is
not evidence of tracked coverage.[^readme][^ignore]

The observations are source-backed; no independent verification event or
successful full-project build is asserted.

[^project]: [Project and type-checker configuration](../pyproject.toml).
[^version]: [Interpreter pin](../.python-version).
[^lock]: [Dependency lockfile](../uv.lock).
[^readme]: [Runtime and usage documentation](../README.md).
[^attributes]: [Git line-ending policy](../.gitattributes).
[^ignore]: [Ignore patterns](../.gitignore).
