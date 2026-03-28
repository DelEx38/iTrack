#!/usr/bin/env python3
"""
DCBP - Script de synchronisation de la mémoire.

Usage:
    python sync_memory.py [--quick]

Options:
    --quick     Synchronisation rapide (derniers commits seulement)

Ce script:
1. Analyse les changements git récents
2. Met à jour PROGRESS.md avec un résumé
3. Détecte les patterns récurrents
"""

import subprocess
import sys
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


def run_git(cmd: list) -> str:
    """Exécute une commande git et retourne la sortie."""
    try:
        result = subprocess.run(
            ["git"] + cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def get_recent_commits(limit: int = 5) -> list:
    """Récupère les commits récents."""
    output = run_git(["log", f"-{limit}", "--oneline"])
    if not output:
        return []
    return output.split("\n")


def get_changed_files(since: str = "HEAD~5") -> list:
    """Récupère les fichiers modifiés."""
    output = run_git(["diff", "--name-only", since])
    if not output:
        return []
    return output.split("\n")


def sync_memory(quick: bool = False):
    """Synchronise la mémoire avec l'état git."""
    dcbp = get_dcbp_root()
    progress_file = dcbp / "PROGRESS.md"

    if not progress_file.exists():
        print("PROGRESS.md not found", file=sys.stderr)
        return

    # Récupérer les infos git
    commits = get_recent_commits(3 if quick else 10)
    changed_files = get_changed_files("HEAD~3" if quick else "HEAD~10")
    branch = run_git(["branch", "--show-current"])

    # Créer le résumé
    timestamp = datetime.now().isoformat()
    summary = f"""
---

## Sync {timestamp[:10]}

### Branche actuelle
`{branch}`

### Commits récents
"""
    for commit in commits:
        summary += f"- {commit}\n"

    summary += f"""
### Fichiers modifiés ({len(changed_files)})
"""
    for f in changed_files[:10]:
        summary += f"- `{f}`\n"

    if len(changed_files) > 10:
        summary += f"- ... et {len(changed_files) - 10} autres\n"

    # Ajouter au PROGRESS.md
    content = progress_file.read_text()

    # Trouver le premier "---" après le header et insérer après
    lines = content.split("\n")
    insert_idx = 0
    found_first = False
    for i, line in enumerate(lines):
        if line.strip() == "---":
            if found_first:
                insert_idx = i + 1
                break
            found_first = True

    if insert_idx > 0:
        lines.insert(insert_idx, summary)
        content = "\n".join(lines)
        progress_file.write_text(content)
        print(f"✓ Synchronized PROGRESS.md")
        print(f"  - {len(commits)} commits")
        print(f"  - {len(changed_files)} files changed")
    else:
        print("Could not find insertion point in PROGRESS.md", file=sys.stderr)


def main():
    quick = "--quick" in sys.argv

    try:
        sync_memory(quick)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
