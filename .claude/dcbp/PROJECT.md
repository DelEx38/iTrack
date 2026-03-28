# Clinical Study Tracker

> Application Python de suivi d'études cliniques avec interface Flet et génération Excel.

## Informations générales

- **Nom** : Clinical Study Tracker (iTrack)
- **Description** : Outil de suivi complet pour ARC (Attaché de Recherche Clinique)
- **Démarré le** : 2026-03-13
- **Migration Flet** : 2026-03-28

## Stack technique

### Langages
- Python 3.11+

### Bibliothèques
- **flet** : Interface graphique moderne cross-platform (Desktop, Web, Mobile)
- **openpyxl** : Génération et manipulation de fichiers Excel
- **sqlite3** : Base de données locale

### Outils
- **venv** : Environnement virtuel Python
- **PyInstaller** : Conversion en .exe portable (à faire)

## Architecture

### Structure
```
excel/
├── .venv/                       # Environnement virtuel
├── CLAUDE.md                    # Guide Claude Code
├── main.py                      # Point d'entrée Flet
├── requirements.txt             # Dépendances
├── src/
│   ├── __init__.py
│   ├── app.py                   # Application principale Flet
│   ├── components/              # Composants UI réutilisables
│   │   ├── __init__.py
│   │   ├── sidebar.py           # Navigation latérale
│   │   └── stat_card.py         # Carte statistique
│   ├── views/                   # Écrans de l'application
│   │   ├── __init__.py
│   │   ├── landing.py           # Page d'accueil (sélection étude)
│   │   ├── dashboard.py         # Tableau de bord
│   │   ├── patients.py          # Gestion patients
│   │   ├── visits.py            # Visites
│   │   ├── adverse_events.py    # EI/EIG
│   │   ├── documents.py         # Consentements
│   │   ├── queries.py           # Data management
│   │   ├── sites.py             # Centres investigateurs
│   │   ├── monitoring.py        # Suivi monitoring
│   │   └── settings.py          # Configuration
│   ├── database/                # Couche SQLite
│   │   ├── __init__.py
│   │   ├── models.py            # Database + schéma
│   │   └── queries.py           # Requêtes CRUD
│   └── excel_generator/         # Génération Excel
│       ├── __init__.py
│       ├── generator.py         # Fonctions de base
│       ├── styles.py            # Mise en forme
│       ├── templates.py         # Templates génériques
│       └── clinical.py          # Templates recherche clinique
├── data/                        # Base SQLite (etude.db)
└── output/                      # Fichiers Excel générés
```

## Écrans de l'application

| Écran | Description |
|-------|-------------|
| Landing | Sélection d'étude, création nouvelle étude |
| Dashboard | Vue d'ensemble (stats, alertes, visites à venir) |
| Sites | Centres investigateurs, staff, objectifs recrutement |
| Patients | Liste patients, statuts, filtres |
| Visits | Grille des visites, fenêtres, calcul dates cibles |
| Adverse Events | EI/EIG, sévérité, déclarations |
| Documents | Consentements, versions, reconsentement |
| Queries | Data management, âge des queries |
| Monitoring | Visites de monitoring par site |
| Settings | Configuration visites, types consentements |

## Conventions

### Nommage
- Variables/fonctions : `snake_case`
- Classes : `PascalCase`
- Fichiers : `snake_case.py`

### Style
- Type hints obligatoires
- Docstrings Google style
- Code et commentaires en français

### Flet
- Utiliser `ft.Colors.XXX` (avec C majuscule)
- Utiliser `ft.Icons.XXX` (avec I majuscule)
- Utiliser `ft.Button` au lieu de `ft.ElevatedButton` (déprécié)
- `content=ft.Text("...")` pour le texte des boutons

## Commandes

```bash
# Activer l'environnement virtuel
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Installation des dépendances
pip install -r requirements.txt

# Lancer l'application
python main.py

# Lancer en mode web
flet run --web main.py
```

## Points d'attention

### À faire systématiquement
- Activer le venv avant de travailler
- Tester l'application après chaque modification
- Fermer le fichier Excel avant régénération

### API Flet 0.80+
- `ft.app()` déprécié → utiliser `ft.app(main)`
- Pas de `text=` dans les boutons → utiliser `content=ft.Text(...)`
- `on_change` des Dropdown → `on_select`
- `ft.dropdown.Option` → `ft.DropdownOption`
