# -*- coding: utf-8 -*-
"""
Gestion des événements indésirables (EI/EIG).
"""

import asyncio
import flet as ft
from typing import Optional, Dict, List
from datetime import datetime
from src.theme import AppColors, Typography, Spacing, Radius
from src.components import StatusBadge, StatChip, ConfirmDialog, AppTable


class AEDialog(ft.AlertDialog):
    """Dialogue d'ajout/modification d'événement indésirable."""

    SEVERITIES = ["Mild", "Moderate", "Severe"]
    OUTCOMES = ["Recovered", "Recovering", "Not Recovered", "Fatal", "Unknown"]
    CAUSALITIES = ["Related", "Possibly Related", "Not Related", "Unknown"]

    def __init__(self, on_save, patients: List[Dict], ae: Optional[Dict] = None):
        self.ae = ae
        self.on_save = on_save

        # Patient
        self.patient_dropdown = ft.Dropdown(
            label="Patient *",
            options=[
                ft.DropdownOption(key=str(p["id"]), text=p.get("patient_number", ""))
                for p in patients
            ],
            value=str(ae.get("patient_id")) if ae else None,
            width=250,
            border_radius=Radius.INPUT,
        )

        # Terme
        self.term_field = ft.TextField(
            label="AE Term *",
            value=ae.get("ae_term", "") if ae else "",
            autofocus=True,
            border_radius=Radius.INPUT,
        )

        # Dates
        self.start_date_field = ft.TextField(
            label="Start Date (YYYY-MM-DD) *",
            value=str(ae.get("start_date", "")) if ae else "",
            border_radius=Radius.INPUT,
        )
        self.end_date_field = ft.TextField(
            label="End Date (YYYY-MM-DD)",
            value=str(ae.get("end_date", "") or "") if ae else "",
            border_radius=Radius.INPUT,
        )

        # Sévérité
        self.severity_dropdown = ft.Dropdown(
            label="Severity",
            options=[ft.DropdownOption(key=s, text=s) for s in self.SEVERITIES],
            value=ae.get("severity", "Mild") if ae else "Mild",
            width=150,
            border_radius=Radius.INPUT,
        )

        # SAE
        self.sae_switch = ft.Switch(
            label="Serious (SAE)",
            value=ae.get("is_serious", False) if ae else False,
        )

        # Date de déclaration SAE
        self.reporting_date_field = ft.TextField(
            label="SAE Reporting Date",
            value=str(ae.get("reporting_date", "") or "") if ae else "",
            border_radius=Radius.INPUT,
        )

        # Outcome
        self.outcome_dropdown = ft.Dropdown(
            label="Outcome",
            options=[ft.DropdownOption(key=o, text=o) for o in self.OUTCOMES],
            value=ae.get("outcome", "Recovering") if ae else "Recovering",
            width=180,
            border_radius=Radius.INPUT,
        )

        # Causalité
        self.causality_dropdown = ft.Dropdown(
            label="Causality",
            options=[ft.DropdownOption(key=c, text=c) for c in self.CAUSALITIES],
            value=ae.get("causality", "Unknown") if ae else "Unknown",
            width=180,
            border_radius=Radius.INPUT,
        )

        # Notes
        self.notes_field = ft.TextField(
            label="Notes",
            value=ae.get("notes", "") if ae else "",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_radius=Radius.INPUT,
        )

        content = ft.Column(
            [
                self.patient_dropdown,
                self.term_field,
                ft.Row([self.start_date_field, self.end_date_field], spacing=Spacing.SM),
                ft.Row([self.severity_dropdown, self.outcome_dropdown, self.causality_dropdown], spacing=Spacing.SM),
                ft.Row([self.sae_switch, self.reporting_date_field], spacing=Spacing.LG),
                self.notes_field,
            ],
            spacing=Spacing.MD,
            tight=True,
            width=500,
        )

        super().__init__(
            title=ft.Text("Edit Adverse Event" if ae else "New Adverse Event", **Typography.H4),
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
        if not self.patient_dropdown.value:
            errors.append("Patient required")
        if not self.term_field.value:
            self.term_field.error_text = "Required"
            errors.append("Term required")
        if not self.start_date_field.value:
            self.start_date_field.error_text = "Required"
            errors.append("Start date required")

        if errors:
            self.page.update()
            return

        result = {
            "patient_id": int(self.patient_dropdown.value),
            "ae_term": self.term_field.value,
            "start_date": self.start_date_field.value,
            "end_date": self.end_date_field.value or None,
            "severity": self.severity_dropdown.value,
            "is_serious": self.sae_switch.value,
            "reporting_date": self.reporting_date_field.value or None,
            "outcome": self.outcome_dropdown.value,
            "causality": self.causality_dropdown.value,
            "notes": self.notes_field.value,
        }

        if self.ae:
            result["id"] = self.ae["id"]

        self.open = False
        self.page.update()
        self.on_save(result)


class AdverseEventsView(ft.Container):
    """Vue de gestion des événements indésirables."""

    OUTCOMES = ["Recovered", "Recovering", "Not Recovered", "Fatal", "Unknown"]

    def __init__(self, patient_queries, ae_queries):
        self.patient_queries = patient_queries
        self.ae_queries = ae_queries

        # Titre
        title = ft.Text("Adverse Events", **Typography.H2)

        # Bouton ajouter
        add_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("Add AE")],
                spacing=Spacing.XS,
            ),
            on_click=self._add_ae,
            bgcolor=AppColors.PRIMARY,
            color=AppColors.TEXT_ON_PRIMARY,
        )

        # Recherche
        self.search_field = ft.TextField(
            hint_text="Search...",
            prefix_icon=ft.Icons.SEARCH,
            width=250,
            on_change=self._on_search,
            border_radius=Radius.INPUT,
        )

        # Filtre outcome
        self.outcome_filter = ft.Dropdown(
            label="Outcome",
            options=[ft.DropdownOption(key="All", text="All")] +
                    [ft.DropdownOption(key=o, text=o) for o in self.OUTCOMES],
            value="All",
            width=150,
            on_select=self._on_filter_change,
            border_radius=Radius.INPUT,
        )

        header = ft.Row(
            [title, ft.Container(expand=True), self.search_field, self.outcome_filter, add_btn],
        )

        # Stats
        self.stats_row = ft.Row(spacing=Spacing.SM)

        # Tableau
        self.ae_table = AppTable(
            columns=["Patient", "AE Term", "Start", "Severity", "SAE", "Outcome", "Actions"],
        )

        content = ft.Column(
            [
                header,
                ft.Container(height=Spacing.SM),
                self.stats_row,
                ft.Container(height=Spacing.SM),
                self.ae_table,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(content=content, padding=Spacing.PAGE_PADDING, expand=True, alignment=ft.Alignment.TOP_LEFT)

        self._load_ae()

    def _load_ae(self, search: str = "", outcome_filter: str = "All"):
        """Charge les événements indésirables."""
        ae_list = self.ae_queries.get_all()
        patients = {p["id"]: p for p in self.patient_queries.get_all()}

        # Filtrer
        if search:
            search_lower = search.lower()
            ae_list = [
                ae for ae in ae_list
                if search_lower in (ae.get("ae_term", "") or "").lower()
                or search_lower in (patients.get(ae["patient_id"], {}).get("patient_number", "") or "").lower()
            ]

        if outcome_filter != "All":
            ae_list = [ae for ae in ae_list if ae.get("outcome") == outcome_filter]

        # Stats
        self._update_stats(ae_list)

        # Tableau
        rows = []
        for ae in ae_list:
            patient = patients.get(ae["patient_id"], {})
            severity = ae.get("severity", "Mild")
            outcome = ae.get("outcome", "Unknown")
            is_serious = ae.get("is_serious", False)

            # Indicateur délai SAE
            sae_indicator = "-"
            sae_color = None
            if is_serious:
                sae_indicator = "SAE"
                sae_color = AppColors.ERROR
                if ae.get("reporting_date") and ae.get("start_date"):
                    try:
                        start = datetime.strptime(str(ae["start_date"]), "%Y-%m-%d")
                        reported = datetime.strptime(str(ae["reporting_date"]), "%Y-%m-%d")
                        delta = (reported - start).days
                        if delta <= 1:
                            sae_indicator = "SAE (<24h)"
                            sae_color = AppColors.SUCCESS
                        else:
                            sae_indicator = f"SAE (+{delta}d)"
                            sae_color = AppColors.ERROR
                    except Exception:
                        pass

            rows.append([
                ft.Text(patient.get("patient_number", "?"), **Typography.TABLE_CELL),
                ft.Text(ae.get("ae_term", ""), **Typography.TABLE_CELL),
                ft.Text(str(ae.get("start_date", "-")), **Typography.TABLE_CELL),
                StatusBadge.ae_severity(severity),
                ft.Text(
                    sae_indicator,
                    **Typography.TABLE_CELL,
                    color=sae_color,
                    weight=ft.FontWeight.BOLD if is_serious else None,
                ),
                StatusBadge.ae_outcome(outcome),
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_size=18,
                            on_click=lambda e, a=ae: self._edit_ae(a),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_size=18,
                            icon_color=AppColors.ERROR,
                            on_click=lambda e, a=ae: self._delete_ae(a),
                        ),
                    ],
                    spacing=0,
                ),
            ])
        self.ae_table.set_rows(rows)

    def _update_stats(self, ae_list: List[Dict]):
        """Met à jour les statistiques."""
        self.stats_row.controls.clear()

        total = len(ae_list)
        sae = sum(1 for ae in ae_list if ae.get("is_serious"))
        ongoing = sum(1 for ae in ae_list if ae.get("outcome") in ["Recovering", "Not Recovered"])
        recovered = sum(1 for ae in ae_list if ae.get("outcome") == "Recovered")
        fatal = sum(1 for ae in ae_list if ae.get("outcome") == "Fatal")

        self.stats_row.controls.extend([
            StatChip("Total", total, AppColors.INFO),
            StatChip("SAE", sae, AppColors.ERROR),
            StatChip("Ongoing", ongoing, AppColors.WARNING),
            StatChip("Recovered", recovered, AppColors.SUCCESS),
            StatChip("Fatal", fatal, AppColors.ERROR),
        ])

    async def _on_search(self, e):
        term = e.data
        await asyncio.sleep(0.25)
        if self.search_field.value != term:
            return
        self._load_ae(search=self.search_field.value, outcome_filter=self.outcome_filter.value)
        if self.page:
            self.page.update()

    def _on_filter_change(self, e):
        self._load_ae(search=self.search_field.value, outcome_filter=e.data)
        if self.page:
            self.page.update()

    def _add_ae(self, e):
        patients = self.patient_queries.get_all()

        def on_save(data):
            try:
                self.ae_queries.create(**data)
                self._load_ae(self.search_field.value, self.outcome_filter.value)
                if self.page:
                    self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = AEDialog(on_save=on_save, patients=patients)
        self.page.open(dialog)

    def _edit_ae(self, ae: Dict):
        patients = self.patient_queries.get_all()

        def on_save(data):
            try:
                self.ae_queries.update(data["id"], **{k: v for k, v in data.items() if k != "id"})
                self._load_ae(self.search_field.value, self.outcome_filter.value)
                if self.page:
                    self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = AEDialog(on_save=on_save, patients=patients, ae=ae)
        self.page.open(dialog)

    def _delete_ae(self, ae: Dict):
        def on_confirm():
            try:
                self.ae_queries.delete(ae["id"])
                self._load_ae(self.search_field.value, self.outcome_filter.value)
                if self.page:
                    self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        ConfirmDialog(
            title="Delete AE",
            message=f"Delete adverse event '{ae.get('ae_term')}'?",
            confirm_text="Delete",
            on_confirm=on_confirm,
            danger=True,
        ).show(self.page)
