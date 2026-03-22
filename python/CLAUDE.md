# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Application de suivi d'études cliniques pour ARC (Attaché de Recherche Clinique). Deux versions :
- **Python/CustomTkinter** (legacy) : dans ce dossier `excel/`
- **Flutter** (actif) : dans `C:\dev\cst\` - Application moderne cross-platform

## Stack Technique

### Flutter (version principale)
- **Framework** : Flutter 3.41+
- **Langage** : Dart
- **UI** : Material 3, thème dark
- **Base de données** : SQLite (sqflite_common_ffi) - à implémenter
- **Projet** : `C:\dev\cst\`

### Python (legacy)
- **Langage** : Python 3.8+
- **Excel** : openpyxl
- **GUI** : CustomTkinter
- **Base de données** : SQLite

## Structure

```
C:\dev\cst\                      # Projet Flutter (ACTIF)
├── lib\
│   ├── main.dart
│   ├── models\                  # Modèles de données
│   ├── screens\                 # Écrans (8 onglets)
│   ├── widgets\                 # Composants réutilisables
│   └── services\                # Services (DB, etc.)
└── pubspec.yaml

excel/                           # Projet Python (legacy)
├── CLAUDE.md                    # Ce fichier
├── .claude/dcbp/                # Mémoire projet DCBP
├── main.py
├── src/
│   ├── excel_generator/
│   ├── database/
│   └── gui/
└── output/
```

## Commandes Flutter

```bash
# IMPORTANT : Lancer l'app après chaque modification
cd C:\dev\cst
C:\dev\flutter\bin\flutter run -d chrome

# Analyse du code
C:\dev\flutter\bin\flutter analyze C:\dev\cst

# Hot reload : appuyer sur 'r' dans le terminal pendant l'exécution
# Hot restart : appuyer sur 'R' dans le terminal
```

## Workflow de développement Flutter

**IMPORTANT** : Après chaque modification de code Flutter, lancer l'application pour vérifier que les changements fonctionnent :

```bash
cd C:\dev\cst && C:\dev\flutter\bin\flutter run -d chrome
```

Si l'app est déjà en cours d'exécution, utiliser :
- `r` : Hot reload (changements rapides)
- `R` : Hot restart (changements structurels)

## Commandes Python (legacy)

```bash
pip install -r requirements.txt

# Générer le fichier de suivi d'étude
python -c "from src.excel_generator import create_visit_tracking; create_visit_tracking(25, 50, 'output/suivi.xlsx')"
```

## Architecture des Modules

### clinical.py - Suivi d'étude clinique
Fonction principale : `create_visit_tracking(num_visits, num_patients, output_path)`

Génère un fichier Excel avec 8 onglets :
1. **Settings** : Fenêtres de visite + versions consentements par type
2. **Suivi Patients** : Infos patient + visites (mise en forme conditionnelle vert/rouge)
3. **Documents** : Consentements multiples avec dropdown filtré
4. **Événements Indésirables** : EI/EIG
5. **Traitement IP** : Dispensation, compliance
6. **Queries** : Data management
7. **Monitoring** : Suivi par patient
8. **Dashboard** : Compteurs automatiques

### Logique métier
- **V1** = visite de référence (pas de fenêtre)
- **V2-V25** = calculées par rapport à V1 + Jour cible ± Fenêtre
- **Consentements** = tableaux séparés par type, libellé concaténé (Type + Version + Date)
- **Format date** = anglais US `[$-409]DD-MMM-YY`

## Conventions

- Code et commentaires en français
- Type hints obligatoires
- Nommage : `snake_case` (variables/fonctions), `PascalCase` (classes)

## Conventions UI Flutter

- **Pastilles/Badges** : Sur une même page, toutes les pastilles d'un même type doivent avoir la même largeur fixe (ex: `width: 95` pour les statuts patients, `width: 80` pour les statuts visites). Utiliser `textAlign: TextAlign.center` pour centrer le texte.
- **Dropdowns** : Utiliser `isExpanded: true` pour éviter les overflow sur les textes longs.
- **Tableaux** : Colonnes en `Expanded(flex: X)` pour répartition équitable.
- **Couleurs par statut** : Définies dans les extensions des enums (ex: `PatientStatus.color`).

## Points d'attention

- Fermer le fichier Excel avant régénération (PermissionError sinon)
- Les noms de tableaux Excel ne doivent pas contenir d'espaces
- Tester les dropdown après modification des types de consentements
