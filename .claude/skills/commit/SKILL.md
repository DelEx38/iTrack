---
name: commit
description: "Commits intelligents avec messages conventionnels et vérifications."
argument-hint: "[message optionnel]"
allowed-tools: Read, Glob, Grep, Bash
---

# /commit - Commits Intelligents

Création de commits avec messages conventionnels, analyse des changements et vérifications.

## Usage

```
/commit                    # Analyse et propose un message
/commit "fix: bug auth"    # Utilise le message fourni
/commit -a                 # Mode autonome (commit direct)
```

## Workflow

### Phase 1: Analyze
1. Exécuter `git status` pour voir les fichiers modifiés
2. Exécuter `git diff --staged` pour les changements stagés
3. Si rien n'est stagé, exécuter `git diff` pour les changements non stagés
4. Identifier le type de changement (feat, fix, refactor, docs, test, chore)

### Phase 2: Validate
1. Vérifier qu'il n'y a pas de fichiers sensibles (.env, secrets, credentials)
2. Vérifier que les changements ne sont pas trop volumineux (suggérer split si > 10 fichiers)
3. Vérifier la cohérence des changements (un seul concern par commit)

### Phase 3: Stage
1. Si fichiers non stagés, proposer les fichiers à stager
2. Demander confirmation (sauf mode -a)
3. Exécuter `git add` sur les fichiers sélectionnés

### Phase 4: Commit
1. Générer un message suivant Conventional Commits :
   - `feat:` nouvelle fonctionnalité
   - `fix:` correction de bug
   - `refactor:` refactoring sans changement fonctionnel
   - `docs:` documentation
   - `test:` ajout/modification de tests
   - `chore:` maintenance, dépendances
   - `style:` formatage, linting
2. Format : `type(scope): description courte`
3. Ajouter body si changements complexes
4. Demander confirmation du message (sauf mode -a)
5. Exécuter le commit

### Phase 5: Report
Afficher :
```
╔════════════════════════════════════════════════════════════╗
║  COMMIT CRÉÉ                                               ║
╚════════════════════════════════════════════════════════════╝

Hash    : [short hash]
Message : [message]
Fichiers: [nombre] fichiers modifiés

[liste des fichiers]

───────────────────────────────────────────────────────────────
→ Prochain: git push | /commit (autres changements)
╚═════════════════════════════════════════════════════════════╝
```

## Conventional Commits

| Type | Description |
|------|-------------|
| feat | Nouvelle fonctionnalité |
| fix | Correction de bug |
| docs | Documentation uniquement |
| style | Formatage (pas de changement de code) |
| refactor | Refactoring (pas de feat ni fix) |
| test | Ajout ou correction de tests |
| chore | Maintenance, dépendances, config |

## Notes
- Ne jamais committer de fichiers sensibles
- Préférer des commits atomiques (un seul concern)
- Le scope est optionnel : `feat(auth): add login`
