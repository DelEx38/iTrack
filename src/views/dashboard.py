"""
Dashboard avec statistiques et vue d'ensemble.
"""

import flet as ft
from components.stat_card import StatCard


class DashboardView(ft.Container):
    """Vue du tableau de bord."""

    def __init__(self, patient_queries, visit_queries, ae_queries):
        self.patient_queries = patient_queries
        self.visit_queries = visit_queries
        self.ae_queries = ae_queries

        # Titre
        title = ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD)

        # Cartes de statistiques
        self.card_total = StatCard(title="Total Patients", value="0", color="#3a7ebf", icon=ft.Icons.PEOPLE)
        self.card_screening = StatCard(title="Screening", value="0", color="#f0ad4e", icon=ft.Icons.HOURGLASS_EMPTY)
        self.card_included = StatCard(title="Included", value="0", color="#5cb85c", icon=ft.Icons.CHECK_CIRCLE)
        self.card_ae = StatCard(title="Adverse Events", value="0", color="#d9534f", icon=ft.Icons.WARNING)

        stats_row = ft.Row([self.card_total, self.card_screening, self.card_included, self.card_ae], spacing=15)

        # Section visites à venir
        self.visits_list = ft.ListView(spacing=5, height=200, auto_scroll=False)
        self.visits_list.controls.append(
            ft.Text("No upcoming visits", color=ft.Colors.GREY_500, italic=True)
        )

        visits_section = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Upcoming Visits", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=self.visits_list,
                        border_radius=10,
                        bgcolor=ft.Colors.SURFACE_CONTAINER,
                        padding=10,
                        expand=True,
                    ),
                ],
                spacing=10,
            ),
            expand=True,
        )

        # Section alertes
        self.alerts_list = ft.ListView(spacing=5, height=200, auto_scroll=False)
        self.alerts_list.controls.append(
            ft.Text("No alerts", color=ft.Colors.GREY_500, italic=True)
        )

        alerts_section = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Alerts & Notifications", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=self.alerts_list,
                        border_radius=10,
                        bgcolor=ft.Colors.SURFACE_CONTAINER,
                        padding=10,
                        expand=True,
                    ),
                ],
                spacing=10,
            ),
            expand=True,
        )

        # Layout principal
        content = ft.Column(
            [
                title,
                ft.Container(height=20),
                stats_row,
                ft.Container(height=20),
                ft.Row([visits_section, alerts_section], spacing=15, expand=True),
            ],
            expand=True,
        )

        super().__init__(content=content, padding=20, expand=True)

        # Charger les données
        self.refresh_data()

    def refresh_data(self) -> None:
        """Rafraîchit les données du dashboard."""
        status_counts = self.patient_queries.count_by_status()
        total = sum(status_counts.values())

        self.card_total.value_text.value = str(total)
        self.card_screening.value_text.value = str(status_counts.get("Screening", 0))
        self.card_included.value_text.value = str(status_counts.get("Included", 0))

        ae_counts = self.ae_queries.count_by_status()
        self.card_ae.value_text.value = str(ae_counts.get("total", 0))
