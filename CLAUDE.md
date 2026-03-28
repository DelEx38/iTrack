# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Application de suivi d'études cliniques pour ARC (Attaché de Recherche Clinique).
Interface graphique moderne avec **Flet** (Python).

## Stack Technique

- **Langage** : Python 3.11+
- **GUI** : Flet (cross-platform: Desktop, Web, Mobile)
- **Excel** : openpyxl
- **Base de données** : SQLite

## Structure

```
excel/
├── .venv/                       # Environnement virtuel
├── CLAUDE.md                    # Ce fichier
├── .claude/dcbp/                # Mémoire projet DCBP
├── main.py                      # Point d'entrée
├── requirements.txt             # Dépendances
├── src/
│   ├── app.py                   # Application principale Flet
│   ├── components/              # Composants UI réutilisables
│   ├── views/                   # Écrans de l'application
│   ├── database/                # Couche SQLite
│   └── excel_generator/         # Génération Excel
├── data/                        # Base SQLite (etude.db)
└── output/                      # Fichiers Excel générés
```

## Commandes

```bash
# Activer l'environnement virtuel
.venv\Scripts\activate           # Windows
source .venv/bin/activate        # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python main.py

# Lancer en mode web
flet run --web main.py
```

## Architecture des Modules

### Écrans (views/)
| Écran | Description |
|-------|-------------|
| landing.py | Sélection d'étude |
| dashboard.py | Vue d'ensemble |
| sites.py | Centres investigateurs |
| patients.py | Gestion patients |
| visits.py | Suivi des visites |
| adverse_events.py | EI/EIG |
| documents.py | Consentements |
| queries.py | Data management |
| monitoring.py | Visites monitoring |
| settings.py | Configuration |

### clinical.py - Génération Excel
Fonction principale : `create_visit_tracking(num_visits, num_patients, output_path)`

Génère un fichier Excel avec 8 onglets :
1. **Settings** : Fenêtres de visite + versions consentements
2. **Suivi Patients** : Infos patient + visites
3. **Documents** : Consentements multiples
4. **Événements Indésirables** : EI/EIG
5. **Traitement IP** : Dispensation, compliance
6. **Queries** : Data management
7. **Monitoring** : Suivi par patient
8. **Dashboard** : Compteurs automatiques

### Logique métier
- **V1** = visite de référence (pas de fenêtre)
- **V2-V25** = calculées par rapport à V1 + Jour cible ± Fenêtre
- **Consentements** = tableaux séparés par type
- **Format date** = anglais US `[$-409]DD-MMM-YY`

## Conventions

- Code et commentaires en français
- Type hints obligatoires
- Nommage : `snake_case` (variables/fonctions), `PascalCase` (classes)

## Conventions Flet

- Utiliser `ft.Colors.XXX` (C majuscule)
- Utiliser `ft.Icons.XXX` (I majuscule)
- Utiliser `ft.Button` (pas `ft.ElevatedButton`, déprécié)
- Texte boutons : `content=ft.Text("...")`
- Dropdown : `on_select` (pas `on_change`), `ft.DropdownOption`

## Points d'attention

- Activer le venv avant de travailler
- Fermer le fichier Excel avant régénération
- Tester l'app après chaque modification
