# Tâches et Backlog

---

## En cours

- [x] Compléter les frames manquants de l'application
- [x] Migration Flutter - Écrans manquants
- [x] Persistance SQLite Flutter

---

## À faire

### Priorité haute - Flutter
- [x] Écrans Flutter : Visits, AE, Documents, Queries, Settings
- [x] Connexion SQLite (sqflite_common_ffi)
- [x] CRUD complet avec persistance
- [x] Export Excel depuis Flutter

### Priorité haute - Python (legacy)
- [x] Frame "Visites" : enregistrement avec vérification fenêtre
- [x] Frame "Adverse Events" : déclaration EI/EIG
- [x] Frame "Documents" : gestion consentements
- [x] Frame "Queries" : suivi data management
- [x] Frame "Settings" : configuration étude et visites
- [ ] Conversion en .exe portable (PyInstaller)

### Priorité moyenne - Fonctionnalités
- [ ] Tests unitaires SoaParserService (Format 1 & 2)
- [ ] Alertes visites hors fenêtre
- [ ] Génération automatique de rapports (PDF)
- [ ] Dashboard temps réel dans l'application
- [ ] Historique des modifications (audit trail)
- [ ] Import de données existantes (Excel → SQLite)

### Priorité basse - Améliorations Excel
- [ ] Ajouter des graphiques (barres, lignes, camembert)
- [ ] Nouveaux types de consentements configurables
- [ ] Export multi-format (CSV, PDF)

---

## Terminé

### Import SoA (v13)
- [x] Support SoA Format 2 (visites avec jour intégré "V1 D0")
- [x] Détection automatique Format 1 vs Format 2
- [x] Parsing des jours négatifs (D-28 pour screening)
- [x] Support français (J0, J7)
- [x] 6 patterns de fenêtres supportés

### Génération Excel
- [x] Structure de base (generator.py)
- [x] Mise en forme avancée (styles.py)
- [x] Système de templates (templates.py)
- [x] Templates génériques : facture, budget, planning

### Suivi d'étude clinique
- [x] Onglet Settings avec fenêtres de visite
- [x] Onglet Suivi Patients avec mise en forme conditionnelle
- [x] Calcul fenêtres basé sur V1 (visite de référence)
- [x] Format de date anglais US
- [x] Onglet Documents avec consentements multiples
- [x] Dropdown filtré par type de consentement
- [x] Libellé concaténé (Type + Version + Date)
- [x] Onglet Événements Indésirables
- [x] Onglet Traitement IP
- [x] Onglet Queries avec statut coloré
- [x] Onglet Monitoring
- [x] Onglet Dashboard avec compteurs automatiques

### Documentation
- [x] CLAUDE.md
- [x] PROJECT.md
- [x] PROGRESS.md
- [x] TASKS.md
- [x] Skill /excel avec workflow guidé

### Application Python (v2)
- [x] Base de données SQLite (models.py, queries.py)
- [x] Application principale CustomTkinter (app.py)
- [x] Sidebar navigation avec thème dark/light
- [x] Dashboard avec cartes statistiques
- [x] Frame Patients : liste, recherche, ajout, modification, suppression
- [x] Dialogue PatientDialog avec validation
- [x] Export Excel depuis l'application
- [x] Point d'entrée main.py

### Gestion des études (v3)
- [x] Frame "Études" avec liste et recherche
- [x] Formulaire étude complet (tous les champs réglementaires)
- [x] Système de vendors dynamique (ajout/suppression)
- [x] 8 types de vendors prédéfinis
- [x] Migration schéma base de données

### Frame Visites (v4)
- [x] Sélecteur patient avec recherche
- [x] Grille des 25 visites avec dates cibles calculées
- [x] Indicateur Window Check (OK/OUT) avec delta
- [x] Barre de statistiques (6 compteurs)
- [x] Légende visuelle des statuts
- [x] Dialogue d'enregistrement avec vérification fenêtre

### Frame Adverse Events (v4)
- [x] Légende visuelle (sévérité + outcome)
- [x] Barre de statistiques (5 compteurs)
- [x] Recherche patient + filtre outcome
- [x] Champ reporting_date pour SAE
- [x] Indicateur délai SAE (< 24h / +Xd)
- [x] Bouton Delete avec confirmation

### Frame Documents (v4)
- [x] ManageTypesDialog (gestion types/versions)
- [x] Stats par type d'ICF
- [x] Recherche patient + filtre type
- [x] Indicateur complétude (All signed / Missing)
- [x] Détection nouvelle version (reconsentement)
- [x] Boutons Edit/Delete

### Frame Queries (v4)
- [x] Barre de statistiques (5 compteurs)
- [x] Recherche patient + filtre âge
- [x] Indicateur d'âge en jours
- [x] Quick actions (Ans/Close)
- [x] Resolution date dans formulaire
- [x] Bouton Delete

### Landing Page (v5)
- [x] Grille de cartes d'études (3 colonnes)
- [x] Stats par étude (patients, visites, AE)
- [x] Clic sur nom → accès au dashboard de l'étude
- [x] Bouton Home dans la sidebar
- [x] Création d'étude depuis la landing

### Sites / Centres (v6)
- [x] Table sites avec relation many-to-many (study_sites)
- [x] SitesFrame avec liste, stats, recherche, filtre
- [x] SiteDialog pour création/modification
- [x] AddSiteToStudyDialog pour ajouter site existant
- [x] Statut par étude (Active/On Hold/Closed)
- [x] Compteur patients par site

### Sites - Infos par étude (v7)
- [x] Champs study_sites : PI, activation_date, first_patient_date, target_patients
- [x] StudySiteDialog pour éditer les infos spécifiques
- [x] Affichage enrichi en contexte étude (PI, dates, progression)

---

## Backlog / Idées

- ~~Multi-études : gérer plusieurs études dans la même application~~ (FAIT)
- Synchronisation cloud : backup automatique
- Mode offline-first avec sync
- Génération de CRF électroniques
