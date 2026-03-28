"""
Gestion du monitoring.
"""

import flet as ft
from typing import Optional, Dict, List
from datetime import datetime


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
        )

        # Date
        self.date_field = ft.TextField(
            label="Monitoring Date (YYYY-MM-DD) *",
            value=str(entry.get("monitoring_date", "")) if entry else datetime.now().strftime("%Y-%m-%d"),
            autofocus=True,
        )

        # Type
        self.type_dropdown = ft.Dropdown(
            label="Type",
            options=[ft.DropdownOption(key=t, text=t) for t in self.TYPES],
            value=entry.get("monitoring_type", "Source Data Verification") if entry else "Source Data Verification",
            width=300,
        )

        # Findings
        self.findings_field = ft.TextField(
            label="Findings",
            value=entry.get("findings", "") if entry else "",
            multiline=True,
            min_lines=3,
            max_lines=6,
        )

        # Actions
        self.actions_field = ft.TextField(
            label="Actions Required",
            value=entry.get("actions_required", "") if entry else "",
            multiline=True,
            min_lines=2,
            max_lines=4,
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
            spacing=15,
            tight=True,
            width=450,
        )

        super().__init__(
            title=ft.Text("Edit Monitoring Entry" if entry else "New Monitoring Entry"),
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
        "Source Data Verification": "#5bc0de",
        "Query Resolution": "#f0ad4e",
        "Protocol Review": "#5cb85c",
        "Safety Review": "#d9534f",
        "Other": "#777777",
    }

    def __init__(self, patient_queries, monitoring_queries):
        self.patient_queries = patient_queries
        self.monitoring_queries = monitoring_queries

        # Titre
        title = ft.Text("Monitoring", size=24, weight=ft.FontWeight.BOLD)

        # Bouton ajouter
        add_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("Add Entry")],
                spacing=8,
            ),
            on_click=self._add_entry,
            bgcolor=ft.Colors.PRIMARY,
            color=ft.Colors.ON_PRIMARY,
        )

        # Recherche
        self.search_field = ft.TextField(
            hint_text="Search...",
            prefix_icon=ft.Icons.SEARCH,
            width=250,
            on_change=self._on_search,
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
        )

        header = ft.Row(
            [title, ft.Container(expand=True), self.search_field, self.completed_filter, add_btn],
        )

        # Stats
        self.stats_row = ft.Row(spacing=10)

        # Tableau
        self.monitoring_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Patient", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Date", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Findings", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
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
                ft.Container(content=self.monitoring_table, expand=True),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(content=content, padding=20, expand=True)

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

            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(patient.get("patient_number", "?"))),
                    ft.DataCell(ft.Text(str(entry.get("monitoring_date", "-")))),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(mon_type, color=ft.Colors.WHITE, size=12),
                            bgcolor=self.TYPE_COLORS.get(mon_type, "#777"),
                            border_radius=4,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )
                    ),
                    ft.DataCell(ft.Text(findings)),
                    ft.DataCell(
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE if is_completed else ft.Icons.PENDING,
                            color="#5cb85c" if is_completed else "#f0ad4e",
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
                                    icon_color=ft.Colors.ERROR,
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

        by_type = {}
        for entry in entries:
            t = entry.get("monitoring_type", "Other")
            by_type[t] = by_type.get(t, 0) + 1

        stats = [
            ("Total", total, ft.Colors.PRIMARY),
            ("Completed", completed, "#5cb85c"),
            ("Pending", pending, "#f0ad4e"),
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
        self._load_entries(search=self.search_field.value, completed_filter=self.completed_filter.value)
        if self.page:
            self.monitoring_table.update()
            self.stats_row.update()

    def _on_filter_change(self, e):
        self._load_entries(search=self.search_field.value, completed_filter=e.data)
        if self.page:
            self.monitoring_table.update()
            self.stats_row.update()

    def _add_entry(self, e):
        patients = self.patient_queries.get_all()

        def on_save(data):
            try:
                self.monitoring_queries.create(**data)
                self._load_entries(self.search_field.value, self.completed_filter.value)
                if self.page:
                    self.monitoring_table.update()
                    self.stats_row.update()
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
                    self.monitoring_table.update()
                    self.stats_row.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = MonitoringEntryDialog(on_save=on_save, patients=patients, entry=entry)
        self.page.open(dialog)

    def _delete_entry(self, entry: Dict):
        def confirm(e):
            try:
                self.monitoring_queries.delete(entry["id"])
                self._load_entries(self.search_field.value, self.completed_filter.value)
                if self.page:
                    self.monitoring_table.update()
                    self.stats_row.update()
                dialog.open = False
                self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        def cancel(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Delete Entry"),
            content=ft.Text("Delete this monitoring entry?"),
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=cancel),
                ft.Button(content=ft.Text("Delete"), on_click=confirm, bgcolor=ft.Colors.ERROR),
            ],
        )
        self.page.open(dialog)
