"""
Requêtes de base de données pour le suivi d'étude clinique.
"""

from typing import List, Dict, Any, Optional
from datetime import date, timedelta
import sqlite3


class BaseQueries:
    """Classe de base pour les requêtes."""

    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def _dict_from_row(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convertit une Row en dictionnaire."""
        return dict(zip(row.keys(), row))


class PatientQueries(BaseQueries):
    """Requêtes pour la gestion des patients."""

    def __init__(self, connection: sqlite3.Connection, study_id: Optional[int] = None):
        super().__init__(connection)
        self.study_id = study_id

    def set_study(self, study_id: int) -> None:
        """Définit l'étude courante."""
        self.study_id = study_id

    def create(
        self,
        patient_number: str,
        initials: str = "",
        birth_date: Optional[date] = None,
        site_id: str = "",
        status: str = "Screening"
    ) -> int:
        """Crée un nouveau patient."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO patients (study_id, patient_number, initials, birth_date, site_id, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.study_id, patient_number, initials, birth_date, site_id, status))
        self.conn.commit()
        return cursor.lastrowid

    def get_by_id(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un patient par son ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        row = cursor.fetchone()
        return self._dict_from_row(row) if row else None

    def get_by_number(self, patient_number: str) -> Optional[Dict[str, Any]]:
        """Récupère un patient par son numéro."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE patient_number = ?", (patient_number,))
        row = cursor.fetchone()
        return self._dict_from_row(row) if row else None

    def get_all(self) -> List[Dict[str, Any]]:
        """Récupère tous les patients de l'étude courante."""
        cursor = self.conn.cursor()
        if self.study_id:
            cursor.execute("SELECT * FROM patients WHERE study_id = ? ORDER BY patient_number", (self.study_id,))
        else:
            cursor.execute("SELECT * FROM patients ORDER BY patient_number")
        return [self._dict_from_row(row) for row in cursor.fetchall()]

    def update(self, patient_id: int, **kwargs) -> bool:
        """Met à jour un patient."""
        if not kwargs:
            return False

        fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [patient_id]

        cursor = self.conn.cursor()
        cursor.execute(f"""
            UPDATE patients SET {fields}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, values)
        self.conn.commit()
        return cursor.rowcount > 0

    def delete(self, patient_id: int) -> bool:
        """Supprime un patient."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def count_by_status(self) -> Dict[str, int]:
        """Compte les patients par statut pour l'étude courante."""
        cursor = self.conn.cursor()
        if self.study_id:
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM patients
                WHERE study_id = ?
                GROUP BY status
            """, (self.study_id,))
        else:
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM patients
                GROUP BY status
            """)
        return {row["status"]: row["count"] for row in cursor.fetchall()}

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Recherche des patients dans l'étude courante."""
        cursor = self.conn.cursor()
        search_term = f"%{query}%"
        if self.study_id:
            cursor.execute("""
                SELECT * FROM patients
                WHERE study_id = ? AND (patient_number LIKE ? OR initials LIKE ? OR site_id LIKE ?)
                ORDER BY patient_number
            """, (self.study_id, search_term, search_term, search_term))
        else:
            cursor.execute("""
                SELECT * FROM patients
                WHERE patient_number LIKE ? OR initials LIKE ? OR site_id LIKE ?
                ORDER BY patient_number
            """, (search_term, search_term, search_term))
        return [self._dict_from_row(row) for row in cursor.fetchall()]


