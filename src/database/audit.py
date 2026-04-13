"""
Service d'audit trail pour le suivi des modifications (GCP compliant).

Toutes les créations, modifications et suppressions sur les données cliniques
sont enregistrées dans la table audit_log avec l'ancienne et la nouvelle valeur.
"""

import sqlite3
from typing import List, Dict, Any, Optional


class AuditService:
    """
    Service statique d'audit trail.

    Usage :
        AuditService.log(conn, "patients", patient_id, "CREATE", new_value="PT-001")
        AuditService.log(conn, "patients", patient_id, "UPDATE", "status", "Screening", "Included")
        AuditService.log(conn, "patients", patient_id, "DELETE", old_value="PT-001")
    """

    # Tables cliniquement significatives pour le filtre de la vue
    TRACKED_TABLES = {
        "patients":       "Patient",
        "visits":         "Visit",
        "adverse_events": "Adverse Event",
        "queries":        "Query",
        "consents":       "Consent",
    }

    @staticmethod
    def log(
        conn: sqlite3.Connection,
        table_name: str,
        record_id: int,
        action: str,
        field_name: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        changed_by: str = "ARC",
    ) -> None:
        """
        Enregistre une entrée dans audit_log.

        Args:
            conn:        Connexion SQLite active
            table_name:  Nom de la table modifiée
            record_id:   ID de l'enregistrement concerné
            action:      'CREATE', 'UPDATE' ou 'DELETE'
            field_name:  Nom du champ modifié (pour UPDATE)
            old_value:   Ancienne valeur (pour UPDATE/DELETE)
            new_value:   Nouvelle valeur (pour CREATE/UPDATE)
            changed_by:  Utilisateur (défaut: 'ARC')
        """
        try:
            conn.execute(
                """INSERT INTO audit_log
                   (table_name, record_id, action, field_name, old_value, new_value, changed_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (table_name, record_id, action, field_name,
                 str(old_value) if old_value is not None else None,
                 str(new_value) if new_value is not None else None,
                 changed_by),
            )
            conn.commit()
        except Exception:
            # L'audit ne doit jamais faire planter l'opération principale
            pass

    @staticmethod
    def get_logs(
        conn: sqlite3.Connection,
        limit: int = 500,
        table_filter: Optional[str] = None,
        action_filter: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Récupère les entrées d'audit, les plus récentes en premier.

        Args:
            conn:          Connexion SQLite
            limit:         Nombre maximum d'entrées
            table_filter:  Filtrer par table_name
            action_filter: Filtrer par action ('CREATE', 'UPDATE', 'DELETE')
            search:        Recherche dans old_value / new_value / field_name

        Returns:
            Liste de dicts avec les colonnes de audit_log
        """
        conditions = []
        params: list = []

        if table_filter:
            conditions.append("table_name = ?")
            params.append(table_filter)

        if action_filter:
            conditions.append("action = ?")
            params.append(action_filter)

        if search:
            conditions.append(
                "(field_name LIKE ? OR old_value LIKE ? OR new_value LIKE ?)"
            )
            term = f"%{search}%"
            params.extend([term, term, term])

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(limit)

        cursor = conn.execute(
            f"""SELECT * FROM audit_log
                {where}
                ORDER BY changed_at DESC
                LIMIT ?""",
            params,
        )
        cursor.row_factory = sqlite3.Row
        return [dict(row) for row in cursor.fetchall()]
