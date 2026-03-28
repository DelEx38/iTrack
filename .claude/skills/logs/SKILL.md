---
name: logs
description: "Analyse de logs, détection de patterns et diagnostic d'erreurs."
argument-hint: "<fichier log ou 'tail'>"
allowed-tools: Read, Glob, Grep, Bash
---

# /logs - Analyse de Logs

Analyse de logs applicatifs, détection de patterns d'erreurs et diagnostic.

## Usage

```
/logs app.log              # Analyser un fichier de log
/logs errors.log -n 100    # Dernières 100 lignes
/logs tail                 # Suivre les logs en temps réel
/logs -e                   # Erreurs uniquement
/logs -p "timeout"         # Filtrer par pattern
/logs -s                   # Statistiques globales
```

## Workflow

### Phase 1: Detect
1. Identifier le format de log :
   - Standard (timestamp level message)
   - JSON (structured logging)
   - Custom (détecter le pattern)
2. Identifier la source (app, nginx, docker, système)
3. Déterminer la plage temporelle

### Phase 2: Parse
1. Extraire les champs structurés :
   - Timestamp
   - Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - Logger/Module
   - Message
   - Stack trace (si présent)
2. Normaliser les formats de date

### Phase 3: Analyze
1. **Statistiques globales** :
   - Distribution par niveau
   - Fréquence des erreurs
   - Pics d'activité
2. **Détection de patterns** :
   - Erreurs récurrentes
   - Séquences suspectes
   - Corrélations temporelles
3. **Identification des problèmes** :
   - Exceptions uniques
   - Erreurs en cascade
   - Dégradation de performance

### Phase 4: Correlate
1. Lier les erreurs au code source si possible
2. Identifier les fichiers/fonctions concernés
3. Chercher des issues similaires dans ISSUES.md

### Phase 5: Report
```
╔════════════════════════════════════════════════════════════╗
║  ANALYSE DE LOGS                                           ║
╚════════════════════════════════════════════════════════════╝

Fichier  : app.log
Période  : 2024-01-15 08:00 → 2024-01-15 18:00
Lignes   : 15,432

## Distribution par niveau

| Level | Count | % |
|-------|-------|---|
| DEBUG | 8,234 | 53% |
| INFO | 5,891 | 38% |
| WARNING | 876 | 6% |
| ERROR | 398 | 3% |
| CRITICAL | 33 | <1% |

───────────────────────────────────────────────────────────────

## Erreurs principales

### 1. ConnectionTimeout (156 occurrences)
```
ERROR 2024-01-15 14:32:01 db.pool Connection timeout after 30s
```
**Pattern** : Pics à 14:30-15:00 (charge élevée)
**Source probable** : src/db/connection.py:45
**Suggestion** : Augmenter pool_size ou timeout

### 2. ValidationError (89 occurrences)
```
ERROR 2024-01-15 12:15:33 api.handlers Invalid input: email
```
**Pattern** : Constant tout au long de la journée
**Source probable** : src/api/validators.py:23
**Suggestion** : Améliorer la validation côté client

### 3. MemoryWarning (33 occurrences)
```
CRITICAL 2024-01-15 16:45:00 system Memory usage > 90%
```
**Pattern** : Augmentation progressive
**Source probable** : Memory leak possible
**Suggestion** : Profiler l'application

───────────────────────────────────────────────────────────────

## Timeline des incidents

14:30 ┤ ████████ Connection timeouts spike
15:00 ┤ ██ Recovery
16:45 ┤ ████ Memory warnings start
17:30 ┤ ██████████ Service restart

───────────────────────────────────────────────────────────────

## Actions recommandées

1. **Urgent** : Investiguer le memory leak
2. **Important** : Optimiser les connexions DB
3. **Mineur** : Améliorer la validation client

───────────────────────────────────────────────────────────────
→ Debug : /debug "ConnectionTimeout in db.pool"
→ Export : /logs -s > rapport.md
╚═════════════════════════════════════════════════════════════╝
```

## Formats supportés

### Standard
```
2024-01-15 14:32:01 ERROR [module] Message
```

### JSON (structured)
```json
{"timestamp": "2024-01-15T14:32:01Z", "level": "ERROR", "message": "..."}
```

### Nginx
```
192.168.1.1 - - [15/Jan/2024:14:32:01 +0000] "GET /api" 500 1234
```

### Docker
```
2024-01-15T14:32:01.123Z container_name message
```

## Commandes utiles

```bash
# Suivre en temps réel
/logs tail

# Erreurs des dernières 24h
/logs app.log -e --since 24h

# Exporter les statistiques
/logs app.log -s > stats.md
```

## Notes
- Les logs volumineux sont échantillonnés intelligemment
- Les stack traces sont groupées par signature
- Corrélation automatique avec le code source si possible
