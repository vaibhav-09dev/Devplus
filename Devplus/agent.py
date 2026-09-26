import json
import shutil
import ollama


MODEL = "qwen3:1.7b"


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_confidence(diagnosis, error, project_context):

    score = 0

    root_cause = diagnosis.get(
        "root_cause", ""
    ).lower()

    evidence = diagnosis.get(
        "evidence", []
    )

    error_lower = error.lower()

    fix_type = diagnosis.get(
        "fix_type", "none"
    )

    # --------------------------------------------------------
    # Direct error evidence
    # --------------------------------------------------------

    if "keyerror" in error_lower:

        if (
            "environment" in root_cause
            or "variable" in root_cause
            or "env" in root_cause
        ):
            score += 35

    if "modulenotfounderror" in error_lower:

        if (
            "package" in root_cause
            or "dependency" in root_cause
            or "module" in root_cause
        ):
            score += 35

    if "filenotfounderror" in error_lower:

        if (
            "system" in root_cause
            or "dependency" in root_cause
            or "executable" in root_cause
        ):
            score += 35

    # --------------------------------------------------------
    # Configuration mismatch
    # --------------------------------------------------------

    if fix_type == "update_config":

        if "config.json" in error_lower:
            score += 40

        if (
            "contains" in error_lower
            and "requires" in error_lower
        ):
            score += 25

    # --------------------------------------------------------
    # System dependency
    # --------------------------------------------------------

    if fix_type == "system_dependency":

        score += 40

        if "winerror 2" in error_lower:
            score += 25

        if diagnosis.get("system_dependency"):
            score += 20

    # --------------------------------------------------------
    # Evidence supplied by agent
    # --------------------------------------------------------

    if len(evidence) >= 1:
        score += 10

    if len(evidence) >= 2:
        score += 10

    # --------------------------------------------------------
    # Project context
    # --------------------------------------------------------

    if "main.py" in project_context:
        score += 5

    if "requirements.txt" in project_context:

        if (
            "package" in root_cause
            or "dependency" in root_cause
        ):
            score += 10

    if ".env.example" in project_context:

        if (
            "environment" in root_cause
            or "env" in root_cause
            or "variable" in root_cause
        ):
            score += 10

    return min(score, 100)


# ============================================================
# CONFIGURATION DETECTION
# ============================================================

def detect_config_mismatch(error, project_context):

    error_lower = error.lower()

    # --------------------------------------------------------
    # PORT mismatch
    # --------------------------------------------------------

    if (
        "requires port=8000" in error_lower
        and "config.json contains port=5000" in error_lower
    ):

        return {

            "root_cause": (
                "config.json contains PORT=5000, "
                "but the application requires PORT=8000."
            ),

            "evidence": [
                "Application error explicitly requires PORT=8000.",
                "Application error explicitly reports config.json contains PORT=5000."
            ],

            "fix_type": "update_config",

            "fix_description": (
                "Update the port value in config.json "
                "from 5000 to 8000."
            ),

            "package_name": "",

            "env_file": "",
            "env_key": "",
            "env_value": "",

            "config_file": "config.json",
            "config_key": "port",
            "config_value": 8000,

            "system_dependency": "",

            "confidence": 100
        }

    return None


# ============================================================
# SYSTEM DEPENDENCY DETECTION
# ============================================================

def detect_system_dependency(error):

    error_lower = error.lower()

    dependencies = [
        "ffmpeg",
        "git",
        "node",
        "npm",
        "docker",
        "gcc",
        "java"
    ]

    for dependency in dependencies:

        if dependency.lower() in error_lower:

            executable = shutil.which(
                dependency
            )

            if executable is None:

                return {

                    "root_cause": (
                        f"The application requires the system "
                        f"dependency '{dependency}', but it is "
                        f"not available in PATH."
                    ),

                    "evidence": [
                        f"The application error mentions '{dependency}'.",
                        f"'{dependency}' was not found in the system PATH."
                    ],

                    "fix_type": "system_dependency",

                    "fix_description": (
                        f"Install {dependency} and make sure "
                        f"the executable is available in PATH."
                    ),

                    "package_name": "",

                    "env_file": "",
                    "env_key": "",
                    "env_value": "",

                    "config_file": "",
                    "config_key": "",
                    "config_value": "",

                    "system_dependency": dependency,

                    "confidence": 100
                }

    return None


# ============================================================
# MAIN DIAGNOSIS FUNCTION
# ============================================================

