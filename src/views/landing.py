# -*- coding: utf-8 -*-
"""
Page d'accueil avec liste des études.
"""

import asyncio
import flet as ft
from typing import Callable, Dict, List
from src.theme import AppColors, Typography, Spacing, Radius
from src.components import StatusBadge


class StudyCard(ft.Container):
    """Carte représentant une étude."""

    def __init__(self, study: Dict, on_click: Callable[[Dict], None], stats: Dict):
        self.study = study
        self._on_click_callback = on_click

        # Badge phase
        phase = study.get("phase", "")
        phase_badge = StatusBadge.phase(phase) if phase else ft.Container()

        # Numéro d'étude
        study_number = ft.Text(
            study.get("study_number", ""),
            **Typography.BODY_SMALL,
            color=AppColors.TEXT_SECONDARY,
        )

        # Nom d'étude
        study_name = ft.Text(
            study.get("study_name", "Unnamed Study"),
            **Typography.H4,
            color=AppColors.PRIMARY,
        )

        # Sponsor et pathologie
        sponsor = ft.Text(study.get("sponsor", ""), **Typography.BODY_SMALL, color=AppColors.TEXT_SECONDARY)
        pathology = ft.Text(study.get("pathology", ""), **Typography.BODY_SMALL, color=AppColors.TEXT_SECONDARY, italic=True)

        # Stats
        stats_row = ft.Row(
            [
                self._stat_item(ft.Icons.PEOPLE, str(stats["patients"]), "Patients"),
                self._stat_item(ft.Icons.CALENDAR_TODAY, str(stats["visits"]), "Visits"),
                self._stat_item(ft.Icons.WARNING, str(stats["ae"]), "AE"),
            ],
            spacing=Spacing.LG,
        )

        content = ft.Column(
            [
                ft.Row([phase_badge, ft.Container(expand=True), study_number]),
                ft.Container(height=Spacing.SM),
                study_name,
                sponsor,
                pathology,
                ft.Container(height=Spacing.MD),
                stats_row,
            ],
            spacing=Spacing.XS,
        )

        super().__init__(
            content=content,
            padding=Spacing.CARD_PADDING,
            border_radius=Radius.CARD,
            bgcolor=AppColors.SURFACE_VARIANT,
            on_click=self._handle_click,
            on_hover=self._handle_hover,
            width=300,
        )

    def _stat_item(self, icon: str, value: str, label: str) -> ft.Column:
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(icon, size=16, color=AppColors.TEXT_SECONDARY),
                        ft.Text(value, size=14, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=Spacing.XS,
                ),
                ft.Text(label, **Typography.CAPTION, color=AppColors.TEXT_SECONDARY),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.XXXS,
        )

    def _handle_click(self, e):
        self._on_click_callback(self.study)

    def _handle_hover(self, e):
        self.bgcolor = AppColors.SURFACE_ELEVATED if e.data == "true" else AppColors.SURFACE_VARIANT
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
        title = ft.Text("Clinical Study Tracker", **Typography.H1)
        subtitle = ft.Text("Select a study to continue", **Typography.BODY_LARGE, color=AppColors.TEXT_SECONDARY)

        # Barre de recherche
        self.search_field = ft.TextField(
            hint_text="Search studies...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=Radius.INPUT,
            width=400,
            on_change=self._on_search,
        )

        # Bouton nouvelle étude
        new_study_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("+ New Study")],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=Spacing.XS,
            ),
            on_click=lambda e: self.on_new_study(),
            bgcolor=AppColors.PRIMARY,
            color=AppColors.TEXT_ON_PRIMARY,
        )

        header = ft.Column(
            [
                ft.Row([title], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([subtitle], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=Spacing.LG),
                ft.Row([self.search_field, new_study_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=Spacing.LG),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Grille des études
        self.studies_grid = ft.Row(
            wrap=True,
            spacing=Spacing.LG,
            run_spacing=Spacing.LG,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        content = ft.Column(
            [
                ft.Container(height=Spacing.XXL),
                header,
                ft.Container(height=Spacing.XXL),
                ft.Container(content=self.studies_grid, expand=True),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(content=content, padding=Spacing.PAGE_PADDING, expand=True)

        # Charger les études
        self._load_studies()

    def _load_studies(self, search_term: str = "") -> None:
        """Charge les études depuis la base de données."""
        self.studies_grid.controls.clear()

        studies = self.db.get_studies()
        # Une seule requête batch pour toutes les stats
        all_stats = self.db.get_all_studies_stats()

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
                ft.Text(
                    "No studies found. Create your first study!",
                    **Typography.BODY_LARGE,
                    color=AppColors.TEXT_DISABLED,
                    italic=True,
                )
            )
        else:
            empty_stats = {"patients": 0, "visits": 0, "ae": 0}
            for study in studies:
                stats = all_stats.get(study["id"], empty_stats)
                card = StudyCard(study=study, on_click=self.on_study_select, stats=stats)
                self.studies_grid.controls.append(card)

    async def _on_search(self, e):
        term = e.data
        await asyncio.sleep(0.25)
        if self.search_field.value != term:
            return
        self._load_studies(e.control.value)
        if self.page:
            self.page.update()

    def refresh(self) -> None:
        """Rafraîchit la liste des études."""
        self._load_studies(self.search_field.value or "")
        if self.page:
            self.studies_grid.update()
