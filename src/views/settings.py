# -*- coding: utf-8 -*-
"""
Gestion des paramètres de l'étude.
"""

import flet as ft
from typing import Optional, Dict, List
from src.services.soa_parser import SoaParserService
from src.services.soa_pdf_parser import SoaPdfParser
from src.services.excel_importer import ExcelImporter, ImportPreview
from src.theme import AppColors, Typography, Spacing, Radius
from src.components import ConfirmDialog, AppTable



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
                        content=ft.Text(visit["visit_name"], size=13, weight=ft.FontWeight.BOLD),
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
                ft.TextButton(
                    content=ft.Text("Import Data"),
                    on_click=lambda e: self._select_tab(3),
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

        super().__init__(content=content, padding=Spacing.PAGE_PADDING, expand=True, alignment=ft.Alignment.TOP_LEFT)

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
        elif index == 3:
            self._show_data_import()

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
                [ft.Icon(ft.Icons.UPLOAD_FILE, size=18), ft.Text("Import from SoA (Excel/PDF)")],
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
        table = AppTable(columns=["Visit Name", "Target Day", "Window", "Actions"])
        rows = []
        for config in configs:
            rows.append([
                ft.Text(config.get("visit_name", ""), **Typography.TABLE_CELL),
                ft.Text(f"D{config.get('target_day', 0)}", **Typography.TABLE_CELL),
                ft.Text(
                    f"-{config.get('window_before', 0)} / +{config.get('window_after', 0)}",
                    **Typography.TABLE_CELL,
                ),
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
                ),
            ])
        table.set_rows(rows)

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
                    "Import visits from an Excel (.xlsx/.xls) or PDF file containing the Schedule of Assessments (SoA).",
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
        """Ouvre le sélecteur de fichier pour importer un SoA (Excel ou PDF)."""
        file_picker = ft.FilePicker()
        self.page.overlay.append(file_picker)
        self.page.update()

        result = await file_picker.pick_files_async(
            dialog_title="Sélectionner un fichier SoA (Excel ou PDF)",
            allowed_extensions=["xlsx", "xls", "pdf"],
            allow_multiple=False,
        )

        self.page.overlay.remove(file_picker)
        self.page.update()

        if not result or len(result) == 0:
            return

        file_path = result[0].path
        if not file_path:
            self.page.open(ft.SnackBar(content=ft.Text("Impossible de lire le fichier")))
            return

        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            # Router vers le bon parser selon l'extension
            ext = file_path.lower().rsplit(".", 1)[-1]
            if ext == "pdf":
                parser = SoaPdfParser()
            else:
                parser = SoaParserService()

            visits = parser.parse_file(file_bytes)

            if not visits:
                self.page.open(ft.SnackBar(content=ft.Text("Aucune visite trouvée dans le fichier")))
                return

            visit_dicts = [v.to_dict() for v in visits]

            dialog = SoaPreviewDialog(
                visits=visit_dicts,
                on_import=self._on_soa_import,
            )
            self.page.open(dialog)

        except ImportError as ex:
            self.page.open(ft.SnackBar(content=ft.Text(str(ex))))
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
        table = AppTable(columns=["Consent Type", "Versions", "Required", "Actions"])
        rows = []
        for config in configs:
            rows.append([
                ft.Text(config.get("consent_type", ""), **Typography.TABLE_CELL),
                ft.Text(config.get("versions", "1.0"), **Typography.TABLE_CELL),
                ft.Icon(
                    ft.Icons.CHECK if config.get("is_required") else ft.Icons.CLOSE,
                    color=AppColors.SUCCESS if config.get("is_required") else AppColors.ERROR,
                    size=18,
                ),
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
                ),
            ])
        table.set_rows(rows)

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

    # ─── Onglet Import Data ───────────────────────────────────────────────────

    def _show_data_import(self):
        """Affiche l'onglet d'import de données Excel."""
        import_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.UPLOAD_FILE, size=18), ft.Text("Sélectionner un fichier Excel (.xlsx)")],
                spacing=Spacing.XS,
            ),
            on_click=self._import_from_excel,
            bgcolor=AppColors.PRIMARY,
            color=AppColors.TEXT_ON_PRIMARY,
        )

        self.tab_content.content = ft.Column(
            [
                ft.Text("Import de données Excel", **Typography.H5),
                ft.Container(height=Spacing.SM),
                ft.Text(
                    "Importe les données d'un fichier Excel généré par iTrack ou compatible.\n"
                    "Onglets reconnus : Settings (configs visites), Suivi Patients, "
                    "Événements Indésirables.",
                    **Typography.BODY_SMALL,
                    color=AppColors.TEXT_SECONDARY,
                ),
                ft.Container(height=Spacing.MD),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=AppColors.TEXT_SECONDARY)],
                            ),
                            ft.Text(
                                "• Settings → configurations des visites (fenêtres)\n"
                                "• Suivi Patients → patients + dates de visite réalisées\n"
                                "• Événements Indésirables → EI et EIG",
                                **Typography.BODY_SMALL,
                                color=AppColors.TEXT_SECONDARY,
                            ),
                        ],
                        spacing=Spacing.XS,
                    ),
                    padding=Spacing.MD,
                    bgcolor=AppColors.SURFACE_VARIANT,
                    border_radius=8,
                ),
                ft.Container(height=Spacing.LG),
                import_btn,
            ],
            spacing=Spacing.SM,
        )

        try:
            if self.page:
                self.tab_content.update()
        except RuntimeError:
            pass

    async def _import_from_excel(self, e):
        """Ouvre le FilePicker puis affiche le dialog de preview/import."""
        file_picker = ft.FilePicker()
        self.page.overlay.append(file_picker)
        self.page.update()

        result = await file_picker.pick_files_async(
            dialog_title="Sélectionner un fichier Excel iTrack",
            allowed_extensions=["xlsx"],
            allow_multiple=False,
        )

        self.page.overlay.remove(file_picker)
        self.page.update()

        if not result or not result[0].path:
            return

        file_path = result[0].path
        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
        except OSError as ex:
            self.page.open(ft.SnackBar(content=ft.Text(f"Impossible de lire le fichier : {ex}")))
            return

        try:
            importer = ExcelImporter()
            preview = importer.preview(file_bytes)
        except Exception as ex:
            self.page.open(ft.SnackBar(content=ft.Text(f"Erreur analyse : {ex}")))
            return

        if preview.errors:
            self.page.open(ft.SnackBar(content=ft.Text(preview.errors[0])))
            return

        # Afficher le dialog de confirmation
        self._show_import_dialog(file_bytes, preview)

    def _show_import_dialog(self, file_bytes: bytes, preview: ImportPreview):
        """Affiche le dialog de preview + options avant import."""

        # Checkboxes options
        cb_visits = ft.Checkbox(label="Configs de visites", value=True)
        cb_patients = ft.Checkbox(label="Patients et visites réalisées", value=True)
        cb_ae = ft.Checkbox(label="Événements indésirables (EI/EIG)", value=True)

        # Stratégie de conflit
        conflict_dropdown = ft.Dropdown(
            label="Si doublon détecté",
            value="skip",
            options=[
                ft.DropdownOption(key="skip", text="Ignorer (conserver l'existant)"),
                ft.DropdownOption(key="update", text="Mettre à jour l'existant"),
            ],
            width=280,
        )

        # Stats détectées
        def stat_row(icon, label, count, color=None):
            return ft.Row(
                [
                    ft.Icon(icon, size=16, color=color or AppColors.TEXT_SECONDARY),
                    ft.Text(label, **Typography.BODY_SMALL, expand=True),
                    ft.Text(
                        str(count),
                        weight=ft.FontWeight.BOLD,
                        color=AppColors.PRIMARY if count > 0 else AppColors.TEXT_SECONDARY,
                        size=13,
                    ),
                ],
                spacing=Spacing.SM,
            )

        stats_section = ft.Column(
            [
                ft.Text("Données détectées dans le fichier :", **Typography.BODY_SMALL,
                        color=AppColors.TEXT_SECONDARY),
                ft.Container(height=4),
                stat_row(ft.Icons.SETTINGS, "Configs de visites", preview.visit_configs),
                stat_row(ft.Icons.PERSON, "Patients", preview.patients),
                stat_row(ft.Icons.CALENDAR_TODAY, "Visites réalisées", preview.visits),
                stat_row(ft.Icons.WARNING_AMBER, "Événements indésirables", preview.adverse_events),
            ],
            spacing=4,
        )

        warnings = []
        if preview.warnings:
            for w in preview.warnings:
                warnings.append(ft.Text(f"⚠ {w}", color=AppColors.WARNING, size=12))

        content_children = [
            stats_section,
            ft.Divider(),
            ft.Text("Que souhaitez-vous importer ?", **Typography.BODY_SMALL),
            cb_visits,
            cb_patients,
            cb_ae,
            ft.Container(height=Spacing.SM),
            conflict_dropdown,
        ]
        if warnings:
            content_children += [ft.Divider()] + warnings

        def do_import(ev):
            dialog.open = False
            self.page.update()
            self._run_import(
                file_bytes=file_bytes,
                import_visit_configs=cb_visits.value,
                import_patients=cb_patients.value,
                import_ae=cb_ae.value,
                on_conflict=conflict_dropdown.value,
            )

        dialog = ft.AlertDialog(
            title=ft.Text("Import Excel → SQLite", **Typography.H4),
            content=ft.Column(
                content_children,
                spacing=Spacing.SM,
                tight=True,
                width=380,
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Annuler"),
                    on_click=lambda ev: setattr(dialog, "open", False) or self.page.update(),
                ),
                ft.Button(
                    content=ft.Text("Importer"),
                    on_click=do_import,
                    bgcolor=AppColors.PRIMARY,
                    color=AppColors.TEXT_ON_PRIMARY,
                ),
            ],
        )
        self.page.open(dialog)

    def _run_import(
        self,
        file_bytes: bytes,
        import_visit_configs: bool,
        import_patients: bool,
        import_ae: bool,
        on_conflict: str,
    ):
        """Exécute l'import et affiche le résultat."""
        if not self.current_study:
            self.page.open(ft.SnackBar(content=ft.Text("Aucune étude sélectionnée")))
            return

        try:
            importer = ExcelImporter()
            result = importer.import_data(
                file_bytes=file_bytes,
                study_id=self.current_study["id"],
                conn=self.db.connection,
                import_visit_configs=import_visit_configs,
                import_patients=import_patients,
                import_ae=import_ae,
                on_conflict=on_conflict,
            )
        except Exception as ex:
            self.page.open(ft.SnackBar(content=ft.Text(f"Erreur import : {ex}")))
            return

        if result.errors:
            msg = f"Import terminé avec erreurs : {result.errors[0]}"
        else:
            msg = result.summary()

        self.page.open(ft.SnackBar(
            content=ft.Text(msg),
            duration=4000,
        ))

        # Rafraîchir l'onglet visits si des configs ont été importées
        if import_visit_configs and result.visit_configs_updated:
            self._show_data_import()
