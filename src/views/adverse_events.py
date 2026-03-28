"""
Gestion des événements indésirables (EI/EIG).
"""

import flet as ft
from typing import Optional, Dict, List
from datetime import datetime


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
        )

        # Terme
        self.term_field = ft.TextField(
            label="AE Term *",
            value=ae.get("ae_term", "") if ae else "",
            autofocus=True,
        )

        # Dates
        self.start_date_field = ft.TextField(
            label="Start Date (YYYY-MM-DD) *",
            value=str(ae.get("start_date", "")) if ae else "",
        )
        self.end_date_field = ft.TextField(
            label="End Date (YYYY-MM-DD)",
            value=str(ae.get("end_date", "") or "") if ae else "",
        )

        # Sévérité
        self.severity_dropdown = ft.Dropdown(
            label="Severity",
            options=[ft.DropdownOption(key=s, text=s) for s in self.SEVERITIES],
            value=ae.get("severity", "Mild") if ae else "Mild",
            width=150,
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
        )

        # Outcome
        self.outcome_dropdown = ft.Dropdown(
            label="Outcome",
            options=[ft.DropdownOption(key=o, text=o) for o in self.OUTCOMES],
            value=ae.get("outcome", "Recovering") if ae else "Recovering",
            width=180,
        )

        # Causalité
        self.causality_dropdown = ft.Dropdown(
            label="Causality",
            options=[ft.DropdownOption(key=c, text=c) for c in self.CAUSALITIES],
            value=ae.get("causality", "Unknown") if ae else "Unknown",
            width=180,
        )

        # Notes
        self.notes_field = ft.TextField(
            label="Notes",
            value=ae.get("notes", "") if ae else "",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )

        content = ft.Column(
            [
                self.patient_dropdown,
                self.term_field,
                ft.Row([self.start_date_field, self.end_date_field], spacing=10),
                ft.Row([self.severity_dropdown, self.outcome_dropdown, self.causality_dropdown], spacing=10),
                ft.Row([self.sae_switch, self.reporting_date_field], spacing=20),
                self.notes_field,
            ],
            spacing=15,
            tight=True,
            width=500,
        )

        super().__init__(
            title=ft.Text("Edit Adverse Event" if ae else "New Adverse Event"),
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

    SEVERITY_COLORS = {
        "Mild": "#5cb85c",
        "Moderate": "#f0ad4e",
        "Severe": "#d9534f",
    }

    OUTCOME_COLORS = {
        "Recovered": "#5cb85c",
        "Recovering": "#5bc0de",
        "Not Recovered": "#f0ad4e",
        "Fatal": "#d9534f",
        "Unknown": "#777777",
    }

    def __init__(self, patient_queries, ae_queries):
        self.patient_queries = patient_queries
        self.ae_queries = ae_queries

        # Titre
        title = ft.Text("Adverse Events", size=24, weight=ft.FontWeight.BOLD)

        # Bouton ajouter
        add_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD, size=18), ft.Text("Add AE")],
                spacing=8,
            ),
            on_click=self._add_ae,
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

        # Filtre outcome
        self.outcome_filter = ft.Dropdown(
            label="Outcome",
            options=[ft.DropdownOption(key="All", text="All")] +
                    [ft.DropdownOption(key=o, text=o) for o in self.OUTCOME_COLORS.keys()],
            value="All",
            width=150,
            on_select=self._on_filter_change,
        )

        header = ft.Row(
            [title, ft.Container(expand=True), self.search_field, self.outcome_filter, add_btn],
        )

        # Stats
        self.stats_row = ft.Row(spacing=10)

        # Tableau
        self.ae_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Patient", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("AE Term", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Start", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Severity", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("SAE", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Outcome", weight=ft.FontWeight.BOLD)),
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
                ft.Container(content=self.ae_table, expand=True),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(content=content, padding=20, expand=True)

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
        self.ae_table.rows.clear()
        for ae in ae_list:
            patient = patients.get(ae["patient_id"], {})
            severity = ae.get("severity", "Mild")
            outcome = ae.get("outcome", "Unknown")
            is_serious = ae.get("is_serious", False)

            # Indicateur délai SAE
            sae_indicator = "-"
            if is_serious:
                sae_indicator = "SAE"
                if ae.get("reporting_date") and ae.get("start_date"):
                    try:
                        start = datetime.strptime(str(ae["start_date"]), "%Y-%m-%d")
                        reported = datetime.strptime(str(ae["reporting_date"]), "%Y-%m-%d")
                        delta = (reported - start).days
                        if delta <= 1:
                            sae_indicator = "SAE (<24h)"
                        else:
                            sae_indicator = f"SAE (+{delta}d)"
                    except Exception:
                        pass

            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(patient.get("patient_number", "?"))),
                    ft.DataCell(ft.Text(ae.get("ae_term", ""))),
                    ft.DataCell(ft.Text(str(ae.get("start_date", "-")))),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(severity, color=ft.Colors.WHITE, size=12),
                            bgcolor=self.SEVERITY_COLORS.get(severity, "#777"),
                            border_radius=4,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )
                    ),
                    ft.DataCell(
                        ft.Text(
                            sae_indicator,
                            color="#d9534f" if is_serious and "+d" in sae_indicator else None,
                            weight=ft.FontWeight.BOLD if is_serious else None,
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(outcome, color=ft.Colors.WHITE, size=12),
                            bgcolor=self.OUTCOME_COLORS.get(outcome, "#777"),
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
                                    on_click=lambda e, a=ae: self._edit_ae(a),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_size=18,
                                    icon_color=ft.Colors.ERROR,
                                    on_click=lambda e, a=ae: self._delete_ae(a),
                                ),
                            ],
                            spacing=0,
                        )
                    ),
                ],
            )
            self.ae_table.rows.append(row)

    def _update_stats(self, ae_list: List[Dict]):
        """Met à jour les statistiques."""
        self.stats_row.controls.clear()

        total = len(ae_list)
        sae = sum(1 for ae in ae_list if ae.get("is_serious"))
        ongoing = sum(1 for ae in ae_list if ae.get("outcome") in ["Recovering", "Not Recovered"])
        recovered = sum(1 for ae in ae_list if ae.get("outcome") == "Recovered")
        fatal = sum(1 for ae in ae_list if ae.get("outcome") == "Fatal")

        stats = [
            ("Total", total, ft.Colors.PRIMARY),
            ("SAE", sae, "#d9534f"),
            ("Ongoing", ongoing, "#f0ad4e"),
            ("Recovered", recovered, "#5cb85c"),
            ("Fatal", fatal, "#d9534f"),
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
        self._load_ae(search=self.search_field.value, outcome_filter=self.outcome_filter.value)
        if self.page:
            self.ae_table.update()
            self.stats_row.update()

    def _on_filter_change(self, e):
        self._load_ae(search=self.search_field.value, outcome_filter=e.data)
        if self.page:
            self.ae_table.update()
            self.stats_row.update()

    def _add_ae(self, e):
        patients = self.patient_queries.get_all()

        def on_save(data):
            try:
                self.ae_queries.create(**data)
                self._load_ae(self.search_field.value, self.outcome_filter.value)
                if self.page:
                    self.ae_table.update()
                    self.stats_row.update()
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
                    self.ae_table.update()
                    self.stats_row.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = AEDialog(on_save=on_save, patients=patients, ae=ae)
        self.page.open(dialog)

    def _delete_ae(self, ae: Dict):
        def confirm(e):
            try:
                self.ae_queries.delete(ae["id"])
                self._load_ae(self.search_field.value, self.outcome_filter.value)
                if self.page:
                    self.ae_table.update()
                    self.stats_row.update()
                dialog.open = False
                self.page.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        def cancel(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Delete AE"),
            content=ft.Text(f"Delete adverse event '{ae.get('ae_term')}'?"),
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=cancel),
                ft.Button(content=ft.Text("Delete"), on_click=confirm, bgcolor=ft.Colors.ERROR),
            ],
        )
        self.page.open(dialog)
