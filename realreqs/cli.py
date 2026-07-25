import argparse
import os

from .scanner import scan_project
from .stdlib_filter import filter_third_party_imports
from .resolver import resolve_all


def build_requirements_content(resolved: dict[str, str]) -> str:
    """
    Format resolved packages into requirements.txt content.
    """
    lines = [f"{name}=={version}" for name, version in sorted(resolved.items())]
    return "\n".join(lines) + "\n"


def run(project_dir: str, output_file: str, assume_yes: bool = False, verbose: bool = False) -> None:
    """
    Scan the project and safely generate a requirements.txt file.
    """
    if not os.path.isdir(project_dir):
        print(f"Error: '{project_dir}' is not a valid directory.")
        return

    print(f"Scanning {project_dir} for imports...")
    all_imports = scan_project(project_dir)

    if not all_imports:
        print(f"\nNo Python files or imports found in '{project_dir}'.")
        print("Check that this is the correct project directory. No file was written.")
        return

    third_party = filter_third_party_imports(all_imports, project_dir)

    if not third_party:
        print(
            "\nNo third-party dependencies detected — this project appears to use "
            "only the standard library and/or local modules."
        )
        if not assume_yes:
            response = input("Write an empty requirements.txt anyway? [y/N]: ").strip().lower()
            if response != "y":
                print("No file was written.")
                return
        else:
            print("Proceeding (--yes passed): writing empty requirements.txt.")

    output_path = os.path.join(project_dir, output_file)

    if os.path.exists(output_path) and not assume_yes:
        response = input(
            f"\n'{output_file}' already exists at {output_path}. Overwrite? [y/N]: "
        ).strip().lower()
        if response != "y":
            print("No file was written.")
            return

    resolved, unresolved = resolve_all(third_party)
    content = build_requirements_content(resolved)

    if verbose:
        print(f"\n({len(third_party)} import path(s) scanned, resolved to {len(resolved)} package(s))")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        print(f"\nError: could not write to '{output_path}': {e}")
        return

    print(f"\nWrote {len(resolved)} package(s) to {output_path}")

    if unresolved:
        print(f"\nWarning: {len(unresolved)} import(s) could not be resolved automatically:")
        for name in sorted(unresolved):
            print(f"  - {name}")
        print("These may need to be added to requirements.txt manually.")


def main():
    """
    Parse command-line arguments and start the requirements generator.
    """
    parser = argparse.ArgumentParser(
        prog="realreqs",
        description="Generate an accurate requirements.txt by reading real installed package metadata - no guessing, no PyPI lookups.",
    )

    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="Path to the project directory to scan (default: current directory).",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="requirements.txt",
        help="Output filename (default: requirements.txt).",
    )

    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation prompts (for scripts and automated workflows).",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show additional detail about import scanning and resolution.",
    )

    args = parser.parse_args()
    run(args.project_dir, args.output, assume_yes=args.yes, verbose=args.verbose)


if __name__ == "__main__":
    main()