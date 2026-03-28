"""
Gestion des paramètres de l'étude.
"""

import flet as ft
from typing import Optional, Dict, List


class VisitConfigDialog(ft.AlertDialog):
    """Dialogue d'ajout/modification de configuration de visite."""

    def __init__(self, on_save, config: Optional[Dict] = None):
        self.config = config
        self.on_save = on_save

        # Nom de la visite
        self.name_field = ft.TextField(
            label="Visit Name *",
            value=config.get("visit_name", "") if config else "",
            autofocus=True,
        )

        # Jour cible
        self.day_field = ft.TextField(
            label="Target Day (0 = reference visit) *",
            value=str(config.get("target_day", "")) if config else "",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        # Fenêtre avant
        self.window_before_field = ft.TextField(
            label="Window Before (days)",
            value=str(config.get("window_before", "0")) if config else "0",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        # Fenêtre après
        self.window_after_field = ft.TextField(
            label="Window After (days)",
            value=str(config.get("window_after", "0")) if config else "0",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        content = ft.Column(
            [
                self.name_field,
                self.day_field,
                ft.Row([self.window_before_field, self.window_after_field], spacing=10),
            ],
            spacing=15,
            tight=True,
            width=350,
        )

        super().__init__(
            title=ft.Text("Edit Visit" if config else "New Visit"),
            content=content,
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=self._cancel),
                ft.Button(content=ft.Text("Save"), on_click=self._save),
            ],
        )

    def _cancel(self, e):
        self.open = False
        self.page.update()

    def _save(self, e):
        errors = []
        if not self.name_field.value:
            self.name_field.error_text = "Required"
            errors.append("Name required")
        if not self.day_field.value:
            self.day_field.error_text = "Required"
            errors.append("Day required")

        if errors:
            self.page.update()
            return

        result = {
            "visit_name": self.name_field.value,
            "target_day": int(self.day_field.value),
            "window_before": int(self.window_before_field.value or 0),
            "window_after": int(self.window_after_field.value or 0),
        }

        if self.config:
            result["id"] = self.config["id"]

        self.open = False
        self.page.update()
        self.on_save(result)


class ConsentConfigDialog(ft.AlertDialog):
    """Dialogue d'ajout/modification de type de consentement."""

    def __init__(self, on_save, config: Optional[Dict] = None):
        self.config = config
        self.on_save = on_save

        # Type de consentement
        self.type_field = ft.TextField(
            label="Consent Type *",
            value=config.get("consent_type", "") if config else "",
            autofocus=True,
        )

        # Versions disponibles
        self.versions_field = ft.TextField(
            label="Available Versions (comma-separated)",
            value=config.get("versions", "1.0") if config else "1.0",
            hint_text="e.g. 1.0, 1.1, 2.0",
        )

        # Obligatoire
        self.required_switch = ft.Switch(
            label="Required",
            value=config.get("is_required", True) if config else True,
        )

        content = ft.Column(
            [
                self.type_field,
                self.versions_field,
                self.required_switch,
            ],
            spacing=15,
            tight=True,
            width=350,
        )

        super().__init__(
            title=ft.Text("Edit Consent Type" if config else "New Consent Type"),
            content=content,
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=self._cancel),
                ft.Button(content=ft.Text("Save"), on_click=self._save),
            ],
        )

    def _cancel(self, e):
        self.open = False
        self.page.update()

    def _save(self, e):
        if not self.type_field.value:
            self.type_field.error_text = "Required"
            self.page.update()
            return

        result = {
            "consent_type": self.type_field.value,
            "versions": self.versions_field.value or "1.0",
            "is_required": self.required_switch.value,
        }

        if self.config:
            result["id"] = self.config["id"]

        self.open = False
        self.page.update()
        self.on_save(result)


