#!/usr/bin/env python3
"""
DCBP - Script d'initialisation de tâche.

Usage:
    python init_task.py <feature_name> [--workflow dev|debug|review]

Exemple:
    python init_task.py add-authentication
    python init_task.py fix-login-bug --workflow debug

Retourne le task_id généré (ex: 01-add-authentication)
"""

import sys
import os
import re
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


def to_kebab_case(text: str) -> str:
    """Convertit un texte en kebab-case."""
    # Remplacer les espaces et underscores par des tirets
    text = re.sub(r'[\s_]+', '-', text)
    # Garder seulement les caractères alphanumériques et tirets
    text = re.sub(r'[^a-zA-Z0-9-]', '', text)
    # Convertir en minuscules
    return text.lower()


def get_next_task_number(output_dir: Path) -> int:
    """Trouve le prochain numéro de tâche disponible."""
    if not output_dir.exists():
        return 1

    existing = list(output_dir.iterdir())
    if not existing:
        return 1

    numbers = []
    for folder in existing:
        if folder.is_dir():
            match = re.match(r'^(\d+)-', folder.name)
            if match:
                numbers.append(int(match.group(1)))

    return max(numbers, default=0) + 1


def init_task(feature_name: str, workflow: str = "dev") -> str:
    """Initialise une nouvelle tâche et retourne le task_id."""
    dcbp = get_dcbp_root()
    output_dir = dcbp / "output" / workflow

    # Créer le dossier output si nécessaire
    output_dir.mkdir(parents=True, exist_ok=True)

    # Générer le task_id
    feature_kebab = to_kebab_case(feature_name)
    task_num = get_next_task_number(output_dir)
    task_id = f"{task_num:02d}-{feature_kebab}"

    # Créer le dossier de la tâche
    task_dir = output_dir / task_id
    task_dir.mkdir(exist_ok=True)

    # Créer le fichier d'init
    timestamp = datetime.now().isoformat()
    init_content = f"""# DCBP {workflow.title()}: {task_id}

**Created:** {timestamp}
**Feature:** {feature_name}
**Workflow:** {workflow}

## Configuration
| Setting | Value |
|---------|-------|
| task_id | {task_id} |
| workflow | {workflow} |

## Progress
| Step | Status | Timestamp |
|------|--------|-----------|
| 00-init | ✓ Complete | {timestamp} |
"""

    init_file = task_dir / "00-init.md"
    init_file.write_text(init_content)

    return task_id


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    feature_name = sys.argv[1]
    workflow = "dev"

    # Parser les arguments optionnels
    if "--workflow" in sys.argv:
        idx = sys.argv.index("--workflow")
        if idx + 1 < len(sys.argv):
            workflow = sys.argv[idx + 1]

    try:
        task_id = init_task(feature_name, workflow)
        print(task_id)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
