# -*- coding: utf-8 -*-
"""
Vue Audit Trail - historique des modifications GCP.
"""

import flet as ft
from typing import Optional, Dict
from src.database.audit import AuditService
from src.theme import AppColors, Typography, Spacing, Radius
from src.components import StatChip, SectionHeader, EmptyState, AppTable


# Couleurs par action
_ACTION_COLORS = {
    "CREATE": AppColors.SUCCESS,
    "UPDATE": AppColors.WARNING if hasattr(AppColors, "WARNING") else "#F59E0B",
    "DELETE": AppColors.ERROR,
}

# Labels lisibles pour les tables
_TABLE_LABELS = {
    "patients":       "Patient",
    "visits":         "Visit",
    "adverse_events": "Adverse Event",
    "queries":        "Query",
    "consents":       "Consent",
}


class AuditView(ft.Container):
    """Vue de l'historique des modifications (audit trail)."""

    def __init__(self, db_connection):
        self.conn = db_connection

        # Filtres
        self._table_filter: Optional[str] = None
        self._action_filter: Optional[str] = None
        self._search_term: str = ""

        # Champ de recherche
        self.search_field = ft.TextField(
            hint_text="Search in values...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=Radius.INPUT,
            height=40,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
            on_change=self._on_search_change,
            expand=True,
        )

        # Filtres table
        self.table_dd = ft.Dropdown(
            label="Entity",
            options=[ft.DropdownOption(key="", text="All entities")] + [
                ft.DropdownOption(key=k, text=v)
                for k, v in _TABLE_LABELS.items()
            ],
            value="",
            on_select=self._on_table_filter,
            width=160,
            dense=True,
            border_radius=Radius.INPUT,
        )

        # Filtre action
        self.action_dd = ft.Dropdown(
            label="Action",
            options=[
                ft.DropdownOption(key="", text="All actions"),
                ft.DropdownOption(key="CREATE", text="Create"),
                ft.DropdownOption(key="UPDATE", text="Update"),
                ft.DropdownOption(key="DELETE", text="Delete"),
            ],
            value="",
            on_select=self._on_action_filter,
            width=140,
            dense=True,
            border_radius=Radius.INPUT,
        )

        # Bouton refresh
        refresh_btn = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Refresh",
            on_click=lambda e: self._refresh(),
        )

        toolbar = ft.Row(
            [self.search_field, self.table_dd, self.action_dd, refresh_btn],
            spacing=Spacing.SM,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Stat chips
        self.chip_total  = StatChip(label="Total", value="0", color=AppColors.INFO)
        self.chip_create = StatChip(label="Creates", value="0", color=AppColors.SUCCESS)
        self.chip_update = StatChip(label="Updates", value="0", color="#F59E0B")
        self.chip_delete = StatChip(label="Deletes", value="0", color=AppColors.ERROR)

        stats_row = ft.Row(
            [self.chip_total, self.chip_create, self.chip_update, self.chip_delete],
            spacing=Spacing.SM,
        )

        # Container de la table
        self.table_container = ft.Container(expand=True)

        content = ft.Column(
            [
                ft.Text("Audit Trail", **Typography.H2),
                ft.Container(height=Spacing.SM),
                stats_row,
                ft.Container(height=Spacing.SM),
                toolbar,
                ft.Container(height=Spacing.SM),
                self.table_container,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(
            content=content,
            padding=Spacing.PAGE_PADDING,
            expand=True,
            alignment=ft.Alignment.TOP_LEFT,
        )

        self._refresh()

    # ------------------------------------------------------------------
    # Callbacks filtres
    # ------------------------------------------------------------------

    def _on_search_change(self, e):
        self._search_term = e.control.value or ""
        self._refresh()

    def _on_table_filter(self, e):
        self._table_filter = e.control.value or None
        self._refresh()

    def _on_action_filter(self, e):
        self._action_filter = e.control.value or None
        self._refresh()

    # ------------------------------------------------------------------
    # Chargement et affichage
    # ------------------------------------------------------------------

    def _refresh(self) -> None:
        """Recharge et affiche les entrées d'audit."""
        logs = AuditService.get_logs(
            self.conn,
            limit=500,
            table_filter=self._table_filter or None,
            action_filter=self._action_filter or None,
            search=self._search_term or None,
        )

        # Mettre à jour les chips
        all_logs = AuditService.get_logs(self.conn, limit=10000)
        self.chip_total.value_text.value  = str(len(all_logs))
        self.chip_create.value_text.value = str(sum(1 for l in all_logs if l["action"] == "CREATE"))
        self.chip_update.value_text.value = str(sum(1 for l in all_logs if l["action"] == "UPDATE"))
        self.chip_delete.value_text.value = str(sum(1 for l in all_logs if l["action"] == "DELETE"))

        if not logs:
            self.table_container.content = EmptyState(
                title="No audit entries",
                description="Changes to patients, visits and adverse events will appear here",
                icon=ft.Icons.HISTORY,
            )
        else:
            self.table_container.content = self._build_table(logs)

        try:
            if self.page:
                self.table_container.update()
                self.chip_total.update()
                self.chip_create.update()
                self.chip_update.update()
                self.chip_delete.update()
        except RuntimeError:
            pass

    def _build_table(self, logs) -> AppTable:
        """Construit l'AppTable à partir des entrées d'audit."""
        table = AppTable(
            columns=["Date/Time", "Action", "Entity", "Record ID", "Field", "Old Value", "New Value"],
        )
        rows = []
        for entry in logs:
            action    = entry.get("action", "")
            table_name = entry.get("table_name", "")
            field     = entry.get("field_name") or ""
            old_val   = entry.get("old_value") or ""
            new_val   = entry.get("new_value") or ""
            changed_at = str(entry.get("changed_at", ""))[:16]
            record_id  = entry.get("record_id", "")

            action_color = _ACTION_COLORS.get(action, AppColors.TEXT_SECONDARY)
            action_badge = ft.Container(
                content=ft.Text(
                    action,
                    size=10,
                    weight=ft.FontWeight.BOLD,
                    color=AppColors.TEXT_ON_PRIMARY,
                ),
                bgcolor=action_color,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                border_radius=4,
            )

            rows.append([
                ft.Text(changed_at, **Typography.TABLE_CELL, size=11),
                action_badge,
                ft.Text(_TABLE_LABELS.get(table_name, table_name), **Typography.TABLE_CELL),
                ft.Text(str(record_id), **Typography.TABLE_CELL),
                ft.Text(field, **Typography.TABLE_CELL, color=AppColors.TEXT_SECONDARY),
                ft.Text(_truncate(old_val, 30), **Typography.TABLE_CELL, color=AppColors.ERROR),
                ft.Text(_truncate(new_val, 30), **Typography.TABLE_CELL, color=AppColors.SUCCESS),
            ])

        table.set_rows(rows)
        return table


def _truncate(text: str, max_len: int = 40) -> str:
    return text if len(text) <= max_len else text[:max_len - 3] + "..."
