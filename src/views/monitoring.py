# -*- coding: utf-8 -*-
"""
Gestion du monitoring.
"""

import asyncio
import flet as ft
from typing import Optional, Dict, List
from datetime import datetime
from src.theme import AppColors, Typography, Spacing, Radius
from src.components import StatusBadge, StatChip, ConfirmDialog


class MonitoringEntryDialog(ft.AlertDialog):
    """Dialogue d'ajout/modification d'entrée de monitoring."""

    TYPES = ["Source Data Verification", "Query Resolution", "Protocol Review", "Safety Review", "Other"]

    def __init__(self, on_save, patients: List[Dict], entry: Optional[Dict] = None):
        self.entry = entry
        self.on_save = on_save

        # Patient
        self.patient_dropdown = ft.Dropdown(
            label="Patient *",
            options=[
                ft.DropdownOption(key=str(p["id"]), text=p.get("patient_number", ""))
                for p in patients
            ],
            value=str(entry.get("patient_id")) if entry else None,
            width=250,
            border_radius=Radius.INPUT,
        )

        # Date
        self.date_field = ft.TextField(
            label="Monitoring Date (YYYY-MM-DD) *",
            value=str(entry.get("monitoring_date", "")) if entry else datetime.now().strftime("%Y-%m-%d"),
            autofocus=True,
            border_radius=Radius.INPUT,
        )

        # Type
        self.type_dropdown = ft.Dropdown(
            label="Type",
            options=[ft.DropdownOption(key=t, text=t) for t in self.TYPES],
            value=entry.get("monitoring_type", "Source Data Verification") if entry else "Source Data Verification",
            width=300,
            border_radius=Radius.INPUT,
        )

        # Findings
        self.findings_field = ft.TextField(
            label="Findings",
            value=entry.get("findings", "") if entry else "",
            multiline=True,
            min_lines=3,
            max_lines=6,
            border_radius=Radius.INPUT,
        )

        # Actions
        self.actions_field = ft.TextField(
            label="Actions Required",
            value=entry.get("actions_required", "") if entry else "",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_radius=Radius.INPUT,
        )

        # Complété
        self.completed_switch = ft.Switch(
            label="Completed",
            value=entry.get("is_completed", False) if entry else False,
        )

        content = ft.Column(
            [
                self.patient_dropdown,
                self.date_field,
                self.type_dropdown,
                self.findings_field,
                self.actions_field,
                self.completed_switch,
            ],
            spacing=Spacing.MD,
            tight=True,
            width=450,
        )

        super().__init__(
            title=ft.Text("Edit Monitoring Entry" if entry else "New Monitoring Entry", **Typography.H4),
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
        if not self.date_field.value:
            self.date_field.error_text = "Required"
            errors.append("Date required")

        if errors:
            self.page.update()
            return

        result = {
            "patient_id": int(self.patient_dropdown.value),
            "monitoring_date": self.date_field.value,
            "monitoring_type": self.type_dropdown.value,
            "findings": self.findings_field.value or None,
            "actions_required": self.actions_field.value or None,
            "is_completed": self.completed_switch.value,
        }

        if self.entry:
            result["id"] = self.entry["id"]

        self.open = False
        self.page.update()
        self.on_save(result)


class MonitoringView(ft.Container):
    """Vue de gestion du monitoring."""

    TYPE_COLORS = {
        "Source Data Verification": AppColors.INFO,
        "Query Resolution": AppColors.WARNING,
        "Protocol Review": AppColors.SUCCESS,
        "Safety Review": AppColors.ERROR,
        "Other": AppColors.NEUTRAL,
    }

    def __init__(self, patient_queries, monitoring_queries):
        self.patient_queries = patient_queries
        self.monitoring_queries = monitoring_queries

        # Titre
        title = ft.Text("Monitoring", **Typography.H2)

        # Bouton ajouter
        add_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("Add Entry")],
                spacing=Spacing.XS,
            ),
            on_click=self._add_entry,
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

        # Filtre complété
        self.completed_filter = ft.Dropdown(
            label="Status",
            options=[
                ft.DropdownOption(key="All", text="All"),
                ft.DropdownOption(key="Completed", text="Completed"),
                ft.DropdownOption(key="Pending", text="Pending"),
            ],
            value="All",
            width=150,
            on_select=self._on_filter_change,
            border_radius=Radius.INPUT,
        )

        header = ft.Row(
            [title, ft.Container(expand=True), self.search_field, self.completed_filter, add_btn],
        )

        # Stats
        self.stats_row = ft.Row(spacing=Spacing.SM)

        # Tableau
        self.monitoring_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Patient", **Typography.TABLE_HEADER)),
                ft.DataColumn(ft.Text("Date", **Typography.TABLE_HEADER)),
                ft.DataColumn(ft.Text("Type", **Typography.TABLE_HEADER)),
                ft.DataColumn(ft.Text("Findings", **Typography.TABLE_HEADER)),
                ft.DataColumn(ft.Text("Status", **Typography.TABLE_HEADER)),
                ft.DataColumn(ft.Text("Actions", **Typography.TABLE_HEADER)),
            ],
            rows=[],
            border=ft.border.all(1, AppColors.BORDER),
            border_radius=Radius.TABLE,
            heading_row_color=AppColors.SURFACE_VARIANT,
        )

        content = ft.Column(
            [
                header,
                ft.Container(height=Spacing.SM),
                self.stats_row,
                ft.Container(height=Spacing.SM),
                ft.Container(content=self.monitoring_table, expand=True),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(content=content, padding=Spacing.PAGE_PADDING, expand=True)

        self._load_entries()

    def _load_entries(self, search: str = "", completed_filter: str = "All"):
        """Charge les entrées de monitoring."""
        entries = self.monitoring_queries.get_all()
        patients = {p["id"]: p for p in self.patient_queries.get_all()}

        # Filtrer
        if search:
            search_lower = search.lower()
            entries = [
                e for e in entries
                if search_lower in (e.get("findings", "") or "").lower()
                or search_lower in (e.get("monitoring_type", "") or "").lower()
                or search_lower in (patients.get(e["patient_id"], {}).get("patient_number", "") or "").lower()
            ]

        if completed_filter == "Completed":
            entries = [e for e in entries if e.get("is_completed")]
        elif completed_filter == "Pending":
            entries = [e for e in entries if not e.get("is_completed")]

        # Stats
        self._update_stats(entries)

        # Tableau
        self.monitoring_table.rows.clear()
        for entry in entries:
            patient = patients.get(entry["patient_id"], {})
            mon_type = entry.get("monitoring_type", "Other")
            is_completed = entry.get("is_completed", False)
            findings = entry.get("findings", "") or "-"
            if len(findings) > 40:
                findings = findings[:40] + "..."

            # Badge type
            type_badge = ft.Container(
                content=ft.Text(mon_type, **Typography.BADGE, color=AppColors.TEXT_ON_PRIMARY),
                bgcolor=self.TYPE_COLORS.get(mon_type, AppColors.NEUTRAL),
                border_radius=Radius.BADGE,
                padding=Spacing.badge(),
            )

            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(patient.get("patient_number", "?"), **Typography.TABLE_CELL)),
                    ft.DataCell(ft.Text(str(entry.get("monitoring_date", "-")), **Typography.TABLE_CELL)),
                    ft.DataCell(type_badge),
                    ft.DataCell(ft.Text(findings, **Typography.TABLE_CELL)),
                    ft.DataCell(
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE if is_completed else ft.Icons.PENDING,
                            color=AppColors.SUCCESS if is_completed else AppColors.WARNING,
                            size=20,
                        )
                    ),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_size=18,
                                    on_click=lambda e, en=entry: self._edit_entry(en),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_size=18,
                                    icon_color=AppColors.ERROR,
                                    on_click=lambda e, en=entry: self._delete_entry(en),
                                ),
                            ],
                            spacing=0,
                        )
                    ),
                ],
            )
            self.monitoring_table.rows.append(row)

    def _update_stats(self, entries: List[Dict]):
        """Met à jour les statistiques."""
        self.stats_row.controls.clear()

        total = len(entries)
        completed = sum(1 for e in entries if e.get("is_completed"))
        pending = total - completed

        self.stats_row.controls.extend([
            StatChip("Total", total, AppColors.INFO),
            StatChip("Completed", completed, AppColors.SUCCESS),
            StatChip("Pending", pending, AppColors.WARNING),
        ])

    async def _on_search(self, e):
        term = e.data
        await asyncio.sleep(0.25)
        if self.search_field.value != term:
            return
        self._load_entries(search=self.search_field.value, completed_filter=self.completed_filter.value)
        if self.page:
            self.page.update()

    def _on_filter_change(self, e):
        self._load_entries(search=self.search_field.value, completed_filter=e.data)
        if self.page:
            self.page.update()

    def _add_entry(self, e):
        patients = self.patient_queries.get_all()

        def on_save(data):
            try:
                self.monitoring_queries.create(**data)
                self._load_entries(self.search_field.value, self.completed_filter.value)
                if self.page:
                    self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = MonitoringEntryDialog(on_save=on_save, patients=patients)
        self.page.open(dialog)

    def _edit_entry(self, entry: Dict):
        patients = self.patient_queries.get_all()

        def on_save(data):
            try:
                self.monitoring_queries.update(data["id"], **{k: v for k, v in data.items() if k != "id"})
                self._load_entries(self.search_field.value, self.completed_filter.value)
                if self.page:
                    self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = MonitoringEntryDialog(on_save=on_save, patients=patients, entry=entry)
        self.page.open(dialog)

    def _delete_entry(self, entry: Dict):
        def on_confirm():
            try:
                self.monitoring_queries.delete(entry["id"])
                self._load_entries(self.search_field.value, self.completed_filter.value)
                if self.page:
                    self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        ConfirmDialog(
            title="Delete Entry",
            message="Delete this monitoring entry?",
            confirm_text="Delete",
            on_confirm=on_confirm,
            danger=True,
        ).show(self.page)
