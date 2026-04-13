"""
Service de calcul des alertes de fenêtre de visite.

Analyse l'ensemble des patients et de leurs visites pour détecter :
- Visites réalisées hors fenêtre (OUT_OF_WINDOW)
- Visites non réalisées dont la fenêtre est fermée (OVERDUE)
- Visites dont la fenêtre se ferme dans <= UPCOMING_DAYS jours (UPCOMING)
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


UPCOMING_DAYS = 7  # Jours avant fermeture de fenêtre pour déclencher l'alerte


@dataclass
class VisitAlert:
    """Alerte liée à une visite hors fenêtre ou imminente."""

    alert_type: str          # "OUT_OF_WINDOW" | "OVERDUE" | "UPCOMING"
    patient_number: str
    patient_id: int
    visit_name: str
    visit_config_id: int
    target_date: Optional[date] = None
    window_start: Optional[date] = None
    window_end: Optional[date] = None
    actual_date: Optional[date] = None
    delta_days: Optional[int] = None   # Écart vs date cible (positif = en avance)
    days_remaining: Optional[int] = None  # Jours avant fermeture fenêtre

    @property
    def severity(self) -> str:
        """Sévérité : 'error' | 'warning' | 'info'."""
        if self.alert_type == "OUT_OF_WINDOW":
            return "error"
        if self.alert_type == "OVERDUE":
            return "warning"
        return "info"

    @property
    def label(self) -> str:
        """Libellé court de l'alerte."""
        if self.alert_type == "OUT_OF_WINDOW":
            sign = "+" if self.delta_days > 0 else ""
            return f"Out of window ({sign}{self.delta_days}d)"
        if self.alert_type == "OVERDUE":
            days = (date.today() - self.window_end).days
            return f"Overdue by {days}d"
        return f"Window closes in {self.days_remaining}d"


class WindowAlertService:
    """
    Calcule les alertes de fenêtre pour tous les patients d'une étude.

    Usage :
        alerts = WindowAlertService.get_alerts(patient_queries, visit_queries)
    """

    @staticmethod
    def get_alerts(patient_queries, visit_queries) -> List[VisitAlert]:
        """
        Retourne toutes les alertes actives, triées par sévérité puis patient.

        Args:
            patient_queries : PatientQueries avec study_id défini
            visit_queries   : VisitQueries avec study_id défini

        Returns:
            Liste de VisitAlert (OUT_OF_WINDOW, OVERDUE, UPCOMING)
        """
        today = date.today()
        alerts: List[VisitAlert] = []

        patients = patient_queries.get_all()
        visit_configs = visit_queries.get_configs()

        # Trouver la config de référence (target_day == 0)
        ref_config_id = next(
            (vc["id"] for vc in visit_configs if vc.get("target_day", -1) == 0),
            None,
        )

        for patient in patients:
            pid = patient["id"]
            patient_visits = visit_queries.get_by_patient(pid)
            visits_by_config = {v["visit_config_id"]: v for v in patient_visits}

            # Date V1 (visite de référence)
            v1_date = WindowAlertService._get_v1_date(visits_by_config, ref_config_id)

            for vc in visit_configs:
                cid = vc["id"]
                target_day   = vc.get("target_day", 0)
                window_before = vc.get("window_before", 0)
                window_after  = vc.get("window_after", 0)

                # Pas d'alerte sur la visite de référence elle-même
                if target_day == 0:
                    continue

                # Sans V1, on ne peut pas calculer les dates
                if v1_date is None:
                    continue

                target_date  = v1_date + timedelta(days=target_day)
                window_start = target_date - timedelta(days=window_before)
                window_end   = target_date + timedelta(days=window_after)

                visit = visits_by_config.get(cid)

                if visit and visit.get("visit_date"):
                    # Visite réalisée — vérifier si hors fenêtre
                    actual = WindowAlertService._parse_date(visit["visit_date"])
                    if actual:
                        delta = (actual - target_date).days
                        if not (window_start <= actual <= window_end):
                            alerts.append(VisitAlert(
                                alert_type="OUT_OF_WINDOW",
                                patient_number=patient.get("patient_number", ""),
                                patient_id=pid,
                                visit_name=vc.get("visit_name", ""),
                                visit_config_id=cid,
                                target_date=target_date,
                                window_start=window_start,
                                window_end=window_end,
                                actual_date=actual,
                                delta_days=delta,
                            ))
                else:
                    # Visite non réalisée
                    if today > window_end:
                        # Fenêtre fermée → OVERDUE
                        alerts.append(VisitAlert(
                            alert_type="OVERDUE",
                            patient_number=patient.get("patient_number", ""),
                            patient_id=pid,
                            visit_name=vc.get("visit_name", ""),
                            visit_config_id=cid,
                            target_date=target_date,
                            window_start=window_start,
                            window_end=window_end,
                        ))
                    elif today >= window_start:
                        days_left = (window_end - today).days
                        if days_left <= UPCOMING_DAYS:
                            # Fenêtre ouverte mais se ferme bientôt → UPCOMING
                            alerts.append(VisitAlert(
                                alert_type="UPCOMING",
                                patient_number=patient.get("patient_number", ""),
                                patient_id=pid,
                                visit_name=vc.get("visit_name", ""),
                                visit_config_id=cid,
                                target_date=target_date,
                                window_start=window_start,
                                window_end=window_end,
                                days_remaining=days_left,
                            ))

        # Trier : OUT > OVERDUE > UPCOMING, puis par patient
        order = {"OUT_OF_WINDOW": 0, "OVERDUE": 1, "UPCOMING": 2}
        alerts.sort(key=lambda a: (order.get(a.alert_type, 9), a.patient_number))
        return alerts

    @staticmethod
    def _get_v1_date(visits_by_config: dict, ref_config_id: Optional[int]) -> Optional[date]:
        """Retourne la date de la visite de référence (target_day=0)."""
        if ref_config_id is None:
            return None
        v1 = visits_by_config.get(ref_config_id)
        if v1 and v1.get("visit_date"):
            return WindowAlertService._parse_date(v1["visit_date"])
        return None

    @staticmethod
    def _parse_date(value) -> Optional[date]:
        """Convertit string ou date en objet date."""
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                from datetime import datetime
                return datetime.strptime(value[:10], "%Y-%m-%d").date()
            except ValueError:
                return None
        return None
