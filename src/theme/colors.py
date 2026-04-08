# -*- coding: utf-8 -*-
"""
Palette de couleurs centralisée pour l'application.

Utilisation:
    from src.theme import AppColors

    ft.Container(bgcolor=AppColors.SUCCESS)
    ft.Text(color=AppColors.TEXT_PRIMARY)
"""


class AppColors:
    """Couleurs de l'application Clinical Study Tracker."""

    # ═══════════════════════════════════════════════════════════════
    # STATUTS - Couleurs sémantiques
    # ═══════════════════════════════════════════════════════════════

    SUCCESS = "#4CAF50"       # Vert - Actif, Complété, OK
    SUCCESS_LIGHT = "#81C784"
    SUCCESS_DARK = "#388E3C"

    WARNING = "#FF9800"       # Orange - Attention, En attente
    WARNING_LIGHT = "#FFB74D"
    WARNING_DARK = "#F57C00"

    ERROR = "#F44336"         # Rouge - Erreur, Critique, Hors fenêtre
    ERROR_LIGHT = "#E57373"
    ERROR_DARK = "#D32F2F"

    INFO = "#2196F3"          # Bleu - Information
    INFO_LIGHT = "#64B5F6"
    INFO_DARK = "#1976D2"

    NEUTRAL = "#9E9E9E"       # Gris - Inactif, Neutre
    NEUTRAL_LIGHT = "#BDBDBD"
    NEUTRAL_DARK = "#757575"

    # ═══════════════════════════════════════════════════════════════
    # PHASES D'ÉTUDE
    # ═══════════════════════════════════════════════════════════════

    PHASE_I = "#2196F3"       # Bleu
    PHASE_II = "#4CAF50"      # Vert
    PHASE_III = "#FF9800"     # Orange
    PHASE_IV = "#F44336"      # Rouge

    @staticmethod
    def get_phase_color(phase: str) -> str:
        """Retourne la couleur associée à une phase d'étude."""
        phase_colors = {
            "Phase I": AppColors.PHASE_I,
            "Phase II": AppColors.PHASE_II,
            "Phase III": AppColors.PHASE_III,
            "Phase IV": AppColors.PHASE_IV,
            "I": AppColors.PHASE_I,
            "II": AppColors.PHASE_II,
            "III": AppColors.PHASE_III,
            "IV": AppColors.PHASE_IV,
        }
        return phase_colors.get(phase, AppColors.INFO)

    # ═══════════════════════════════════════════════════════════════
    # STATUTS PATIENT
    # ═══════════════════════════════════════════════════════════════

    PATIENT_SCREENING = "#64B5F6"    # Bleu clair
    PATIENT_INCLUDED = "#4CAF50"     # Vert
    PATIENT_COMPLETED = "#9E9E9E"    # Gris
    PATIENT_WITHDRAWN = "#F44336"    # Rouge
    PATIENT_SCREEN_FAIL = "#FF9800"  # Orange

    @staticmethod
    def get_patient_status_color(status: str) -> str:
        """Retourne la couleur associée à un statut patient."""
        status_colors = {
            "Screening": AppColors.PATIENT_SCREENING,
            "Included": AppColors.PATIENT_INCLUDED,
            "Completed": AppColors.PATIENT_COMPLETED,
            "Withdrawn": AppColors.PATIENT_WITHDRAWN,
            "Screen Failure": AppColors.PATIENT_SCREEN_FAIL,
        }
        return status_colors.get(status, AppColors.NEUTRAL)

    # ═══════════════════════════════════════════════════════════════
    # STATUTS SITE
    # ═══════════════════════════════════════════════════════════════

    SITE_ACTIVE = "#4CAF50"      # Vert
    SITE_ON_HOLD = "#FF9800"     # Orange
    SITE_CLOSED = "#9E9E9E"      # Gris

    @staticmethod
    def get_site_status_color(status: str) -> str:
        """Retourne la couleur associée à un statut de site."""
        status_colors = {
            "Active": AppColors.SITE_ACTIVE,
            "On Hold": AppColors.SITE_ON_HOLD,
            "Closed": AppColors.SITE_CLOSED,
        }
        return status_colors.get(status, AppColors.NEUTRAL)

    # ═══════════════════════════════════════════════════════════════
    # VISITES
    # ═══════════════════════════════════════════════════════════════

    VISIT_COMPLETED = "#4CAF50"      # Vert
    VISIT_IN_WINDOW = "#4CAF50"      # Vert
    VISIT_OUT_WINDOW = "#F44336"     # Rouge
    VISIT_PENDING = "#FF9800"        # Orange
    VISIT_MISSED = "#9E9E9E"         # Gris
    VISIT_REFERENCE = "#2196F3"      # Bleu (V1)

    @staticmethod
    def get_visit_status_color(status: str) -> str:
        """Retourne la couleur associée à un statut de visite."""
        status_colors = {
            "Completed": AppColors.VISIT_COMPLETED,
            "In Window": AppColors.VISIT_IN_WINDOW,
            "Out of Window": AppColors.VISIT_OUT_WINDOW,
            "Pending": AppColors.VISIT_PENDING,
            "Missed": AppColors.VISIT_MISSED,
        }
        return status_colors.get(status, AppColors.NEUTRAL)

    # ═══════════════════════════════════════════════════════════════
    # ÉVÉNEMENTS INDÉSIRABLES
    # ═══════════════════════════════════════════════════════════════

    AE_MILD = "#81C784"          # Vert clair
    AE_MODERATE = "#FFB74D"      # Orange clair
    AE_SEVERE = "#E57373"        # Rouge clair
    AE_SAE = "#D32F2F"           # Rouge foncé

    AE_ONGOING = "#FF9800"       # Orange
    AE_RECOVERED = "#4CAF50"     # Vert
    AE_FATAL = "#212121"         # Noir
    AE_UNKNOWN = "#9E9E9E"       # Gris

    @staticmethod
    def get_ae_severity_color(severity: str) -> str:
        """Retourne la couleur associée à une sévérité d'EI."""
        severity_colors = {
            "Mild": AppColors.AE_MILD,
            "Moderate": AppColors.AE_MODERATE,
            "Severe": AppColors.AE_SEVERE,
        }
        return severity_colors.get(severity, AppColors.NEUTRAL)

    @staticmethod
    def get_ae_outcome_color(outcome: str) -> str:
        """Retourne la couleur associée à un outcome d'EI."""
        outcome_colors = {
            "Ongoing": AppColors.AE_ONGOING,
            "Recovered": AppColors.AE_RECOVERED,
            "Recovered with sequelae": AppColors.SUCCESS_LIGHT,
            "Fatal": AppColors.AE_FATAL,
            "Unknown": AppColors.AE_UNKNOWN,
        }
        return outcome_colors.get(outcome, AppColors.NEUTRAL)

    # ═══════════════════════════════════════════════════════════════
    # QUERIES
    # ═══════════════════════════════════════════════════════════════

    QUERY_OPEN = "#F44336"       # Rouge
    QUERY_ANSWERED = "#FF9800"   # Orange
    QUERY_CLOSED = "#4CAF50"     # Vert
    QUERY_OVERDUE = "#D32F2F"    # Rouge foncé

    @staticmethod
    def get_query_status_color(status: str) -> str:
        """Retourne la couleur associée à un statut de query."""
        status_colors = {
            "Open": AppColors.QUERY_OPEN,
            "Answered": AppColors.QUERY_ANSWERED,
            "Closed": AppColors.QUERY_CLOSED,
        }
        return status_colors.get(status, AppColors.NEUTRAL)

    # ═══════════════════════════════════════════════════════════════
    # DOCUMENTS / CONSENTEMENTS
    # ═══════════════════════════════════════════════════════════════

    CONSENT_SIGNED = "#4CAF50"       # Vert
    CONSENT_MISSING = "#F44336"      # Rouge
    CONSENT_UPDATE = "#FF9800"       # Orange (nouvelle version)

    @staticmethod
    def get_consent_status_color(status: str) -> str:
        """Retourne la couleur associée à un statut de consentement."""
        status_colors = {
            "Signed": AppColors.CONSENT_SIGNED,
            "Missing": AppColors.CONSENT_MISSING,
            "Update": AppColors.CONSENT_UPDATE,
        }
        return status_colors.get(status, AppColors.NEUTRAL)

    # ═══════════════════════════════════════════════════════════════
    # MONITORING
    # ═══════════════════════════════════════════════════════════════

    MONITORING_ON_SITE = "#4CAF50"   # Vert
    MONITORING_REMOTE = "#2196F3"    # Bleu
    MONITORING_PHONE = "#9C27B0"     # Violet

    @staticmethod
    def get_monitoring_type_color(type_: str) -> str:
        """Retourne la couleur associée à un type de monitoring."""
        type_colors = {
            "On-site": AppColors.MONITORING_ON_SITE,
            "Remote": AppColors.MONITORING_REMOTE,
            "Phone": AppColors.MONITORING_PHONE,
        }
        return type_colors.get(type_, AppColors.NEUTRAL)

    # ═══════════════════════════════════════════════════════════════
    # TEXTE
    # ═══════════════════════════════════════════════════════════════

    TEXT_PRIMARY = "#FFFFFF"         # Blanc (dark mode)
    TEXT_SECONDARY = "#B0B0B0"       # Gris clair
    TEXT_DISABLED = "#666666"        # Gris foncé
    TEXT_ON_PRIMARY = "#FFFFFF"      # Texte sur couleur primaire
    TEXT_ON_DARK = "#FFFFFF"         # Texte sur fond sombre
    TEXT_ON_LIGHT = "#212121"        # Texte sur fond clair

    # ═══════════════════════════════════════════════════════════════
    # SURFACES (Dark Mode)
    # ═══════════════════════════════════════════════════════════════

    SURFACE = "#1E1E1E"              # Fond principal
    SURFACE_VARIANT = "#2D2D2D"      # Fond secondaire (cartes)
    SURFACE_CONTAINER = "#252525"    # Conteneurs
    SURFACE_ELEVATED = "#333333"     # Éléments surélevés

    BORDER = "#404040"               # Bordures
    BORDER_LIGHT = "#505050"         # Bordures claires
    DIVIDER = "#3D3D3D"              # Séparateurs

    # ═══════════════════════════════════════════════════════════════
    # ACCENTS
    # ═══════════════════════════════════════════════════════════════

    PRIMARY = "#2196F3"              # Bleu principal
    PRIMARY_LIGHT = "#64B5F6"
    PRIMARY_DARK = "#1976D2"

    SECONDARY = "#03DAC6"            # Cyan accent
    SECONDARY_LIGHT = "#64FFDA"
    SECONDARY_DARK = "#00B8A2"
