---
name: bugfix
description: "Investigation et correction de bugs."
argument-hint: "<description du bug>"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

# /bugfix - Investigation de Bugs

Investigation et correction de bugs.

## Usage

```
/bugfix <description du bug>
/bugfix -a <bug>       # Mode autonome
/bugfix -r <bug_id>    # Reprendre un debug
```

## Workflow

### Phase 1: Reproduce
1. Comprendre le bug décrit
2. Identifier les étapes de reproduction
3. Confirmer le comportement attendu vs actuel
4. Vérifier ISSUES.md pour bugs similaires

### Phase 2: Investigate
1. Localiser le code concerné
2. Analyser les causes possibles
3. Identifier la cause racine
4. Documenter les findings

### Phase 3: Fix
1. Implémenter le correctif
2. S'assurer de ne pas introduire de régression
3. Ajouter des tests si nécessaire

### Phase 4: Verify
1. Vérifier que le bug est corrigé
2. Exécuter les tests
3. Mettre à jour ISSUES.md
4. Mettre à jour PROGRESS.md
