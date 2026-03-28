---
name: review
description: "Revue de code structurée."
argument-hint: "<fichier ou dossier>"
allowed-tools: Read, Glob, Grep
---

# /review - Revue de Code

Revue de code structurée.

## Usage

```
/review <fichier ou dossier>
/review -a <cible>    # Mode autonome
```

## Workflow

### Phase 1: Scope
1. Identifier les fichiers à reviewer
2. Comprendre le contexte des changements
3. Définir les critères de revue

### Phase 2: Analyze
1. Vérifier la qualité du code
2. Détecter les bugs potentiels
3. Évaluer la lisibilité
4. Vérifier les conventions
5. Classifier les problèmes par sévérité

### Phase 3: Report
1. Générer le rapport de revue
2. Calculer le score de qualité
3. Mettre à jour ISSUES.md si problèmes critiques
4. Mettre à jour PROGRESS.md

## Classification des problèmes

| Sévérité | Description |
|----------|-------------|
| Critique | Bug, faille sécurité, crash |
| Majeur | Performance, mauvaise pratique |
| Mineur | Style, nommage, documentation |
| Suggestion | Amélioration optionnelle |
