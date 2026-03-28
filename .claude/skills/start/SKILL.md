---
name: start
description: "Initialise une nouvelle session de travail. Charge le contexte complet du projet et suggère quoi faire."
allowed-tools: Read, Glob, Grep
---

# /start - Initialisation de Session

Lance une nouvelle session de travail avec tout le contexte nécessaire.

## Workflow

### Phase 1: Charger le contexte
1. Lire `.claude/dcbp/PROJECT.md` - Stack, architecture, conventions
2. Lire `.claude/dcbp/PROGRESS.md` - Dernières sessions (2-3 dernières)
3. Lire `.claude/dcbp/TASKS.md` - Backlog et tâches en cours
4. Lire `.claude/dcbp/ISSUES.md` - Bugs et dette technique
5. Lire `.claude/dcbp/DECISIONS.md` - Décisions architecturales

### Phase 2: Analyser
1. Extraire la dernière session et prochaines étapes
2. Compter les tâches (en cours / à faire / terminées)
3. Identifier les bugs critiques/majeurs
4. Noter les décisions récentes

### Phase 3: Afficher le résumé

Générer un rapport au format suivant :

```markdown
╔════════════════════════════════════════════════════════════╗
║  SESSION DCBP INITIALISÉE                                  ║
╚════════════════════════════════════════════════════════════╝

## Projet : [nom]

**Stack** : [stack résumée]

───────────────────────────────────────────────────────────────

## Dernière session

**[date]** - [titre]

### Ce qui a été fait
- [point 1]
- [point 2]

### Prochaines étapes suggérées
→ [étape 1]
→ [étape 2]

───────────────────────────────────────────────────────────────

## Tâches

### En cours [~]
- [~] [tâche 1]

### À faire (priorité haute)
- [ ] [tâche 2]

**Statistiques** : X en cours | Y à faire | Z terminées

───────────────────────────────────────────────────────────────

## Issues ouvertes

| Sévérité | Count |
|----------|-------|
| Critique | X |
| Majeur | Y |

───────────────────────────────────────────────────────────────

## Suggestions pour cette session

1. **[action prioritaire]** - [raison]
2. **[action secondaire]** - [raison]
3. **[action optionnelle]** - [raison]

───────────────────────────────────────────────────────────────
Skills : /dev <feature> | /debug <bug> | /review <file> | /status
╚═════════════════════════════════════════════════════════════╝
```
