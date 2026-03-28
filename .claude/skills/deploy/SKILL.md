---
name: deploy
description: "Workflow de déploiement avec vérifications et rollback."
argument-hint: "[environnement: dev|staging|prod]"
allowed-tools: Read, Glob, Grep, Bash
---

# /deploy - Déploiement

Workflow de déploiement structuré avec vérifications pré/post et rollback.

## Usage

```
/deploy                    # Déploie en dev (défaut)
/deploy staging            # Déploie en staging
/deploy prod               # Déploie en production (confirmations)
/deploy -a staging         # Mode autonome
/deploy --dry-run prod     # Simulation sans déploiement
```

## Workflow

### Phase 1: Pre-check
1. Vérifier l'environnement cible
2. Vérifier la branche Git actuelle
3. Vérifier qu'il n'y a pas de changements non commités
4. Identifier la configuration de déploiement :
   - Docker (Dockerfile, docker-compose.yml)
   - CI/CD (.github/workflows/, .gitlab-ci.yml)
   - Cloud (serverless.yml, app.yaml, etc.)

### Phase 2: Validate
1. Exécuter les linters (`ruff`, `flake8`, `black --check`)
2. Exécuter les tests (`pytest`)
3. Vérifier les vulnérabilités (`pip-audit` si disponible)
4. Build de test si applicable
5. **Si échec** → Arrêter et reporter les erreurs

### Phase 3: Confirm (prod uniquement)
1. Afficher le résumé des changements depuis le dernier déploiement
2. Afficher les risques potentiels
3. Demander confirmation explicite
4. Pour prod : demander double confirmation

### Phase 4: Deploy
1. Créer un tag de version si configuré
2. Exécuter le script de déploiement détecté :
   - Docker : `docker-compose up -d --build`
   - GitHub Actions : `git push` (trigger workflow)
   - Heroku : `git push heroku main`
   - Custom : script défini dans config
3. Capturer les logs de déploiement

### Phase 5: Verify
1. Attendre que le déploiement soit terminé
2. Exécuter les health checks si configurés
3. Vérifier les endpoints critiques
4. **Si échec** → Proposer rollback

### Phase 6: Report
```
╔════════════════════════════════════════════════════════════╗
║  DÉPLOIEMENT TERMINÉ                                       ║
╚════════════════════════════════════════════════════════════╝

Environnement : staging
Version       : v1.2.3 (abc1234)
Durée         : 2m 34s
Status        : ✅ SUCCESS

## Pré-checks
- ✅ Tests : 45/45 passed
- ✅ Lint : no issues
- ✅ Build : successful

## Déploiement
- ✅ Image built : myapp:v1.2.3
- ✅ Container deployed
- ✅ Health check passed

## Endpoints vérifiés
- ✅ /health : 200 OK (45ms)
- ✅ /api/v1/status : 200 OK (120ms)

───────────────────────────────────────────────────────────────
→ Rollback : /deploy --rollback staging
→ Logs : docker logs myapp-staging
╚═════════════════════════════════════════════════════════════╝
```

## Configuration

Le skill détecte automatiquement la configuration, mais peut être personnalisé via `.claude/deploy.yml` :

```yaml
environments:
  dev:
    branch: develop
    auto_deploy: true
    checks:
      - lint
      - test

  staging:
    branch: main
    checks:
      - lint
      - test
      - security
    deploy_cmd: "docker-compose -f docker-compose.staging.yml up -d"

  prod:
    branch: main
    require_tag: true
    checks:
      - lint
      - test
      - security
      - build
    deploy_cmd: "kubectl apply -f k8s/"
    health_check: "https://api.example.com/health"
```

## Rollback

```
/deploy --rollback staging    # Rollback au déploiement précédent
```

1. Identifier la version précédente
2. Redéployer cette version
3. Vérifier les health checks

## Notes
- Toujours tester en staging avant prod
- Ne jamais déployer avec des tests qui échouent
- Garder les logs de déploiement
- Documenter les rollbacks effectués
