---
name: docs
description: "Génération de documentation Python (docstrings, README, API docs)."
argument-hint: "<fichier, module ou 'readme'>"
allowed-tools: Read, Edit, Write, Glob, Grep
---

# /docs - Documentation Python

Génération et mise à jour de documentation pour projets Python.

## Usage

```
/docs auth.py              # Docstrings pour un fichier
/docs src/services/        # Documenter un module
/docs readme               # Générer/mettre à jour README
/docs api                  # Générer doc API
/docs -s google            # Style Google (défaut)
/docs -s numpy             # Style NumPy
/docs -a <cible>           # Mode autonome
```

## Workflow

### Phase 1: Analyze
1. Identifier le type de documentation demandé
2. Lire le code source
3. Détecter le style de docstrings existant (Google, NumPy, Sphinx)
4. Identifier les éléments à documenter :
   - Modules (description, exports)
   - Classes (purpose, attributes)
   - Fonctions (params, returns, raises)
   - Constantes importantes

### Phase 2: Generate

#### Pour les docstrings :
1. Générer les docstrings manquantes
2. Compléter les docstrings incomplètes
3. Format selon le style choisi

#### Pour README :
1. Analyser la structure du projet
2. Détecter les dépendances (requirements.txt, pyproject.toml)
3. Identifier les points d'entrée
4. Générer les sections standard

#### Pour API docs :
1. Extraire toutes les interfaces publiques
2. Générer la documentation de référence
3. Ajouter des exemples d'utilisation

### Phase 3: Review
1. Vérifier la cohérence des descriptions
2. S'assurer que tous les paramètres sont documentés
3. Vérifier les types (si typing présent)

### Phase 4: Apply
1. Appliquer les modifications
2. Ne pas modifier le code fonctionnel

### Phase 5: Report
```
╔════════════════════════════════════════════════════════════╗
║  DOCUMENTATION GÉNÉRÉE                                     ║
╚════════════════════════════════════════════════════════════╝

Style : Google
Cible : src/auth/

## Éléments documentés
- 3 modules
- 8 classes
- 24 fonctions
- 5 constantes

## Fichiers modifiés
- src/auth/__init__.py (module docstring)
- src/auth/handlers.py (+12 docstrings)
- src/auth/models.py (+8 docstrings)

## Statistiques
| Type | Avant | Après |
|------|-------|-------|
| Documenté | 45% | 98% |
| Complet | 20% | 95% |

───────────────────────────────────────────────────────────────
→ Manquant : [éléments non documentés, si any]
╚═════════════════════════════════════════════════════════════╝
```

## Styles de docstrings

### Google (défaut)
```python
def function(param1: str, param2: int) -> bool:
    """Description courte.

    Description longue si nécessaire.

    Args:
        param1: Description du premier paramètre.
        param2: Description du second paramètre.

    Returns:
        Description de la valeur retournée.

    Raises:
        ValueError: Si param2 est négatif.
    """
```

### NumPy
```python
def function(param1: str, param2: int) -> bool:
    """
    Description courte.

    Parameters
    ----------
    param1 : str
        Description du premier paramètre.
    param2 : int
        Description du second paramètre.

    Returns
    -------
    bool
        Description de la valeur retournée.

    Raises
    ------
    ValueError
        Si param2 est négatif.
    """
```

## Structure README

```markdown
# Nom du Projet

Description courte.

## Installation

## Usage

## Configuration

## API Reference

## Contributing

## License
```

## Notes
- Préférer Google style pour les nouveaux projets
- Documenter le "pourquoi", pas le "quoi"
- Inclure des exemples pour les fonctions complexes
- Garder les descriptions concises mais complètes
