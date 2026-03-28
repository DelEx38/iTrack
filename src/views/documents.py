"""
Gestion des documents et consentements.
"""

import flet as ft
from typing import Optional, Dict, List


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
        )

        # Version
        self.version_dropdown = ft.Dropdown(
            label="Version *",
            options=[],
            width=200,
        )

        # Date de signature
        self.date_field = ft.TextField(
            label="Signature Date (YYYY-MM-DD) *",
            value=str(existing_consent.get("consent_date", "")) if existing_consent else "",
            autofocus=True,
        )

        # Notes
        self.notes_field = ft.TextField(
            label="Notes",
            value=existing_consent.get("notes", "") if existing_consent else "",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )

        content = ft.Column(
            [
                ft.Text(f"Patient: {patient.get('patient_number')}", size=12, color=ft.Colors.GREY_500),
                ft.Divider(),
                self.type_dropdown,
                self.version_dropdown,
                self.date_field,
                self.notes_field,
            ],
            spacing=15,
            tight=True,
            width=350,
        )

        super().__init__(
            title=ft.Text("Edit Consent" if existing_consent else "New Consent"),
            content=content,
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=self._cancel),
                ft.Button(content=ft.Text("Save"), on_click=self._save),
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
            self.version_dropdown.update()

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
        title = ft.Text("Documents & Consents", size=24, weight=ft.FontWeight.BOLD)

        # Sélecteur de patient
        self.patient_dropdown = ft.Dropdown(
            label="Select Patient",
            options=[],
            width=300,
            on_select=self._on_patient_change,
        )

        header = ft.Row(
            [title, ft.Container(expand=True), self.patient_dropdown],
        )

        # Stats
        self.stats_row = ft.Row(spacing=10)

        # Tableau des consentements
        self.consents_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Version", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Date", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Notes", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            heading_row_color=ft.Colors.SURFACE_CONTAINER,
        )

        # Bouton ajouter
        self.add_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("Add Consent")],
                spacing=8,
            ),
            on_click=self._add_consent,
            bgcolor=ft.Colors.PRIMARY,
            color=ft.Colors.ON_PRIMARY,
        )

        content = ft.Column(
            [
                header,
                ft.Container(height=10),
                self.stats_row,
                ft.Container(height=10),
                ft.Row([ft.Container(expand=True), self.add_btn]),
                ft.Container(height=10),
                ft.Container(content=self.consents_table, expand=True),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(content=content, padding=20, expand=True)

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
            self.consents_table.update()
            self.stats_row.update()

    def _load_consents(self, patient_id: int):
        """Charge les consentements d'un patient."""
        consents = self.consent_queries.get_by_patient(patient_id)
        configs = {c["id"]: c for c in self.consent_queries.get_configs()}

        # Stats
        self._update_stats(consents, configs)

        # Tableau
        self.consents_table.rows.clear()
        for consent in consents:
            config = configs.get(consent.get("consent_config_id"), {})

            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(config.get("consent_type", "?"))),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(consent.get("version", "-"), size=12),
                            bgcolor=ft.Colors.PRIMARY,
                            border_radius=4,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )
                    ),
                    ft.DataCell(ft.Text(str(consent.get("consent_date", "-")))),
                    ft.DataCell(ft.Text(consent.get("notes", "-") or "-", max_lines=1)),
                    ft.DataCell(
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
                                    icon_color=ft.Colors.ERROR,
                                    on_click=lambda e, c=consent: self._delete_consent(c),
                                ),
                            ],
                            spacing=0,
                        )
                    ),
                ],
            )
            self.consents_table.rows.append(row)

    def _update_stats(self, consents: List[Dict], configs: Dict):
        """Met à jour les statistiques."""
        self.stats_row.controls.clear()

        total = len(consents)
        by_type = {}
        for consent in consents:
            config = configs.get(consent.get("consent_config_id"), {})
            ctype = config.get("consent_type", "Unknown")
            by_type[ctype] = by_type.get(ctype, 0) + 1

        stats = [("Total", total, ft.Colors.PRIMARY)]
        for ctype, count in by_type.items():
            stats.append((ctype, count, "#5cb85c"))

        for label, value, color in stats:
            chip = ft.Container(
                content=ft.Row(
                    [ft.Text(label, size=12), ft.Text(str(value), weight=ft.FontWeight.BOLD, color=color)],
                    spacing=5,
                ),
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                border_radius=20,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            )
            self.stats_row.controls.append(chip)

    def _add_consent(self, e):
        patient_id = int(self.patient_dropdown.value)
        patient = self.patients.get(patient_id)
        configs = self.consent_queries.get_configs()

        def on_save(data):
            try:
                self.consent_queries.create(**data)
                self._load_consents(patient_id)
                if self.page:
                    self.consents_table.update()
                    self.stats_row.update()
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
                    self.consents_table.update()
                    self.stats_row.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = ConsentDialog(on_save=on_save, consent_configs=configs, patient=patient, existing_consent=consent)
        self.page.open(dialog)

    def _delete_consent(self, consent: Dict):
        patient_id = int(self.patient_dropdown.value)

        def confirm(e):
            try:
                self.consent_queries.delete(consent["id"])
                self._load_consents(patient_id)
                if self.page:
                    self.consents_table.update()
                    self.stats_row.update()
                dialog.open = False
                self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        def cancel(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Delete Consent"),
            content=ft.Text("Delete this consent record?"),
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=cancel),
                ft.Button(content=ft.Text("Delete"), on_click=confirm, bgcolor=ft.Colors.ERROR),
            ],
        )
        self.page.open(dialog)
