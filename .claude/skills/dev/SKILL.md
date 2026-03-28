---
name: dev
description: "Développement structuré d'une fonctionnalité en plusieurs phases."
argument-hint: "<description de la feature>"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

# /dev - Développement Structuré

Développement d'une fonctionnalité en 7 phases.

## Usage

```
/dev <description de la feature>
/dev -a <feature>     # Mode autonome (sans confirmations)
/dev -r <task_id>     # Reprendre une tâche
```

## Workflow

### Phase 1: Init
1. Générer un task_id unique (DEV-XXX)
2. Parser les flags (-a, -s, -r)
3. Créer le contexte initial

### Phase 2: Context
1. Lire PROJECT.md pour le contexte projet
2. Lire PROGRESS.md pour l'historique récent
3. Analyser les fichiers pertinents
4. Identifier les patterns existants

### Phase 3: Design
1. Définir l'approche technique
2. Lister les fichiers à créer/modifier
3. Identifier les dépendances
4. Demander confirmation (sauf mode -a)

### Phase 4: Implement
1. Suivre le plan établi
2. Respecter les conventions du projet
3. Créer/modifier les fichiers nécessaires

### Phase 5: Verify
1. Exécuter les linters
2. Lancer les tests
3. Vérifier le build

### Phase 6: Review
1. Auto-revue du code
2. Détecter les problèmes potentiels
3. Suggérer des améliorations

### Phase 7: Complete
1. Mettre à jour PROGRESS.md
2. Mettre à jour TASKS.md
3. Documenter les décisions dans DECISIONS.md si nécessaire
