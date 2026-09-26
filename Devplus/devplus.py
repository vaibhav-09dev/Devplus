import typer
from dependency_graph import build_dependency_graph

from scanner import (
    scan_project,
    read_relevant_files,
)

from runner import run_project
from agent import diagnose
from fixer import apply_fix


app = typer.Typer(
    help="DevPulse - Agentic Local Setup & Bug Diagnostics"
)


MAX_ATTEMPTS = 5


@app.command()
def init():

    print()
    print("⚡ DevPulse")
    print("=" * 55)

    # --------------------------------------------------
    # 1. Scan project
    # --------------------------------------------------

    print("\n🔍 Scanning project...")

    project = scan_project()

    print(f"✓ Project type: {project['project_type']}")
    print(f"✓ Files found: {len(project['files'])}")

    environment = project["environment"]

    print(f"✓ OS: {environment['os']}")
    print(f"✓ Python: {environment['python_version']}")

    # --------------------------------------------------
    # 2. Initial project context
    # --------------------------------------------------

    print("\n📂 Reading project configuration...")

    context = read_relevant_files(
        project["files"]
    )
    graph = build_dependency_graph(context)
    print("\n📊 DEPENDENCY GRAPH")
    print("-" * 55)

    for node in graph["nodes"]: 
       print(
        f"{node['label']} "
        f"[{node['status']}]"
    )

    for filename in context:
        print(f"✓ {filename}")

    # --------------------------------------------------
    # 3. Agentic repair loop
    # --------------------------------------------------

    for attempt in range(1, MAX_ATTEMPTS + 1):

        print("\n")
        print("=" * 55)
        print(f"🔄 REPAIR ATTEMPT {attempt}/{MAX_ATTEMPTS}")
        print("=" * 55)

        # --------------------------------------------------
        # Run application
        # --------------------------------------------------

        print("\n🚀 Starting application...")
        print("-" * 55)

        result = run_project(
            project["project_type"]
        )

        # --------------------------------------------------
        # SUCCESS
        # --------------------------------------------------

        if result["success"]:

            print("\n" + "=" * 55)
            print("🎉 APPLICATION STARTED SUCCESSFULLY")
            print("=" * 55)

            print(
                "\nDevPulse verified that the application "
                "runs successfully."
            )

            return

        # --------------------------------------------------
        # ERROR
        # --------------------------------------------------

        print("\n❌ Application failed.")

        error = result["stderr"]

        if result["stdout"]:

            error += (
                "\n\nSTDOUT:\n"
                + result["stdout"]
            )

        print("\nError:")
        print(error[:5000])

        # --------------------------------------------------
        # Refresh project context
        # --------------------------------------------------
        # Important:
        # After every fix, files such as .env or
        # config.json may have changed.

        try:

            project = scan_project()

            context = read_relevant_files(
                project["files"]
            )

        except Exception as e:

            print(
                f"\n⚠ Could not refresh project context: {e}"
            )

        # --------------------------------------------------
        # AI Diagnosis
        # --------------------------------------------------

        print(
            "\n🤖 Analyzing locally with Ollama..."
        )

        print("-" * 55)

        diagnosis = diagnose(
            error=error,
            project_context=context,
            environment=environment,
        )

        # --------------------------------------------------
        # Display diagnosis
        # --------------------------------------------------

        print("\n🔍 ROOT CAUSE")
        print("-" * 55)

        print(
            diagnosis.get(
                "root_cause",
                "Unknown"
            )
        )

        # --------------------------------------------------
        # Evidence
        # --------------------------------------------------

        print("\n📌 EVIDENCE")
        print("-" * 55)

        evidence = diagnosis.get(
            "evidence",
            []
        )

        for item in evidence:

            print(f"  • {item}")

        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------

        print(
            f"\nConfidence: "
            f"{diagnosis.get('confidence', 0)}%"
        )

        # --------------------------------------------------
        # Proposed fix
        # --------------------------------------------------

        print("\n🔧 PROPOSED FIX")
        print("-" * 55)

        print(
            diagnosis.get(
                "fix_description",
                "No fix available."
            )
        )

        fix_type = diagnosis.get(
            "fix_type",
            "none"
        )

        # --------------------------------------------------
        # No automatic fix
        # --------------------------------------------------

        if fix_type == "none":

            print(
                "\n❌ No automatic fix available."
            )

            print(
                "DevPulse cannot safely repair "
                "this problem automatically."
            )

            return

        # --------------------------------------------------
        # User approval
        # --------------------------------------------------

        print()

        approved = typer.confirm(
            "Apply this fix?"
        )

        if not approved:

            print(
                "\n⏹ Fix rejected."
            )

            return

        # --------------------------------------------------
        # Apply fix
        # --------------------------------------------------

        print("\n🛠 Applying fix...")

        fix_result = apply_fix(
            diagnosis
        )

        if not fix_result["success"]:

            print(
                f"\n❌ Fix failed:\n"
                f"{fix_result['message']}"
            )

            return

        print(
            f"✓ {fix_result['message']}"
        )

        # --------------------------------------------------
        # IMPORTANT:
        # Do NOT stop here.
        #
        # The for-loop automatically starts another
        # attempt and discovers the next error.
        # --------------------------------------------------

        print(
            "\n✓ Fix applied."
        )

        print(
            "🔄 Continuing diagnostic loop..."
        )

    # --------------------------------------------------
    # Maximum attempts reached
    # --------------------------------------------------

    print("\n" + "=" * 55)
    print("❌ MAXIMUM REPAIR ATTEMPTS REACHED")
    print("=" * 55)

    print(
        f"\nDevPulse attempted "
        f"{MAX_ATTEMPTS} repairs."
    )

    print(
        "Manual investigation may be required."
    )


if __name__ == "__main__":
    app()