import json
import os
from pathlib import Path

print("\nDevPulse Demo Application")
print("=" * 50)


# --------------------------------------------------
# 1. Dependency check
# --------------------------------------------------

try:
    import rich
except ImportError:
    raise RuntimeError(
        "Required Python package 'rich' is not installed."
    )

print("Dependency check passed")


# --------------------------------------------------
# 2. Environment variable check
# --------------------------------------------------

database_url = os.environ.get("DATABASE_URL")

if not database_url:
    raise RuntimeError(
        "Required environment variable 'DATABASE_URL' is not set."
    )

print("Environment variables validated")


# --------------------------------------------------
# 3. Configuration check
# --------------------------------------------------

config_file = Path("config.json")

if not config_file.exists():
    raise RuntimeError(
        "config.json was not found."
    )

with open(config_file, "r") as f:
    config = json.load(f)


required_port = 8000
actual_port = config.get("port")

if actual_port != required_port:
    raise RuntimeError(
        f"Application requires PORT={required_port}, "
        f"but config.json contains PORT={actual_port}"
    )

print("Configuration validated")


# --------------------------------------------------
# 4. Simulated application startup
# --------------------------------------------------

print("\nStarting application...")

print(f"Database: {database_url}")
print(f"Server configured on port {actual_port}")

print("\n" + "=" * 50)
print("APPLICATION STARTED SUCCESSFULLY")
print("=" * 50)