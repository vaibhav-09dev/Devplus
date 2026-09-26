from pathlib import Path
import json
import re
import sys


def build_dependency_graph(project_context):

    nodes = []
    edges = []

    # Root
    nodes.append({
        "id": "app",
        "label": "Application",
        "type": "application",
        "status": "active"
    })

    # ------------------------------------------------
    # Python dependencies
    # ------------------------------------------------

    requirements = project_context.get(
        "requirements.txt",
        ""
    )

    if requirements:

        nodes.append({
            "id": "python_deps",
            "label": "Python Packages",
            "type": "category",
            "status": "active"
        })

        edges.append({
            "source": "app",
            "target": "python_deps"
        })

        for line in requirements.splitlines():

            line = line.strip()

            if not line or line.startswith("#"):
                continue

            # Remove version specifier
            package = re.split(
                r"[<>=!~]",
                line
            )[0].strip()

            if not package:
                continue

            package_id = (
                "package_"
                + package.lower().replace("-", "_")
            )

            installed = check_package(package)

            nodes.append({
                "id": package_id,
                "label": package,
                "type": "package",
                "status": (
                    "healthy"
                    if installed
                    else "missing"
                )
            })

            edges.append({
                "source": "python_deps",
                "target": package_id
            })

    # ------------------------------------------------
    # Environment
    # ------------------------------------------------

    if ".env.example" in project_context:

        nodes.append({
            "id": "environment",
            "label": "Environment",
            "type": "category",
            "status": "active"
        })

        edges.append({
            "source": "app",
            "target": "environment"
        })

        env_content = project_context[
            ".env.example"
        ]

        for line in env_content.splitlines():

            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key = line.split(
                "=",
                1
            )[0].strip()

            key_id = (
                "env_"
                + key.lower()
            )

            nodes.append({
                "id": key_id,
                "label": key,
                "type": "environment_variable",
                "status": "configured"
            })

            edges.append({
                "source": "environment",
                "target": key_id
            })

    # ------------------------------------------------
    # JSON configuration
    # ------------------------------------------------

    if "config.json" in project_context:

        nodes.append({
            "id": "config",
            "label": "Configuration",
            "type": "category",
            "status": "active"
        })

        edges.append({
            "source": "app",
            "target": "config"
        })

        try:

            config = json.loads(
                project_context["config.json"]
            )

            for key, value in config.items():

                key_id = (
                    "config_"
                    + str(key).lower()
                )

                nodes.append({
                    "id": key_id,
                    "label": f"{key}: {value}",
                    "type": "configuration",
                    "status": "configured"
                })

                edges.append({
                    "source": "config",
                    "target": key_id
                })

        except json.JSONDecodeError:
            pass

    return {
        "nodes": nodes,
        "edges": edges
    }


def check_package(package):

    try:

        __import__(
            package.replace("-", "_")
        )

        return True

    except ImportError:

        return False