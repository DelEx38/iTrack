# -*- coding: utf-8 -*-
"""
Gestion des queries (data management).
"""

import asyncio
import flet as ft
from typing import Optional, Dict, List
from src.theme import AppColors, Typography, Spacing, Radius
from src.components import StatusBadge, StatChip, ConfirmDialog, AppTable


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
            border_radius=Radius.INPUT,
        )

        # Champ / Variable
        self.field_field = ft.TextField(
            label="Field / Variable *",
            value=query.get("field_name", "") if query else "",
            autofocus=True,
            border_radius=Radius.INPUT,
        )

        # Description
        self.description_field = ft.TextField(
            label="Query Description *",
            value=query.get("description", "") if query else "",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_radius=Radius.INPUT,
        )

        # Priorité
        self.priority_dropdown = ft.Dropdown(
            label="Priority",
            options=[ft.DropdownOption(key=p, text=p) for p in self.PRIORITIES],
            value=query.get("priority", "Medium") if query else "Medium",
            width=150,
            border_radius=Radius.INPUT,
        )

        # Statut
        self.status_dropdown = ft.Dropdown(
            label="Status",
            options=[ft.DropdownOption(key=s, text=s) for s in self.STATUSES],
            value=query.get("status", "Open") if query else "Open",
            width=150,
            border_radius=Radius.INPUT,
        )

        # Réponse
        self.response_field = ft.TextField(
            label="Response",
            value=query.get("response", "") if query else "",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_radius=Radius.INPUT,
        )

        content = ft.Column(
            [
                self.patient_dropdown,
                self.field_field,
                self.description_field,
                ft.Row([self.priority_dropdown, self.status_dropdown], spacing=Spacing.SM),
                self.response_field,
            ],
            spacing=Spacing.MD,
            tight=True,
            width=450,
        )

        super().__init__(
            title=ft.Text("Edit Query" if query else "New Query", **Typography.H4),
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

    STATUSES = ["Open", "Answered", "Closed"]

    PRIORITY_COLORS = {
        "Low": AppColors.INFO,
        "Medium": AppColors.WARNING,
        "High": AppColors.ERROR,
    }

    def __init__(self, patient_queries, query_queries):
        self.patient_queries = patient_queries
        self.query_queries = query_queries

        # Titre
        title = ft.Text("Data Queries", **Typography.H2)

        # Bouton ajouter
        add_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("New Query")],
                spacing=Spacing.XS,
            ),
            on_click=self._add_query,
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

        # Filtre statut
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
        )

        # Stats
        self.stats_row = ft.Row(spacing=Spacing.SM)

        # Tableau
        self.queries_table = AppTable(
            columns=["Patient", "Field", "Description", "Priority", "Status", "Actions"],
        )

        content = ft.Column(
            [
                header,
                ft.Container(height=Spacing.SM),
                self.stats_row,
                ft.Container(height=Spacing.SM),
                self.queries_table,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(content=content, padding=Spacing.PAGE_PADDING, expand=True, alignment=ft.Alignment.TOP_LEFT)

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
        rows = []
        for query in queries:
            patient = patients.get(query["patient_id"], {})
            status = query.get("status", "Open")
            priority = query.get("priority", "Medium")

            priority_badge = ft.Container(
                content=ft.Text(priority, **Typography.BADGE, color=AppColors.TEXT_ON_PRIMARY),
                bgcolor=self.PRIORITY_COLORS.get(priority, AppColors.NEUTRAL),
                border_radius=Radius.BADGE,
                padding=Spacing.badge(),
            )
            desc = query.get("description", "")
            rows.append([
                ft.Text(patient.get("patient_number", "?"), **Typography.TABLE_CELL),
                ft.Text(query.get("field_name", ""), size=13, weight=ft.FontWeight.BOLD),
                ft.Text(desc[:50] + "..." if len(desc) > 50 else desc, **Typography.TABLE_CELL),
                priority_badge,
                StatusBadge.query_status(status),
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
                            icon_color=AppColors.ERROR,
                            on_click=lambda e, q=query: self._delete_query(q),
                        ),
                    ],
                    spacing=0,
                ),
            ])
        self.queries_table.set_rows(rows)

    def _update_stats(self, queries: List[Dict]):
        """Met à jour les statistiques."""
        self.stats_row.controls.clear()

        total = len(queries)
        open_count = sum(1 for q in queries if q.get("status") == "Open")
        answered = sum(1 for q in queries if q.get("status") == "Answered")
        closed = sum(1 for q in queries if q.get("status") == "Closed")
        high_priority = sum(1 for q in queries if q.get("priority") == "High" and q.get("status") != "Closed")

        self.stats_row.controls.extend([
            StatChip("Total", total, AppColors.INFO),
            StatChip("Open", open_count, AppColors.ERROR),
            StatChip("Answered", answered, AppColors.WARNING),
            StatChip("Closed", closed, AppColors.SUCCESS),
            StatChip("High Priority", high_priority, AppColors.ERROR),
        ])

    async def _on_search(self, e):
        term = e.data
        await asyncio.sleep(0.25)
        if self.search_field.value != term:
            return
        self._load_queries(search=self.search_field.value, status_filter=self.status_filter.value)
        if self.page:
            self.page.update()

    def _on_filter_change(self, e):
        self._load_queries(search=self.search_field.value, status_filter=e.data)
        if self.page:
            self.page.update()

    def _add_query(self, e):
        patients = self.patient_queries.get_all()

        def on_save(data):
            try:
                self.query_queries.create(**data)
                self._load_queries(self.search_field.value, self.status_filter.value)
                if self.page:
                    self.page.update()
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
                    self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = QueryDialog(on_save=on_save, patients=patients, query=query)
        self.page.open(dialog)

    def _delete_query(self, query: Dict):
        def on_confirm():
            try:
                self.query_queries.delete(query["id"])
                self._load_queries(self.search_field.value, self.status_filter.value)
                if self.page:
                    self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        ConfirmDialog(
            title="Delete Query",
            message=f"Delete query for field '{query.get('field_name')}'?",
            confirm_text="Delete",
            on_confirm=on_confirm,
            danger=True,
        ).show(self.page)
