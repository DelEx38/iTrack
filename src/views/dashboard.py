# -*- coding: utf-8 -*-
"""
Dashboard avec statistiques et vue d'ensemble.
"""

from datetime import date, timedelta

import flet as ft
from src.components import StatCard, GenericCard, SectionHeader, EmptyState
from src.theme import AppColors, Typography, Spacing
from src.services.report_generator import ReportGenerator
from src.services.window_alert import WindowAlertService


class DashboardView(ft.Container):
    """Vue du tableau de bord."""

    def __init__(self, patient_queries, visit_queries, ae_queries, query_queries=None, current_study=None):
        self.patient_queries = patient_queries
        self.visit_queries = visit_queries
        self.ae_queries = ae_queries
        self.query_queries = query_queries
        self.current_study = current_study or {}

        # Titre + bouton export
        export_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.PICTURE_AS_PDF, size=16), ft.Text("Export PDF")],
                spacing=4,
                tight=True,
            ),
            on_click=self._export_pdf,
            bgcolor=AppColors.PRIMARY,
            color=AppColors.TEXT_ON_PRIMARY,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
        )
        title = ft.Row(
            [ft.Text("Dashboard", **Typography.H2), ft.Container(expand=True), export_btn],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

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
            accent_color=AppColors.INFO,
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
            accent_color=AppColors.WARNING,
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

        super().__init__(content=content, padding=Spacing.PAGE_PADDING, expand=True, alignment=ft.Alignment.TOP_LEFT)

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

        # Alertes fenêtres + visites imminentes
        self._refresh_alerts()
        self._refresh_upcoming_visits()

    def _refresh_upcoming_visits(self) -> None:
        """Peuple la section 'Upcoming Visits' avec les visites à réaliser dans les 14 jours."""
        try:
            from src.services.window_alert import WindowAlertService
            today = date.today()
            horizon = today + timedelta(days=14)

            patients = self.patient_queries.get_all()
            visit_configs = self.visit_queries.get_configs()

            # Config de référence (target_day == 0)
            ref_id = next((vc["id"] for vc in visit_configs if vc.get("target_day", -1) == 0), None)

            upcoming = []
            for patient in patients:
                pid = patient["id"]
                visits_by_config = {
                    v["visit_config_id"]: v
                    for v in self.visit_queries.get_by_patient(pid)
                }
                # Date V1
                v1_entry = visits_by_config.get(ref_id) if ref_id else None
                if not v1_entry or not v1_entry.get("visit_date"):
                    continue
                v1_date = WindowAlertService._parse_date(v1_entry["visit_date"])
                if not v1_date:
                    continue

                for vc in visit_configs:
                    td = vc.get("target_day", 0)
                    if td == 0:
                        continue
                    if vc["id"] in visits_by_config:
                        continue  # Déjà réalisée
                    target = v1_date + timedelta(days=td)
                    if today <= target <= horizon:
                        upcoming.append((target, patient.get("patient_number", ""), vc.get("visit_name", "")))

            upcoming.sort()  # Trier par date

            if not upcoming:
                self._show_empty_visits()
            else:
                rows = []
                for target, pnum, vname in upcoming[:8]:
                    days_left = (target - today).days
                    color = AppColors.ERROR if days_left <= 3 else (
                        AppColors.WARNING if days_left <= 7 else AppColors.INFO
                    )
                    rows.append(ft.Row([
                        ft.Icon(ft.Icons.EVENT, color=color, size=14),
                        ft.Text(pnum, size=12, weight=ft.FontWeight.BOLD, width=70),
                        ft.Text(vname, size=12, width=40),
                        ft.Text(str(target), size=11, color=AppColors.TEXT_SECONDARY, expand=True),
                        ft.Text(f"in {days_left}d", size=11, color=color),
                    ], spacing=Spacing.XS))
                self.visits_content.controls = rows

            try:
                if self.page:
                    self.visits_content.update()
            except RuntimeError:
                pass
        except Exception:
            self._show_empty_visits()

    def _refresh_alerts(self) -> None:
        """Calcule et affiche les alertes de fenêtre."""
        try:
            alerts = WindowAlertService.get_alerts(
                self.patient_queries, self.visit_queries
            )
        except Exception:
            alerts = []

        if not alerts:
            self._show_empty_alerts()
            return

        # Couleurs par type
        _colors = {
            "OUT_OF_WINDOW": AppColors.ERROR,
            "OVERDUE":       "#F59E0B",
            "UPCOMING":      AppColors.INFO,
        }
        _icons = {
            "OUT_OF_WINDOW": ft.Icons.ERROR,
            "OVERDUE":       ft.Icons.WARNING,
            "UPCOMING":      ft.Icons.SCHEDULE,
        }

        rows = []
        for alert in alerts[:8]:  # Limiter à 8 dans le dashboard
            color = _colors.get(alert.alert_type, AppColors.TEXT_SECONDARY)
            icon  = _icons.get(alert.alert_type, ft.Icons.INFO)
            rows.append(
                ft.Row(
                    [
                        ft.Icon(icon, color=color, size=16),
                        ft.Text(
                            alert.patient_number,
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            width=70,
                        ),
                        ft.Text(alert.visit_name, size=12, width=50),
                        ft.Text(alert.label, size=11, color=color, expand=True),
                    ],
                    spacing=Spacing.XS,
                )
            )

        self.alerts_content.controls = rows

        # Suffix si trop d'alertes
        if len(alerts) > 8:
            self.alerts_content.controls.append(
                ft.Text(
                    f"... and {len(alerts) - 8} more. Go to Visits.",
                    size=10,
                    color=AppColors.TEXT_SECONDARY,
                    italic=True,
                )
            )

        try:
            if self.page:
                self.alerts_content.update()
        except RuntimeError:
            pass

    async def _export_pdf(self, e) -> None:
        """Ouvre un FilePicker pour choisir où enregistrer le rapport PDF."""
        study_ref = self.current_study.get("study_number", "report")

        file_picker = ft.FilePicker()
        self.page.overlay.append(file_picker)
        self.page.update()

        result = await file_picker.save_file_async(
            dialog_title="Enregistrer le rapport PDF",
            file_name=f"iTrack_{study_ref}_report.pdf",
            allowed_extensions=["pdf"],
        )

        self.page.overlay.remove(file_picker)
        self.page.update()

        if not result or not result.path:
            return

        output_path = result.path
        if not output_path.lower().endswith(".pdf"):
            output_path += ".pdf"

        try:
            gen = ReportGenerator(
                study=self.current_study,
                patient_queries=self.patient_queries,
                visit_queries=self.visit_queries,
                ae_queries=self.ae_queries,
                query_queries=self.query_queries,
            )
            gen.generate(output_path)
            self.page.open(ft.SnackBar(
                content=ft.Text(f"Rapport généré : {output_path}"),
                duration=4000,
            ))
        except ImportError as ex:
            self.page.open(ft.SnackBar(content=ft.Text(str(ex))))
        except Exception as ex:
            self.page.open(ft.SnackBar(content=ft.Text(f"Erreur : {ex}")))
