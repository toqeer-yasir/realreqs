import importlib.metadata
from collections import defaultdict


def build_import_to_distribution_map() -> dict[str, list[str]]:
    """
    Return a mapping of top-level import names to the installed distributions
    that provide them.
    """
    return importlib.metadata.packages_distributions()


def find_owning_distribution(full_import_path: str, candidate_distributions: list[str]) -> str | None:
    """
    Return the distribution that provides the given import path.

    This resolves namespace packages by checking which candidate distribution
    contains the requested module or package.
    """
    path_as_module = full_import_path.replace(".", "/") + ".py"
    path_as_package = full_import_path.replace(".", "/") + "/__init__.py"

    for dist_name in candidate_distributions:
        try:
            dist = importlib.metadata.distribution(dist_name)
        except importlib.metadata.PackageNotFoundError:
            continue

        if dist.files is None:
            continue

        installed_paths = {str(f) for f in dist.files}

        if any(p.endswith(path_as_module) or p.endswith(path_as_package) for p in installed_paths):
            return dist_name

    return None


def resolve_all(import_paths: set[str]) -> tuple[dict[str, str], set[str]]:
    """
    Resolve import paths to installed package versions.

    Returns a mapping of distribution names to versions, along with any
    unresolved top-level imports.
    """
    mapping = build_import_to_distribution_map()

    resolved = {}
    unresolved = set()

    by_top_level = defaultdict(list)
    for path in import_paths:
        by_top_level[path.split(".")[0]].append(path)

    for top_level, full_paths in sorted(by_top_level.items()):
        if top_level not in mapping:
            unresolved.add(top_level)
            continue

        distribution_names = mapping[top_level]

        if len(distribution_names) == 1:
            candidates = {distribution_names[0]}
        else:
            candidates = set()
            for full_path in full_paths:
                owner = find_owning_distribution(full_path, distribution_names)
                if owner:
                    candidates.add(owner)

            if not candidates:
                normalized = top_level.replace("_", "-").lower()
                exact_match = next(
                    (d for d in distribution_names if d.replace("_", "-").lower() == normalized),
                    None,
                )
                candidates = {exact_match or distribution_names[0]}

        for dist_name in candidates:
            try:
                version = importlib.metadata.version(dist_name)
                resolved[dist_name] = version
            except importlib.metadata.PackageNotFoundError:
                continue

        if not any(c in resolved for c in candidates):
            unresolved.add(top_level)

    return resolved, unresolved