class VisitQueries(BaseQueries):
    """Requêtes pour la gestion des visites."""

    def get_configs(self) -> List[Dict[str, Any]]:
        """Récupère la configuration des visites."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM visit_config ORDER BY visit_order")
        return [self._dict_from_row(row) for row in cursor.fetchall()]

    def get_config(self, config_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une configuration de visite par son ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM visit_config WHERE id = ?", (config_id,))
        row = cursor.fetchone()
        return self._dict_from_row(row) if row else None

    def get_by_patient(self, patient_id: int) -> List[Dict[str, Any]]:
        """Récupère toutes les visites d'un patient."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT v.*, vc.visit_name, vc.target_day, vc.window_before, vc.window_after
            FROM visits v
            JOIN visit_config vc ON v.visit_config_id = vc.id
            WHERE v.patient_id = ?
            ORDER BY vc.visit_order
        """, (patient_id,))
        return [self._dict_from_row(row) for row in cursor.fetchall()]

    def update(self, visit_id: int, **kwargs) -> bool:
        """Met à jour une visite."""
        if not kwargs:
            return False

        fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [visit_id]

        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE visits SET {fields} WHERE id = ?", values)
        self.conn.commit()
        return cursor.rowcount > 0

    def update_config(
        self,
        visit_id: int,
        target_day: int,
        window_before: int,
        window_after: int
    ) -> bool:
        """Met à jour la configuration d'une visite."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE visit_config
            SET target_day = ?, window_before = ?, window_after = ?
            WHERE id = ?
        """, (target_day, window_before, window_after, visit_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def record_visit(
        self,
        patient_id: int,
        visit_config_id: int,
        visit_date: date,
        status: str = "Completed",
        comments: str = ""
    ) -> int:
        """Enregistre une visite réalisée."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO visits (patient_id, visit_config_id, visit_date, status, comments)
            VALUES (?, ?, ?, ?, ?)
        """, (patient_id, visit_config_id, visit_date, status, comments))
        self.conn.commit()
        return cursor.lastrowid

    def get_patient_visits(self, patient_id: int) -> List[Dict[str, Any]]:
        """Récupère toutes les visites d'un patient."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT v.*, vc.visit_name, vc.target_day, vc.window_before, vc.window_after
            FROM visits v
            JOIN visit_config vc ON v.visit_config_id = vc.id
            WHERE v.patient_id = ?
            ORDER BY vc.visit_order
        """, (patient_id,))
        return [self._dict_from_row(row) for row in cursor.fetchall()]

    def check_window(self, patient_id: int, visit_config_id: int, visit_date: date) -> Dict[str, Any]:
        """Vérifie si une visite est dans la fenêtre."""
        cursor = self.conn.cursor()

        # Récupérer la config de la visite
        cursor.execute("SELECT * FROM visit_config WHERE id = ?", (visit_config_id,))
        config = cursor.fetchone()
        if not config:
            return {"valid": False, "error": "Visit config not found"}

        # Récupérer la date de V1
        cursor.execute("""
            SELECT v.visit_date
            FROM visits v
            JOIN visit_config vc ON v.visit_config_id = vc.id
            WHERE v.patient_id = ? AND vc.visit_order = 1
        """, (patient_id,))
        v1_row = cursor.fetchone()

        if not v1_row or not v1_row["visit_date"]:
            return {"valid": True, "message": "V1 not recorded yet"}

        v1_date = v1_row["visit_date"]
        target_date = v1_date + timedelta(days=config["target_day"])
        min_date = target_date + timedelta(days=config["window_before"])
        max_date = target_date + timedelta(days=config["window_after"])

        is_valid = min_date <= visit_date <= max_date
        delta = (visit_date - target_date).days

        return {
            "valid": is_valid,
            "target_date": target_date,
            "min_date": min_date,
            "max_date": max_date,
            "actual_date": visit_date,
            "delta_days": delta
        }


class ConsentQueries(BaseQueries):
    """Requêtes pour la gestion des consentements."""

    def get_configs(self) -> List[Dict[str, Any]]:
        """Récupère les configurations de consentement."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM consent_config ORDER BY consent_type")
        return [self._dict_from_row(row) for row in cursor.fetchall()]

    def get_by_patient(self, patient_id: int) -> List[Dict[str, Any]]:
        """Récupère les consentements d'un patient."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.*, cc.consent_type
            FROM consents c
            LEFT JOIN consent_config cc ON c.consent_config_id = cc.id
            WHERE c.patient_id = ?
            ORDER BY c.consent_date
        """, (patient_id,))
        return [self._dict_from_row(row) for row in cursor.fetchall()]

    def create(self, patient_id: int, consent_config_id: int, version: str, consent_date: str, notes: str = None) -> int:
        """Crée un consentement."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO consents (patient_id, consent_config_id, version, consent_date, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (patient_id, consent_config_id, version, consent_date, notes))
        self.conn.commit()
        return cursor.lastrowid

    def update(self, consent_id: int, **kwargs) -> bool:
        """Met à jour un consentement."""
        if not kwargs:
            return False

        fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [consent_id]

        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE consents SET {fields} WHERE id = ?", values)
        self.conn.commit()
        return cursor.rowcount > 0

    def delete(self, consent_id: int) -> bool:
        """Supprime un consentement."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM consents WHERE id = ?", (consent_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_types(self) -> List[Dict[str, Any]]:
        """Récupère les types de consentement."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM consent_types ORDER BY type_name")
        return [self._dict_from_row(row) for row in cursor.fetchall()]

    def add_type(self, type_name: str) -> int:
        """Ajoute un type de consentement."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO consent_types (type_name) VALUES (?)", (type_name,))
        self.conn.commit()
        return cursor.lastrowid

    def delete_type(self, type_id: int) -> None:
        """Supprime un type de consentement et ses versions."""
        cursor = self.conn.cursor()
        # Supprimer les versions associées d'abord
        cursor.execute("DELETE FROM consent_versions WHERE consent_type_id = ?", (type_id,))
        cursor.execute("DELETE FROM consent_types WHERE id = ?", (type_id,))
        self.conn.commit()

    def delete_version(self, version_id: int) -> None:
        """Supprime une version de consentement."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM consent_versions WHERE id = ?", (version_id,))
        self.conn.commit()

    def add_version(
        self,
        consent_type_id: int,
        version: str,
        version_date: Optional[date] = None,
        comments: str = ""
    ) -> int:
        """Ajoute une version de consentement."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO consent_versions (consent_type_id, version, version_date, comments)
            VALUES (?, ?, ?, ?)
        """, (consent_type_id, version, version_date, comments))
        self.conn.commit()
        return cursor.lastrowid

    def get_versions(self, consent_type_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Récupère les versions de consentement."""
        cursor = self.conn.cursor()
        if consent_type_id:
            cursor.execute("""
                SELECT cv.*, ct.type_name
                FROM consent_versions cv
                JOIN consent_types ct ON cv.consent_type_id = ct.id
                WHERE cv.consent_type_id = ?
                ORDER BY cv.version
            """, (consent_type_id,))
        else:
            cursor.execute("""
                SELECT cv.*, ct.type_name
                FROM consent_versions cv
                JOIN consent_types ct ON cv.consent_type_id = ct.id
                ORDER BY ct.type_name, cv.version
            """)
        return [self._dict_from_row(row) for row in cursor.fetchall()]

    def record_consent(
        self,
        patient_id: int,
        consent_version_id: int,
        signature_date: date,
        comments: str = ""
    ) -> int:
        """Enregistre un consentement signé."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO patient_consents (patient_id, consent_version_id, signature_date, comments)
            VALUES (?, ?, ?, ?)
        """, (patient_id, consent_version_id, signature_date, comments))
        self.conn.commit()
        return cursor.lastrowid

    def get_patient_consents(self, patient_id: int) -> List[Dict[str, Any]]:
        """Récupère les consentements d'un patient."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT pc.*, cv.version, cv.version_date, ct.type_name
            FROM patient_consents pc
            JOIN consent_versions cv ON pc.consent_version_id = cv.id
            JOIN consent_types ct ON cv.consent_type_id = ct.id
            WHERE pc.patient_id = ?
            ORDER BY pc.signature_date
        """, (patient_id,))
        return [self._dict_from_row(row) for row in cursor.fetchall()]


