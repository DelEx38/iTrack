---
name: archive
description: "Archive les anciennes sessions de PROGRESS.md pour économiser des tokens."
argument-hint: "[nombre_sessions_a_garder]"
allowed-tools: Read, Edit, Write
---

# /archive - Archivage de PROGRESS.md

Archive les anciennes sessions pour garder PROGRESS.md léger et économiser des tokens.

## Usage

```
/archive        # Garde les 5 dernières sessions (défaut)
/archive 3      # Garde les 3 dernières sessions
/archive 10     # Garde les 10 dernières sessions
```

## Workflow

### Phase 1: Analyser PROGRESS.md
1. Lire `.claude/dcbp/PROGRESS.md`
2. Identifier chaque session par le pattern `## [YYYY-MM-DD]`
3. Compter le nombre total de sessions
4. Si sessions ≤ N à garder → rien à archiver, terminer

### Phase 2: Séparer les sessions
1. Garder les N dernières sessions (plus récentes)
2. Archiver les autres (plus anciennes)

### Phase 3: Créer l'archive
1. Créer/mettre à jour `.claude/dcbp/archive/PROGRESS-{YYYY-MM}.md`
2. Grouper les sessions archivées par mois
3. Conserver l'ordre chronologique inverse

### Phase 4: Mettre à jour PROGRESS.md
1. Garder le header (titre + description)
2. Garder uniquement les N dernières sessions

### Phase 5: Afficher le résumé

```markdown
╔════════════════════════════════════════════════════════════╗
║  ARCHIVAGE TERMINÉ                                         ║
╚════════════════════════════════════════════════════════════╝

Sessions avant  : X
Sessions après  : Y (gardées)
Sessions archivées : Z

Fichiers modifiés :
- .claude/dcbp/PROGRESS.md (réduit)
- .claude/dcbp/archive/PROGRESS-YYYY-MM.md (créé/mis à jour)

Estimation tokens économisés : ~[estimation]

───────────────────────────────────────────────────────────────
Conseil : Lancez /archive quand PROGRESS.md dépasse 10 KB
╚═════════════════════════════════════════════════════════════╝
```

## Notes
- Ne jamais supprimer de sessions, toujours archiver
- Tokens économisés ≈ (taille archivée en bytes) / 3.5
