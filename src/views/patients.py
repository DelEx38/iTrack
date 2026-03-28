"""
Gestion des patients.
"""

import flet as ft
from typing import Optional, Dict, List
from datetime import date


class PatientDialog(ft.AlertDialog):
    """Dialogue d'ajout/modification de patient."""

    STATUSES = ["Screening", "Included", "Completed", "Withdrawn", "Screen Failure"]

    def __init__(self, on_save, patient: Optional[Dict] = None):
        self.patient = patient
        self.on_save = on_save
        self.result = None

        # Champs
        self.number_field = ft.TextField(
            label="Patient Number *",
            value=patient.get("patient_number", "") if patient else "",
            autofocus=True,
        )
        self.initials_field = ft.TextField(
            label="Initials",
            value=patient.get("initials", "") if patient else "",
        )
        self.birth_date_field = ft.TextField(
            label="Birth Date (YYYY-MM-DD)",
            value=str(patient.get("birth_date", "")) if patient else "",
        )
        self.status_dropdown = ft.Dropdown(
            label="Status",
            options=[ft.DropdownOption(key=s, text=s) for s in self.STATUSES],
            value=patient.get("status", "Screening") if patient else "Screening",
            width=200,
        )
        self.inclusion_date_field = ft.TextField(
            label="Inclusion Date (YYYY-MM-DD)",
            value=str(patient.get("inclusion_date", "")) if patient else "",
        )

        content = ft.Column(
            [
                self.number_field,
                self.initials_field,
                self.birth_date_field,
                self.status_dropdown,
                self.inclusion_date_field,
            ],
            spacing=15,
            tight=True,
        )

        super().__init__(
            title=ft.Text("Edit Patient" if patient else "New Patient"),
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
        if not self.number_field.value:
            self.number_field.error_text = "Required"
            self.number_field.update()
            return

        self.result = {
            "patient_number": self.number_field.value,
            "initials": self.initials_field.value,
            "birth_date": self.birth_date_field.value or None,
            "status": self.status_dropdown.value,
            "inclusion_date": self.inclusion_date_field.value or None,
        }

        if self.patient:
            self.result["id"] = self.patient["id"]

        self.open = False
        self.page.update()
        self.on_save(self.result)


class PatientsView(ft.Container):
    """Vue de gestion des patients."""

    STATUS_COLORS = {
        "Screening": "#f0ad4e",
        "Included": "#5cb85c",
        "Completed": "#5bc0de",
        "Withdrawn": "#d9534f",
        "Screen Failure": "#777777",
    }

    def __init__(self, patient_queries, visit_queries, consent_queries):
        self.patient_queries = patient_queries
        self.visit_queries = visit_queries
        self.consent_queries = consent_queries

        # Titre
        title = ft.Text("Patients", size=24, weight=ft.FontWeight.BOLD)

        # Bouton ajouter
        add_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("Add Patient")],
                spacing=8,
            ),
            on_click=self._add_patient,
            bgcolor=ft.Colors.PRIMARY,
            color=ft.Colors.ON_PRIMARY,
        )

        # Barre de recherche
        self.search_field = ft.TextField(
            hint_text="Search patients...",
            prefix_icon=ft.Icons.SEARCH,
            width=300,
            on_change=self._on_search,
        )

        # Filtre par statut
        self.status_filter = ft.Dropdown(
            label="Status",
            options=[ft.DropdownOption(key="All", text="All")] +
                    [ft.DropdownOption(key=s, text=s) for s in self.STATUS_COLORS.keys()],
            value="All",
            width=150,
            on_select=self._on_filter_change,
        )

        header = ft.Row(
            [title, ft.Container(expand=True), self.search_field, self.status_filter, add_btn],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Stats
        self.stats_row = ft.Row(spacing=10)

        # Tableau des patients
        self.patients_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Patient #", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Initials", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Inclusion Date", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            heading_row_color=ft.Colors.SURFACE_CONTAINER,
        )

        content = ft.Column(
            [
                header,
                ft.Container(height=10),
                self.stats_row,
                ft.Container(height=10),
                ft.Container(
                    content=self.patients_table,
                    expand=True,
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(content=content, padding=20, expand=True)

        self._load_patients()

    def _load_patients(self, search: str = "", status_filter: str = "All"):
        """Charge les patients depuis la base."""
        patients = self.patient_queries.get_all()

        # Filtrer
        if search:
            search_lower = search.lower()
            patients = [
                p for p in patients
                if search_lower in (p.get("patient_number", "") or "").lower()
                or search_lower in (p.get("initials", "") or "").lower()
            ]

        if status_filter != "All":
            patients = [p for p in patients if p.get("status") == status_filter]

        # Mettre à jour les stats
        self._update_stats()

        # Mettre à jour le tableau
        self.patients_table.rows.clear()
        for patient in patients:
            status = patient.get("status", "Screening")
            status_color = self.STATUS_COLORS.get(status, "#777777")

            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(patient.get("patient_number", ""))),
                    ft.DataCell(ft.Text(patient.get("initials", ""))),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(status, color=ft.Colors.WHITE, size=12),
                            bgcolor=status_color,
                            border_radius=4,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )
                    ),
                    ft.DataCell(ft.Text(str(patient.get("inclusion_date", "") or "-"))),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_size=18,
                                    on_click=lambda e, p=patient: self._edit_patient(p),
                                    tooltip="Edit",
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_size=18,
                                    icon_color=ft.Colors.ERROR,
                                    on_click=lambda e, p=patient: self._delete_patient(p),
                                    tooltip="Delete",
                                ),
                            ],
                            spacing=0,
                        )
                    ),
                ],
            )
            self.patients_table.rows.append(row)

    def _update_stats(self):
        """Met à jour les statistiques."""
        counts = self.patient_queries.count_by_status()
        total = sum(counts.values())

        self.stats_row.controls.clear()

        stats = [
            ("Total", total, ft.Colors.PRIMARY),
            ("Screening", counts.get("Screening", 0), "#f0ad4e"),
            ("Included", counts.get("Included", 0), "#5cb85c"),
            ("Completed", counts.get("Completed", 0), "#5bc0de"),
            ("Withdrawn", counts.get("Withdrawn", 0), "#d9534f"),
        ]

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

    def _on_search(self, e):
        self._load_patients(
            search=self.search_field.value,
            status_filter=self.status_filter.value,
        )
        if self.page:
            self.patients_table.update()
            self.stats_row.update()

    def _on_filter_change(self, e):
        self._load_patients(
            search=self.search_field.value,
            status_filter=e.data,
        )
        if self.page:
            self.patients_table.update()
            self.stats_row.update()

    def _add_patient(self, e):
        def on_save(data):
            try:
                self.patient_queries.create(**data)
                self._load_patients(self.search_field.value, self.status_filter.value)
                self.patients_table.update()
                self.stats_row.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = PatientDialog(on_save=on_save)
        self.page.open(dialog)

    def _edit_patient(self, patient: Dict):
        def on_save(data):
            try:
                self.patient_queries.update(data["id"], **{k: v for k, v in data.items() if k != "id"})
                self._load_patients(self.search_field.value, self.status_filter.value)
                self.patients_table.update()
                self.stats_row.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = PatientDialog(on_save=on_save, patient=patient)
        self.page.open(dialog)

    def _delete_patient(self, patient: Dict):
        def confirm_delete(e):
            try:
                self.patient_queries.delete(patient["id"])
                self._load_patients(self.search_field.value, self.status_filter.value)
                self.patients_table.update()
                self.stats_row.update()
                dialog.open = False
                self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        def cancel(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Delete patient {patient.get('patient_number')}?"),
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=cancel),
                ft.Button(content=ft.Text("Delete"), on_click=confirm_delete, bgcolor=ft.Colors.ERROR),
            ],
        )
        self.page.open(dialog)
