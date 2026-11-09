---
type: Reference
title: Scraper result contract
description: The shared scraper result shape and its use by the rename-script generator.
tags: [python, scrapers, ScrapeResult, generate_rename_script, renaming]
sources:
  - id: scrapers
    resource: ../scrapers.py
  - id: generator
    resource: ../generate_rename_script.py
generated:
  by: codex/gpt-6
  at: 2026-11-09T12:38:36Z
---

# Shared interface

`scrapers.py` defines `ScrapeResult` as a `TypedDict` with `title: str`,
`performers: list[str]`, and `source: str`. The abstract
`BaseScraper.fetch_info()` returns `ScrapeResult | None`.[^scrapers]

`BaseScraper._get_soup()` uses requests and Beautiful Soup's `html.parser`.
It reports `requests.exceptions.RequestException` and returns `None` on that
failure. `_get_meta_content()` checks that a metadata value is a string, and
`_extract_unique_performers()` returns sorted, unique names. Reuse these
helpers when extending the existing scrapers.[^scrapers]

# Consumer

`generate_rename_script.py` tries `DMMScraper`, `AVWikiScraper`,
`AVWikiDBScraper`, and `MissAVScraper` in that order, accepting the first result
with a title. It then removes performer names from the title and constructs
rename commands. A change to the result shape must account for this
consumer.[^generator]

The generator reads an input file list and writes a sibling `.sh` file after
successful lookups. Its output includes `mv -f` commands using the configured
`DEST_DIR`; generating the file does not execute those commands. Review the
generated paths and overwrite behavior before running it.[^generator]

# Evidence limits

These facts were read from source on 2026-11-09. They do not establish that
external sites are reachable or that their HTML still matches the parsers.
The existing broad exception handlers in the consumer are observations, not
a new recommendation to use broad catches. No live scraping or file moves
were used to establish this concept.

[^scrapers]: [Shared scraper implementation](../scrapers.py).
[^generator]: [Rename-script consumer](../generate_rename_script.py).
