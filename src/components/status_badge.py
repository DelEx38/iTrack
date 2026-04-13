# -*- coding: utf-8 -*-
"""
Badge de statut réutilisable.

Utilisation:
    StatusBadge("Active", AppColors.SUCCESS)
    StatusBadge.patient_status("Included")
    StatusBadge.site_status("On Hold")
"""

import flet as ft
from src.theme import AppColors, Typography, Spacing, Radius


class StatusBadge(ft.Container):
    """Badge coloré pour afficher un statut."""

    def __init__(
        self,
        text: str,
        bgcolor: str = AppColors.NEUTRAL,
        text_color: str = AppColors.TEXT_ON_DARK,
        width: int = None,
    ):
        self.text_control = ft.Text(
            text,
            **Typography.BADGE,
            color=text_color,
            text_align=ft.TextAlign.CENTER,
        )

        super().__init__(
            content=self.text_control,
            bgcolor=bgcolor,
            border_radius=Radius.BADGE,
            padding=Spacing.badge(),
            width=width,
            alignment=ft.Alignment.CENTER,
        )

    def update_status(self, text: str, bgcolor: str) -> None:
        """Met à jour le statut affiché."""
        self.text_control.value = text
        self.bgcolor = bgcolor
        if self.page:
            self.update()

    # ═══════════════════════════════════════════════════════════════
    # FACTORIES POUR DIFFÉRENTS TYPES DE STATUTS
    # ═══════════════════════════════════════════════════════════════

    BADGE_WIDTH = 120

    @classmethod
    def patient_status(cls, status: str, width: int = BADGE_WIDTH) -> "StatusBadge":
        """Crée un badge pour un statut patient."""
        return cls(
            text=status,
            bgcolor=AppColors.get_patient_status_color(status),
            width=width,
        )

    @classmethod
    def site_status(cls, status: str, width: int = BADGE_WIDTH) -> "StatusBadge":
        """Crée un badge pour un statut de site."""
        return cls(
            text=status,
            bgcolor=AppColors.get_site_status_color(status),
            width=width,
        )

    @classmethod
    def visit_status(cls, status: str, width: int = BADGE_WIDTH) -> "StatusBadge":
        """Crée un badge pour un statut de visite."""
        return cls(
            text=status,
            bgcolor=AppColors.get_visit_status_color(status),
            width=width,
        )

    @classmethod
    def ae_severity(cls, severity: str, width: int = BADGE_WIDTH) -> "StatusBadge":
        """Crée un badge pour une sévérité d'EI."""
        return cls(
            text=severity,
            bgcolor=AppColors.get_ae_severity_color(severity),
            width=width,
        )

    @classmethod
    def ae_outcome(cls, outcome: str, width: int = BADGE_WIDTH) -> "StatusBadge":
        """Crée un badge pour un outcome d'EI."""
        text_color = AppColors.TEXT_ON_LIGHT if outcome == "Fatal" else AppColors.TEXT_ON_DARK
        return cls(
            text=outcome,
            bgcolor=AppColors.get_ae_outcome_color(outcome),
            text_color=text_color,
            width=width,
        )

    @classmethod
    def query_status(cls, status: str, width: int = BADGE_WIDTH) -> "StatusBadge":
        """Crée un badge pour un statut de query."""
        return cls(
            text=status,
            bgcolor=AppColors.get_query_status_color(status),
            width=width,
        )

    @classmethod
    def consent_status(cls, status: str, width: int = BADGE_WIDTH) -> "StatusBadge":
        """Crée un badge pour un statut de consentement."""
        return cls(
            text=status,
            bgcolor=AppColors.get_consent_status_color(status),
            width=width,
        )

    @classmethod
    def monitoring_type(cls, type_: str, width: int = BADGE_WIDTH) -> "StatusBadge":
        """Crée un badge pour un type de monitoring."""
        return cls(
            text=type_,
            bgcolor=AppColors.get_monitoring_type_color(type_),
            width=width,
        )

    @classmethod
    def phase(cls, phase: str, width: int = BADGE_WIDTH) -> "StatusBadge":
        """Crée un badge pour une phase d'étude."""
        return cls(
            text=phase,
            bgcolor=AppColors.get_phase_color(phase),
            width=width,
        )


class StatChip(ft.Container):
    """Chip pour afficher une statistique inline (label: value)."""

    def __init__(
        self,
        label: str,
        value: str | int,
        color: str = AppColors.NEUTRAL,
    ):
        self.value_text = ft.Text(
            str(value),
            size=12,
            weight=ft.FontWeight.BOLD,
        )

        content = ft.Row(
            [
                ft.Text(f"{label}:", **Typography.CHIP),
                self.value_text,
            ],
            spacing=Spacing.XXS,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        super().__init__(
            content=content,
            bgcolor=color,
            border_radius=Radius.CHIP,
            padding=Spacing.chip(),
            width=140,
            alignment=ft.Alignment.CENTER,
        )

    def update_value(self, value: str | int) -> None:
        """Met à jour la valeur affichée."""
        self.value_text.value = str(value)
        if self.page:
            self.update()
