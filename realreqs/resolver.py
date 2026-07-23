import importlib.metadata


def build_import_to_distribution_map() -> dict[str, list[str]]:
    """
    Build a mapping from import names to the installed package(s) that provide them.
    """
    return importlib.metadata.packages_distributions()


def resolve_package(
    import_name: str,
    mapping: dict[str, list[str]],
) -> tuple[str, str] | None:
    """
    Resolve one import name to its package name and installed version.
    """
    if import_name in mapping:
        distribution_names = mapping[import_name]

        normalized_import = import_name.replace("_", "-").lower()

        exact_match = next(
            (
                d
                for d in distribution_names
                if d.replace("_", "-").lower() == normalized_import
            ),
            None,
        )

        distribution_name = exact_match or distribution_names[0]

        try:
            version = importlib.metadata.version(distribution_name)
            return distribution_name, version
        except importlib.metadata.PackageNotFoundError:
            pass

    try:
        version = importlib.metadata.version(import_name)
        return import_name, version
    except importlib.metadata.PackageNotFoundError:
        pass

    return None


def resolve_all(import_names: set[str]) -> tuple[dict[str, str], set[str]]:
    """
    Resolve multiple imports into installed packages and collect any unresolved imports.
    """
    mapping = build_import_to_distribution_map()

    resolved = {}
    unresolved = set()

    for import_name in sorted(import_names):
        result = resolve_package(import_name, mapping)

        if result is not None:
            distribution_name, version = result
            resolved[distribution_name] = version
        else:
            unresolved.add(import_name)

    return resolved, unresolved