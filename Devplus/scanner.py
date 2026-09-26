from pathlib import Path
import os
import sys
import platform


IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".idea",
    ".vscode",
}


def scan_project():
    root = Path.cwd()

    files = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if any(part in IGNORE_DIRS for part in path.parts):
            continue

        files.append(str(path.relative_to(root)))

    project_type = detect_project_type(files)

    return {
        "root": str(root),
        "project_type": project_type,
        "files": files,
        "environment": get_environment(),
    }


def detect_project_type(files):
    files_lower = {file.lower() for file in files}

    # Python project detection
    if (
        "requirements.txt" in files_lower
        or "pyproject.toml" in files_lower
        or "main.py" in files_lower
        or "app.py" in files_lower
        or "run.py" in files_lower
    ):
        return "Python"

    # Node.js project detection
    if "package.json" in files_lower:
        return "Node.js"

    return "Unknown"


def get_environment():
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": sys.version.split()[0],
        "cwd": os.getcwd(),
    }


def read_relevant_files(files):
    context = {}

    important_files = [
        "requirements.txt",
        "pyproject.toml",
        "package.json",
        ".env.example",
        "README.md",
    ]

    for file in files:
        filename = Path(file).name

        if file in important_files or filename in important_files:
            try:
                path = Path(file)

                if path.exists():
                    content = path.read_text(
                        encoding="utf-8",
                        errors="ignore"
                    )

                    # Don't send huge files to the model
                    context[file] = content[:8000]

            except Exception:
                pass

    # Add Python source files
    python_files = [
        file for file in files
        if file.endswith(".py")
    ]

    for file in python_files[:10]:
        try:
            path = Path(file)

            content = path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            context[file] = content[:8000]

        except Exception:
            pass

    return context