class AdverseEventQueries(BaseQueries):
    """Requêtes pour la gestion des événements indésirables."""

    def __init__(self, connection: sqlite3.Connection, study_id: Optional[int] = None):
        super().__init__(connection)
        self.study_id = study_id

    def set_study(self, study_id: int) -> None:
        """Définit l'étude courante."""
        self.study_id = study_id

    def get_all(self) -> List[Dict[str, Any]]:
        """Récupère tous les EI de l'étude courante."""
        cursor = self.conn.cursor()
        if self.study_id:
            cursor.execute("""
                SELECT ae.*, p.patient_number
                FROM adverse_events ae
                JOIN patients p ON ae.patient_id = p.id
                WHERE p.study_id = ?
                ORDER BY ae.start_date DESC
            """, (self.study_id,))
        else:
            cursor.execute("""
                SELECT ae.*, p.patient_number
                FROM adverse_events ae
                JOIN patients p ON ae.patient_id = p.id
                ORDER BY ae.start_date DESC
            """)
        return [self._dict_from_row(row) for row in cursor.fetchall()]

    def create(self, patient_id: int, ae_term: str, start_date: str, end_date: str = None,
               severity: str = "Mild", is_serious: bool = False, reporting_date: str = None,
               outcome: str = "Recovering", causality: str = "Unknown", notes: str = None, **kwargs) -> int:
        """Crée un événement indésirable."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO adverse_events
            (patient_id, ae_term, start_date, end_date, severity, is_serious, reporting_date, outcome, causality, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (patient_id, ae_term, start_date, end_date, severity, int(is_serious), reporting_date, outcome, causality, notes))
        self.conn.commit()
        return cursor.lastrowid

    def delete(self, ae_id: int) -> bool:
        """Supprime un EI."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM adverse_events WHERE id = ?", (ae_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_by_patient(self, patient_id: int) -> List[Dict[str, Any]]:
        """Récupère les EI d'un patient."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM adverse_events
            WHERE patient_id = ?
            ORDER BY ae_number
        """, (patient_id,))
        return [self._dict_from_row(row) for row in cursor.fetchall()]

    def get_all_serious(self) -> List[Dict[str, Any]]:
        """Récupère tous les EIG de l'étude courante."""
        cursor = self.conn.cursor()
        if self.study_id:
            cursor.execute("""
                SELECT ae.*, p.patient_number
                FROM adverse_events ae
                JOIN patients p ON ae.patient_id = p.id
                WHERE ae.is_serious = 1 AND p.study_id = ?
                ORDER BY ae.start_date DESC
            """, (self.study_id,))
        else:
            cursor.execute("""
                SELECT ae.*, p.patient_number
                FROM adverse_events ae
                JOIN patients p ON ae.patient_id = p.id
                WHERE ae.is_serious = 1
                ORDER BY ae.start_date DESC
            """)
        return [self._dict_from_row(row) for row in cursor.fetchall()]

    def update(self, ae_id: int, **kwargs) -> bool:
        """Met à jour un EI."""
        if not kwargs:
            return False

        fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [ae_id]

        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE adverse_events SET {fields} WHERE id = ?", values)
        self.conn.commit()
        return cursor.rowcount > 0

    def count_by_status(self) -> Dict[str, int]:
        """Compte les EI par statut pour l'étude courante."""
        cursor = self.conn.cursor()
        if self.study_id:
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN ae.is_serious = 1 THEN 1 ELSE 0 END) as serious,
                    SUM(CASE WHEN ae.outcome = 'Ongoing' OR ae.outcome IS NULL THEN 1 ELSE 0 END) as ongoing
                FROM adverse_events ae
                JOIN patients p ON ae.patient_id = p.id
                WHERE p.study_id = ?
            """, (self.study_id,))
        else:
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN is_serious = 1 THEN 1 ELSE 0 END) as serious,
                    SUM(CASE WHEN outcome = 'Ongoing' OR outcome IS NULL THEN 1 ELSE 0 END) as ongoing
                FROM adverse_events
            """)
        row = cursor.fetchone()
        return {
            "total": row["total"] or 0,
            "serious": row["serious"] or 0,
            "ongoing": row["ongoing"] or 0
        }


