---
name: refactor
description: "Refactoring structuré avec analyse, proposition et vérification."
argument-hint: "<fichier ou pattern à refactorer>"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

# /refactor - Refactoring Structuré

Refactoring de code avec analyse des code smells, proposition de changements et vérification.

## Usage

```
/refactor auth.py              # Refactorer un fichier
/refactor src/services/        # Refactorer un dossier
/refactor -t extract-method    # Technique spécifique
/refactor -a <cible>           # Mode autonome
```

## Workflow

### Phase 1: Analyze
1. Lire le code cible
2. Détecter les code smells :
   - Fonctions trop longues (> 30 lignes)
   - Classes trop grandes
   - Duplication de code
   - Nesting excessif (> 3 niveaux)
   - Paramètres trop nombreux (> 4)
   - Magic numbers/strings
   - Dead code
3. Évaluer la complexité cyclomatique
4. Identifier les dépendances

### Phase 2: Propose
1. Lister les refactorings possibles par priorité
2. Pour chaque refactoring, expliquer :
   - Le problème actuel
   - La solution proposée
   - L'impact sur le code
3. Demander confirmation (sauf mode -a)

### Phase 3: Execute
1. Appliquer les refactorings approuvés
2. Techniques disponibles :
   - **Extract Method** : découper une fonction
   - **Extract Class** : séparer les responsabilités
   - **Rename** : améliorer le nommage
   - **Inline** : simplifier les abstractions inutiles
   - **Move** : réorganiser le code
   - **Replace Magic** : constantes nommées
   - **Simplify Conditional** : réduire la complexité

### Phase 4: Verify
1. Vérifier la syntaxe (import du module)
2. Exécuter les tests existants
3. Vérifier que le comportement est identique
4. Si échec, proposer un rollback

### Phase 5: Report
```
╔════════════════════════════════════════════════════════════╗
║  REFACTORING TERMINÉ                                       ║
╚════════════════════════════════════════════════════════════╝

Fichier : auth.py

## Changements appliqués
1. ✅ Extract Method: `_validate_token()` depuis `authenticate()`
2. ✅ Rename: `x` → `user_session`
3. ✅ Replace Magic: `3600` → `SESSION_TIMEOUT`

## Métriques
| Métrique | Avant | Après |
|----------|-------|-------|
| Lignes | 245 | 198 |
| Complexité max | 12 | 6 |
| Fonctions | 8 | 11 |

## Tests
✅ 15/15 tests passent

───────────────────────────────────────────────────────────────
→ Suggestions restantes : [refactorings non appliqués]
╚═════════════════════════════════════════════════════════════╝
```

## Techniques de refactoring

| Technique | Quand l'utiliser |
|-----------|------------------|
| Extract Method | Fonction > 20 lignes, code dupliqué |
| Extract Class | Classe avec multiples responsabilités |
| Rename | Nom non descriptif ou trompeur |
| Inline | Abstraction inutile, indirection excessive |
| Replace Conditional with Polymorphism | Switch/if complexes |
| Introduce Parameter Object | > 3 paramètres liés |

## Notes
- Toujours vérifier les tests après refactoring
- Un refactoring = un commit
- Ne pas changer le comportement (sauf bugs évidents)
- Préférer les petits refactorings incrémentaux
