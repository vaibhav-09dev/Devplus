from pathlib import Path
import subprocess
import sys
import shutil
import json

def handle_system_dependency(diagnosis):

    dependency = diagnosis.get(
        "system_dependency",
        "unknown"
    )

    print("\n⚠ SYSTEM DEPENDENCY")
    print("-" * 55)

    print(
        f"DevPulse detected that '{dependency}' "
        "is required by the application."
    )

    print(
        f"'{dependency}' is not available in your "
        "system PATH."
    )

    print("\nDevPulse will not automatically modify "
          "your system.")

    print("\nRecommended action:")

    if dependency == "ffmpeg":

        print("""
1. Install FFmpeg.
2. Add FFmpeg's bin directory to PATH.
3. Restart your terminal.
4. Run DevPulse again.
""")

    elif dependency == "node":

        print("""
Install Node.js and make sure `node` is available
from your terminal.
""")

    elif dependency == "git":

        print("""
Install Git and make sure `git` is available
from your terminal.
""")

    elif dependency == "docker":

        print("""
Install Docker Desktop and make sure Docker is
running.
""")

    else:

        print(
            f"Install '{dependency}' and make sure "
            "it is available in PATH."
        )

    return {
        "success": False,
        "manual_action_required": True,
        "message": (
            f"System dependency '{dependency}' "
            "requires manual installation."
        ),
    }
def apply_fix(diagnosis):

    fix_type = diagnosis.get("fix_type")

    if fix_type == "create_env":
        return create_env_file(diagnosis)

    if fix_type == "install_python_package":
        return install_python_package(diagnosis)

    if fix_type == "update_env":
        return update_env_variable(diagnosis)

    if fix_type == "update_config":
        return update_config_file(diagnosis)
    if fix_type == "system_dependency":
        return handle_system_dependency(diagnosis)

    return {
        "success": False,
        "message": "No automatic fix available.",
    }


def create_env_file(diagnosis):

    root = Path.cwd()

    env_example = root / ".env.example"
    env_file = root / ".env"

    if not env_example.exists():
        return {
            "success": False,
            "message": ".env.example does not exist.",
        }

    if env_file.exists():
        return {
            "success": False,
            "message": ".env already exists.",
        }

    try:

        shutil.copy(env_example, env_file)

        return {
            "success": True,
            "message": "Created .env from .env.example.",
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }


def install_python_package(diagnosis):

    package_name = diagnosis.get(
        "package_name", ""
    ).strip()

    if not package_name:
        return {
            "success": False,
            "message": "No package name provided by the agent.",
        }

    # Basic safety check
    if any(
        character in package_name
        for character in [";", "&", "|", "`", ">", "<"]
    ):
        return {
            "success": False,
            "message": "Unsafe package name rejected.",
        }

    print(
        f"\nInstalling Python package: {package_name}"
    )

    try:

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                package_name,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0:

            return {
                "success": True,
                "message": f"Installed {package_name}.",
            }

        return {
            "success": False,
            "message": result.stderr,
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }


def update_env_variable(diagnosis):

    root = Path.cwd()

    env_file = root / ".env"

    key = diagnosis.get(
        "env_key", ""
    ).strip()

    value = str(
        diagnosis.get("env_value", "")
    ).strip()

    if not key:
        return {
            "success": False,
            "message": "No environment variable key provided.",
        }

    if not value:
        return {
            "success": False,
            "message": "No environment variable value provided.",
        }

    if not env_file.exists():
        return {
            "success": False,
            "message": ".env does not exist.",
        }

    if any(
        character in key
        for character in ["=", "\n", "\r"]
    ):
        return {
            "success": False,
            "message": "Unsafe environment variable key rejected.",
        }

    if "\n" in value or "\r" in value:
        return {
            "success": False,
            "message": "Unsafe environment variable value rejected.",
        }

    try:

        lines = env_file.read_text(
            encoding="utf-8"
        ).splitlines()

        updated = False
        new_lines = []

        for line in lines:

            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                new_lines.append(line)
                continue

            if "=" not in line:
                new_lines.append(line)
                continue

            current_key = line.split(
                "=", 1
            )[0].strip()

            if current_key == key:

                new_lines.append(
                    f"{key}={value}"
                )

                updated = True

            else:

                new_lines.append(line)

        if not updated:

            new_lines.append(
                f"{key}={value}"
            )

        env_file.write_text(
            "\n".join(new_lines) + "\n",
            encoding="utf-8",
        )

        return {
            "success": True,
            "message": f"Updated {key} in .env.",
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }


def update_config_file(diagnosis):

    root = Path.cwd()

    config_file = diagnosis.get(
        "config_file", ""
    ).strip()

    config_key = diagnosis.get(
        "config_key", ""
    ).strip()

    config_value = diagnosis.get(
        "config_value"
    )

    # -----------------------------------------
    # Validate AI output
    # -----------------------------------------

    if not config_file:

        return {
            "success": False,
            "message": "No configuration file provided.",
        }

    if not config_key:

        return {
            "success": False,
            "message": "No configuration key provided.",
        }

    config_path = root / config_file

    # -----------------------------------------
    # Security: only allow JSON files
    # -----------------------------------------

    if config_path.suffix.lower() != ".json":

        return {
            "success": False,
            "message": "Only JSON configuration files can be automatically modified.",
        }

    if not config_path.exists():

        return {
            "success": False,
            "message": f"{config_file} does not exist.",
        }

    try:

        # -----------------------------------------
        # Read JSON
        # -----------------------------------------

        with open(
            config_path,
            "r",
            encoding="utf-8"
        ) as f:

            config = json.load(f)

        # -----------------------------------------
        # Make sure key exists
        # -----------------------------------------

        if config_key not in config:

            return {
                "success": False,
                "message": (
                    f"Configuration key "
                    f"'{config_key}' not found "
                    f"in {config_file}."
                ),
            }

        old_value = config[config_key]

        # -----------------------------------------
        # Apply change
        # -----------------------------------------

        config[config_key] = config_value

        # -----------------------------------------
        # Write JSON
        # -----------------------------------------

        with open(
            config_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                config,
                f,
                indent=4
            )

        return {
            "success": True,
            "message": (
                f"Updated {config_file}: "
                f"{config_key} "
                f"{old_value} -> "
                f"{config_value}"
            ),
        }

    except json.JSONDecodeError:

        return {
            "success": False,
            "message": (
                f"{config_file} contains invalid JSON."
            ),
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }