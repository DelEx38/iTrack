"""
Application principale Flet - Clinical Study Tracker.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional, Dict

import flet as ft

from database.models import Database
from theme.colors import AppColors
from database.queries import PatientQueries, VisitQueries, ConsentQueries, AdverseEventQueries, QueryQueries, MonitoringQueries
from components.sidebar import Sidebar
from views.dashboard import DashboardView
from views.landing import LandingView
from views.patients import PatientsView
from views.sites import SitesView
from views.visits import VisitsView
from views.adverse_events import AdverseEventsView
from views.documents import DocumentsView
from views.queries import QueriesView
from views.monitoring import MonitoringView
from views.settings import SettingsView
from views.audit import AuditView

_APP_VERSION = "1.0.0"


def _assets_path() -> Path:
    """Retourne le chemin du dossier assets (dev + PyInstaller)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "assets"
    return Path(__file__).parent.parent / "assets"


class ClinicalStudyApp:
    """Application principale."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.current_view: Optional[ft.Control] = None
        self.current_study: Optional[Dict] = None

        # Attributs initialisés plus tard (après splash)
        self.db: Optional[Database] = None
        self.studies: list = []
        self.patient_queries = None
        self.visit_queries = None
        self.consent_queries = None
        self.ae_queries = None
        self.query_queries = None
        self.monitoring_queries = None
        self.sidebar: Optional[ft.Control] = None
        self.view_container: Optional[ft.Container] = None
        self.main_row: Optional[ft.Row] = None

        # Configuration de base de la page
        self.page.title = "iTrack — Clinical Study Tracker"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.spacing = 0
        self.page.window.min_width = 1270
        self.page.window.min_height = 760
        self.page.window.width = 1270
        self.page.window.height = 760

        icon_file = _assets_path() / "icon.png"
        if icon_file.exists():
            self.page.window.icon = str(icon_file)

        self.page.bgcolor = AppColors.SURFACE

        _dark_scheme = ft.ColorScheme(
            primary=AppColors.PRIMARY,
            on_primary=AppColors.TEXT_ON_PRIMARY,
            primary_container=AppColors.PRIMARY_DARK,
            on_primary_container=AppColors.PRIMARY_LIGHT,
            secondary=AppColors.SECONDARY,
            on_secondary="#000000",
            error=AppColors.ERROR,
            on_error=AppColors.TEXT_ON_PRIMARY,
            surface=AppColors.SURFACE,
            on_surface=AppColors.TEXT_PRIMARY,
            surface_container=AppColors.SURFACE_VARIANT,
            on_surface_variant=AppColors.TEXT_SECONDARY,
            outline=AppColors.BORDER,
            outline_variant=AppColors.DIVIDER,
        )
        self.page.theme = ft.Theme(use_material3=True)
        self.page.dark_theme = ft.Theme(
            color_scheme=_dark_scheme,
            use_material3=True,
        )

        # Afficher le splash screen immédiatement
        self._splash_status = ft.Text(
            "Initialisation...",
            size=12,
            color=ft.Colors.GREY_500,
        )
        self.page.add(self._build_splash())
        self.page.update()

        # Lancer l'initialisation asynchrone
        page.run_task(self._initialize_async)

    # ─── Splash screen ────────────────────────────────────────────────────────

    def _build_splash(self) -> ft.Container:
        """Construit l'écran de démarrage."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.MEDICAL_SERVICES_ROUNDED,
                            size=72,
                            color=ft.Colors.BLUE_400,
                        ),
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Container(height=20),
                    ft.Text(
                        "iTrack",
                        size=44,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Text(
                        "Clinical Study Tracker",
                        size=15,
                        color=ft.Colors.BLUE_200,
                    ),
                    ft.Container(height=48),
                    ft.ProgressRing(
                        width=28,
                        height=28,
                        stroke_width=3,
                        color=ft.Colors.BLUE_400,
                    ),
                    ft.Container(height=12),
                    self._splash_status,
                    ft.Container(height=32),
                    ft.Text(
                        f"v{_APP_VERSION}",
                        size=11,
                        color=ft.Colors.GREY_700,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            expand=True,
            bgcolor="#0D1117",
            alignment=ft.Alignment.CENTER,
        )

    async def _initialize_async(self):
        """Initialisation asynchrone : DB → UI principale → landing."""
        await asyncio.sleep(0.6)  # Laisser le splash s'afficher

        # Init base de données
        self._splash_status.value = "Chargement de la base de données..."
        self.page.update()
        await asyncio.sleep(0.05)

        self._init_database()

        self._splash_status.value = "Préparation de l'interface..."
        self.page.update()
        await asyncio.sleep(0.05)

        # Construire l'UI principale
        self._build_main_ui()

        # Effacer le splash et afficher la landing
        self.page.controls.clear()
        self.page.add(self.main_row)
        self._show_landing()

    def _init_database(self):
        """Initialisation synchrone de la base de données."""
        self.db = Database()
        self.db.connect()
        self.db.init_schema()

        self.studies = self.db.get_studies()
        if not self.studies:
            study_id = self.db.create_study(study_number="STUDY-001", study_name="My First Study")
            self.studies = self.db.get_studies()
            self.current_study = self.db.get_study_by_id(study_id)
        else:
            self.current_study = self.studies[0]

        self.db.init_default_data(study_id=self.current_study["id"], num_visits=25)

        study_id = self.current_study["id"]
        self.patient_queries = PatientQueries(self.db.connection, study_id)
        self.visit_queries = VisitQueries(self.db.connection, study_id)
        self.consent_queries = ConsentQueries(self.db.connection, study_id)
        self.ae_queries = AdverseEventQueries(self.db.connection, study_id)
        self.query_queries = QueryQueries(self.db.connection, study_id)
        self.monitoring_queries = MonitoringQueries(self.db.connection, study_id)

    def _build_main_ui(self):
        """Construit sidebar + layout principal."""
        self.sidebar = Sidebar(
            on_navigate=self._on_navigate,
            on_study_change=self._on_study_change,
            studies=self.studies,
            current_study=self.current_study,
        )
        self.view_container = ft.AnimatedSwitcher(
            content=ft.Container(expand=True),
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=180,
            reverse_duration=100,
            switch_in_curve=ft.AnimationCurve.EASE_OUT,
            switch_out_curve=ft.AnimationCurve.EASE_IN,
            expand=True,
        )
        self.main_row = ft.Row(
            [self.sidebar, self.view_container],
            spacing=0,
            expand=True,
        )

    def _on_navigate(self, view_name: str) -> None:
        """Callback de navigation."""
        if view_name == "home":
            self._show_landing()
        elif view_name == "dashboard":
            self._show_dashboard()
        elif view_name == "patients":
            self._show_patients()
        elif view_name == "sites":
            self._show_sites()
        elif view_name == "visits":
            self._show_visits()
        elif view_name == "adverse_events":
            self._show_adverse_events()
        elif view_name == "documents":
            self._show_documents()
        elif view_name == "queries":
            self._show_queries()
        elif view_name == "monitoring":
            self._show_monitoring()
        elif view_name == "audit":
            self._show_audit()
        elif view_name == "settings":
            self._show_settings()
        elif view_name == "export":
            self._export_excel()
        else:
            self._show_placeholder(view_name.replace("_", " ").title())

    def _on_study_change(self, study_identifier: str) -> None:
        """Callback quand l'étude change."""
        for study in self.studies:
            if study.get("study_number") == study_identifier or study.get("study_name") == study_identifier:
                self.current_study = study
                sid = study["id"]
                self.patient_queries.set_study(sid)
                self.visit_queries.set_study(sid)
                self.consent_queries.set_study(sid)
                self.ae_queries.set_study(sid)
                self.query_queries.set_study(sid)
                self.monitoring_queries.set_study(sid)
                self._update_title()
                self._show_dashboard()
                break

    def _refresh_studies(self) -> None:
        """Rafraîchit la liste des études."""
        self.studies = self.db.get_studies()
        self.sidebar.update_studies(self.studies, self.current_study)

    def _update_title(self) -> None:
        """Met à jour le titre de la fenêtre."""
        if self.current_study:
            study_label = self.current_study.get('study_number') or self.current_study.get('study_name') or ''
            self.page.title = f"Clinical Study Tracker - {study_label}"
        else:
            self.page.title = "Clinical Study Tracker"
        self.page.update()

    def _switch_view(self, view: ft.Control) -> None:
        """Change la vue principale."""
        self.current_view = view
        self.view_container.content = view
        self.page.update()

    def _show_landing(self) -> None:
        """Affiche la landing page."""
        self.sidebar.visible = False

        view = LandingView(
            db=self.db,
            on_study_select=self._on_study_select_from_landing,
            on_new_study=self._new_study_from_landing,
        )
        self._switch_view(view)

    def _on_study_select_from_landing(self, study: Dict) -> None:
        """Callback quand une étude est sélectionnée depuis la landing."""
        self.current_study = study
        sid = study["id"]
        self.patient_queries.set_study(sid)
        self.visit_queries.set_study(sid)
        self.consent_queries.set_study(sid)
        self.ae_queries.set_study(sid)
        self.query_queries.set_study(sid)
        self.monitoring_queries.set_study(sid)
        self._update_title()

        # Afficher la sidebar
        self.sidebar.visible = True
        self.sidebar.update_studies(self.studies, self.current_study)

        # Afficher le dashboard
        self._show_dashboard()

    def _new_study_from_landing(self) -> None:
        """Ouvre le dialogue pour créer une nouvelle étude."""
        def close_dialog(e):
            dialog.open = False
            self.page.update()

        def create_study(e):
            study_number = number_field.value
            study_name = name_field.value

            if study_number and study_name:
                try:
                    self.db.create_study(study_number=study_number, study_name=study_name)
                    self._refresh_studies()
                    dialog.open = False
                    self.page.update()
                    if isinstance(self.current_view, LandingView):
                        self.current_view.refresh()
                except Exception as ex:
                    self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        number_field = ft.TextField(label="Study Number", autofocus=True)
        name_field = ft.TextField(label="Study Name")

        dialog = ft.AlertDialog(
            title=ft.Text("New Study"),
            content=ft.Column([number_field, name_field], tight=True, spacing=20),
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=close_dialog),
                ft.Button(content=ft.Text("Create"), on_click=create_study),
            ],
        )

        self.page.open(dialog)

    def _show_dashboard(self) -> None:
        """Affiche le dashboard."""
        self.sidebar.set_active("dashboard")
        view = DashboardView(
            patient_queries=self.patient_queries,
            visit_queries=self.visit_queries,
            ae_queries=self.ae_queries,
            query_queries=self.query_queries,
            current_study=self.current_study,
        )
        self._switch_view(view)

    def _show_patients(self) -> None:
        """Affiche la vue patients."""
        self.sidebar.set_active("patients")
        view = PatientsView(
            patient_queries=self.patient_queries,
        )
        self._switch_view(view)

    def _show_sites(self) -> None:
        """Affiche la vue sites."""
        self.sidebar.set_active("sites")
        view = SitesView(
            db=self.db,
            current_study=self.current_study,
        )
        self._switch_view(view)

    def _show_visits(self) -> None:
        """Affiche la vue visites."""
        self.sidebar.set_active("visits")
        view = VisitsView(
            patient_queries=self.patient_queries,
            visit_queries=self.visit_queries,
        )
        self._switch_view(view)

    def _show_adverse_events(self) -> None:
        """Affiche la vue événements indésirables."""
        self.sidebar.set_active("adverse_events")
        view = AdverseEventsView(
            patient_queries=self.patient_queries,
            ae_queries=self.ae_queries,
        )
        self._switch_view(view)

    def _show_documents(self) -> None:
        """Affiche la vue documents."""
        self.sidebar.set_active("documents")
        view = DocumentsView(
            patient_queries=self.patient_queries,
            consent_queries=self.consent_queries,
        )
        self._switch_view(view)

    def _show_queries(self) -> None:
        """Affiche la vue queries."""
        self.sidebar.set_active("queries")
        view = QueriesView(
            patient_queries=self.patient_queries,
            query_queries=self.query_queries,
        )
        self._switch_view(view)

    def _show_monitoring(self) -> None:
        """Affiche la vue monitoring."""
        self.sidebar.set_active("monitoring")
        view = MonitoringView(
            patient_queries=self.patient_queries,
            monitoring_queries=self.monitoring_queries,
        )
        self._switch_view(view)

    def _show_audit(self) -> None:
        """Affiche la vue audit trail."""
        self.sidebar.set_active("audit")
        view = AuditView(db_connection=self.db.connection)
        self._switch_view(view)

    def _show_settings(self) -> None:
        """Affiche la vue paramètres."""
        self.sidebar.set_active("settings")
        view = SettingsView(
            db=self.db,
            current_study=self.current_study,
        )
        self._switch_view(view)

    def _show_placeholder(self, title: str) -> None:
        """Affiche une vue placeholder (à implémenter)."""
        view = ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(height=20),
                    ft.Text(f"La vue '{title}' sera implémentée prochainement.", color=ft.Colors.GREY_500),
                    ft.Container(height=20),
                    ft.ProgressRing(),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=ft.Alignment.CENTER,
        )
        self._switch_view(view)

    def _export_excel(self) -> None:
        """Exporte les données de l'étude courante en Excel."""
        def save_file(e: ft.FilePickerResultEvent):
            if not e.path:
                return
            try:
                from excel_generator import create_visit_tracking

                # Compter les visites et patients réels de l'étude courante
                num_visits = len(self.visit_queries.get_configs())
                num_patients = len(self.patient_queries.get_all())

                # Garantir des valeurs minimales
                num_visits = max(num_visits, 1)
                num_patients = max(num_patients, 1)

                wb = create_visit_tracking(num_visits=num_visits, num_patients=num_patients)
                wb.save(e.path)
                self.page.open(ft.SnackBar(
                    content=ft.Text(f"Export réussi : {num_patients} patients, {num_visits} visites"),
                    duration=4000,
                ))
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Erreur export : {ex}")))

        study_name = self.current_study.get("study_name", "study") if self.current_study else "study"
        default_name = f"suivi_{study_name.replace(' ', '_')}.xlsx"

        file_picker = ft.FilePicker(on_result=save_file)
        self.page.overlay.append(file_picker)
        self.page.update()

        file_picker.save_file(file_name=default_name, allowed_extensions=["xlsx"])

    def close(self) -> None:
        """Ferme l'application proprement."""
        self.db.close()


def main(page: ft.Page):
    """Point d'entrée Flet."""
    app = ClinicalStudyApp(page)
    page.on_disconnect = lambda _: app.close()
