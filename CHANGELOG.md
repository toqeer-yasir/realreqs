# Changelog

## [0.1.2] - 2026-07-25

### Fixed

- Correctly resolves imports from **namespace packages that span multiple
  distributions** (e.g. `langgraph`, where `langgraph.checkpoint.postgres.aio`
  is actually provided by the separate `langgraph-checkpoint-postgres`
  distribution, not the base `langgraph` package). Previously, only the
  top-level import name was tracked, so submodule-specific dependencies
  belonging to different distributions under the same namespace were
  silently missed.
- The scanner now preserves the full dotted import path (e.g.
  `langgraph.checkpoint.postgres.aio`) instead of collapsing it to the
  top-level name (`langgraph`) immediately, so the resolver has enough
  information to disambiguate cases where multiple distributions share a
  namespace.
- The resolver now checks each candidate distribution's actual installed
  file listing to determine which one truly provides a given submodule,
  instead of guessing based on name similarity alone.
- Removed a misleading progress message that reported the number of raw
  import _paths_ found as if it were the number of _packages_ resolved,
  which could differ (and confuse users) whenever a project imports
  multiple submodules from the same underlying package.

### Added

- `-v` / `--verbose` flag to show additional detail about how many import
  paths were scanned versus how many packages they resolved to.

## [0.1.1] - 2026-07-25

### Fixed

- No longer silently writes a misleading `requirements.txt` in ambiguous
  situations:
  - If no Python files or imports are found at all (e.g. wrong directory),
    the tool now prints a clear error and writes no file, instead of
    silently producing an empty one.
  - If imports are found but none resolve to third-party dependencies
    (e.g. a project using only the standard library), the tool now asks
    for confirmation before writing an empty file.
  - If `requirements.txt` already exists at the target location, the tool
    now asks for confirmation before overwriting it, instead of silently
    replacing it.
- File write failures (e.g. permission errors, disk full) now print a
  clear error message instead of crashing with a raw traceback.
- Invalid project directories are now detected up front with a clear
  error message, instead of silently producing an empty result.

### Added

- `-y` / `--yes` flag to skip all confirmation prompts, for use in
  scripts, CI pipelines, or other non-interactive environments.

## [0.1.0] - 2026-07-23

### Added

- Initial release.
- Scans a project directory for imports using Python's `ast` module.
- Filters out standard library modules (via `sys.stdlib_module_names`)
  and the project's own local modules.
- Resolves remaining imports to their real installed package name and
  version using `importlib.metadata` — entirely offline, no PyPI lookups,
  no hardcoded name-mapping tables.
- Reports any unresolved imports clearly instead of guessing.
- CLI command `realreqs`, with optional project path (`realreqs <path>`)
  and custom output filename (`-o`/`--output`).
