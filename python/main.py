"""
Point d'entrée principal de l'application Clinical Study Tracker.
"""

import sys
from pathlib import Path

# Ajouter src au path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from gui.app import main

if __name__ == "__main__":
    main()