class QueryQueries(BaseQueries):
    """Requêtes pour la gestion des queries (data management)."""

    def __init__(self, connection: sqlite3.Connection, study_id: Optional[int] = None):
        super().__init__(connection)
        self.study_id = study_id

    def set_study(self, study_id: int) -> None:
        """Définit l'étude courante."""
        self.study_id = study_id

    def get_all(self) -> List[Dict[str, Any]]:
        """Récupère toutes les queries de l'étude courante."""
        cursor = self.conn.cursor()
        if self.study_id:
            cursor.execute("""
                SELECT q.*, p.patient_number
                FROM queries q
                JOIN patients p ON q.patient_id = p.id
                WHERE p.study_id = ?
                ORDER BY q.created_at DESC
            """, (self.study_id,))
        else:
            cursor.execute("""
                SELECT q.*, p.patient_number
                FROM queries q
                JOIN patients p ON q.patient_id = p.id
                ORDER BY q.created_at DESC
            """)
        return [self._dict_from_row(row) for row in cursor.fetchall()]

    def create(self, patient_id: int, field_name: str, description: str,
               priority: str = "Medium", status: str = "Open", response: str = None) -> int:
        """Crée une query."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO queries (patient_id, field_name, description, priority, status, response)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (patient_id, field_name, description, priority, status, response))
        self.conn.commit()
        return cursor.lastrowid

    def update(self, query_id: int, **kwargs) -> bool:
        """Met à jour une query."""
        if not kwargs:
            return False

        fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [query_id]

        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE queries SET {fields}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
        self.conn.commit()
        return cursor.rowcount > 0

    def delete(self, query_id: int) -> bool:
        """Supprime une query."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM queries WHERE id = ?", (query_id,))
        self.conn.commit()
        return cursor.rowcount > 0


