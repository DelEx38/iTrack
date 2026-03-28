"""
Page d'accueil avec liste des études.
"""

import flet as ft
from typing import Callable, Dict, List


class StudyCard(ft.Container):
    """Carte représentant une étude."""

    PHASE_COLORS = {
        "Phase I": "#2196F3",
        "Phase II": "#4CAF50",
        "Phase III": "#FF9800",
        "Phase IV": "#F44336",
    }

    def __init__(self, study: Dict, on_click: Callable[[Dict], None], db):
        self.study = study
        self._on_click_callback = on_click
        self.db = db

        # Récupérer les stats
        stats = self._get_study_stats()

        # Badge phase
        phase = study.get("phase", "")
        phase_color = self.PHASE_COLORS.get(phase, "#9E9E9E")

        phase_badge = ft.Container(
            content=ft.Text(phase or "N/A", size=12, color=ft.Colors.WHITE),
            bgcolor=phase_color,
            border_radius=4,
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
        ) if phase else ft.Container()

        # Numéro d'étude
        study_number = ft.Text(
            study.get("study_number", ""),
            size=12,
            color=ft.Colors.GREY_500,
        )

        # Nom d'étude
        study_name = ft.Text(
            study.get("study_name", "Unnamed Study"),
            size=18,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.PRIMARY,
        )

        # Sponsor et pathologie
        sponsor = ft.Text(study.get("sponsor", ""), size=12, color=ft.Colors.GREY_600)
        pathology = ft.Text(study.get("pathology", ""), size=12, color=ft.Colors.GREY_600, italic=True)

        # Stats
        stats_row = ft.Row(
            [
                self._stat_item(ft.Icons.PEOPLE, str(stats["patients"]), "Patients"),
                self._stat_item(ft.Icons.CALENDAR_TODAY, str(stats["visits"]), "Visits"),
                self._stat_item(ft.Icons.WARNING, str(stats["ae"]), "AE"),
            ],
            spacing=20,
        )

        content = ft.Column(
            [
                ft.Row([phase_badge, ft.Container(expand=True), study_number]),
                ft.Container(height=10),
                study_name,
                sponsor,
                pathology,
                ft.Container(height=15),
                stats_row,
            ],
            spacing=5,
        )

        super().__init__(
            content=content,
            padding=20,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            on_click=self._handle_click,
            on_hover=self._handle_hover,
            width=300,
        )

    def _stat_item(self, icon: str, value: str, label: str) -> ft.Column:
        return ft.Column(
            [
                ft.Row(
                    [ft.Icon(icon, size=16, color=ft.Colors.GREY_500), ft.Text(value, weight=ft.FontWeight.BOLD)],
                    spacing=5,
                ),
                ft.Text(label, size=10, color=ft.Colors.GREY_500),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        )

    def _get_study_stats(self) -> Dict:
        """Récupère les statistiques de l'étude."""
        try:
            cursor = self.db.connection.cursor()
            study_id = self.study["id"]

            cursor.execute("SELECT COUNT(*) FROM patients WHERE study_id = ?", (study_id,))
            patients = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM visits v JOIN patients p ON v.patient_id = p.id WHERE p.study_id = ?",
                (study_id,)
            )
            visits = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM adverse_events WHERE study_id = ?", (study_id,))
            ae = cursor.fetchone()[0]

            return {"patients": patients, "visits": visits, "ae": ae}
        except Exception:
            return {"patients": 0, "visits": 0, "ae": 0}

    def _handle_click(self, e):
        self._on_click_callback(self.study)

    def _handle_hover(self, e):
        self.bgcolor = ft.Colors.SECONDARY_CONTAINER if e.data == "true" else ft.Colors.SURFACE_CONTAINER
        if self.page:
            self.update()


class LandingView(ft.Container):
    """Vue de la page d'accueil avec la liste des études."""

    def __init__(
        self,
        db,
        on_study_select: Callable[[Dict], None],
        on_new_study: Callable[[], None],
    ):
        self.db = db
        self.on_study_select = on_study_select
        self.on_new_study = on_new_study

        # Titre
        title = ft.Text("Clinical Study Tracker", size=32, weight=ft.FontWeight.BOLD)
        subtitle = ft.Text("Select a study to continue", size=16, color=ft.Colors.GREY_500)

        # Barre de recherche
        self.search_field = ft.TextField(
            hint_text="Search studies...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=10,
            width=400,
            on_change=self._on_search,
        )

        # Bouton nouvelle étude
        new_study_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("+ New Study")],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            on_click=lambda e: self.on_new_study(),
            bgcolor=ft.Colors.PRIMARY,
            color=ft.Colors.ON_PRIMARY,
        )

        header = ft.Column(
            [
                ft.Row([title], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([subtitle], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=20),
                ft.Row([self.search_field, new_study_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Grille des études
        self.studies_grid = ft.Row(
            wrap=True,
            spacing=20,
            run_spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        content = ft.Column(
            [
                ft.Container(height=40),
                header,
                ft.Container(height=40),
                ft.Container(content=self.studies_grid, expand=True),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(content=content, padding=20, expand=True)

        # Charger les études
        self._load_studies()

    def _load_studies(self, search_term: str = "") -> None:
        """Charge les études depuis la base de données."""
        self.studies_grid.controls.clear()

        studies = self.db.get_studies()

        if search_term:
            search_lower = search_term.lower()
            studies = [
                s for s in studies
                if search_lower in (s.get("study_number", "") or "").lower()
                or search_lower in (s.get("study_name", "") or "").lower()
                or search_lower in (s.get("sponsor", "") or "").lower()
            ]

        if not studies:
            self.studies_grid.controls.append(
                ft.Text("No studies found. Create your first study!", size=16, color=ft.Colors.GREY_500, italic=True)
            )
        else:
            for study in studies:
                card = StudyCard(study=study, on_click=self.on_study_select, db=self.db)
                self.studies_grid.controls.append(card)

    def _on_search(self, e):
        self._load_studies(e.control.value)
        if self.page:
            self.studies_grid.update()

    def refresh(self) -> None:
        """Rafraîchit la liste des études."""
        self._load_studies(self.search_field.value or "")
        if self.page:
            self.studies_grid.update()
