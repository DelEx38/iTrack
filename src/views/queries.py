"""
Gestion des queries (data management).
"""

import flet as ft
from typing import Optional, Dict, List
from datetime import datetime


class QueryDialog(ft.AlertDialog):
    """Dialogue d'ajout/modification de query."""

    STATUSES = ["Open", "Answered", "Closed"]
    PRIORITIES = ["Low", "Medium", "High"]

    def __init__(self, on_save, patients: List[Dict], query: Optional[Dict] = None):
        self.query = query
        self.on_save = on_save

        # Patient
        self.patient_dropdown = ft.Dropdown(
            label="Patient *",
            options=[
                ft.DropdownOption(key=str(p["id"]), text=p.get("patient_number", ""))
                for p in patients
            ],
            value=str(query.get("patient_id")) if query else None,
            width=250,
        )

        # Champ / Variable
        self.field_field = ft.TextField(
            label="Field / Variable *",
            value=query.get("field_name", "") if query else "",
            autofocus=True,
        )

        # Description
        self.description_field = ft.TextField(
            label="Query Description *",
            value=query.get("description", "") if query else "",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )

        # Priorité
        self.priority_dropdown = ft.Dropdown(
            label="Priority",
            options=[ft.DropdownOption(key=p, text=p) for p in self.PRIORITIES],
            value=query.get("priority", "Medium") if query else "Medium",
            width=150,
        )

        # Statut
        self.status_dropdown = ft.Dropdown(
            label="Status",
            options=[ft.DropdownOption(key=s, text=s) for s in self.STATUSES],
            value=query.get("status", "Open") if query else "Open",
            width=150,
        )

        # Réponse
        self.response_field = ft.TextField(
            label="Response",
            value=query.get("response", "") if query else "",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )

        content = ft.Column(
            [
                self.patient_dropdown,
                self.field_field,
                self.description_field,
                ft.Row([self.priority_dropdown, self.status_dropdown], spacing=10),
                self.response_field,
            ],
            spacing=15,
            tight=True,
            width=450,
        )

        super().__init__(
            title=ft.Text("Edit Query" if query else "New Query"),
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
        if not self.field_field.value:
            self.field_field.error_text = "Required"
            errors.append("Field required")
        if not self.description_field.value:
            self.description_field.error_text = "Required"
            errors.append("Description required")

        if errors:
            self.page.update()
            return

        result = {
            "patient_id": int(self.patient_dropdown.value),
            "field_name": self.field_field.value,
            "description": self.description_field.value,
            "priority": self.priority_dropdown.value,
            "status": self.status_dropdown.value,
            "response": self.response_field.value or None,
        }

        if self.query:
            result["id"] = self.query["id"]

        self.open = False
        self.page.update()
        self.on_save(result)


class QueriesView(ft.Container):
    """Vue de gestion des queries."""

    STATUS_COLORS = {
        "Open": "#d9534f",
        "Answered": "#f0ad4e",
        "Closed": "#5cb85c",
    }

    PRIORITY_COLORS = {
        "Low": "#5bc0de",
        "Medium": "#f0ad4e",
        "High": "#d9534f",
    }

    def __init__(self, patient_queries, query_queries):
        self.patient_queries = patient_queries
        self.query_queries = query_queries

        # Titre
        title = ft.Text("Data Queries", size=24, weight=ft.FontWeight.BOLD)

        # Bouton ajouter
        add_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("New Query")],
                spacing=8,
            ),
            on_click=self._add_query,
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

        # Filtre statut
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
        )

        # Stats
        self.stats_row = ft.Row(spacing=10)

        # Tableau
        self.queries_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Patient", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Field", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Description", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Priority", weight=ft.FontWeight.BOLD)),
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
                ft.Container(content=self.queries_table, expand=True),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(content=content, padding=20, expand=True)

        self._load_queries()

    def _load_queries(self, search: str = "", status_filter: str = "All"):
        """Charge les queries."""
        queries = self.query_queries.get_all()
        patients = {p["id"]: p for p in self.patient_queries.get_all()}

        # Filtrer
        if search:
            search_lower = search.lower()
            queries = [
                q for q in queries
                if search_lower in (q.get("field_name", "") or "").lower()
                or search_lower in (q.get("description", "") or "").lower()
                or search_lower in (patients.get(q["patient_id"], {}).get("patient_number", "") or "").lower()
            ]

        if status_filter != "All":
            queries = [q for q in queries if q.get("status") == status_filter]

        # Stats
        self._update_stats(queries)

        # Tableau
        self.queries_table.rows.clear()
        for query in queries:
            patient = patients.get(query["patient_id"], {})
            status = query.get("status", "Open")
            priority = query.get("priority", "Medium")

            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(patient.get("patient_number", "?"))),
                    ft.DataCell(ft.Text(query.get("field_name", ""), weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(query.get("description", "")[:50] + "..." if len(query.get("description", "")) > 50 else query.get("description", ""))),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(priority, color=ft.Colors.WHITE, size=12),
                            bgcolor=self.PRIORITY_COLORS.get(priority, "#777"),
                            border_radius=4,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(status, color=ft.Colors.WHITE, size=12),
                            bgcolor=self.STATUS_COLORS.get(status, "#777"),
                            border_radius=4,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )
                    ),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_size=18,
                                    on_click=lambda e, q=query: self._edit_query(q),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_size=18,
                                    icon_color=ft.Colors.ERROR,
                                    on_click=lambda e, q=query: self._delete_query(q),
                                ),
                            ],
                            spacing=0,
                        )
                    ),
                ],
            )
            self.queries_table.rows.append(row)

    def _update_stats(self, queries: List[Dict]):
        """Met à jour les statistiques."""
        self.stats_row.controls.clear()

        total = len(queries)
        open_count = sum(1 for q in queries if q.get("status") == "Open")
        answered = sum(1 for q in queries if q.get("status") == "Answered")
        closed = sum(1 for q in queries if q.get("status") == "Closed")
        high_priority = sum(1 for q in queries if q.get("priority") == "High" and q.get("status") != "Closed")

        stats = [
            ("Total", total, ft.Colors.PRIMARY),
            ("Open", open_count, "#d9534f"),
            ("Answered", answered, "#f0ad4e"),
            ("Closed", closed, "#5cb85c"),
            ("High Priority", high_priority, "#d9534f"),
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
        self._load_queries(search=self.search_field.value, status_filter=self.status_filter.value)
        if self.page:
            self.queries_table.update()
            self.stats_row.update()

    def _on_filter_change(self, e):
        self._load_queries(search=self.search_field.value, status_filter=e.data)
        if self.page:
            self.queries_table.update()
            self.stats_row.update()

    def _add_query(self, e):
        patients = self.patient_queries.get_all()

        def on_save(data):
            try:
                self.query_queries.create(**data)
                self._load_queries(self.search_field.value, self.status_filter.value)
                if self.page:
                    self.queries_table.update()
                    self.stats_row.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = QueryDialog(on_save=on_save, patients=patients)
        self.page.open(dialog)

    def _edit_query(self, query: Dict):
        patients = self.patient_queries.get_all()

        def on_save(data):
            try:
                self.query_queries.update(data["id"], **{k: v for k, v in data.items() if k != "id"})
                self._load_queries(self.search_field.value, self.status_filter.value)
                if self.page:
                    self.queries_table.update()
                    self.stats_row.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = QueryDialog(on_save=on_save, patients=patients, query=query)
        self.page.open(dialog)

    def _delete_query(self, query: Dict):
        def confirm(e):
            try:
                self.query_queries.delete(query["id"])
                self._load_queries(self.search_field.value, self.status_filter.value)
                if self.page:
                    self.queries_table.update()
                    self.stats_row.update()
                dialog.open = False
                self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        def cancel(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Delete Query"),
            content=ft.Text(f"Delete query for field '{query.get('field_name')}'?"),
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=cancel),
                ft.Button(content=ft.Text("Delete"), on_click=confirm, bgcolor=ft.Colors.ERROR),
            ],
        )
        self.page.open(dialog)
