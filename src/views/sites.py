"""
Gestion des sites / centres investigateurs.
"""

import flet as ft
from typing import Optional, Dict, List


class SiteDialog(ft.AlertDialog):
    """Dialogue d'ajout/modification de site."""

    STATUSES = ["Active", "On Hold", "Closed"]

    def __init__(self, on_save, db, site: Optional[Dict] = None, study_site: Optional[Dict] = None):
        self.site = site
        self.study_site = study_site
        self.on_save = on_save
        self.result = None

        # Champs du site
        self.number_field = ft.TextField(
            label="Site Number *",
            value=site.get("site_number", "") if site else "",
            autofocus=True,
        )
        self.name_field = ft.TextField(
            label="Site Name *",
            value=site.get("name", "") if site else "",
        )
        self.city_field = ft.TextField(
            label="City",
            value=site.get("city", "") if site else "",
        )
        self.country_field = ft.TextField(
            label="Country",
            value=site.get("country", "") if site else "",
        )

        # Champs spécifiques à l'étude
        self.status_dropdown = ft.Dropdown(
            label="Status",
            options=[ft.DropdownOption(key=s, text=s) for s in self.STATUSES],
            value=study_site.get("status", "Active") if study_site else "Active",
            width=200,
        )
        self.pi_field = ft.TextField(
            label="Principal Investigator",
            value=study_site.get("principal_investigator", "") if study_site else "",
        )
        self.target_field = ft.TextField(
            label="Recruitment Target",
            value=str(study_site.get("target_patients", "") or "") if study_site else "",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        content = ft.Column(
            [
                ft.Text("Site Information", weight=ft.FontWeight.BOLD),
                self.number_field,
                self.name_field,
                ft.Row([self.city_field, self.country_field], spacing=10),
                ft.Divider(),
                ft.Text("Study-specific Information", weight=ft.FontWeight.BOLD),
                self.status_dropdown,
                self.pi_field,
                self.target_field,
            ],
            spacing=10,
            tight=True,
            width=400,
        )

        super().__init__(
            title=ft.Text("Edit Site" if site else "New Site"),
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
        if not self.number_field.value or not self.name_field.value:
            if not self.number_field.value:
                self.number_field.error_text = "Required"
            if not self.name_field.value:
                self.name_field.error_text = "Required"
            self.page.update()
            return

        self.result = {
            "site": {
                "site_number": self.number_field.value,
                "name": self.name_field.value,
                "city": self.city_field.value,
                "country": self.country_field.value,
            },
            "study_site": {
                "status": self.status_dropdown.value,
                "principal_investigator": self.pi_field.value,
                "target_patients": int(self.target_field.value) if self.target_field.value else None,
            },
        }

        if self.site:
            self.result["site"]["id"] = self.site["id"]
        if self.study_site:
            self.result["study_site"]["id"] = self.study_site["id"]

        self.open = False
        self.page.update()
        self.on_save(self.result)


class SitesView(ft.Container):
    """Vue de gestion des sites."""

    STATUS_COLORS = {
        "Active": "#5cb85c",
        "On Hold": "#f0ad4e",
        "Closed": "#d9534f",
    }

    def __init__(self, db, current_study: Optional[Dict] = None):
        self.db = db
        self.current_study = current_study

        # Titre
        title = ft.Text("Sites", size=24, weight=ft.FontWeight.BOLD)

        # Bouton ajouter
        add_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("Add Site")],
                spacing=8,
            ),
            on_click=self._add_site,
            bgcolor=ft.Colors.PRIMARY,
            color=ft.Colors.ON_PRIMARY,
        )

        # Barre de recherche
        self.search_field = ft.TextField(
            hint_text="Search sites...",
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
        )

        # Stats
        self.stats_row = ft.Row(spacing=10)

        # Tableau des sites
        self.sites_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Site #", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("City", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("PI", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Patients", weight=ft.FontWeight.BOLD)),
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
                ft.Container(content=self.sites_table, expand=True),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(content=content, padding=20, expand=True)

        self._load_sites()

    def _load_sites(self, search: str = "", status_filter: str = "All"):
        """Charge les sites depuis la base."""
        if not self.current_study:
            return

        study_id = self.current_study["id"]
        sites = self.db.get_study_sites(study_id)

        # Filtrer
        if search:
            search_lower = search.lower()
            sites = [
                s for s in sites
                if search_lower in (s.get("site_number", "") or "").lower()
                or search_lower in (s.get("name", "") or "").lower()
                or search_lower in (s.get("city", "") or "").lower()
            ]

        if status_filter != "All":
            sites = [s for s in sites if s.get("status") == status_filter]

        # Mettre à jour les stats
        self._update_stats(sites)

        # Mettre à jour le tableau
        self.sites_table.rows.clear()
        for site in sites:
            status = site.get("status", "Active")
            status_color = self.STATUS_COLORS.get(status, "#777777")

            # Compter les patients
            patient_count = self._get_patient_count(site.get("site_id"))
            target = site.get("target_patients")
            progress_text = f"{patient_count}"
            if target:
                progress_text = f"{patient_count}/{target}"

            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(site.get("site_number", ""))),
                    ft.DataCell(ft.Text(site.get("name", ""))),
                    ft.DataCell(ft.Text(site.get("city", "") or "-")),
                    ft.DataCell(ft.Text(site.get("principal_investigator", "") or "-")),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(status, color=ft.Colors.WHITE, size=12),
                            bgcolor=status_color,
                            border_radius=4,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )
                    ),
                    ft.DataCell(ft.Text(progress_text)),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_size=18,
                                    on_click=lambda e, s=site: self._edit_site(s),
                                    tooltip="Edit",
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_size=18,
                                    icon_color=ft.Colors.ERROR,
                                    on_click=lambda e, s=site: self._remove_site(s),
                                    tooltip="Remove from study",
                                ),
                            ],
                            spacing=0,
                        )
                    ),
                ],
            )
            self.sites_table.rows.append(row)

    def _get_patient_count(self, site_id: int) -> int:
        """Compte les patients d'un site."""
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM patients WHERE site_id = ?", (site_id,))
            return cursor.fetchone()[0]
        except Exception:
            return 0

    def _update_stats(self, sites: List[Dict]):
        """Met à jour les statistiques."""
        self.stats_row.controls.clear()

        total = len(sites)
        active = sum(1 for s in sites if s.get("status") == "Active")
        on_hold = sum(1 for s in sites if s.get("status") == "On Hold")
        closed = sum(1 for s in sites if s.get("status") == "Closed")

        stats = [
            ("Total", total, ft.Colors.PRIMARY),
            ("Active", active, "#5cb85c"),
            ("On Hold", on_hold, "#f0ad4e"),
            ("Closed", closed, "#d9534f"),
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
        self._load_sites(search=self.search_field.value, status_filter=self.status_filter.value)
        if self.page:
            self.sites_table.update()
            self.stats_row.update()

    def _on_filter_change(self, e):
        self._load_sites(search=self.search_field.value, status_filter=e.data)
        if self.page:
            self.sites_table.update()
            self.stats_row.update()

    def _add_site(self, e):
        def on_save(data):
            try:
                # Créer le site
                site_id = self.db.create_site(**data["site"])
                # Ajouter à l'étude
                self.db.add_site_to_study(
                    self.current_study["id"],
                    site_id,
                    **data["study_site"]
                )
                self._load_sites(self.search_field.value, self.status_filter.value)
                if self.page:
                    self.sites_table.update()
                    self.stats_row.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = SiteDialog(on_save=on_save, db=self.db)
        self.page.open(dialog)

    def _edit_site(self, site: Dict):
        def on_save(data):
            try:
                self.db.update_site(site["site_id"], **data["site"])
                self.db.update_study_site(site["id"], **data["study_site"])
                self._load_sites(self.search_field.value, self.status_filter.value)
                if self.page:
                    self.sites_table.update()
                    self.stats_row.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        site_data = {
            "id": site.get("site_id"),
            "site_number": site.get("site_number"),
            "name": site.get("name"),
            "city": site.get("city"),
            "country": site.get("country"),
        }
        study_site_data = {
            "id": site.get("id"),
            "status": site.get("status"),
            "principal_investigator": site.get("principal_investigator"),
            "target_patients": site.get("target_patients"),
        }

        dialog = SiteDialog(on_save=on_save, db=self.db, site=site_data, study_site=study_site_data)
        self.page.open(dialog)

    def _remove_site(self, site: Dict):
        def confirm_remove(e):
            try:
                self.db.remove_site_from_study(self.current_study["id"], site["site_id"])
                self._load_sites(self.search_field.value, self.status_filter.value)
                if self.page:
                    self.sites_table.update()
                    self.stats_row.update()
                dialog.open = False
                self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        def cancel(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Remove Site"),
            content=ft.Text(f"Remove site {site.get('site_number')} from this study?"),
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=cancel),
                ft.Button(content=ft.Text("Remove"), on_click=confirm_remove, bgcolor=ft.Colors.ERROR),
            ],
        )
        self.page.open(dialog)
