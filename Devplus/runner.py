import subprocess
import sys
from pathlib import Path
import os


def load_env_file():
    """
    Load variables from .env into the environment
    used by the project subprocess.
    """

    env = os.environ.copy()

    env_file = Path.cwd() / ".env"

    if not env_file.exists():
        return env

    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Ignore empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Ignore invalid lines
            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            key = key.strip()
            value = value.strip()

            # Remove surrounding quotes
            if (
                len(value) >= 2
                and value[0] == value[-1]
                and value[0] in ('"', "'")
            ):
                value = value[1:-1]

            env[key] = value

    return env


def detect_command(project_type):
    """
    Detect a simple command to start the project.
    """

    root = Path.cwd()

    if project_type == "Python":

        if (root / "main.py").exists():
            return [sys.executable, "main.py"]

        if (root / "app.py").exists():
            return [sys.executable, "app.py"]

        if (root / "run.py").exists():
            return [sys.executable, "run.py"]

        return None

    if project_type == "Node.js":

        package_json = root / "package.json"

        if package_json.exists():
            return ["npm", "run", "dev"]

    return None


def run_project(project_type):

    command = detect_command(project_type)

    if command is None:
        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": "Could not automatically detect project entry point.",
            "command": None,
        }

    print(f"Running: {' '.join(command)}")

    try:

        # Load .env before starting the user's project
        env = load_env_file()

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )

        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": command,
        }

    except subprocess.TimeoutExpired as e:

        return {
            "success": False,
            "return_code": -1,
            "stdout": e.stdout or "",
            "stderr": "Process timed out after 30 seconds.",
            "command": command,
        }

    except Exception as e:

        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": str(e),
            "command": command,
        }