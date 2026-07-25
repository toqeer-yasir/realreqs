# realreqs

Generate an accurate `requirements.txt` by reading real installed package metadata — no guessing, no PyPI lookups, no hardcoded name mappings.

## Why

Tools like `pipreqs` scan your code for imports, which is great — but when it comes time to figure out the _version_ of each package, they rely on a hardcoded, manually-maintained table mapping import names to PyPI package names. That table goes stale fast, especially for fast-moving ecosystems (like LangChain) that split into many sub-packages. When the table doesn't have an entry, these tools silently fall back to asking PyPI for the _latest_ version — which may not be what you actually have installed and tested against.

`realreqs` avoids this entirely by reading your **local environment's own installed package metadata** directly, using Python's built-in `importlib.metadata`. If a package is installed, `realreqs` finds its real name and exact version — no external lookups, no staleness, no guessing.

`realreqs` also correctly handles **namespace packages that span multiple distributions** — for example, `langgraph.checkpoint.postgres.aio` is provided by the separate `langgraph-checkpoint-postgres` distribution, not the base `langgraph` package. Rather than tracking only the top-level import name, `realreqs` checks each candidate distribution's actual installed files to determine which one truly provides the specific submodule your code uses — so sub-package dependencies aren't silently missed.

## Installation

```bash
pip install realreqs
```

## Usage

```bash
realreqs
```

Scans the current directory, finds every third-party import, resolves each to its real installed package name and version, and writes `requirements.txt`.

Optional arguments:

```bash
realreqs /path/to/project        # scan a different directory
realreqs -o deps.txt             # custom output filename
realreqs -y                      # skip confirmation prompts (for scripts/CI)
realreqs -v                      # show additional scan/resolution detail
```

### Confirmation prompts

`realreqs` will ask before:

- Writing an empty `requirements.txt` (no third-party dependencies detected)
- Overwriting an existing `requirements.txt` at the target location

Pass `-y` / `--yes` to skip these prompts automatically — recommended when running `realreqs` as part of an automated script or CI pipeline.

## How it works

1. **Scan** — walks your project and parses every `.py` file with Python's `ast` module to find all import statements, preserving the full dotted path (e.g. `langgraph.checkpoint.postgres.aio`) rather than just the top-level name.
2. **Filter** — removes standard library modules (via `sys.stdlib_module_names`) and your project's own local modules, based on each import's top-level name.
3. **Resolve** — for each remaining import, looks up the real installed distribution name and version using `importlib.metadata`, entirely offline. When a top-level name maps to more than one installed distribution (a shared namespace), `realreqs` checks each candidate's actual installed files to find the one that truly provides the specific submodule used.
4. **Write** — outputs a clean, alphabetically sorted `requirements.txt`.

Any import that can't be resolved (e.g. not actually installed) is reported clearly as a warning, rather than silently guessed.

## Requirements

Python 3.10+ (uses `sys.stdlib_module_names`, added in 3.10).

## License

Copyright (c) 2026 Toqeer Yasir. All rights reserved.

This software is made available for use via PyPI. Modification and
redistribution are not permitted without explicit permission from the author.
