"""
Modèles de base de données SQLite pour le suivi d'étude clinique.
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime, date
from typing import Optional


def get_app_path() -> Path:
    """
    Retourne le chemin du dossier de l'application.

    Compatible PyInstaller : utilise le dossier de l'exécutable.
    En développement : utilise le dossier du projet.
    """
    if getattr(sys, 'frozen', False):
        # Mode PyInstaller : à côté de l'exécutable
        return Path(sys.executable).parent
    else:
        # Mode développement : dossier du projet
        return Path(__file__).parent.parent.parent


class Database:
    """Gestionnaire de connexion à la base de données SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Chemin par défaut : data/etude.db à côté de l'application
            app_path = get_app_path()
            self.db_path = app_path / "data" / "etude.db"
        else:
            self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        """Établit la connexion à la base de données."""
        if self.connection is None:
            self.connection = sqlite3.connect(
                self.db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            self.connection.row_factory = sqlite3.Row
            self._enable_foreign_keys()
        return self.connection

    def _enable_foreign_keys(self) -> None:
        """Active les clés étrangères."""
        self.connection.execute("PRAGMA foreign_keys = ON")

    def close(self) -> None:
        """Ferme la connexion."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def init_schema(self) -> None:
        """Initialise le schéma de la base de données."""
        conn = self.connect()
        cursor = conn.cursor()

        # Table des études (étendue)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS studies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                study_number TEXT NOT NULL,
                study_name TEXT,
                eu_ct_number TEXT,
                nct_number TEXT,
                phase TEXT,
                investigational_product TEXT,
                comparator TEXT,
                pathology TEXT,
                study_title TEXT,
                sponsor TEXT,
                status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table des types de vendors
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendor_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name TEXT NOT NULL,
                UNIQUE(type_name)
            )
        """)

        # Table des vendors par étude
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_vendors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                study_id INTEGER NOT NULL,
                vendor_type_id INTEGER NOT NULL,
                vendor_name TEXT NOT NULL,
                contact TEXT,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (study_id) REFERENCES studies(id) ON DELETE CASCADE,
                FOREIGN KEY (vendor_type_id) REFERENCES vendor_types(id)
            )
        """)

        # Table des paramètres d'étude (legacy, gardé pour compatibilité)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                study_name TEXT NOT NULL,
                protocol_number TEXT,
                sponsor TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table des visites prévues (configuration)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visit_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                visit_name TEXT NOT NULL,
                visit_order INTEGER NOT NULL,
                target_day INTEGER NOT NULL DEFAULT 0,
                window_before INTEGER NOT NULL DEFAULT 0,
                window_after INTEGER NOT NULL DEFAULT 0,
                UNIQUE(visit_name)
            )
        """)

        # Table des types de consentement
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consent_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name TEXT NOT NULL,
                UNIQUE(type_name)
            )
        """)

        # Table des versions de consentement
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consent_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                consent_type_id INTEGER NOT NULL,
                version TEXT NOT NULL,
                version_date DATE,
                comments TEXT,
                FOREIGN KEY (consent_type_id) REFERENCES consent_types(id)
            )
        """)

        # Table des patients
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                study_id INTEGER,
                patient_number TEXT NOT NULL,
                initials TEXT,
                birth_date DATE,
                site_id TEXT,
                screening_date DATE,
                inclusion_date DATE,
                randomization_number TEXT,
                randomization_arm TEXT,
                status TEXT DEFAULT 'Screening',
                exit_date DATE,
                exit_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (study_id) REFERENCES studies(id),
                UNIQUE(study_id, patient_number)
            )
        """)

        # Table des visites réalisées
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                visit_config_id INTEGER NOT NULL,
                visit_date DATE,
                status TEXT DEFAULT 'Planned',
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (visit_config_id) REFERENCES visit_config(id),
                UNIQUE(patient_id, visit_config_id)
            )
        """)

        # Table des consentements signés
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patient_consents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                consent_version_id INTEGER NOT NULL,
                signature_date DATE NOT NULL,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (consent_version_id) REFERENCES consent_versions(id)
            )
        """)

        # Table des événements indésirables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS adverse_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                ae_number INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                description TEXT NOT NULL,
                severity TEXT,
                seriousness TEXT,
                causality TEXT,
                action_taken TEXT,
                outcome TEXT,
                is_serious INTEGER DEFAULT 0,
                reporting_date DATE,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            )
        """)

        # Table des dispensations de traitement
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS treatments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                visit_id INTEGER,
                dispensation_date DATE NOT NULL,
                batch_number TEXT,
                quantity_dispensed INTEGER,
                quantity_returned INTEGER,
                compliance_percent REAL,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (visit_id) REFERENCES visits(id)
            )
        """)

        # Table des queries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                visit_id INTEGER,
                query_number INTEGER NOT NULL,
                crf_field TEXT,
                description TEXT NOT NULL,
                open_date DATE NOT NULL,
                response_date DATE,
                resolution_date DATE,
                status TEXT DEFAULT 'Open',
                site_response TEXT,
                dm_comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (visit_id) REFERENCES visits(id)
            )
        """)

        # Table des visites de monitoring
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                study_id INTEGER NOT NULL,
                visit_number INTEGER NOT NULL,
                visit_type TEXT,
                start_date DATE NOT NULL,
                end_date DATE,
                confirmation_letter_date DATE,
                report_submission_date DATE,
                turnover_count INTEGER DEFAULT 0,
                report_approval_date DATE,
                followup_letter_date DATE,
                expenses_submission_date DATE,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (study_id) REFERENCES studies(id)
            )
        """)

        # Table d'audit (historique des modifications)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                field_name TEXT,
                old_value TEXT,
                new_value TEXT,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                changed_by TEXT
            )
        """)

        # Table de configuration des consentements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consent_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                consent_type TEXT NOT NULL,
                versions TEXT DEFAULT '1.0',
                is_required INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table des consentements (nouveau format)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                consent_config_id INTEGER NOT NULL,
                version TEXT NOT NULL,
                consent_date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (consent_config_id) REFERENCES consent_config(id)
            )
        """)

        # Table de monitoring (entrées par patient)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitoring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                monitoring_date DATE NOT NULL,
                monitoring_type TEXT DEFAULT 'Source Data Verification',
                findings TEXT,
                actions_required TEXT,
                is_completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            )
        """)

        # Table des sites/centres investigateurs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_number TEXT NOT NULL UNIQUE,
                site_name TEXT,
                principal_investigator TEXT,
                address TEXT,
                city TEXT,
                country TEXT,
                phone TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table de liaison études-sites (many-to-many)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                study_id INTEGER NOT NULL,
                site_id INTEGER NOT NULL,
                status TEXT DEFAULT 'Active',
                principal_investigator TEXT,
                activation_date DATE,
                first_patient_date DATE,
                target_patients INTEGER DEFAULT 0,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (study_id) REFERENCES studies(id) ON DELETE CASCADE,
                FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE,
                UNIQUE(study_id, site_id)
            )
        """)

        conn.commit()

        # Migrations
        self._run_migrations(cursor, conn)

    def _run_migrations(self, cursor, conn) -> None:
        """Exécute les migrations nécessaires."""
        # Migration: ajouter study_id à patients si manquant
        try:
            cursor.execute("SELECT study_id FROM patients LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE patients ADD COLUMN study_id INTEGER")
            conn.commit()

        # Migration: ajouter les nouvelles colonnes à studies si manquantes
        studies_columns = [
            ("study_number", "TEXT"),
            ("study_name", "TEXT"),
            ("eu_ct_number", "TEXT"),
            ("nct_number", "TEXT"),
            ("investigational_product", "TEXT"),
            ("comparator", "TEXT"),
            ("pathology", "TEXT"),
            ("study_title", "TEXT"),
            ("protocol_version", "TEXT"),
        ]

        for col_name, col_type in studies_columns:
            try:
                cursor.execute(f"SELECT {col_name} FROM studies LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute(f"ALTER TABLE studies ADD COLUMN {col_name} {col_type}")
                conn.commit()

        # Migration: ajouter les nouvelles colonnes à study_sites si manquantes
        study_sites_columns = [
            ("principal_investigator", "TEXT"),
            ("first_patient_date", "DATE"),
        ]

        for col_name, col_type in study_sites_columns:
            try:
                cursor.execute(f"SELECT {col_name} FROM study_sites LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute(f"ALTER TABLE study_sites ADD COLUMN {col_name} {col_type}")
                conn.commit()

        # Migration: ajouter les nouvelles colonnes à adverse_events si manquantes
        ae_columns = [
            ("ae_term", "TEXT"),
            ("notes", "TEXT"),
        ]

        for col_name, col_type in ae_columns:
            try:
                cursor.execute(f"SELECT {col_name} FROM adverse_events LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute(f"ALTER TABLE adverse_events ADD COLUMN {col_name} {col_type}")
                conn.commit()

        # Migration: ajouter les nouvelles colonnes à queries si manquantes
        queries_columns = [
            ("field_name", "TEXT"),
            ("priority", "TEXT DEFAULT 'Medium'"),
            ("response", "TEXT"),
            ("updated_at", "TIMESTAMP"),
        ]

        for col_name, col_type in queries_columns:
            try:
                cursor.execute(f"SELECT {col_name} FROM queries LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute(f"ALTER TABLE queries ADD COLUMN {col_name} {col_type}")
                conn.commit()

    def init_default_data(self, num_visits: int = 25) -> None:
        """Initialise les données par défaut."""
        conn = self.connect()
        cursor = conn.cursor()

        # Vérifier si déjà initialisé
        cursor.execute("SELECT COUNT(*) FROM visit_config")
        if cursor.fetchone()[0] > 0:
            return

        # Visites par défaut
        for i in range(1, num_visits + 1):
            cursor.execute(
                "INSERT INTO visit_config (visit_name, visit_order, target_day, window_before, window_after) VALUES (?, ?, ?, ?, ?)",
                (f"V{i}", i, 0, 0, 0)
            )

        # Types de consentement par défaut
        consent_types = ["ICF Principal", "ICF Sous-étude PK", "ICF Génétique"]
        for ct in consent_types:
            cursor.execute("INSERT INTO consent_types (type_name) VALUES (?)", (ct,))

        # Types de vendors par défaut
        cursor.execute("SELECT COUNT(*) FROM vendor_types")
        if cursor.fetchone()[0] == 0:
            vendor_types = [
                "eCRF",
                "IWRS",
                "Central Lab",
                "Central Pathology",
                "Central Imaging",
                "Central ECG",
                "Remboursement frais patient",
                "Home Visit"
            ]
            for vt in vendor_types:
                cursor.execute("INSERT INTO vendor_types (type_name) VALUES (?)", (vt,))

        conn.commit()

    def get_studies(self) -> list:
        """Récupère toutes les études."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM studies ORDER BY study_number")
        return [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    def create_study(self, study_number: str, study_name: str = "", eu_ct_number: str = "",
                     nct_number: str = "", phase: str = "", investigational_product: str = "",
                     comparator: str = "", pathology: str = "", study_title: str = "",
                     sponsor: str = "") -> int:
        """Crée une nouvelle étude."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO studies (study_number, study_name, eu_ct_number, nct_number,
               phase, investigational_product, comparator, pathology, study_title, sponsor)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (study_number, study_name, eu_ct_number, nct_number, phase,
             investigational_product, comparator, pathology, study_title, sponsor)
        )
        conn.commit()
        return cursor.lastrowid

    def update_study(self, study_id: int, **kwargs) -> None:
        """Met à jour une étude."""
        conn = self.connect()
        cursor = conn.cursor()
        allowed_fields = ["study_number", "study_name", "eu_ct_number", "nct_number",
                          "phase", "investigational_product", "comparator", "pathology",
                          "study_title", "sponsor", "status"]
        updates = []
        values = []
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                values.append(value)
        if updates:
            values.append(study_id)
            cursor.execute(f"UPDATE studies SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()

    def delete_study(self, study_id: int) -> None:
        """Supprime une étude."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM studies WHERE id = ?", (study_id,))
        conn.commit()

    def get_study_by_id(self, study_id: int) -> dict:
        """Récupère une étude par son ID."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM studies WHERE id = ?", (study_id,))
        row = cursor.fetchone()
        if row:
            return dict(zip([d[0] for d in cursor.description], row))
        return None

    # ========== Méthodes pour les vendors ==========

    def get_vendor_types(self) -> list:
        """Récupère tous les types de vendors."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendor_types ORDER BY type_name")
        return [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    def get_study_vendors(self, study_id: int) -> list:
        """Récupère les vendors d'une étude."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sv.*, vt.type_name
            FROM study_vendors sv
            JOIN vendor_types vt ON sv.vendor_type_id = vt.id
            WHERE sv.study_id = ?
            ORDER BY vt.type_name
        """, (study_id,))
        return [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    def add_study_vendor(self, study_id: int, vendor_type_id: int, vendor_name: str,
                         contact: str = "", comments: str = "") -> int:
        """Ajoute un vendor à une étude."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO study_vendors (study_id, vendor_type_id, vendor_name, contact, comments)
               VALUES (?, ?, ?, ?, ?)""",
            (study_id, vendor_type_id, vendor_name, contact, comments)
        )
        conn.commit()
        return cursor.lastrowid

    def update_study_vendor(self, vendor_id: int, vendor_type_id: int = None,
                            vendor_name: str = None, contact: str = None,
                            comments: str = None) -> None:
        """Met à jour un vendor."""
        conn = self.connect()
        cursor = conn.cursor()
        updates = []
        values = []
        if vendor_type_id is not None:
            updates.append("vendor_type_id = ?")
            values.append(vendor_type_id)
        if vendor_name is not None:
            updates.append("vendor_name = ?")
            values.append(vendor_name)
        if contact is not None:
            updates.append("contact = ?")
            values.append(contact)
        if comments is not None:
            updates.append("comments = ?")
            values.append(comments)
        if updates:
            values.append(vendor_id)
            cursor.execute(f"UPDATE study_vendors SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()

    def delete_study_vendor(self, vendor_id: int) -> None:
        """Supprime un vendor."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM study_vendors WHERE id = ?", (vendor_id,))
        conn.commit()

    # ========== Méthodes pour les sites ==========

    def get_all_sites(self) -> list:
        """Récupère tous les sites."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sites ORDER BY site_number")
        return [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    def get_site_by_id(self, site_id: int) -> dict:
        """Récupère un site par son ID."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sites WHERE id = ?", (site_id,))
        row = cursor.fetchone()
        if row:
            return dict(zip([d[0] for d in cursor.description], row))
        return None

    def create_site(self, site_number: str, site_name: str = "",
                    principal_investigator: str = "", address: str = "",
                    city: str = "", country: str = "", phone: str = "",
                    email: str = "") -> int:
        """Crée un nouveau site."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO sites (site_number, site_name, principal_investigator,
               address, city, country, phone, email)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (site_number, site_name, principal_investigator, address,
             city, country, phone, email)
        )
        conn.commit()
        return cursor.lastrowid

    def update_site(self, site_id: int, **kwargs) -> None:
        """Met à jour un site."""
        conn = self.connect()
        cursor = conn.cursor()
        allowed_fields = ["site_number", "site_name", "principal_investigator",
                          "address", "city", "country", "phone", "email"]
        updates = []
        values = []
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                values.append(value)
        if updates:
            values.append(site_id)
            cursor.execute(f"UPDATE sites SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()

    def delete_site(self, site_id: int) -> None:
        """Supprime un site."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sites WHERE id = ?", (site_id,))
        conn.commit()

    # ========== Méthodes pour les study_sites (liaison étude-site) ==========

    def get_study_sites(self, study_id: int) -> list:
        """Récupère les sites d'une étude avec leurs infos."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ss.*, s.site_number, s.site_name, s.principal_investigator,
                   s.city, s.country, s.phone, s.email,
                   (SELECT COUNT(*) FROM patients p WHERE p.site_id = s.site_number
                    AND p.study_id = ss.study_id) as patient_count
            FROM study_sites ss
            JOIN sites s ON ss.site_id = s.id
            WHERE ss.study_id = ?
            ORDER BY s.site_number
        """, (study_id,))
        return [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    def get_site_studies(self, site_id: int) -> list:
        """Récupère les études auxquelles participe un site."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ss.*, st.study_number, st.study_name, st.phase, st.sponsor
            FROM study_sites ss
            JOIN studies st ON ss.study_id = st.id
            WHERE ss.site_id = ?
            ORDER BY st.study_number
        """, (site_id,))
        return [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    def add_site_to_study(self, study_id: int, site_id: int, status: str = "Active",
                          principal_investigator: str = "", activation_date: str = None,
                          first_patient_date: str = None, target_patients: int = 0,
                          comments: str = "") -> int:
        """Ajoute un site à une étude."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO study_sites (study_id, site_id, status, principal_investigator,
               activation_date, first_patient_date, target_patients, comments)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (study_id, site_id, status, principal_investigator, activation_date,
             first_patient_date, target_patients, comments)
        )
        conn.commit()
        return cursor.lastrowid

    def update_study_site(self, study_site_id: int, **kwargs) -> None:
        """Met à jour la liaison étude-site."""
        conn = self.connect()
        cursor = conn.cursor()
        allowed_fields = ["status", "principal_investigator", "activation_date",
                          "first_patient_date", "target_patients", "comments"]
        updates = []
        values = []
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                values.append(value)
        if updates:
            values.append(study_site_id)
            cursor.execute(f"UPDATE study_sites SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()

    def remove_site_from_study(self, study_site_id: int) -> None:
        """Retire un site d'une étude."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM study_sites WHERE id = ?", (study_site_id,))
        conn.commit()

    def get_study_site_by_id(self, study_site_id: int) -> dict:
        """Récupère une liaison étude-site par son ID."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ss.*, s.site_number, s.site_name, s.city, s.country
            FROM study_sites ss
            JOIN sites s ON ss.site_id = s.id
            WHERE ss.id = ?
        """, (study_site_id,))
        row = cursor.fetchone()
        if row:
            return dict(zip([d[0] for d in cursor.description], row))
        return None

    def get_sites_not_in_study(self, study_id: int) -> list:
        """Récupère les sites qui ne participent pas encore à une étude."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM sites
            WHERE id NOT IN (SELECT site_id FROM study_sites WHERE study_id = ?)
            ORDER BY site_number
        """, (study_id,))
        return [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    # ========== Méthodes pour les visit_config ==========

    def get_visit_configs(self) -> list:
        """Récupère toutes les configurations de visites."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM visit_config ORDER BY visit_order")
        return [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    def create_visit_config(self, visit_name: str, target_day: int = 0,
                            window_before: int = 0, window_after: int = 0) -> int:
        """Crée une configuration de visite."""
        conn = self.connect()
        cursor = conn.cursor()
        # Trouver le prochain visit_order
        cursor.execute("SELECT COALESCE(MAX(visit_order), 0) + 1 FROM visit_config")
        visit_order = cursor.fetchone()[0]
        cursor.execute(
            """INSERT INTO visit_config (visit_name, visit_order, target_day, window_before, window_after)
               VALUES (?, ?, ?, ?, ?)""",
            (visit_name, visit_order, target_day, window_before, window_after)
        )
        conn.commit()
        return cursor.lastrowid

    def update_visit_config(self, config_id: int, **kwargs) -> None:
        """Met à jour une configuration de visite."""
        conn = self.connect()
        cursor = conn.cursor()
        allowed_fields = ["visit_name", "target_day", "window_before", "window_after"]
        updates = []
        values = []
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                values.append(value)
        if updates:
            values.append(config_id)
            cursor.execute(f"UPDATE visit_config SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()

    def delete_visit_config(self, config_id: int) -> None:
        """Supprime une configuration de visite."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM visit_config WHERE id = ?", (config_id,))
        conn.commit()

    # ========== Méthodes pour les consent_config ==========

    def get_consent_configs(self) -> list:
        """Récupère toutes les configurations de consentements."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM consent_config ORDER BY consent_type")
        return [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    def create_consent_config(self, consent_type: str, versions: str = "1.0",
                               is_required: bool = True) -> int:
        """Crée une configuration de consentement."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO consent_config (consent_type, versions, is_required) VALUES (?, ?, ?)",
            (consent_type, versions, int(is_required))
        )
        conn.commit()
        return cursor.lastrowid

    def update_consent_config(self, config_id: int, **kwargs) -> None:
        """Met à jour une configuration de consentement."""
        conn = self.connect()
        cursor = conn.cursor()
        allowed_fields = ["consent_type", "versions", "is_required"]
        updates = []
        values = []
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                if field == "is_required":
                    values.append(int(value))
                else:
                    values.append(value)
        if updates:
            values.append(config_id)
            cursor.execute(f"UPDATE consent_config SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()

    def delete_consent_config(self, config_id: int) -> None:
        """Supprime une configuration de consentement."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM consent_config WHERE id = ?", (config_id,))
        conn.commit()