class MonitoringQueries(BaseQueries):
    """Requêtes pour la gestion du monitoring."""

    def __init__(self, connection: sqlite3.Connection, study_id: Optional[int] = None):
        super().__init__(connection)
        self.study_id = study_id

    def set_study(self, study_id: int) -> None:
        """Définit l'étude courante."""
        self.study_id = study_id

    def get_all(self) -> List[Dict[str, Any]]:
        """Récupère toutes les entrées de monitoring de l'étude courante."""
        cursor = self.conn.cursor()
        if self.study_id:
            cursor.execute("""
                SELECT m.*, p.patient_number
                FROM monitoring m
                JOIN patients p ON m.patient_id = p.id
                WHERE p.study_id = ?
                ORDER BY m.monitoring_date DESC
            """, (self.study_id,))
        else:
            cursor.execute("""
                SELECT m.*, p.patient_number
                FROM monitoring m
                JOIN patients p ON m.patient_id = p.id
                ORDER BY m.monitoring_date DESC
            """)
        return [self._dict_from_row(row) for row in cursor.fetchall()]

    def create(self, patient_id: int, monitoring_date: str, monitoring_type: str = "Source Data Verification",
               findings: str = None, actions_required: str = None, is_completed: bool = False) -> int:
        """Crée une entrée de monitoring."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO monitoring (patient_id, monitoring_date, monitoring_type, findings, actions_required, is_completed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (patient_id, monitoring_date, monitoring_type, findings, actions_required, int(is_completed)))
        self.conn.commit()
        return cursor.lastrowid

    def update(self, entry_id: int, **kwargs) -> bool:
        """Met à jour une entrée de monitoring."""
        if not kwargs:
            return False

        # Convertir is_completed en int si présent
        if "is_completed" in kwargs:
            kwargs["is_completed"] = int(kwargs["is_completed"])

        fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [entry_id]

        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE monitoring SET {fields} WHERE id = ?", values)
        self.conn.commit()
        return cursor.rowcount > 0

    def delete(self, entry_id: int) -> bool:
        """Supprime une entrée de monitoring."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM monitoring WHERE id = ?", (entry_id,))
        self.conn.commit()
        return cursor.rowcount > 0
