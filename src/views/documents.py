# -*- coding: utf-8 -*-
"""
Gestion des documents et consentements.
"""

import flet as ft
from typing import Optional, Dict, List
from src.theme import AppColors, Typography, Spacing, Radius
from src.components import StatChip, ConfirmDialog, AppTable


class ConsentDialog(ft.AlertDialog):
    """Dialogue d'ajout/modification de consentement."""

    def __init__(self, on_save, consent_configs: List[Dict], patient: Dict, existing_consent: Optional[Dict] = None):
        self.consent_configs = consent_configs
        self.patient = patient
        self.existing_consent = existing_consent
        self.on_save = on_save

        # Type de consentement
        self.type_dropdown = ft.Dropdown(
            label="Consent Type *",
            options=[
                ft.DropdownOption(key=str(c["id"]), text=c.get("consent_type", ""))
                for c in consent_configs
            ],
            value=str(existing_consent.get("consent_config_id")) if existing_consent else None,
            width=300,
            on_select=self._on_type_change,
            border_radius=Radius.INPUT,
        )

        # Version
        self.version_dropdown = ft.Dropdown(
            label="Version *",
            options=[],
            width=200,
            border_radius=Radius.INPUT,
        )

        # Date de signature
        self.date_field = ft.TextField(
            label="Signature Date (YYYY-MM-DD) *",
            value=str(existing_consent.get("consent_date", "")) if existing_consent else "",
            autofocus=True,
            border_radius=Radius.INPUT,
        )

        # Notes
        self.notes_field = ft.TextField(
            label="Notes",
            value=existing_consent.get("notes", "") if existing_consent else "",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_radius=Radius.INPUT,
        )

        content = ft.Column(
            [
                ft.Text(f"Patient: {patient.get('patient_number')}", **Typography.BODY_SMALL, color=AppColors.TEXT_SECONDARY),
                ft.Divider(),
                self.type_dropdown,
                self.version_dropdown,
                self.date_field,
                self.notes_field,
            ],
            spacing=Spacing.MD,
            tight=True,
            width=350,
        )

        super().__init__(
            title=ft.Text("Edit Consent" if existing_consent else "New Consent", **Typography.H4),
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

        # Si édition, charger les versions
        if existing_consent:
            self._load_versions(existing_consent.get("consent_config_id"))
            self.version_dropdown.value = existing_consent.get("version")

    def _on_type_change(self, e):
        config_id = int(e.data)
        self._load_versions(config_id)
        if self.page:
            self.page.update()

    def _load_versions(self, config_id: int):
        config = next((c for c in self.consent_configs if c["id"] == config_id), None)
        if config:
            versions = config.get("versions", ["1.0"])
            if isinstance(versions, str):
                versions = versions.split(",")
            self.version_dropdown.options = [
                ft.DropdownOption(key=v.strip(), text=v.strip()) for v in versions
            ]
            if versions:
                self.version_dropdown.value = versions[0].strip()

    def _cancel(self, e):
        self.open = False
        self.page.update()

    def _save(self, e):
        errors = []
        if not self.type_dropdown.value:
            errors.append("Type required")
        if not self.version_dropdown.value:
            errors.append("Version required")
        if not self.date_field.value:
            self.date_field.error_text = "Required"
            errors.append("Date required")

        if errors:
            self.page.update()
            return

        result = {
            "patient_id": self.patient["id"],
            "consent_config_id": int(self.type_dropdown.value),
            "version": self.version_dropdown.value,
            "consent_date": self.date_field.value,
            "notes": self.notes_field.value,
        }

        if self.existing_consent:
            result["id"] = self.existing_consent["id"]

        self.open = False
        self.page.update()
        self.on_save(result)


class DocumentsView(ft.Container):
    """Vue de gestion des documents."""

    def __init__(self, patient_queries, consent_queries):
        self.patient_queries = patient_queries
        self.consent_queries = consent_queries

        # Titre
        title = ft.Text("Documents & Consents", **Typography.H2)

        # Sélecteur de patient
        self.patient_dropdown = ft.Dropdown(
            label="Select Patient",
            options=[],
            width=300,
            on_select=self._on_patient_change,
            border_radius=Radius.INPUT,
        )

        header = ft.Row(
            [title, ft.Container(expand=True), self.patient_dropdown],
        )

        # Stats
        self.stats_row = ft.Row(spacing=Spacing.SM)

        # Tableau des consentements
        self.consents_table = AppTable(
            columns=["Type", "Version", "Date", "Notes", "Actions"],
        )

        # Bouton ajouter
        self.add_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("Add Consent")],
                spacing=Spacing.XS,
            ),
            on_click=self._add_consent,
            bgcolor=AppColors.PRIMARY,
            color=AppColors.TEXT_ON_PRIMARY,
        )

        content = ft.Column(
            [
                header,
                ft.Container(height=Spacing.SM),
                self.stats_row,
                ft.Container(height=Spacing.SM),
                ft.Row([ft.Container(expand=True), self.add_btn]),
                ft.Container(height=Spacing.SM),
                self.consents_table,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(content=content, padding=Spacing.PAGE_PADDING, expand=True, alignment=ft.Alignment.TOP_LEFT)

        self._load_patients()

    def _load_patients(self):
        """Charge la liste des patients."""
        patients = self.patient_queries.get_all()
        self.patients = {p["id"]: p for p in patients}

        self.patient_dropdown.options = [
            ft.DropdownOption(
                key=str(p["id"]),
                text=f"{p.get('patient_number', '')} - {p.get('status', '')}"
            )
            for p in patients
        ]

        if patients:
            self.patient_dropdown.value = str(patients[0]["id"])
            self._load_consents(patients[0]["id"])

    def _on_patient_change(self, e):
        patient_id = int(e.data)
        self._load_consents(patient_id)
        if self.page:
            self.page.update()

    def _load_consents(self, patient_id: int):
        """Charge les consentements d'un patient."""
        consents = self.consent_queries.get_by_patient(patient_id)
        configs = {c["id"]: c for c in self.consent_queries.get_configs()}

        # Stats
        self._update_stats(consents, configs)

        # Tableau
        rows = []
        for consent in consents:
            config = configs.get(consent.get("consent_config_id"), {})
            rows.append([
                ft.Text(config.get("consent_type", "?"), **Typography.TABLE_CELL),
                ft.Container(
                    content=ft.Text(consent.get("version", "-"), **Typography.BADGE, color=AppColors.TEXT_ON_PRIMARY),
                    bgcolor=AppColors.PRIMARY,
                    border_radius=Radius.BADGE,
                    padding=Spacing.badge(),
                ),
                ft.Text(str(consent.get("consent_date", "-")), **Typography.TABLE_CELL),
                ft.Text(consent.get("notes", "-") or "-", **Typography.TABLE_CELL, max_lines=1),
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_size=18,
                            on_click=lambda e, c=consent: self._edit_consent(c),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_size=18,
                            icon_color=AppColors.ERROR,
                            on_click=lambda e, c=consent: self._delete_consent(c),
                        ),
                    ],
                    spacing=0,
                ),
            ])
        self.consents_table.set_rows(rows)

    def _update_stats(self, consents: List[Dict], configs: Dict):
        """Met à jour les statistiques."""
        self.stats_row.controls.clear()

        total = len(consents)
        by_type: Dict[str, int] = {}
        for consent in consents:
            config = configs.get(consent.get("consent_config_id"), {})
            ctype = config.get("consent_type", "Unknown")
            by_type[ctype] = by_type.get(ctype, 0) + 1

        self.stats_row.controls.append(StatChip("Total", total, AppColors.INFO))
        for ctype, count in by_type.items():
            self.stats_row.controls.append(StatChip(ctype, count, AppColors.SUCCESS))

    def _add_consent(self, e):
        patient_id = int(self.patient_dropdown.value)
        patient = self.patients.get(patient_id)
        configs = self.consent_queries.get_configs()

        def on_save(data):
            try:
                self.consent_queries.create(**data)
                self._load_consents(patient_id)
                if self.page:
                    self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = ConsentDialog(on_save=on_save, consent_configs=configs, patient=patient)
        self.page.open(dialog)

    def _edit_consent(self, consent: Dict):
        patient_id = int(self.patient_dropdown.value)
        patient = self.patients.get(patient_id)
        configs = self.consent_queries.get_configs()

        def on_save(data):
            try:
                self.consent_queries.update(data["id"], **{k: v for k, v in data.items() if k != "id"})
                self._load_consents(patient_id)
                if self.page:
                    self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = ConsentDialog(on_save=on_save, consent_configs=configs, patient=patient, existing_consent=consent)
        self.page.open(dialog)

    def _delete_consent(self, consent: Dict):
        patient_id = int(self.patient_dropdown.value)

        def on_confirm():
            try:
                self.consent_queries.delete(consent["id"])
                self._load_consents(patient_id)
                if self.page:
                    self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        ConfirmDialog(
            title="Delete Consent",
            message="Delete this consent record?",
            confirm_text="Delete",
            on_confirm=on_confirm,
            danger=True,
        ).show(self.page)
