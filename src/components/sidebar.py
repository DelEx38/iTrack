"""
Barre latérale de navigation.
"""

import flet as ft
from typing import Callable, List, Dict, Optional


class NavButton(ft.Container):
    """Bouton de navigation stylisé."""

    def __init__(
        self,
        text: str,
        icon: str,
        on_click: Callable,
        selected: bool = False,
    ):
        self._text = text
        self._icon = icon
        self._on_click_callback = on_click
        self._selected = selected

        self.icon_widget = ft.Icon(
            icon,
            color=ft.Colors.PRIMARY if selected else ft.Colors.ON_SURFACE_VARIANT,
            size=20,
        )
        self.text_widget = ft.Text(
            text,
            color=ft.Colors.PRIMARY if selected else ft.Colors.ON_SURFACE_VARIANT,
            size=14,
        )

        super().__init__(
            content=ft.Row(
                [self.icon_widget, self.text_widget],
                spacing=12,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_radius=8,
            bgcolor=ft.Colors.PRIMARY_CONTAINER if selected else None,
            on_click=self._handle_click,
            on_hover=self._handle_hover,
        )

    def _handle_click(self, e):
        self._on_click_callback(self._text)

    def _handle_hover(self, e):
        if not self._selected:
            self.bgcolor = ft.Colors.SURFACE_CONTAINER if e.data == "true" else None
            if self.page:
                self.update()

    def set_selected(self, selected: bool):
        self._selected = selected
        color = ft.Colors.PRIMARY if selected else ft.Colors.ON_SURFACE_VARIANT
        self.icon_widget.color = color
        self.text_widget.color = color
        self.bgcolor = ft.Colors.PRIMARY_CONTAINER if selected else None
        if self.page:
            self.update()


class Sidebar(ft.Container):
    """Barre latérale avec navigation et sélecteur d'étude."""

    def __init__(
        self,
        on_navigate: Callable[[str], None],
        on_study_change: Callable[[str], None],
        studies: List[Dict],
        current_study: Optional[Dict] = None,
    ):
        self.on_navigate = on_navigate
        self.on_study_change = on_study_change
        self.current_view = "dashboard"
        self.nav_buttons: Dict[str, NavButton] = {}

        # Logo
        logo = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.MEDICAL_SERVICES, size=32, color=ft.Colors.PRIMARY),
                    ft.Text(
                        "Clinical Study\nTracker",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=ft.padding.symmetric(vertical=20),
        )

        # Sélecteur d'étude
        study_names = self._get_study_names(studies)
        current_name = self._get_current_study_name(current_study)

        self.study_dropdown = ft.Dropdown(
            label="Study",
            options=[ft.DropdownOption(key=name, text=name) for name in study_names],
            value=current_name,
            on_select=self._on_study_selected,
            width=180,
            dense=True,
        )

        study_selector = ft.Container(
            content=self.study_dropdown,
            padding=ft.padding.symmetric(horizontal=10, vertical=10),
        )

        # Boutons de navigation
        nav_items = [
            ("Dashboard", ft.Icons.DASHBOARD, "dashboard"),
            ("Sites", ft.Icons.LOCATION_ON, "sites"),
            ("Patients", ft.Icons.PEOPLE, "patients"),
            ("Visits", ft.Icons.CALENDAR_TODAY, "visits"),
            ("Adverse Events", ft.Icons.WARNING, "adverse_events"),
            ("Documents", ft.Icons.DESCRIPTION, "documents"),
            ("Queries", ft.Icons.QUESTION_ANSWER, "queries"),
            ("Monitoring", ft.Icons.VISIBILITY, "monitoring"),
        ]

        nav_buttons_list = []
        for text, icon, key in nav_items:
            btn = NavButton(
                text=text,
                icon=icon,
                on_click=lambda name, k=key: self._handle_nav_click(k),
                selected=(key == self.current_view),
            )
            self.nav_buttons[key] = btn
            nav_buttons_list.append(btn)

        nav_section = ft.Column(nav_buttons_list, spacing=4)

        # Séparateur
        separator = ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT)

        # Bouton Export
        export_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.DOWNLOAD, size=18), ft.Text("Export Excel")],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            on_click=lambda e: self._handle_nav_click("export"),
            bgcolor=ft.Colors.PRIMARY,
            color=ft.Colors.ON_PRIMARY,
            width=180,
        )

        export_section = ft.Container(
            content=export_btn,
            padding=ft.padding.symmetric(horizontal=10, vertical=10),
        )

        # Bouton Settings
        settings_btn = NavButton(
            text="Settings",
            icon=ft.Icons.SETTINGS,
            on_click=lambda name: self._handle_nav_click("settings"),
        )
        self.nav_buttons["settings"] = settings_btn

        # Contenu complet
        content = ft.Column(
            [
                logo,
                study_selector,
                ft.Container(content=nav_section, padding=ft.padding.symmetric(horizontal=10)),
                ft.Container(expand=True),
                separator,
                export_section,
                ft.Container(
                    content=settings_btn,
                    padding=ft.padding.symmetric(horizontal=10, vertical=10),
                ),
            ],
            spacing=0,
        )

        super().__init__(
            content=content,
            width=200,
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.only(right=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)),
        )

    def _get_study_names(self, studies: List[Dict]) -> List[str]:
        if not studies:
            return ["No study"]
        return [s.get("study_number") or s.get("study_name") or "No name" for s in studies]

    def _get_current_study_name(self, study: Optional[Dict]) -> str:
        if not study:
            return ""
        return study.get("study_number") or study.get("study_name") or ""

    def _on_study_selected(self, e):
        self.on_study_change(e.data)

    def _handle_nav_click(self, view_name: str):
        self.set_active(view_name)
        self.on_navigate(view_name)

    def set_active(self, view_name: str):
        """Met en surbrillance le bouton actif."""
        self.current_view = view_name
        for key, btn in self.nav_buttons.items():
            btn.set_selected(key == view_name)

    def update_studies(self, studies: List[Dict], current_study: Optional[Dict] = None):
        """Met à jour la liste des études."""
        study_names = self._get_study_names(studies)
        self.study_dropdown.options = [ft.DropdownOption(key=name, text=name) for name in study_names]
        if current_study:
            self.study_dropdown.value = self._get_current_study_name(current_study)
        if self.page:
            self.study_dropdown.update()

    def show(self):
        self.visible = True
        if self.page:
            self.update()

    def hide(self):
        self.visible = False
        if self.page:
            self.update()
