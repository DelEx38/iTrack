---
name: test
description: "Génération et exécution de tests Python (pytest/unittest)."
argument-hint: "<fichier ou fonction à tester>"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

# /test - Tests Python

Génération, exécution et analyse de tests Python.

## Usage

```
/test auth.py              # Génère des tests pour auth.py
/test src/                  # Teste tout le dossier src/
/test -r                    # Lance tous les tests existants
/test -c                    # Affiche la couverture
/test -a <cible>            # Mode autonome
```

## Workflow

### Phase 1: Detect
1. Détecter le framework de test (pytest > unittest)
2. Identifier la structure de tests existante (tests/, test_*, *_test.py)
3. Vérifier pytest.ini ou setup.cfg pour la configuration
4. Identifier les fixtures et helpers existants

### Phase 2: Analyze
1. Lire le fichier/module cible
2. Identifier les fonctions/classes à tester
3. Analyser les dépendances et imports
4. Identifier les cas edge cases

### Phase 3: Generate
1. Créer/mettre à jour le fichier de test correspondant
2. Générer les tests unitaires :
   - Tests des cas nominaux (happy path)
   - Tests des cas d'erreur
   - Tests des edge cases
3. Utiliser les fixtures existantes si disponibles
4. Ajouter les mocks nécessaires

### Phase 4: Execute
1. Exécuter les tests : `pytest <fichier> -v`
2. Capturer les résultats
3. Si échecs, analyser et proposer des corrections

### Phase 5: Coverage (si -c)
1. Exécuter : `pytest --cov=<module> --cov-report=term-missing`
2. Analyser les lignes non couvertes
3. Suggérer des tests supplémentaires

### Phase 6: Report
```
╔════════════════════════════════════════════════════════════╗
║  TESTS TERMINÉS                                            ║
╚════════════════════════════════════════════════════════════╝

Résultat : ✅ PASSED (ou ❌ FAILED)

Tests    : X passed, Y failed, Z skipped
Durée    : X.XXs
Coverage : XX% (si -c)

───────────────────────────────────────────────────────────────

## Fichiers de test créés/modifiés
- tests/test_auth.py (+15 tests)

## Lignes non couvertes (si -c)
- auth.py:45-50 (error handling)
- auth.py:78 (edge case)

───────────────────────────────────────────────────────────────
→ Suggestions : [tests supplémentaires recommandés]
╚═════════════════════════════════════════════════════════════╝
```

## Structure de test recommandée

```python
import pytest
from module import fonction

class TestFonction:
    """Tests pour fonction()"""

    def test_nominal_case(self):
        """Test du cas nominal."""
        result = fonction(valid_input)
        assert result == expected

    def test_edge_case(self):
        """Test des limites."""
        ...

    def test_error_case(self):
        """Test des erreurs."""
        with pytest.raises(ExpectedException):
            fonction(invalid_input)
```

## Notes
- Préférer pytest à unittest
- Nommer les tests de manière descriptive
- Un test = un comportement
- Utiliser des fixtures pour le setup commun