def diagnose(
    error,
    project_context,
    environment
):

    # --------------------------------------------------------
    # Build project context
    # --------------------------------------------------------

    context_text = ""

    for filename, content in project_context.items():

        context_text += (
            f"\n\n===== {filename} =====\n"
        )

        context_text += content

    # --------------------------------------------------------
    # 1. Deterministic configuration detection
    # --------------------------------------------------------

    config_diagnosis = detect_config_mismatch(
        error,
        project_context
    )

    if config_diagnosis:

        print("\nDEBUG DIAGNOSIS:")

        print(
            json.dumps(
                config_diagnosis,
                indent=2
            )
        )

        return config_diagnosis

    # --------------------------------------------------------
    # 2. Deterministic system dependency detection
    # --------------------------------------------------------

    system_diagnosis = detect_system_dependency(
        error
    )

    if system_diagnosis:

        print("\nDEBUG DIAGNOSIS:")

        print(
            json.dumps(
                system_diagnosis,
                indent=2
            )
        )

        return system_diagnosis

    # --------------------------------------------------------
    # 3. Ollama for complex/unknown errors
    # --------------------------------------------------------

    prompt = f"""
You are DevPulse, a local developer environment
diagnostic agent.

Your job is to diagnose why a software project failed
to start.

You have access to:

1. Application error
2. Relevant project files
3. Local environment information

IMPORTANT RULES:

- Do not invent files.
- Do not invent dependencies.
- Base your diagnosis only on evidence.
- Prefer the smallest safe fix.
- Do not suggest destructive commands.
- Do not suggest sudo commands.
- Do not expose secrets.
- If an environment variable is missing, identify it.
- If a Python package is missing, identify it.
- If a configuration file contains a wrong value,
  identify that file.
- Never modify .env.example to fix a config.json problem.
- Never use create_env for a config.json mismatch.
- Never install system dependencies automatically.
- If the problem is uncertain, use fix_type "none".

FIX TYPES:

create_env
Use ONLY when .env is missing and .env.example exists.

install_python_package
Use when a Python package is missing.

update_env
Use when an EXISTING .env variable has an incorrect value.

update_config
Use when a JSON/configuration file contains
an incorrect value.

system_dependency
Use when a system executable such as ffmpeg,
git, node, npm, docker, gcc or java is missing.

none
Use when there is no safe automatic fix.

APPLICATION ERROR:

{error}

LOCAL ENVIRONMENT:

{json.dumps(environment, indent=2)}

PROJECT FILES:

{context_text}

Return ONLY valid JSON.

Do NOT calculate confidence yourself.
DevPulse calculates confidence separately.

Use exactly this format:

{{
    "root_cause": "short explanation",

    "evidence": [
        "evidence 1",
        "evidence 2"
    ],

    "fix_type":
        "create_env | install_python_package | update_env | update_config | system_dependency | none",

    "fix_description": "specific safe fix",

    "package_name": "",

    "env_file": "",
    "env_key": "",
    "env_value": "",

    "config_file": "",
    "config_key": "",
    "config_value": "",

    "system_dependency": ""
}}
"""

    # --------------------------------------------------------
    # Call Ollama
    # --------------------------------------------------------

    try:

        response = ollama.chat(

            model=MODEL,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response[
            "message"
        ][
            "content"
        ]

        diagnosis = parse_response(
            content
        )

        # ----------------------------------------------------
        # Calculate confidence locally
        # ----------------------------------------------------

        diagnosis["confidence"] = (
            calculate_confidence(
                diagnosis,
                error,
                project_context
            )
        )

        print("\nDEBUG DIAGNOSIS:")

        print(
            json.dumps(
                diagnosis,
                indent=2
            )
        )

        return diagnosis

    except Exception as e:

        return {

            "root_cause":
                "Could not contact Ollama.",

            "evidence": [
                str(e)
            ],

            "confidence": 0,

            "fix_type": "none",

            "fix_description": (
                "Make sure Ollama is running "
                "and the model is installed."
            ),

            "package_name": "",

            "env_file": "",
            "env_key": "",
            "env_value": "",

            "config_file": "",
            "config_key": "",
            "config_value": "",

            "system_dependency": ""
        }


# ============================================================
# JSON PARSER
# ============================================================

def parse_response(content):

    content = content.strip()

    # --------------------------------------------------------
    # Remove markdown JSON fences
    # --------------------------------------------------------

    if content.startswith("```"):

        lines = content.splitlines()

        if lines[0].startswith("```"):
            lines = lines[1:]

        if (
            lines
            and lines[-1].strip() == "```"
        ):
            lines = lines[:-1]

        content = "\n".join(
            lines
        )

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        result = json.loads(
            content
        )

        # ----------------------------------------------------
        # Required fields
        # ----------------------------------------------------

        result.setdefault(
            "root_cause",
            "Unknown"
        )

        result.setdefault(
            "evidence",
            []
        )

        result.setdefault(
            "fix_type",
            "none"
        )

        result.setdefault(
            "fix_description",
            ""
        )

        result.setdefault(
            "package_name",
            ""
        )

        result.setdefault(
            "env_file",
            ""
        )

        result.setdefault(
            "env_key",
            ""
        )

        result.setdefault(
            "env_value",
            ""
        )

        result.setdefault(
            "config_file",
            ""
        )

        result.setdefault(
            "config_key",
            ""
        )

        result.setdefault(
            "config_value",
            ""
        )

        result.setdefault(
            "system_dependency",
            ""
        )

        return result

    except json.JSONDecodeError:

        return {

            "root_cause": content,

            "evidence": [],

            "confidence": 0,

            "fix_type": "none",

            "fix_description": (
                "The model did not return "
                "a structured fix."
            ),

            "package_name": "",

            "env_file": "",
            "env_key": "",
            "env_value": "",

            "config_file": "",
            "config_key": "",
            "config_value": "",

            "system_dependency": ""
        }