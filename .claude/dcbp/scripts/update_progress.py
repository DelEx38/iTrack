#!/usr/bin/env python3
"""
DCBP - Script de mise à jour de progression.

Usage:
    python update_progress.py <task_id> <step_num> <step_name> <status>

Exemple:
    python update_progress.py 01-add-auth 01 context in_progress
    python update_progress.py 01-add-auth 01 context complete
"""

import sys
import os
from datetime import datetime
from pathlib import Path


def get_dcbp_root() -> Path:
    """Trouve le dossier .claude/dcbp le plus proche."""
    current = Path.cwd()
    while current != current.parent:
        dcbp_path = current / ".claude" / "dcbp"
        if dcbp_path.exists():
            return dcbp_path
        current = current.parent
    raise FileNotFoundError(".claude/dcbp folder not found")


def update_progress(task_id: str, step_num: str, step_name: str, status: str):
    """Met à jour le fichier de progression d'une tâche."""
    dcbp = get_dcbp_root()
    output_dir = dcbp / "output" / "dev" / task_id

    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    step_file = output_dir / f"{step_num}-{step_name}.md"
    timestamp = datetime.now().isoformat()

    if status == "in_progress":
        # Créer ou mettre à jour le fichier
        header = f"# Step {step_num}: {step_name.title()}\n\n"
        header += f"**Started:** {timestamp}\n"
        header += f"**Status:** 🔄 In Progress\n\n"
        header += "---\n\n"

        if not step_file.exists():
            step_file.write_text(header)
        print(f"✓ Started step {step_num}-{step_name}")

    elif status == "complete":
        # Ajouter le footer de complétion
        content = step_file.read_text() if step_file.exists() else ""
        footer = f"\n\n---\n\n"
        footer += f"**Completed:** {timestamp}\n"
        footer += f"**Status:** ✓ Complete\n"

        # Remplacer le status in_progress par complete
        content = content.replace("**Status:** 🔄 In Progress", "**Status:** ✓ Complete")
        content += footer

        step_file.write_text(content)
        print(f"✓ Completed step {step_num}-{step_name}")

    else:
        print(f"Unknown status: {status}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)

    task_id = sys.argv[1]
    step_num = sys.argv[2]
    step_name = sys.argv[3]
    status = sys.argv[4]

    try:
        update_progress(task_id, step_num, step_name, status)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
