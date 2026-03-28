"""
Gestion des visites.
"""

import flet as ft
from typing import Optional, Dict, List
from datetime import datetime, timedelta


class VisitDialog(ft.AlertDialog):
    """Dialogue d'enregistrement de visite."""

    def __init__(self, on_save, visit_config: Dict, patient: Dict, existing_visit: Optional[Dict] = None):
        self.visit_config = visit_config
        self.patient = patient
        self.existing_visit = existing_visit
        self.on_save = on_save

        # Calculer la date cible
        v1_date = patient.get("v1_date")
        target_day = visit_config.get("target_day", 0)
        window_before = visit_config.get("window_before", 0)
        window_after = visit_config.get("window_after", 0)

        target_date = None
        window_start = None
        window_end = None

        if v1_date and target_day > 0:
            if isinstance(v1_date, str):
                v1_date = datetime.strptime(v1_date, "%Y-%m-%d").date()
            target_date = v1_date + timedelta(days=target_day)
            window_start = target_date - timedelta(days=window_before)
            window_end = target_date + timedelta(days=window_after)

        # Infos
        info_text = f"Patient: {patient.get('patient_number')}\n"
        info_text += f"Visit: {visit_config.get('visit_name')}\n"
        if target_date:
            info_text += f"Target: {target_date} (Day {target_day})\n"
            info_text += f"Window: {window_start} to {window_end}"

        # Champs
        self.date_field = ft.TextField(
            label="Visit Date (YYYY-MM-DD) *",
            value=str(existing_visit.get("visit_date", "")) if existing_visit else "",
            autofocus=True,
        )

        self.status_dropdown = ft.Dropdown(
            label="Status",
            options=[
                ft.DropdownOption(key="Completed", text="Completed"),
                ft.DropdownOption(key="Missed", text="Missed"),
                ft.DropdownOption(key="Pending", text="Pending"),
            ],
            value=existing_visit.get("status", "Completed") if existing_visit else "Completed",
            width=200,
        )

        self.notes_field = ft.TextField(
            label="Notes",
            value=existing_visit.get("notes", "") if existing_visit else "",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )

        content = ft.Column(
            [
                ft.Text(info_text, size=12, color=ft.Colors.GREY_500),
                ft.Divider(),
                self.date_field,
                self.status_dropdown,
                self.notes_field,
            ],
            spacing=15,
            tight=True,
            width=350,
        )

        super().__init__(
            title=ft.Text(f"Record Visit - {visit_config.get('visit_name')}"),
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
        if not self.date_field.value and self.status_dropdown.value != "Missed":
            self.date_field.error_text = "Required"
            self.page.update()
            return

        result = {
            "patient_id": self.patient["id"],
            "visit_config_id": self.visit_config["id"],
            "visit_date": self.date_field.value or None,
            "status": self.status_dropdown.value,
            "notes": self.notes_field.value,
        }

        if self.existing_visit:
            result["id"] = self.existing_visit["id"]

        self.open = False
        self.page.update()
        self.on_save(result)


class VisitsView(ft.Container):
    """Vue de gestion des visites."""

    STATUS_COLORS = {
        "Completed": "#5cb85c",
        "Pending": "#f0ad4e",
        "Missed": "#d9534f",
    }

    def __init__(self, patient_queries, visit_queries):
        self.patient_queries = patient_queries
        self.visit_queries = visit_queries

        # Titre
        title = ft.Text("Visits", size=24, weight=ft.FontWeight.BOLD)

        # Sélecteur de patient
        self.patient_dropdown = ft.Dropdown(
            label="Select Patient",
            options=[],
            width=300,
            on_select=self._on_patient_change,
        )

        # Info patient
        self.patient_info = ft.Text("", size=12, color=ft.Colors.GREY_500)

        header = ft.Row(
            [title, ft.Container(expand=True), self.patient_dropdown],
        )

        # Stats
        self.stats_row = ft.Row(spacing=10)

        # Grille des visites
        self.visits_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Visit", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Day", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Target Date", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actual Date", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Window", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            heading_row_color=ft.Colors.SURFACE_CONTAINER,
        )

        # Légende
        legend = ft.Row(
            [
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=12, height=12, bgcolor="#5cb85c", border_radius=2),
                        ft.Text("In Window", size=12),
                    ], spacing=5),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=12, height=12, bgcolor="#d9534f", border_radius=2),
                        ft.Text("Out of Window", size=12),
                    ], spacing=5),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=12, height=12, bgcolor="#f0ad4e", border_radius=2),
                        ft.Text("Pending", size=12),
                    ], spacing=5),
                ),
            ],
            spacing=20,
        )

        content = ft.Column(
            [
                header,
                self.patient_info,
                ft.Container(height=10),
                self.stats_row,
                ft.Container(height=10),
                legend,
                ft.Container(height=10),
                ft.Container(content=self.visits_table, expand=True),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(content=content, padding=20, expand=True)

        self._load_patients()

    def _load_patients(self):
        """Charge la liste des patients."""
        patients = self.patient_queries.get_all()
        self.patients = {p["id"]: p for p in patients}

        self.patient_dropdown.options = [
            ft.DropdownOption(
                key=str(p["id"]),
                text=f"{p.get('patient_number', '')} - {p.get('status', '')}"
            )
            for p in patients
        ]

        if patients:
            self.patient_dropdown.value = str(patients[0]["id"])
            self._load_visits(patients[0]["id"])

    def _on_patient_change(self, e):
        patient_id = int(e.data)
        self._load_visits(patient_id)
        if self.page:
            self.visits_table.update()
            self.stats_row.update()
            self.patient_info.update()

    def _load_visits(self, patient_id: int):
        """Charge les visites pour un patient."""
        patient = self.patients.get(patient_id)
        if not patient:
            return

        # Info patient
        v1_date = self._get_v1_date(patient_id)
        self.patient_info.value = f"V1 Date: {v1_date or 'Not recorded'}"

        # Charger la config des visites
        visit_configs = self.visit_queries.get_configs()
        visits = self.visit_queries.get_by_patient(patient_id)
        visits_by_config = {v["visit_config_id"]: v for v in visits}

        # Stats
        completed = sum(1 for v in visits if v.get("status") == "Completed")
        in_window = 0
        out_window = 0
        pending = len(visit_configs) - len(visits)

        self.visits_table.rows.clear()

        for config in visit_configs:
            visit = visits_by_config.get(config["id"])
            target_day = config.get("target_day", 0)
            window_before = config.get("window_before", 0)
            window_after = config.get("window_after", 0)

            # Calculer la date cible
            target_date = "-"
            window_check = "-"
            window_color = None

            if v1_date and target_day > 0:
                if isinstance(v1_date, str):
                    v1 = datetime.strptime(v1_date, "%Y-%m-%d").date()
                else:
                    v1 = v1_date
                target = v1 + timedelta(days=target_day)
                target_date = str(target)

                if visit and visit.get("visit_date"):
                    visit_date = visit["visit_date"]
                    if isinstance(visit_date, str):
                        visit_date = datetime.strptime(visit_date, "%Y-%m-%d").date()
                    delta = (visit_date - target).days

                    if -window_before <= delta <= window_after:
                        window_check = f"OK ({delta:+d}d)"
                        window_color = "#5cb85c"
                        in_window += 1
                    else:
                        window_check = f"OUT ({delta:+d}d)"
                        window_color = "#d9534f"
                        out_window += 1

            # Statut
            status = visit.get("status", "Pending") if visit else "Pending"
            status_color = self.STATUS_COLORS.get(status, "#777777")

            # Nom de la visite
            visit_name = config.get("visit_name", "")
            if target_day == 0:
                visit_name += " (REF)"

            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(visit_name, weight=ft.FontWeight.BOLD if target_day == 0 else None)),
                    ft.DataCell(ft.Text(f"D{target_day}" if target_day >= 0 else f"D{target_day}")),
                    ft.DataCell(ft.Text(target_date)),
                    ft.DataCell(ft.Text(str(visit.get("visit_date", "-")) if visit else "-")),
                    ft.DataCell(
                        ft.Text(window_check, color=window_color) if window_color else ft.Text(window_check)
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(status, color=ft.Colors.WHITE, size=12),
                            bgcolor=status_color,
                            border_radius=4,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )
                    ),
                    ft.DataCell(
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_size=18,
                            on_click=lambda e, c=config, v=visit: self._record_visit(c, v),
                            tooltip="Record/Edit",
                        )
                    ),
                ],
            )
            self.visits_table.rows.append(row)

        # Mettre à jour les stats
        self._update_stats(completed, in_window, out_window, pending)

    def _get_v1_date(self, patient_id: int):
        """Récupère la date V1 d'un patient."""
        visits = self.visit_queries.get_by_patient(patient_id)
        for v in visits:
            config = self.visit_queries.get_config(v.get("visit_config_id"))
            if config and config.get("target_day") == 0:
                return v.get("visit_date")
        return None

    def _update_stats(self, completed: int, in_window: int, out_window: int, pending: int):
        """Met à jour les statistiques."""
        self.stats_row.controls.clear()

        stats = [
            ("Completed", completed, "#5cb85c"),
            ("In Window", in_window, "#5cb85c"),
            ("Out of Window", out_window, "#d9534f"),
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

    def _record_visit(self, config: Dict, existing_visit: Optional[Dict]):
        """Ouvre le dialogue d'enregistrement de visite."""
        patient_id = int(self.patient_dropdown.value)
        patient = self.patients.get(patient_id)

        # Ajouter la date V1 au patient
        patient["v1_date"] = self._get_v1_date(patient_id)

        def on_save(data):
            try:
                if existing_visit:
                    self.visit_queries.update(data["id"], **{k: v for k, v in data.items() if k != "id"})
                else:
                    self.visit_queries.record_visit(**data)
                self._load_visits(patient_id)
                if self.page:
                    self.visits_table.update()
                    self.stats_row.update()
            except Exception as ex:
                self.page.open(ft.SnackBar(content=ft.Text(f"Error: {ex}")))

        dialog = VisitDialog(on_save=on_save, visit_config=config, patient=patient, existing_visit=existing_visit)
        self.page.open(dialog)