class SettingsView(ft.Container):
    """Vue des paramètres de l'étude."""

    def __init__(self, db, current_study: Optional[Dict] = None):
        self.db = db
        self.current_study = current_study
        self.selected_tab = 0

        # Titre
        title = ft.Text("Study Settings", size=24, weight=ft.FontWeight.BOLD)

        # Boutons d'onglets
        self.tab_buttons = ft.Row(
            [
                ft.TextButton(
                    content=ft.Text("Study Info"),
                    on_click=lambda e: self._select_tab(0),
                    style=ft.ButtonStyle(color=ft.Colors.PRIMARY),
                ),
                ft.TextButton(
                    content=ft.Text("Visits"),
                    on_click=lambda e: self._select_tab(1),
                ),
                ft.TextButton(
                    content=ft.Text("Consent Types"),
                    on_click=lambda e: self._select_tab(2),
                ),
            ],
            spacing=10,
        )

        # Container pour le contenu de l'onglet
        self.tab_content = ft.Container(expand=True)

        content = ft.Column(
            [
                title,
                ft.Container(height=10),
                self.tab_buttons,
                ft.Divider(),
                ft.Container(height=10),
                self.tab_content,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(content=content, padding=20, expand=True)

        self._show_study_info()

    def _select_tab(self, index: int):
        self.selected_tab = index
        # Mettre à jour les styles des boutons
        for i, btn in enumerate(self.tab_buttons.controls):
            btn.style = ft.ButtonStyle(
                color=ft.Colors.PRIMARY if i == index else ft.Colors.ON_SURFACE_VARIANT
            )

        if index == 0:
            self._show_study_info()
        elif index == 1:
            self._show_visits()
        elif index == 2:
            self._show_consent_types()

        try:
            if self.page:
                self.tab_buttons.update()
        except RuntimeError:
            pass

    def _show_study_info(self):
        """Affiche les informations de l'étude."""
        study = self.current_study or {}

        # Champs
        self.study_number_field = ft.TextField(
            label="Study Number",
            value=study.get("study_number", ""),
            width=300,
        )
        self.study_name_field = ft.TextField(
            label="Study Name",
            value=study.get("study_name", ""),
            width=400,
        )
        self.sponsor_field = ft.TextField(
            label="Sponsor",
            value=study.get("sponsor", ""),
            width=300,
        )
        self.protocol_field = ft.TextField(
            label="Protocol Version",
            value=study.get("protocol_version", ""),
            width=200,
        )

        save_btn = ft.Button(
            content=ft.Text("Save Changes"),
            on_click=self._save_study_info,
            bgcolor=ft.Colors.PRIMARY,
            color=ft.Colors.ON_PRIMARY,
        )

        self.tab_content.content = ft.Column(
            [
                ft.Text("Study Information", weight=ft.FontWeight.BOLD, size=16),
                ft.Container(height=10),
                self.study_number_field,
                self.study_name_field,
                self.sponsor_field,
                self.protocol_field,
                ft.Container(height=20),
                save_btn,
            ],
            spacing=15,
        )

        try:
            if self.page:
                self.tab_content.update()
        except RuntimeError:
            pass

    def _save_study_info(self, e):
        if not self.current_study:
            return

        try:
            self.db.update_study(
                self.current_study["id"],
                study_number=self.study_number_field.value,
                study_name=self.study_name_field.value,
                sponsor=self.sponsor_field.value,
                protocol_version=self.protocol_field.value,
            )
            self.current_study = self.db.get_study_by_id(self.current_study["id"])
            self.page.open(ft.SnackBar(content=ft.Text("Study info saved successfully")))
        except Exception as ex:
            self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

    def _show_visits(self):
        """Affiche la configuration des visites."""
        configs = self.db.get_visit_configs()

        # Bouton ajouter
        add_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("Add Visit")],
                spacing=8,
            ),
            on_click=self._add_visit_config,
            bgcolor=ft.Colors.PRIMARY,
            color=ft.Colors.ON_PRIMARY,
        )

        # Tableau
        rows = []
        for config in configs:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(config.get("visit_name", ""))),
                    ft.DataCell(ft.Text(f"D{config.get('target_day', 0)}")),
                    ft.DataCell(ft.Text(f"-{config.get('window_before', 0)} / +{config.get('window_after', 0)}")),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_size=18,
                                    on_click=lambda e, c=config: self._edit_visit_config(c),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_size=18,
                                    icon_color=ft.Colors.ERROR,
                                    on_click=lambda e, c=config: self._delete_visit_config(c),
                                ),
                            ],
                            spacing=0,
                        )
                    ),
                ],
            )
            rows.append(row)

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Visit Name", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Target Day", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Window", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD)),
            ],
            rows=rows,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            heading_row_color=ft.Colors.SURFACE_CONTAINER,
        )

        self.tab_content.content = ft.Column(
            [
                ft.Row([
                    ft.Text("Visit Configuration", weight=ft.FontWeight.BOLD, size=16),
                    ft.Container(expand=True),
                    add_btn,
                ]),
                ft.Container(height=10),
                table,
            ],
        )

        try:
            if self.page:
                self.tab_content.update()
        except RuntimeError:
            pass

    def _add_visit_config(self, e):
        def on_save(data):
            try:
                self.db.create_visit_config(**data)
                self._show_visits()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = VisitConfigDialog(on_save=on_save)
        self.page.open(dialog)

    def _edit_visit_config(self, config: Dict):
        def on_save(data):
            try:
                self.db.update_visit_config(data["id"], **{k: v for k, v in data.items() if k != "id"})
                self._show_visits()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = VisitConfigDialog(on_save=on_save, config=config)
        self.page.open(dialog)

    def _delete_visit_config(self, config: Dict):
        def confirm(e):
            try:
                self.db.delete_visit_config(config["id"])
                self._show_visits()
                dialog.open = False
                self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        def cancel(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Delete Visit"),
            content=ft.Text(f"Delete visit '{config.get('visit_name')}'?"),
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=cancel),
                ft.Button(content=ft.Text("Delete"), on_click=confirm, bgcolor=ft.Colors.ERROR),
            ],
        )
        self.page.open(dialog)

    def _show_consent_types(self):
        """Affiche les types de consentements."""
        configs = self.db.get_consent_configs()

        # Bouton ajouter
        add_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("Add Type")],
                spacing=8,
            ),
            on_click=self._add_consent_config,
            bgcolor=ft.Colors.PRIMARY,
            color=ft.Colors.ON_PRIMARY,
        )

        # Tableau
        rows = []
        for config in configs:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(config.get("consent_type", ""))),
                    ft.DataCell(ft.Text(config.get("versions", "1.0"))),
                    ft.DataCell(
                        ft.Icon(
                            ft.Icons.CHECK if config.get("is_required") else ft.Icons.CLOSE,
                            color="#5cb85c" if config.get("is_required") else "#d9534f",
                            size=18,
                        )
                    ),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_size=18,
                                    on_click=lambda e, c=config: self._edit_consent_config(c),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_size=18,
                                    icon_color=ft.Colors.ERROR,
                                    on_click=lambda e, c=config: self._delete_consent_config(c),
                                ),
                            ],
                            spacing=0,
                        )
                    ),
                ],
            )
            rows.append(row)

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Consent Type", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Versions", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Required", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD)),
            ],
            rows=rows,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            heading_row_color=ft.Colors.SURFACE_CONTAINER,
        )

        self.tab_content.content = ft.Column(
            [
                ft.Row([
                    ft.Text("Consent Types", weight=ft.FontWeight.BOLD, size=16),
                    ft.Container(expand=True),
                    add_btn,
                ]),
                ft.Container(height=10),
                table,
            ],
        )

        try:
            if self.page:
                self.tab_content.update()
        except RuntimeError:
            pass

    def _add_consent_config(self, e):
        def on_save(data):
            try:
                self.db.create_consent_config(**data)
                self._show_consent_types()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = ConsentConfigDialog(on_save=on_save)
        self.page.open(dialog)

    def _edit_consent_config(self, config: Dict):
        def on_save(data):
            try:
                self.db.update_consent_config(data["id"], **{k: v for k, v in data.items() if k != "id"})
                self._show_consent_types()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = ConsentConfigDialog(on_save=on_save, config=config)
        self.page.open(dialog)

    def _delete_consent_config(self, config: Dict):
        def confirm(e):
            try:
                self.db.delete_consent_config(config["id"])
                self._show_consent_types()
                dialog.open = False
                self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        def cancel(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Delete Consent Type"),
            content=ft.Text(f"Delete consent type '{config.get('consent_type')}'?"),
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=cancel),
                ft.Button(content=ft.Text("Delete"), on_click=confirm, bgcolor=ft.Colors.ERROR),
            ],
        )
        self.page.open(dialog)
