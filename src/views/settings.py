# -*- coding: utf-8 -*-
"""
Gestion des paramètres de l'étude.
"""

import flet as ft
from typing import Optional, Dict, List
from src.services.soa_parser import SoaParserService
from src.theme import AppColors, Typography, Spacing, Radius
from src.components import ConfirmDialog



class SoaPreviewDialog(ft.AlertDialog):
    """Dialogue de preview des visites importées depuis un SoA Excel."""

    def __init__(self, visits: List[Dict], on_import):
        self.visits = visits
        self.on_import = on_import
        self.selected_visits = {i: True for i in range(len(visits))}

        # Liste des visites avec checkboxes
        visit_rows = []
        for i, visit in enumerate(visits):
            checkbox = ft.Checkbox(
                value=True,
                on_change=lambda e, idx=i: self._toggle_visit(idx, e.control.value),
            )
            window_text = f"-{visit['window_before']}/+{visit['window_after']}" if visit['window_before'] or visit['window_after'] else "0"
            row = ft.Row(
                [
                    checkbox,
                    ft.Container(
                        content=ft.Text(visit["visit_name"], **Typography.TABLE_CELL, weight=ft.FontWeight.BOLD),
                        width=100,
                    ),
                    ft.Container(
                        content=ft.Text(f"D{visit['target_day']}", **Typography.TABLE_CELL),
                        width=60,
                    ),
                    ft.Container(
                        content=ft.Text(window_text, **Typography.TABLE_CELL),
                        width=80,
                    ),
                ],
                spacing=Spacing.SM,
            )
            visit_rows.append(row)

        content = ft.Column(
            [
                ft.Text(
                    f"{len(visits)} visites détectées dans le fichier SoA.",
                    **Typography.BODY,
                ),
                ft.Container(height=Spacing.SM),
                ft.Row(
                    [
                        ft.Container(width=40),
                        ft.Container(content=ft.Text("Visit", **Typography.TABLE_HEADER), width=100),
                        ft.Container(content=ft.Text("Day", **Typography.TABLE_HEADER), width=60),
                        ft.Container(content=ft.Text("Window", **Typography.TABLE_HEADER), width=80),
                    ],
                    spacing=Spacing.SM,
                ),
                ft.Divider(),
                ft.Column(
                    visit_rows,
                    spacing=Spacing.XS,
                    scroll=ft.ScrollMode.AUTO,
                    height=300,
                ),
            ],
            tight=True,
            width=400,
        )

        super().__init__(
            title=ft.Text("Import Schedule of Assessments", **Typography.H4),
            content=content,
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=self._cancel),
                ft.Button(
                    content=ft.Text("Import Selected"),
                    on_click=self._import,
                    bgcolor=AppColors.PRIMARY,
                    color=AppColors.TEXT_ON_PRIMARY,
                ),
            ],
        )

    def _toggle_visit(self, idx: int, value: bool):
        self.selected_visits[idx] = value

    def _cancel(self, e):
        self.open = False
        self.page.update()

    def _import(self, e):
        selected = [
            self.visits[i] for i, selected in self.selected_visits.items() if selected
        ]
        self.open = False
        self.page.update()
        self.on_import(selected)


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
            border_radius=Radius.INPUT,
        )

        # Jour cible
        self.day_field = ft.TextField(
            label="Target Day (0 = reference visit) *",
            value=str(config.get("target_day", "")) if config else "",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=Radius.INPUT,
        )

        # Fenêtre avant
        self.window_before_field = ft.TextField(
            label="Window Before (days)",
            value=str(config.get("window_before", "0")) if config else "0",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=Radius.INPUT,
        )

        # Fenêtre après
        self.window_after_field = ft.TextField(
            label="Window After (days)",
            value=str(config.get("window_after", "0")) if config else "0",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=Radius.INPUT,
        )

        content = ft.Column(
            [
                self.name_field,
                self.day_field,
                ft.Row([self.window_before_field, self.window_after_field], spacing=Spacing.SM),
            ],
            spacing=Spacing.MD,
            tight=True,
            width=350,
        )

        super().__init__(
            title=ft.Text("Edit Visit" if config else "New Visit", **Typography.H4),
            content=content,
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=self._cancel),
                ft.Button(
                    content=ft.Text("Save"),
                    on_click=self._save,
                    bgcolor=AppColors.PRIMARY,
                    color=AppColors.TEXT_ON_PRIMARY,
                ),
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
            border_radius=Radius.INPUT,
        )

        # Versions disponibles
        self.versions_field = ft.TextField(
            label="Available Versions (comma-separated)",
            value=config.get("versions", "1.0") if config else "1.0",
            hint_text="e.g. 1.0, 1.1, 2.0",
            border_radius=Radius.INPUT,
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
            spacing=Spacing.MD,
            tight=True,
            width=350,
        )

        super().__init__(
            title=ft.Text("Edit Consent Type" if config else "New Consent Type", **Typography.H4),
            content=content,
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=self._cancel),
                ft.Button(
                    content=ft.Text("Save"),
                    on_click=self._save,
                    bgcolor=AppColors.PRIMARY,
                    color=AppColors.TEXT_ON_PRIMARY,
                ),
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
        title = ft.Text("Study Settings", **Typography.H2)

        # Boutons d'onglets
        self.tab_buttons = ft.Row(
            [
                ft.TextButton(
                    content=ft.Text("Study Info"),
                    on_click=lambda e: self._select_tab(0),
                    style=ft.ButtonStyle(color=AppColors.PRIMARY),
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
            spacing=Spacing.SM,
        )

        # Container pour le contenu de l'onglet
        self.tab_content = ft.Container(expand=True)

        content = ft.Column(
            [
                title,
                ft.Container(height=Spacing.SM),
                self.tab_buttons,
                ft.Divider(),
                ft.Container(height=Spacing.SM),
                self.tab_content,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(content=content, padding=Spacing.PAGE_PADDING, expand=True)

        self._show_study_info()

    def _select_tab(self, index: int):
        self.selected_tab = index
        # Mettre à jour les styles des boutons
        for i, btn in enumerate(self.tab_buttons.controls):
            btn.style = ft.ButtonStyle(
                color=AppColors.PRIMARY if i == index else AppColors.TEXT_SECONDARY
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
            border_radius=Radius.INPUT,
        )
        self.study_name_field = ft.TextField(
            label="Study Name",
            value=study.get("study_name", ""),
            width=400,
            border_radius=Radius.INPUT,
        )
        self.sponsor_field = ft.TextField(
            label="Sponsor",
            value=study.get("sponsor", ""),
            width=300,
            border_radius=Radius.INPUT,
        )
        self.protocol_field = ft.TextField(
            label="Protocol Version",
            value=study.get("protocol_version", ""),
            width=200,
            border_radius=Radius.INPUT,
        )

        save_btn = ft.Button(
            content=ft.Text("Save Changes"),
            on_click=self._save_study_info,
            bgcolor=AppColors.PRIMARY,
            color=AppColors.TEXT_ON_PRIMARY,
        )

        self.tab_content.content = ft.Column(
            [
                ft.Text("Study Information", **Typography.H5),
                ft.Container(height=Spacing.SM),
                self.study_number_field,
                self.study_name_field,
                self.sponsor_field,
                self.protocol_field,
                ft.Container(height=Spacing.LG),
                save_btn,
            ],
            spacing=Spacing.MD,
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
        configs = self.db.get_visit_configs(study_id=self.current_study["id"] if self.current_study else None)

        # Bouton importer depuis SoA
        import_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.UPLOAD_FILE, size=18), ft.Text("Import from SoA")],
                spacing=Spacing.XS,
            ),
            on_click=self._import_from_soa,
            bgcolor=AppColors.SECONDARY,
            color=AppColors.TEXT_ON_PRIMARY,
        )

        # Bouton ajouter
        add_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("Add Visit")],
                spacing=Spacing.XS,
            ),
            on_click=self._add_visit_config,
            bgcolor=AppColors.PRIMARY,
            color=AppColors.TEXT_ON_PRIMARY,
        )

        # Tableau
        rows = []
        for config in configs:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(config.get("visit_name", ""), **Typography.TABLE_CELL)),
                    ft.DataCell(ft.Text(f"D{config.get('target_day', 0)}", **Typography.TABLE_CELL)),
                    ft.DataCell(ft.Text(
                        f"-{config.get('window_before', 0)} / +{config.get('window_after', 0)}",
                        **Typography.TABLE_CELL,
                    )),
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
                                    icon_color=AppColors.ERROR,
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
                ft.DataColumn(ft.Text("Visit Name", **Typography.TABLE_HEADER)),
                ft.DataColumn(ft.Text("Target Day", **Typography.TABLE_HEADER)),
                ft.DataColumn(ft.Text("Window", **Typography.TABLE_HEADER)),
                ft.DataColumn(ft.Text("Actions", **Typography.TABLE_HEADER)),
            ],
            rows=rows,
            border=ft.border.all(1, AppColors.BORDER),
            border_radius=Radius.TABLE,
            heading_row_color=AppColors.SURFACE_VARIANT,
        )

        self.tab_content.content = ft.Column(
            [
                ft.Row([
                    ft.Text("Visit Configuration", **Typography.H5),
                    ft.Container(expand=True),
                    import_btn,
                    add_btn,
                ], spacing=Spacing.SM),
                ft.Container(height=Spacing.SM),
                ft.Text(
                    "Import visits from an Excel file containing the Schedule of Assessments (SoA).",
                    **Typography.BODY_SMALL,
                    color=AppColors.TEXT_SECONDARY,
                ),
                ft.Container(height=Spacing.SM),
                table,
            ],
        )

        try:
            if self.page:
                self.tab_content.update()
        except RuntimeError:
            pass

    async def _import_from_soa(self, e):
        """Ouvre le sélecteur de fichier pour importer un SoA Excel."""
        # Créer le FilePicker et l'ajouter aux services de la page
        file_picker = ft.FilePicker()
        self.page.services.append(file_picker)
        self.page.update()

        # Ouvrir le dialogue (async dans Flet 0.83+)
        result = await file_picker.pick_files(
            dialog_title="Select SoA Excel file",
            allowed_extensions=["xlsx", "xls"],
            allow_multiple=False,
        )

        # Nettoyer
        self.page.services.remove(file_picker)
        self.page.update()

        if not result or len(result) == 0:
            return

        file_path = result[0].path
        if not file_path:
            self.page.open(ft.SnackBar(content=ft.Text("Impossible de lire le fichier")))
            return

        try:
            # Lire le fichier
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            # Parser le SoA
            parser = SoaParserService()
            visits = parser.parse_file(file_bytes)

            if not visits:
                self.page.open(ft.SnackBar(content=ft.Text("Aucune visite trouvée dans le fichier")))
                return

            # Convertir en dicts
            visit_dicts = [v.to_dict() for v in visits]

            # Afficher le dialogue de preview
            dialog = SoaPreviewDialog(
                visits=visit_dicts,
                on_import=self._on_soa_import,
            )
            self.page.open(dialog)

        except Exception as ex:
            self.page.open(ft.SnackBar(content=ft.Text(f"Erreur: {ex}")))

    def _on_soa_import(self, visits: List[Dict]):
        """Callback pour importer les visites sélectionnées."""
        imported = 0
        errors = 0

        for visit in visits:
            try:
                # Vérifier si la visite existe déjà
                existing = self.db.get_visit_configs(study_id=self.current_study["id"] if self.current_study else None)
                exists = any(v.get("visit_name") == visit["visit_name"] for v in existing)

                if exists:
                    # Mettre à jour
                    for v in existing:
                        if v.get("visit_name") == visit["visit_name"]:
                            self.db.update_visit_config(
                                v["id"],
                                target_day=visit["target_day"],
                                window_before=visit["window_before"],
                                window_after=visit["window_after"],
                            )
                            imported += 1
                            break
                else:
                    # Créer
                    self.db.create_visit_config(
                        visit_name=visit["visit_name"],
                        target_day=visit["target_day"],
                        window_before=visit["window_before"],
                        window_after=visit["window_after"],
                    )
                    imported += 1

            except Exception:
                errors += 1

        # Rafraîchir la vue
        self._show_visits()

        # Message de confirmation
        if errors > 0:
            self.page.open(ft.SnackBar(content=ft.Text(f"{imported} visites importées, {errors} erreurs")))
        else:
            self.page.open(ft.SnackBar(content=ft.Text(f"{imported} visites importées avec succès")))

    def _add_visit_config(self, e):
        def on_save(data):
            try:
                self.db.create_visit_config(**data, study_id=self.current_study["id"] if self.current_study else None)
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
        def on_confirm():
            try:
                self.db.delete_visit_config(config["id"])
                self._show_visits()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        ConfirmDialog(
            title="Delete Visit",
            message=f"Delete visit '{config.get('visit_name')}'?",
            confirm_text="Delete",
            on_confirm=on_confirm,
            danger=True,
        ).show(self.page)

    def _show_consent_types(self):
        """Affiche les types de consentements."""
        configs = self.db.get_consent_configs(study_id=self.current_study["id"] if self.current_study else None)

        # Bouton ajouter
        add_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("Add Type")],
                spacing=Spacing.XS,
            ),
            on_click=self._add_consent_config,
            bgcolor=AppColors.PRIMARY,
            color=AppColors.TEXT_ON_PRIMARY,
        )

        # Tableau
        rows = []
        for config in configs:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(config.get("consent_type", ""), **Typography.TABLE_CELL)),
                    ft.DataCell(ft.Text(config.get("versions", "1.0"), **Typography.TABLE_CELL)),
                    ft.DataCell(
                        ft.Icon(
                            ft.Icons.CHECK if config.get("is_required") else ft.Icons.CLOSE,
                            color=AppColors.SUCCESS if config.get("is_required") else AppColors.ERROR,
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
                                    icon_color=AppColors.ERROR,
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
                ft.DataColumn(ft.Text("Consent Type", **Typography.TABLE_HEADER)),
                ft.DataColumn(ft.Text("Versions", **Typography.TABLE_HEADER)),
                ft.DataColumn(ft.Text("Required", **Typography.TABLE_HEADER)),
                ft.DataColumn(ft.Text("Actions", **Typography.TABLE_HEADER)),
            ],
            rows=rows,
            border=ft.border.all(1, AppColors.BORDER),
            border_radius=Radius.TABLE,
            heading_row_color=AppColors.SURFACE_VARIANT,
        )

        self.tab_content.content = ft.Column(
            [
                ft.Row([
                    ft.Text("Consent Types", **Typography.H5),
                    ft.Container(expand=True),
                    add_btn,
                ]),
                ft.Container(height=Spacing.SM),
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
                self.db.create_consent_config(**data, study_id=self.current_study["id"] if self.current_study else None)
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
        def on_confirm():
            try:
                self.db.delete_consent_config(config["id"])
                self._show_consent_types()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        ConfirmDialog(
            title="Delete Consent Type",
            message=f"Delete consent type '{config.get('consent_type')}'?",
            confirm_text="Delete",
            on_confirm=on_confirm,
            danger=True,
        ).show(self.page)
