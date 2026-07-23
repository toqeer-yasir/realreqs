import sys

from .scanner import walk_project


def get_stdlib_module_names() -> set[str]:
    """
    Return the names of modules included with the current Python installation.
    """
    return set(sys.stdlib_module_names)


def get_local_module_names(project_dir: str) -> set[str]:
    """
    Return the names of the project's own Python files and package folders.
    """
    local_names = set()

    for root, dirs, files in walk_project(project_dir):
        for entry in dirs:
            local_names.add(entry)

        for filename in files:
            if filename.endswith(".py"):
                local_names.add(filename[:-3])

    return local_names


def filter_third_party_imports(
    all_imports: set[str],
    project_dir: str,
) -> set[str]:
    """
    Remove standard-library and local modules, leaving only third-party packages.
    """
    stdlib_names = get_stdlib_module_names()
    local_names = get_local_module_names(project_dir)

    third_party = all_imports - stdlib_names - local_names

    return third_party