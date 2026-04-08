# Journal des sessions

## [2026-04-08] Session 17 - Refactoring vues restantes

### Ce qui a été fait

- [x] `visits.py` : `_update_stats()` → `StatChip` (4 chips)
- [x] `adverse_events.py` : `_update_stats()` → `StatChip` (5 chips), `_delete_ae()` → `ConfirmDialog`
- [x] `queries.py` : `_update_stats()` → `StatChip` (5 chips), `_delete_query()` → `ConfirmDialog`
- [x] `documents.py` : `_update_stats()` → `StatChip`, `_delete_consent()` → `ConfirmDialog`
- [x] Imports centralisés via `from src.components import ...` (plus d'imports directs depuis sous-modules)

### Fichiers modifiés
```
src/views/visits.py
src/views/adverse_events.py
src/views/queries.py
src/views/documents.py
```

### Prochaines étapes
- [ ] Import SoA depuis PDF (pdfplumber ou PyMuPDF)
- [ ] Export PDF des rapports
- [ ] Alertes visites hors fenêtre

→ **Prochaine session** : Nouvelles fonctionnalités (PDF, alertes)

---

## [2026-04-05] Session 16 - Composants UI génériques + Refactoring

### Ce qui a été fait

#### Nouveaux composants (`src/components/`)
- [x] `GenericCard` : Carte réutilisable avec 3 variantes (DEFAULT, ELEVATED, OUTLINED)
  - Props : content, title, icon, actions, variant, padding, expand
  - Styles automatiques selon la variante (bgcolor, border, shadow)

- [x] `SectionHeader` : Titre de section avec divider
  - Props : title, icon, action_button, show_divider
  - Structure : [Icon] Title [Action] + Divider

- [x] `EmptyState` : Affichage quand aucune donnée
  - Props : title, description, icon, action_button
  - Centré avec icône 48px

- [x] `ConfirmDialog` : Dialog de confirmation standardisé
  - Props : title, message, confirm_text, cancel_text, on_confirm, on_cancel, danger
  - Mode danger = bouton rouge
  - Méthodes show(page) et close()

- [x] `FormField` : Wrapper TextField avec validation
  - Props : label, helper, error, required, **textfield_kwargs
  - Indicateur * rouge si required
  - Méthodes value (property), set_error(), validate(), focus()

### Fichiers créés
```
src/components/
├── generic_card.py      (carte générique)
├── section_header.py    (en-tête de section)
├── empty_state.py       (état vide)
├── confirm_dialog.py    (dialog de confirmation)
└── form_field.py        (champ de formulaire)
```

### Fichiers modifiés
- `src/components/__init__.py` - Ajout des exports

### Utilisation
```python
from src.components import (
    GenericCard, CardVariant,
    SectionHeader,
    EmptyState,
    ConfirmDialog,
    FormField,
)

# Carte avec titre et actions
card = GenericCard(
    title="Patients",
    icon=ft.Icons.PEOPLE,
    content=patients_list,
    actions=[save_button],
    variant=CardVariant.ELEVATED,
)

# Section avec action
SectionHeader(
    title="Informations",
    icon=ft.Icons.INFO,
    action_button=edit_button,
)

# État vide
EmptyState(
    title="Aucun patient",
    description="Ajoutez votre premier patient",
    icon=ft.Icons.PERSON_ADD,
    action_button=add_button,
)

# Confirmation de suppression
ConfirmDialog(
    title="Confirmer",
    message="Supprimer ce patient ?",
    confirm_text="Supprimer",
    on_confirm=do_delete,
    danger=True,
).show(page)

# Champ de formulaire
FormField(
    label="Nom du patient",
    required=True,
    helper="Format: NOM Prénom",
)
```

#### Refactoring des vues

**dashboard.py** :
- [x] Sections visites/alertes → `GenericCard` avec titre et icône
- [x] Messages "No data" → `EmptyState` avec description

**patients.py** :
- [x] Champs formulaire → `FormField` avec validation automatique
- [x] Stats manuels → `StatChip`
- [x] Dialog suppression (30 lignes) → `ConfirmDialog` (10 lignes)

**sites.py** :
- [x] Champs formulaire → `FormField` avec validation
- [x] Titres de section → `SectionHeader` avec icônes
- [x] Stats manuels → `StatChip`
- [x] Dialog suppression → `ConfirmDialog`

### Fichiers modifiés
- `src/components/__init__.py` - Ajout des exports
- `src/views/dashboard.py` - Refactoré avec GenericCard, EmptyState
- `src/views/patients.py` - Refactoré avec FormField, StatChip, ConfirmDialog
- `src/views/sites.py` - Refactoré avec FormField, SectionHeader, StatChip, ConfirmDialog

### Résultat
- Code plus concis et maintenable
- Validation des formulaires standardisée
- Dialogs de confirmation uniformisés
- Statistiques cohérentes entre les vues

### Prochaines étapes
- [ ] Refactorer visits.py, adverse_events.py, queries.py, documents.py
- [ ] Support PDF pour import SoA
- [ ] Export PDF des rapports

→ **Prochaine session** : Continuer le refactoring ou nouvelles fonctionnalités

---

## [2026-03-31] Session 15 - Tests unitaires + Build PyInstaller

### Ce qui a été fait

#### Tests unitaires (`tests/test_soa_parser.py`)
- [x] 43 tests pytest couvrant toutes les fonctionnalités
- [x] Tests `_is_visit_header` : 11 tests (V1-V25, Screening, Baseline, EOT, FU, français)
- [x] Tests `_extract_visit_name` : 7 tests (Format 1, Format 2, parenthèses)
- [x] Tests `_parse_window` : 11 tests (6 patterns de fenêtres)
- [x] Tests `VisitConfig` : 4 tests (dataclass, to_dict)
- [x] Tests d'intégration Format 1 & 2
- [x] Tests gestion d'erreurs

#### Build PyInstaller - Application portable
- [x] Fonction `get_app_path()` pour chemin DB compatible PyInstaller
- [x] Base de données à côté du .exe (`data/etude.db`)
- [x] Fichier spec PyInstaller (`clinical_tracker.spec`)
- [x] Script de build (`build.bat`)
- [x] Build réussi : `ClinicalStudyTracker.exe` (~83 Mo)

### Fichiers créés
```
tests/
├── __init__.py
└── test_soa_parser.py    (43 tests)

clinical_tracker.spec     (config PyInstaller)
build.bat                 (script de build)
dist/
└── ClinicalStudyTracker.exe  (application portable)
```

### Fichiers modifiés
- `requirements.txt` - Ajout pytest
- `src/database/models.py` - Fonction `get_app_path()` pour chemin portable

### Distribution
```
ClinicalStudyTracker.exe   # L'application (83 Mo)
data/
└── etude.db               # Créé au premier lancement
```

### Résultat
- Application testée et fonctionnelle
- Persistance SQLite OK
- Prêt pour distribution

### Prochaines étapes
- [ ] Amélioration des graphismes (UI/UX)
- [ ] Support PDF pour import SoA
- [ ] Export PDF des rapports
- [ ] Icône personnalisée pour l'exe

→ **Prochaine session** : Amélioration UI ou nouvelles fonctionnalités

---

## [2026-03-29] Session 14 - Import SoA Excel (Flet)

### Ce qui a été fait

#### SoaParserService Python (`src/services/soa_parser.py`) - NOUVEAU
- [x] Classe `VisitConfig` : dataclass pour les configurations de visites
- [x] Classe `SoaParserService` : service complet de parsing SoA
- [x] Détection automatique de la feuille SoA (par nom ou contenu)
- [x] Extraction des visites (V1, V2, Screening, Baseline, EOT, FU, etc.)
- [x] Parsing des jours cibles (D0, D7, Day 14, J0, J28, Jour X)
- [x] Parsing de 6 patterns de fenêtres (±3, +/-3, -2/+5, -2 to +5, (-2,+5))
- [x] Support Format 1 (jour/fenêtre sur lignes séparées)
- [x] Support Format 2 (jour intégré dans header : "V1 D0", "V2 D7±2")
- [x] Extraction des procédures (lignes avec X ou checkmarks)

#### SoaPreviewDialog (`src/views/settings.py`)
- [x] Dialogue de preview des visites détectées
- [x] Checkboxes pour sélectionner les visites à importer
- [x] Affichage Visit Name, Target Day, Window

#### Intégration Settings
- [x] Bouton "Import from SoA" dans l'onglet Visits
- [x] FilePicker pour sélectionner le fichier Excel
- [x] Import avec mise à jour ou création des visites
- [x] Message de confirmation avec compteur

#### Adaptations Flet 0.83+
- [x] FilePicker est un **Service** (pas un Control) → `page.services.append()`
- [x] `pick_files()` est **async** → `await file_picker.pick_files()`
- [x] `page.open()` n'existe plus → fonctions helper `show_snackbar()` et `show_dialog()`
- [x] Snackbars via `page.overlay` + `snackbar.open = True`
- [x] Dialogues via `page.overlay` + `dialog.open = True`

### Fichiers créés
```
src/services/
├── __init__.py         (nouveau)
└── soa_parser.py       (nouveau)

output/
├── test_soa.xlsx       (fichier test Format 1)
└── test_soa_format2.xlsx (fichier test Format 2)
```

### Fichiers modifiés
- `src/views/settings.py` - Import SoA + adaptations Flet 0.83+

### Tests effectués
| Test | Résultat |
|------|----------|
| Parsing Format 1 (lignes Day/Window) | 8 visites |
| Parsing Format 2 (jours intégrés) | 7 visites |
| Fenêtres symétriques (±3) | OK |
| Fenêtres asymétriques (-3/+5) | OK |
| Jours négatifs (D-28) | OK |
| Import base de données | OK |

### Prochaines étapes
- [ ] Support PDF (via pdfplumber ou PyMuPDF)
- [ ] Tests unitaires SoaParserService
- [ ] Export PDF des rapports

→ **Prochaine session** : Tests ou nouvelles fonctionnalités

---

## [2026-03-25] Session 13 - SoA Format 2

### Ce qui a été fait

#### SoaParserService - Support Format 2
- [x] Nouvelle méthode `_isFormat2Header()` - Détecte si le header contient des jours intégrés
- [x] Nouvelle méthode `_hasIntegratedDay()` - Vérifie si une cellule a un jour intégré
- [x] Nouvelle méthode `_extractVisitName()` - Extrait proprement le nom de visite
- [x] Amélioration `_parseVisitsFromHeader()` - Support complet Format 2
- [x] Amélioration `_parseWindow()` - 6 patterns de fenêtres supportés

#### Formats de visites supportés (Format 2)
| Input | Visit Name | Day | Window |
|-------|------------|-----|--------|
| `V1 D0` | V1 | 0 | 0 |
| `V2 D7±2` | V2 | 7 | ±2 |
| `Screening D-28` | Screening | -28 | 0 |
| `Baseline (Day 0)` | Baseline | 0 | 0 |
| `V4 D21 -2/+5` | V4 | 21 | -2/+5 |
| `EOT D84±7` | EOT | 84 | ±7 |
| `FU D112 +/-14` | FU | 112 | ±14 |
| `V5 J28` | V5 (français) | 28 | 0 |

#### Patterns fenêtres améliorés
- `±3` / `± 3` / `±3 days`
- `+/-3` / `+/- 3`
- `-/+3`
- `-3/+5` / `-3 / +5`
- `-3 to +5` / `-3 à +5`
- `(-3, +5)`

### Fichiers modifiés
- `lib/services/soa_parser_service.dart` - +3 méthodes, amélioration parsing

### Prochaines étapes
- [ ] Tests unitaires SoaParserService
- [ ] Export PDF des rapports

→ **Prochaine session** : Tests unitaires ou nouvelles fonctionnalités

---

## [2026-03-24] Session 12 - Persistance SQLite complète

### Ce qui a été fait

#### DatabaseService - Table Staff (migration v3)
- [x] Ajout de la table `staff` avec schéma complet
  - Champs : id, study_site_id, first_name, last_name, credential, role, start_date, end_date
  - Clé étrangère vers `study_sites` avec CASCADE
- [x] Migration v2 → v3 dans `_onUpgrade()`
- [x] Données de démo staff (6 membres répartis sur 3 sites)
- [x] Méthodes CRUD staff :
  - `getStaffByStudySite(int studySiteId)`
  - `createStaff(StaffMember)`
  - `updateStaff(StaffMember)`
  - `deleteStaff(int id)`
- [x] Nouvelle méthode `getPatientsBySite(int studyId, String siteNumber)`

#### SitesScreen - Connexion BD
- [x] Suppression de `demoSites` (données hard-codées)
- [x] Chargement dynamique via `DatabaseService.getStudySites()`
- [x] Indicateur de chargement
- [x] CRUD complet : Edit et Delete avec persistance
- [x] Rafraîchissement automatique après modifications

#### SiteDetailScreen - Connexion BD
- [x] Suppression de `demoStaffBySite` et `demoPatients`
- [x] Chargement staff via `DatabaseService.getStaffByStudySite()`
- [x] Chargement patients via `DatabaseService.getPatientsBySite()`
- [x] CRUD staff : Add, Edit, Delete avec persistance
- [x] Indicateur de chargement

#### Nettoyage
- [x] Suppression `demoPatients` dans `lib/models/patient.dart`
- [x] Suppression `demoStaffBySite` dans `lib/models/staff.dart`

### Fichiers modifiés
- `lib/services/database_service.dart` - Migration v3, table staff, 5 nouvelles méthodes
- `lib/screens/sites_screen.dart` - Connexion BD complète
- `lib/screens/site_detail_screen.dart` - Connexion BD complète
- `lib/models/patient.dart` - Suppression demo data
- `lib/models/staff.dart` - Suppression demo data

### État de la persistance SQLite

| Écran | Statut |
|-------|--------|
| PatientsScreen | ✅ Connecté |
| VisitsScreen | ✅ Connecté |
| DocumentsScreen | ✅ Connecté |
| AdverseEventsScreen | ✅ Connecté |
| QueriesScreen | ✅ Connecté |
| DashboardScreen | ✅ Connecté |
| SettingsScreen | ✅ Connecté |
| SitesScreen | ✅ Connecté (cette session) |
| SiteDetailScreen | ✅ Connecté (cette session) |

**Persistance SQLite : 100% complète**

### Prochaines étapes
- [ ] Support SoA Format 2 (visites avec jour intégré "V1 D0")
- [ ] Tests unitaires
- [ ] Export PDF des rapports

→ **Prochaine session** : Tests ou nouvelles fonctionnalités

---

## [2026-03-22] Session 11 - GitHub iTrack, Export Excel, Import SoA

### Ce qui a été fait

#### GitHub Repository
- [x] Création du repo GitHub "iTrack" : https://github.com/DelEx38/iTrack
- [x] Push initial du projet Flutter complet
- [x] Fusion du projet Python legacy dans le repo sous `python/`

#### Code Review et Refactoring Python
- [x] Review complète du module `clinical.py`
- [x] Refactoring majeur : 611 → ~400 lignes
  - Extraction des constantes (COLOR_BLUE, FILL_GREEN, etc.)
  - Création de 8 fonctions de sheet (`_create_settings_sheet`, etc.)
  - Création de fonctions utilitaires (`_apply_header_style`, `_create_table`, etc.)
- [x] Correction des bare except clauses dans `models.py`
- [x] Suppression des fichiers inutilisés :
  - `test_clinical.py`
  - `output/test_budget.xlsx`
  - `output/suivi_etude.xlsx`
  - Dossiers `__pycache__`

#### Export Excel Flutter (`lib/services/`)
- [x] `excel_export_service.dart` : Export complet de l'étude
  - 7 onglets : Settings, Patients, Sites, Adverse Events, Documents, Queries, Dashboard
  - Données formatées depuis DatabaseService
- [x] `file_download_service.dart` : Téléchargement cross-platform
  - Conditional imports (stub/web pattern)
  - Support Web via dart:html (Blob + AnchorElement)
- [x] Bouton "Export Excel" dans Dashboard avec loading state

#### Import SoA (Schedule of Assessments)
- [x] `soa_parser_service.dart` : Parser Word .docx
  - Extraction XML depuis archive ZIP (.docx)
  - Détection automatique du tableau SoA
  - Parsing des visites (V1, V2, Screening, Baseline, etc.)
  - Parsing des jours cibles (D0, D7, Day 14, etc.)
  - Parsing des fenêtres (±2, -3/+5, +/- 3 days)
- [x] Intégration dans Settings screen
  - Bouton "Import from SoA" dans l'onglet Visit Windows
  - `_SoaPreviewDialog` : Preview des visites détectées avant import
  - `_VisitConfigDialog` : Édition manuelle d'une visite
  - Sauvegarde via `DatabaseService.saveVisitConfigs`

### Fichiers créés
```
C:\dev\cst\lib\services\
├── excel_export_service.dart    (nouveau)
├── file_download_service.dart   (nouveau)
├── file_download_stub.dart      (nouveau)
├── file_download_web.dart       (nouveau)
└── soa_parser_service.dart      (nouveau)
```

### Fichiers modifiés
- `lib/screens/dashboard_screen.dart` - Bouton Export Excel + données réelles
- `lib/screens/settings_screen.dart` - Import SoA + dialogues preview
- `lib/services/database_service.dart` - Méthode `saveVisitConfigs`
- `python/src/excel_generator/clinical.py` - Refactoring complet
- `python/src/database/models.py` - Fix bare except

### Dépendances ajoutées (pubspec.yaml)
```yaml
archive: ^3.6.1
xml: ^6.5.0
file_picker: ^8.0.0
```

### Décisions techniques
- **Conditional imports** : Pattern stub/web pour supporter dart:html uniquement sur Web
- **SoA Format 1** : Visites en colonnes, ligne Day, ligne Window optionnelle
- **Preview avant import** : L'utilisateur valide les visites détectées avant sauvegarde
- **Excel package Flutter** : Génération côté client sans serveur

### Prochaines étapes
- [ ] Support SoA Format 2 (visites avec jour intégré "V1 D0")
- [ ] Import des procédures depuis SoA
- [ ] Tests unitaires pour SoaParserService
- [ ] Export PDF des rapports

→ **Prochaine session** : Amélioration parsing SoA ou tests

---

## [2026-03-21] Session 10 - Écrans Flutter complets

### Ce qui a été fait

#### Nouveaux modèles (`lib/models/`)
- [x] `visit.dart` : VisitConfig (fenêtres), VisitStatus, Visit avec données de démo
- [x] `adverse_event.dart` : AESeverity, AEOutcome, AECausality, AdverseEvent
- [x] `document.dart` : ConsentType, ConsentVersion, ConsentStatus, PatientConsent
- [x] `query.dart` : QueryStatus, QueryCategory, Query avec indicateur overdue

#### Nouveaux écrans (`lib/screens/`)
- [x] `visits_screen.dart` : Grille des visites par patient
  - Sélecteur de patient avec infos V1
  - Calcul dates cibles (V1 + Target Day)
  - Indicateur Window Check (OK/OUT avec delta)
  - Badge REF pour V1 (visite de référence)
  - Dialogue d'enregistrement avec preview fenêtre

- [x] `adverse_events_screen.dart` : Liste des EI/EIG
  - Stats : Total, SAE, Ongoing, Recovered, Fatal
  - Badge sévérité coloré (Mild/Moderate/Severe)
  - Indicateur délai SAE (<24h ou +Xd retard)
  - Filtre par outcome
  - Formulaire complet avec switch SAE

- [x] `documents_screen.dart` : Gestion consentements
  - Stats par statut (Signed/Missing/Update)
  - Filtre par type de consentement
  - Libellé complet (Type + Version + Date)
  - Détection nouvelle version (reconsentement)
  - ManageTypesDialog pour types et versions

- [x] `queries_screen.dart` : Data management
  - Stats : Total, Open, Answered, Closed, Overdue
  - Indicateur âge en jours (rouge si > 7)
  - Quick actions : Answer et Close rapides
  - Filtre par âge (> 7 jours, > 30 jours)

- [x] `settings_screen.dart` : Configuration étude
  - Onglet Visit Windows avec liste éditable
  - Onglet Consent Types (types + versions)
  - Onglet General (infos étude, export, danger zone)
  - Export/Import configuration

#### Intégration
- [x] Mise à jour `study_home_screen.dart` avec les 5 nouveaux écrans
- [x] Navigation complète : tous les onglets fonctionnels

### Fichiers créés
```
C:\dev\cst\lib\
├── models\
│   ├── visit.dart         (nouveau)
│   ├── adverse_event.dart (nouveau)
│   ├── document.dart      (nouveau)
│   └── query.dart         (nouveau)
└── screens\
    ├── visits_screen.dart          (nouveau)
    ├── adverse_events_screen.dart  (nouveau)
    ├── documents_screen.dart       (nouveau)
    ├── queries_screen.dart         (nouveau)
    └── settings_screen.dart        (nouveau)
```

### Décisions techniques
- **Données de démo cohérentes** : Patients et visites liés par ID
- **V1 comme référence** : Toutes les fenêtres calculées depuis V1
- **Délai SAE** : Indicateur < 24h requis pour pharmacovigilance
- **Query aging** : Indicateur rouge si > 7 jours (standard data management)
- **Reconsentement** : Détection auto des nouvelles versions disponibles

### Prochaines étapes
- [ ] Connecter à SQLite (sqflite_common_ffi)
- [ ] CRUD complet avec persistance réelle
- [ ] Export Excel depuis Flutter
- [ ] Tests unitaires

→ **Prochaine session** : Persistance SQLite et CRUD

---

## [2026-03-20] Session 9 - Migration Flutter

### Ce qui a été fait

#### Migration vers Flutter
- [x] Installation Flutter SDK dans `C:\dev\flutter`
- [x] Création projet Flutter dans `C:\dev\cst` (Clinical Study Tracker)
- [x] Configuration thème Material 3 dark
- [x] NavigationRail avec sidebar contextuelle

#### Modèles de données (`lib/models/`)
- [x] `study.dart` : Modèle Study avec couleurs par phase, données de démo
- [x] `site.dart` : Modèles Site et StudySite avec SiteStatus (Active/On Hold/Closed)
- [x] `patient.dart` : Modèle Patient avec PatientStatus (Screening/Included/Completed/Withdrawn/Screen Failure)
- [x] `staff.dart` : Modèle StaffMember avec credentials (Pr./Dr./M./Ms.) et rôles (PI/SI/SC/PH/PHS/LAB/RAD/OTH)

#### Écrans (`lib/screens/`)
- [x] `landing_screen.dart` : Grille de cartes d'études avec recherche
- [x] `study_home_screen.dart` : Layout principal avec sidebar par étude
- [x] `dashboard_screen.dart` : Vue d'ensemble (stats, sites récents, patients récents)
- [x] `sites_screen.dart` : Liste des sites avec filtres, progression recrutement
- [x] `patients_screen.dart` : Liste des patients avec filtres par statut/site
- [x] `site_detail_screen.dart` : Page détail site avec staff et patients

#### Widgets (`lib/widgets/`)
- [x] `study_card.dart` : Carte d'étude avec badge phase
- [x] `stat_card.dart` : Carte statistique + StatsBar
- [x] `status_badge.dart` : Badge de statut coloré

#### Fonctionnalités implémentées
- [x] Navigation : Landing → Study Home → Sites/Patients/Dashboard
- [x] Numéro de site cliquable → Page détail
- [x] Gestion du staff par site (ajout/modification/suppression)
- [x] Dialogues d'édition pour sites, patients, staff
- [x] Filtres et recherche sur toutes les listes
- [x] Barres de progression recrutement

#### Améliorations esthétiques
- [x] Colonnes réparties équitablement (flex) sur Sites et Patients
- [x] Pastilles de statut avec largeur fixe et texte centré
- [x] Cartes Dashboard harmonisées en hauteur (175px)
- [x] Cartes Sites Overview et Recent Patients alignées (IntrinsicHeight)
- [x] Barre de progression avec marge à droite
- [x] Page détail site : bandeau info sur 2 colonnes x 3 lignes
- [x] Staff et Patients côte à côte avec même hauteur

### Fichiers créés
```
C:\dev\cst\
├── lib\
│   ├── main.dart
│   ├── models\
│   │   ├── study.dart
│   │   ├── site.dart
│   │   ├── patient.dart
│   │   └── staff.dart
│   ├── screens\
│   │   ├── landing_screen.dart
│   │   ├── study_home_screen.dart
│   │   ├── dashboard_screen.dart
│   │   ├── sites_screen.dart
│   │   ├── patients_screen.dart
│   │   └── site_detail_screen.dart
│   ├── widgets\
│   │   ├── study_card.dart
│   │   ├── stat_card.dart
│   │   └── status_badge.dart
│   └── services\
│       └── database_service.dart
└── pubspec.yaml
```

### Décisions techniques
- **Flutter au lieu de CustomTkinter** : UI moderne, cross-platform (desktop, web, mobile)
- **Material 3** : Design system cohérent avec thème dark
- **Données de démo** : Développement rapide sans backend
- **IntrinsicHeight** : Alignement vertical des cartes côte à côte
- **Flex layout** : Colonnes de tableau adaptatives

### Prochaines étapes
- [ ] Implémenter les pages Visits, AE, Documents, Queries, Settings
- [ ] Connecter à SQLite (sqflite_common_ffi)
- [ ] CRUD complet avec persistance
- [ ] Export Excel

→ **Prochaine session** : Compléter les écrans manquants et persistance données

---

## [2026-03-20] Session 8 - Informations sites par étude

### Ce qui a été fait

#### Base de données (`database/models.py`)
- [x] Nouveaux champs dans `study_sites` :
  - `principal_investigator` : PI spécifique à l'étude
  - `first_patient_date` : Date de première inclusion
- [x] Migration automatique pour bases existantes
- [x] Méthode `get_study_site_by_id()` pour récupérer une liaison
- [x] Mise à jour de `add_site_to_study()` et `update_study_site()`

#### Frame Sites (`gui/frames/sites.py`)
- [x] `StudySiteDialog` : formulaire d'édition des infos spécifiques à l'étude
  - Statut (Active/On Hold/Closed)
  - Investigateur principal
  - Date d'activation
  - Date de première inclusion (FPI)
  - Objectif de recrutement
  - Commentaires
- [x] Affichage différencié selon le contexte :
  - **Vue étude** : Site #, Name, PI, Status, Activation, Target (X/Y), FPI
  - **Vue globale** : Site #, Name, City, Status, Patients
- [x] Indicateur de progression recrutement (vert/orange/gris)
- [x] Bouton Edit → `StudySiteDialog` en contexte étude

### Fichiers modifiés
- `src/database/models.py` - Schéma + migration + méthodes
- `src/gui/frames/sites.py` - StudySiteDialog + affichage enrichi

### Décisions techniques
- **PI par étude** : Un même site peut avoir un PI différent selon l'étude
- **FPI** : Date de première inclusion, distincte de la date d'activation
- **Progression visuelle** : Couleur du ratio inclus/cible (vert = atteint, orange = en cours)

→ **Prochaine session** : Conversion PyInstaller ou autre fonctionnalité

---

## [2026-03-19] Session 7 - Sites / Centres investigateurs

### Ce qui a été fait

#### Base de données (`database/models.py`)
- [x] Table `sites` : informations du centre (numéro, nom, adresse, contact)
- [x] Table `study_sites` : relation many-to-many avec études
- [x] CRUD complet : create, get, update, delete pour sites
- [x] Méthodes liaison : add_site_to_study, remove_site_from_study
- [x] get_sites_not_in_study pour ajout de sites existants

#### Frame Sites (`gui/frames/sites.py`) - NOUVEAU
- [x] SiteDialog : formulaire création/modification site (sans PI)
- [x] SelectOrCreateSiteDialog : sélection avec cases à cocher + création
- [x] SitesFrame : liste avec stats, recherche, filtre statut
- [x] Légende visuelle (Active/On Hold/Closed)
- [x] Compteur patients par site
- [x] Actions Edit/Delete

#### Landing Page
- [x] Clic sur nom d'étude → affiche les sites de l'étude (au lieu du dashboard)
- [x] Sidebar masquée sur la landing page

#### Intégration
- [x] Bouton "Sites" dans la sidebar
- [x] Suppression du bouton "Études" (remplacé par landing)

### Fichiers créés/modifiés
- `src/database/models.py` - Tables sites + study_sites + méthodes
- `src/gui/frames/sites.py` - Nouveau
- `src/gui/frames/landing.py` - Navigation vers sites
- `src/gui/app.py` - Intégration
- `src/gui/frames/sidebar.py` - Bouton Sites, suppression Études

### Décisions techniques
- **Relation many-to-many** : Un site peut participer à plusieurs études
- **Statut par étude** : Chaque participation a son propre statut (Active/Closed/On Hold)
- **Site partagé** : Les infos du site sont centralisées, seule la liaison est dupliquée
- **PI retiré du site** : L'investigateur principal est spécifique à l'étude, pas au site
- **Cases à cocher** : Permet de sélectionner plusieurs sites à ajouter en une fois

### À faire (prochaine session)
- [ ] Ajouter des informations supplémentaires sur la page Sites (spécifiques à l'étude)
  - Investigateur principal (par étude)
  - Date d'activation
  - Objectif de recrutement
  - Date de première inclusion
  - etc.

---

## [2026-03-19] Session 6 - Landing Page

### Ce qui a été fait

#### Landing Page (`gui/frames/landing.py`) - NOUVEAU
- [x] Grille de cartes d'études (3 colonnes)
- [x] Carte avec : numéro, phase, nom cliquable, sponsor, pathologie
- [x] Stats par étude (patients, visites, AE)
- [x] Couleurs par phase (I=bleu, II=vert, III=jaune, IV=rouge)
- [x] Recherche d'études
- [x] Bouton "+ New Study" avec dialogue intégré
- [x] Clic sur le nom → sélectionne l'étude et affiche son dashboard

#### Modifications `app.py`
- [x] Import LandingFrame
- [x] Affichage landing au démarrage (au lieu de Dashboard)
- [x] Callback `_on_study_select_from_landing()`
- [x] Callback `_new_study_from_landing()`

#### Modifications `sidebar.py`
- [x] Nouveau bouton "Home" en haut de la navigation
- [x] Réorganisation des boutons (row +1)
- [x] `set_active("home")` supporté

### Fichiers créés/modifiés
- `src/gui/frames/landing.py` - Nouveau
- `src/gui/app.py` - Intégration landing
- `src/gui/frames/sidebar.py` - Bouton Home

### Décisions techniques
- **Landing comme page d'accueil** : Vue d'ensemble de toutes les études
- **Grille 3 colonnes** : Optimisé pour afficher plusieurs études
- **Clic = navigation** : Pas de double-clic, action directe sur le nom

→ **Prochaine session** : Conversion .exe (PyInstaller)

---

## [2026-03-19] Session 5 - Frame Settings

### Ce qui a été fait

#### Frame Settings (`gui/frames/settings.py`)
- [x] Export/Import JSON configuration
- [x] Reset to defaults pour fenêtres de visite
- [x] Stats : compteur des visites configurées
- [x] Validation visuelle (rouge si window_before > target_day)
- [x] Boutons Delete pour types et versions de consentement
- [x] Champ Date dans SelectTypeDialog
- [x] V1 marquée (REF) comme visite de référence

#### Base de données (`database/queries.py`)
- [x] Ajout `delete_type()` dans ConsentQueries
- [x] Ajout `delete_version()` dans ConsentQueries

### Fichiers modifiés
- `src/gui/frames/settings.py` - Améliorations majeures
- `src/database/queries.py` - Méthodes delete

### Décisions techniques
- **Export JSON** : Format portable pour backup/restore configuration
- **Validation temps réel** : Indicateur visuel des fenêtres invalides
- **V1 comme REF** : Cohérent avec le frame Visites

→ **Prochaine session** : Conversion .exe (PyInstaller)

---

## [2026-03-19] Session 4 - Frames Visites et Adverse Events

### Ce qui a été fait

#### Frame Queries (`gui/frames/queries.py`)
- [x] Barre de statistiques (5 compteurs)
- [x] Recherche patient
- [x] Filtre par âge (>7 days, >30 days)
- [x] Champ resolution_date dans le formulaire
- [x] Indicateur d'âge en jours (rouge si >7)
- [x] Quick actions : boutons "Ans" et "Close" rapides
- [x] Bouton Delete avec confirmation
- [x] Légende visuelle des statuts

#### Frame Documents (`gui/frames/documents.py`)
- [x] ManageTypesDialog : gestion des types et versions de consentements
- [x] Barre de statistiques par type d'ICF
- [x] Recherche patient avec filtrage
- [x] Filtre par type de consentement
- [x] Indicateur de complétude ("All signed" / "Missing: X")
- [x] Détection nouvelle version disponible (status "Update")
- [x] Boutons Edit/Delete avec confirmation
- [x] Légende visuelle (Signed/Missing/New version)

#### Frame Adverse Events (`gui/frames/adverse_events.py`)
- [x] Légende visuelle des sévérités et outcomes
- [x] Barre de statistiques avec 5 compteurs (Total, SAE, Ongoing, Recovered, Fatal)
- [x] Recherche patient avec filtrage en temps réel
- [x] Filtre par Outcome (dropdown)
- [x] Champ Reporting Date pour les SAE (date de déclaration)
- [x] Indicateur délai SAE : < 24h (vert) ou +Xd (rouge)
- [x] Bouton Delete avec confirmation
- [x] Couleurs par Outcome dans la liste
- [x] Stats mises à jour selon les filtres actifs

#### Frame Visites (`gui/frames/visits.py`)
- [x] Légende visuelle des statuts et fenêtres (en haut à droite)
- [x] Recherche patient avec filtrage en temps réel
- [x] Barre de statistiques avec 6 compteurs :
  - Total Visits, Completed, In Window, Out of Window, Pending, Missed
- [x] En-tête de tableau avec colonnes explicites
- [x] Calcul et affichage de la date cible (V1 + Target Day)
- [x] Indicateur Window Check : OK/OUT avec delta en jours
- [x] Affichage du statut patient et date V1 dans le sélecteur
- [x] V1 marquée "REF" (référence pour tous les calculs)

#### Améliorations techniques
- [x] Fonction utilitaire `parse_date()` pour éviter duplication
- [x] Gestion correcte des dates (str vs date object)
- [x] Statistiques mises à jour automatiquement

### Fichiers modifiés
- `src/gui/frames/visits.py` - Refonte complète
- `src/gui/frames/adverse_events.py` - Améliorations majeures
- `src/gui/frames/documents.py` - Améliorations majeures + ManageTypesDialog
- `src/gui/frames/queries.py` - Améliorations majeures + Quick actions

### Décisions techniques
- **V1 comme référence** : Toutes les dates cibles calculées depuis V1
- **Statistiques par patient** : Compteurs visibles en permanence
- **Window Check visuel** : Vert = OK, Rouge = OUT avec delta
- **Délai SAE** : Indicateur < 24h requis pour pharmacovigilance
- **Stats dynamiques** : Compteurs mis à jour selon filtres actifs
- **Reconsentement** : Détection auto des nouvelles versions disponibles
- **Query aging** : Indicateur rouge si query > 7 jours

→ **Prochaine session** : Compléter le frame Settings

---

## [2026-03-16] Session 3 - Gestion des études et vendors

### Ce qui a été fait

#### Base de données
- [x] Extension de la table `studies` avec nouveaux champs :
  - study_number, study_name, eu_ct_number, nct_number
  - phase, investigational_product, comparator, pathology
  - study_title, sponsor
- [x] Nouvelle table `vendor_types` : 8 types prédéfinis
  - eCRF, IWRS, Central Lab, Central Pathology
  - Central Imaging, Central ECG, Remboursement frais patient, Home Visit
- [x] Nouvelle table `study_vendors` : relation N:N entre études et vendors
- [x] Méthodes CRUD pour études et vendors dans `models.py`
- [x] Migrations automatiques pour colonnes existantes

#### Interface
- [x] `gui/frames/studies.py` : Nouveau frame de gestion des études
  - StudiesFrame : liste avec recherche
  - StudyDialog : formulaire avec 2 onglets (Informations + Vendors)
  - VendorDialog : ajout/modification de vendors
  - Bouton "+ Ajouter un vendor" dynamique
- [x] Bouton "Études" ajouté dans la sidebar
- [x] Suppression de l'ancien NewStudyDialog simplifié

#### Réorganisation projet
- [x] Déplacement fichiers DCBP vers `.claude/dcbp/`
- [x] Suppression du dossier `dcbp-cli/` (outil externe)
- [x] Mise à jour des skills `/start`, `/archive`, `/etat` pour nouveau chemin

### Fichiers créés/modifiés
- `src/database/models.py` - Schéma étendu + méthodes vendors
- `src/gui/frames/studies.py` - Nouveau
- `src/gui/frames/sidebar.py` - Ajout bouton Études
- `src/gui/app.py` - Intégration StudiesFrame
- `.claude/dcbp/*` - Réorganisation
- `~/.claude/skills/*/SKILL.md` - Mise à jour chemins

### Décisions techniques
- **Vendors dynamiques** : Table séparée pour permettre plusieurs vendors par type
- **Types de vendors prédéfinis** : 8 types standard mais extensibles
- **Structure DCBP dans .claude/** : Regroupe tout ce qui est lié à Claude

→ **Prochaine session** : Compléter les autres frames (Visites, AE, Documents, Queries, Settings)

---

## [2026-03-13] Session 2 - Application CustomTkinter + SQLite

### Ce qui a été fait

#### Base de données SQLite
- [x] `database/models.py` : Classe Database avec schéma complet
  - Tables : study_settings, visit_config, consent_types, consent_versions
  - Tables : patients, visits, patient_consents, adverse_events
  - Tables : treatments, queries, audit_log
  - Initialisation données par défaut (25 visites, 3 types ICF)
- [x] `database/queries.py` : Classes de requêtes CRUD
  - PatientQueries : create, get, update, delete, search, count_by_status
  - VisitQueries : config, record_visit, check_window
  - ConsentQueries : types, versions, patient_consents
  - AdverseEventQueries : create, get, update, count_by_status

#### Interface CustomTkinter
- [x] `gui/app.py` : Application principale ClinicalStudyApp
  - Fenêtre 1400x800, thème dark, navigation par frames
  - Connexion base de données au démarrage
  - Export Excel intégré (filedialog + messagebox)
- [x] `gui/frames/sidebar.py` : Barre latérale de navigation
  - Boutons : Dashboard, Patients, Visites, Adverse Events, Documents, Queries
  - Export Excel, Settings, sélecteur de thème (Dark/Light/System)
- [x] `gui/frames/dashboard.py` : Tableau de bord
  - 4 cartes statistiques (Total, Screening, Included, AE)
  - Section "Upcoming Visits" (placeholder)
  - Section "Alerts & Notifications" (placeholder)
- [x] `gui/frames/patients.py` : Gestion des patients
  - Liste avec recherche et filtre par statut
  - Dialogue d'ajout/modification (PatientDialog)
  - Actions : Edit, Delete avec confirmation
  - Affichage coloré par statut

#### Structure projet
- [x] `main.py` : Point d'entrée avec gestion du path
- [x] `src/__init__.py` : Package principal
- [x] `requirements.txt` : Ajout customtkinter>=5.2.0

### Fichiers créés/modifiés
- `src/database/__init__.py`
- `src/database/models.py`
- `src/database/queries.py`
- `src/gui/__init__.py`
- `src/gui/app.py`
- `src/gui/frames/__init__.py`
- `src/gui/frames/sidebar.py`
- `src/gui/frames/dashboard.py`
- `src/gui/frames/patients.py`
- `main.py`
- `requirements.txt`

### Décisions techniques
- **CustomTkinter** : Interface moderne avec thème dark par défaut
- **SQLite local** : Base dans `data/etude.db`, créée automatiquement
- **Architecture MVC** : Séparation database/gui/excel_generator
- **Frames switchables** : Navigation sans rechargement

### Prochaines étapes
- [ ] Compléter les frames manquants (Visites, AE, Documents, Queries, Settings)
- [ ] Formulaire d'enregistrement de visite avec vérification fenêtre
- [ ] Formulaire de déclaration d'EI
- [ ] Conversion en .exe portable (PyInstaller)

→ **Prochaine session** : Compléter les formulaires et conversion .exe

---

## [2026-03-13] Session initiale - Création du suivi d'étude clinique

### Ce qui a été fait

#### Structure de base
- [x] Création du projet et structure de dossiers
- [x] Module `generator.py` : fonctions de base Excel
- [x] Module `styles.py` : mise en forme avancée (bordures, fusion, formats conditionnels)
- [x] Module `templates.py` : templates génériques (TableTemplate, facture, budget, planning)
- [x] Skill `/excel` avec workflow guidé (collecte d'infos → récapitulatif → génération)

#### Fichier de suivi d'étude clinique (`clinical.py`)
- [x] Onglet Settings : fenêtres de visite (V1-V25)
- [x] Onglet Suivi Patients : infos patient + visites avec mise en forme conditionnelle
- [x] Mise en forme conditionnelle : vert (dans fenêtre) / rouge (hors fenêtre)
- [x] Calcul basé sur V1 (visite de référence) et non date d'inclusion
- [x] Format de date anglais US (`[$-409]DD-MMM-YY`)
- [x] Onglet Documents : consentements multiples avec dropdown filtré par type
- [x] Tableaux séparés par type de consentement (ICF Principal, PK, Génétique)
- [x] Colonne Libellé avec concaténation (Type + Version + Date)
- [x] Onglet Événements Indésirables : EI/EIG complet avec validations
- [x] Onglet Traitement IP : dispensation, lots, compliance
- [x] Onglet Queries : suivi data management avec statut coloré
- [x] Onglet Monitoring : suivi par patient
- [x] Onglet Dashboard : compteurs automatiques (recrutement, sécurité, queries, sorties)

### Fichiers créés/modifiés
- `src/excel_generator/__init__.py`
- `src/excel_generator/generator.py`
- `src/excel_generator/styles.py`
- `src/excel_generator/templates.py`
- `src/excel_generator/clinical.py`
- `.claude/skills/excel/SKILL.md`
- `output/suivi_etude_complet.xlsx`

### Décisions techniques
- **V1 comme référence** : Toutes les fenêtres de visite sont calculées par rapport à V1 (et non date d'inclusion)
- **Tableaux séparés par consentement** : Permet des dropdown filtrés par type
- **Format date US** : Code locale `[$-409]` pour affichage anglais
- **Architecture SQLite envisagée** : Pour la v2 avec formulaires Python

### Prochaines étapes
- [x] Développer l'application Python complète (GUI + SQLite)
- [x] Formulaire d'ajout de patient
- [x] Export Excel à la demande
- [ ] Conversion en .exe portable
