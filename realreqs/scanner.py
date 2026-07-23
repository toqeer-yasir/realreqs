import ast
import os


#folders that should not be scanned because they don't contain project source code.
SKIP_DIRS = {".venv", "venv", "__pycache__", ".git", "node_modules"}


def walk_project(project_dir: str):
    """
    Walk through the project directory while skipping common non-source folders.
    Yields (root, dirs, files) just like os.walk().
    """
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        yield root, dirs, files


def find_python_files(project_dir: str) -> list[str]:
    """
    Find and return the path of every Python (.py) file in the project.
    """
    python_files = []

    for root, dirs, files in walk_project(project_dir):
        for filename in files:
            if filename.endswith(".py"):
                python_files.append(os.path.join(root, filename))

    return python_files


def extract_imports_from_file(file_path: str) -> set[str]:
    """
    Parse a Python file and return the unique top-level modules it imports.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    tree = ast.parse(source_code, filename=file_path)

    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])

        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                imports.add(node.module.split(".")[0])

    return imports


def scan_project(project_dir: str) -> set[str]:
    """
    Scan all Python files in the project and return every unique imported module.
    """
    all_imports = set()
    python_files = find_python_files(project_dir)

    for file_path in python_files:
        try:
            file_imports = extract_imports_from_file(file_path)
            all_imports.update(file_imports)
        except SyntaxError:
            print(f"Warning: Could not parse {file_path}; skipping.")

    return all_imports