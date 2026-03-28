---
name: etat
description: "Vue d'ensemble rapide du projet DCBP. Affiche l'état actuel, les tâches en cours et les prochaines étapes."
allowed-tools: Read, Glob
---

# /etat - Vue d'Ensemble du Projet

Affiche un résumé complet de l'état du projet.

## Workflow

### Phase 1: Collect
1. Lire `.claude/dcbp/PROJECT.md` - contexte général
2. Lire `.claude/dcbp/PROGRESS.md` - dernières sessions
3. Lire `.claude/dcbp/TASKS.md` - état du backlog
4. Lire `.claude/dcbp/ISSUES.md` - bugs ouverts

### Phase 2: Summarize
1. Résumer l'état actuel du projet
2. Lister les tâches en cours
3. Lister les blocages éventuels
4. Suggérer les prochaines actions

## Template de sortie

```markdown
## Status: [nom projet]

### Dernière activité
- Date: ...
- Résumé: ...

### En cours
- [ ] Tâche 1
- [ ] Tâche 2

### Blocages
- Aucun / Liste...

### Bugs ouverts
- X critique(s), Y majeur(s)

### Prochaines étapes suggérées
1. ...
2. ...
```
