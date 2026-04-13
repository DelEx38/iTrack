# -*- coding: utf-8 -*-
"""
Gestion des patients.
"""

import asyncio
import flet as ft
from typing import Optional, Dict
from src.theme import AppColors, Typography, Spacing, Radius
from src.components import StatusBadge, StatChip, FormField, ConfirmDialog, SectionHeader, AppTable


class PatientDialog(ft.AlertDialog):
    """Dialogue d'ajout/modification de patient."""

    STATUSES = ["Screening", "Included", "Completed", "Withdrawn", "Screen Failure"]

    def __init__(self, on_save, patient: Optional[Dict] = None):
        self.patient = patient
        self.on_save = on_save
        self.result = None

        # Champs avec FormField
        self.number_field = FormField(
            label="Patient Number",
            required=True,
            value=patient.get("patient_number", "") if patient else "",
            autofocus=True,
        )
        self.initials_field = FormField(
            label="Initials",
            value=patient.get("initials", "") if patient else "",
        )
        self.birth_date_field = FormField(
            label="Birth Date",
            helper="Format: YYYY-MM-DD",
            value=str(patient.get("birth_date", "")) if patient else "",
        )
        self.status_dropdown = ft.Dropdown(
            label="Status",
            options=[ft.DropdownOption(key=s, text=s) for s in self.STATUSES],
            value=patient.get("status", "Screening") if patient else "Screening",
            width=200,
            border_radius=Radius.INPUT,
        )
        self.inclusion_date_field = FormField(
            label="Inclusion Date",
            helper="Format: YYYY-MM-DD",
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
            spacing=Spacing.SM,
            tight=True,
        )

        super().__init__(
            title=ft.Text(
                "Edit Patient" if patient else "New Patient",
                **Typography.H4,
            ),
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
        # Validation avec FormField
        if not self.number_field.validate():
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

    STATUSES = ["Screening", "Included", "Completed", "Withdrawn", "Screen Failure"]

    def __init__(self, patient_queries):
        self.patient_queries = patient_queries

        # Titre
        title = ft.Text("Patients", **Typography.H2)

        # Bouton ajouter
        add_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("Add Patient")],
                spacing=Spacing.XS,
            ),
            on_click=self._add_patient,
            bgcolor=AppColors.PRIMARY,
            color=AppColors.TEXT_ON_PRIMARY,
        )

        # Barre de recherche
        self.search_field = ft.TextField(
            hint_text="Search patients...",
            prefix_icon=ft.Icons.SEARCH,
            width=300,
            on_change=self._on_search,
            border_radius=Radius.INPUT,
        )

        # Filtre par statut
        self.status_filter = ft.Dropdown(
            label="Status",
            options=[ft.DropdownOption(key="All", text="All")] +
                    [ft.DropdownOption(key=s, text=s) for s in self.STATUSES],
            value="All",
            width=150,
            on_select=self._on_filter_change,
            border_radius=Radius.INPUT,
        )

        header = ft.Row(
            [title, ft.Container(expand=True), self.search_field, self.status_filter, add_btn],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Stats
        self.stats_row = ft.Row(spacing=Spacing.SM)

        # Tableau des patients
        self.patients_table = AppTable(
            columns=["Patient #", "Initials", "Status", "Inclusion Date", "Actions"],
        )

        content = ft.Column(
            [
                header,
                ft.Container(height=Spacing.SM),
                self.stats_row,
                ft.Container(height=Spacing.SM),
                self.patients_table,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(content=content, padding=Spacing.PAGE_PADDING, expand=True, alignment=ft.Alignment.TOP_LEFT)

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
        rows = []
        for patient in patients:
            status = patient.get("status", "Screening")
            rows.append([
                ft.Text(patient.get("patient_number", ""), **Typography.TABLE_CELL),
                ft.Text(patient.get("initials", ""), **Typography.TABLE_CELL),
                StatusBadge.patient_status(status),
                ft.Text(str(patient.get("inclusion_date", "") or "-"), **Typography.TABLE_CELL),
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
                            icon_color=AppColors.ERROR,
                            on_click=lambda e, p=patient: self._delete_patient(p),
                            tooltip="Delete",
                        ),
                    ],
                    spacing=0,
                ),
            ])
        self.patients_table.set_rows(rows)

    def _update_stats(self):
        """Met à jour les statistiques."""
        counts = self.patient_queries.count_by_status()
        total = sum(counts.values())

        self.stats_row.controls = [
            StatChip("Total", str(total), AppColors.INFO),
            StatChip("Screening", str(counts.get("Screening", 0)), AppColors.PATIENT_SCREENING),
            StatChip("Included", str(counts.get("Included", 0)), AppColors.SUCCESS),
            StatChip("Completed", str(counts.get("Completed", 0)), AppColors.NEUTRAL),
            StatChip("Withdrawn", str(counts.get("Withdrawn", 0)), AppColors.ERROR),
        ]

    async def _on_search(self, e):
        term = e.data
        await asyncio.sleep(0.25)
        if self.search_field.value != term:
            return
        self._load_patients(
            search=self.search_field.value,
            status_filter=self.status_filter.value,
        )
        if self.page:
            self.page.update()

    def _on_filter_change(self, e):
        self._load_patients(
            search=self.search_field.value,
            status_filter=e.data,
        )
        if self.page:
            self.page.update()

    def _add_patient(self, e):
        def on_save(data):
            try:
                self.patient_queries.create(**data)
                self._load_patients(self.search_field.value, self.status_filter.value)
                self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = PatientDialog(on_save=on_save)
        self.page.open(dialog)

    def _edit_patient(self, patient: Dict):
        def on_save(data):
            try:
                self.patient_queries.update(data["id"], **{k: v for k, v in data.items() if k != "id"})
                self._load_patients(self.search_field.value, self.status_filter.value)
                self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = PatientDialog(on_save=on_save, patient=patient)
        self.page.open(dialog)

    def _delete_patient(self, patient: Dict):
        def on_confirm():
            try:
                self.patient_queries.delete(patient["id"])
                self._load_patients(self.search_field.value, self.status_filter.value)
                self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = ConfirmDialog(
            title="Confirm Delete",
            message=f"Delete patient {patient.get('patient_number')}?",
            confirm_text="Delete",
            on_confirm=on_confirm,
            danger=True,
        )
        dialog.show(self.page)
