# -*- coding: utf-8 -*-
"""
Dashboard avec statistiques et vue d'ensemble.
"""

import flet as ft
from src.components import StatCard, GenericCard, SectionHeader, EmptyState
from src.theme import AppColors, Typography, Spacing


class DashboardView(ft.Container):
    """Vue du tableau de bord."""

    def __init__(self, patient_queries, visit_queries, ae_queries):
        self.patient_queries = patient_queries
        self.visit_queries = visit_queries
        self.ae_queries = ae_queries

        # Titre
        title = ft.Text("Dashboard", **Typography.H2)

        # Cartes de statistiques
        self.card_total = StatCard(
            title="Total Patients",
            value="0",
            color=AppColors.INFO,
            icon=ft.Icons.PEOPLE
        )
        self.card_screening = StatCard(
            title="Screening",
            value="0",
            color=AppColors.PATIENT_SCREENING,
            icon=ft.Icons.HOURGLASS_EMPTY
        )
        self.card_included = StatCard(
            title="Included",
            value="0",
            color=AppColors.SUCCESS,
            icon=ft.Icons.CHECK_CIRCLE
        )
        self.card_ae = StatCard(
            title="Adverse Events",
            value="0",
            color=AppColors.ERROR,
            icon=ft.Icons.WARNING
        )

        stats_row = ft.Row(
            [self.card_total, self.card_screening, self.card_included, self.card_ae],
            spacing=Spacing.MD,
        )

        # Section visites à venir
        self.visits_content = ft.Column(spacing=Spacing.XS)
        self._show_empty_visits()

        visits_section = GenericCard(
            title="Upcoming Visits",
            icon=ft.Icons.CALENDAR_TODAY,
            content=ft.Container(
                content=self.visits_content,
                height=180,
            ),
            expand=True,
        )

        # Section alertes
        self.alerts_content = ft.Column(spacing=Spacing.XS)
        self._show_empty_alerts()

        alerts_section = GenericCard(
            title="Alerts & Notifications",
            icon=ft.Icons.NOTIFICATIONS,
            content=ft.Container(
                content=self.alerts_content,
                height=180,
            ),
            expand=True,
        )

        # Layout principal
        content = ft.Column(
            [
                title,
                ft.Container(height=Spacing.LG),
                stats_row,
                ft.Container(height=Spacing.LG),
                ft.Row([visits_section, alerts_section], spacing=Spacing.MD, expand=True),
            ],
            expand=True,
        )

        super().__init__(content=content, padding=Spacing.PAGE_PADDING, expand=True)

        # Charger les données
        self.refresh_data()

    def _show_empty_visits(self) -> None:
        """Affiche l'état vide pour les visites."""
        self.visits_content.controls = [
            EmptyState(
                title="No upcoming visits",
                description="All visits are up to date",
                icon=ft.Icons.EVENT_AVAILABLE,
            )
        ]

    def _show_empty_alerts(self) -> None:
        """Affiche l'état vide pour les alertes."""
        self.alerts_content.controls = [
            EmptyState(
                title="No alerts",
                description="Everything looks good",
                icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
            )
        ]

    def refresh_data(self) -> None:
        """Rafraîchit les données du dashboard."""
        status_counts = self.patient_queries.count_by_status()
        total = sum(status_counts.values())

        self.card_total.value_text.value = str(total)
        self.card_screening.value_text.value = str(status_counts.get("Screening", 0))
        self.card_included.value_text.value = str(status_counts.get("Included", 0))

        ae_counts = self.ae_queries.count_by_status()
        self.card_ae.value_text.value = str(ae_counts.get("total", 0))
