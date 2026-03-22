"""
Gestion des événements indésirables (EI/EIG).
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict, Any, List
from datetime import date, timedelta


def parse_date(date_str: str) -> Optional[date]:
    """Parse une date au format YYYY-MM-DD."""
    if not date_str or len(date_str) < 10:
        return None
    try:
        parts = date_str.split("-")
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        return None


class AEDialog(ctk.CTkToplevel):
    """Dialogue pour déclarer/modifier un EI."""

    def __init__(self, parent, patient: Dict, ae_queries, ae_data: Optional[Dict] = None):
        super().__init__(parent)

        self.patient = patient
        self.ae_queries = ae_queries
        self.ae_data = ae_data
        self.result = None

        self.title("Edit Adverse Event" if ae_data else "New Adverse Event")
        self.geometry("550x650")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 550) // 2
        y = (self.winfo_screenheight() - 650) // 2
        self.geometry(f"+{x}+{y}")

        self._create_form()

        if ae_data:
            self._fill_form(ae_data)

    def _create_form(self) -> None:
        """Crée le formulaire."""
        # Info patient
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            info_frame,
            text=f"Patient: {self.patient['patient_number']}",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=5)

        # Formulaire scrollable
        self.form_frame = ctk.CTkScrollableFrame(self, height=450)
        self.form_frame.pack(fill="both", expand=True, padx=20)

        # Date de début
        ctk.CTkLabel(self.form_frame, text="Start Date (YYYY-MM-DD) *").pack(anchor="w", pady=(10, 5))
        self.entry_start = ctk.CTkEntry(self.form_frame, width=150)
        self.entry_start.pack(anchor="w")

        # Date de fin
        ctk.CTkLabel(self.form_frame, text="End Date (YYYY-MM-DD)").pack(anchor="w", pady=(10, 5))
        self.entry_end = ctk.CTkEntry(self.form_frame, width=150)
        self.entry_end.pack(anchor="w")

        # Description
        ctk.CTkLabel(self.form_frame, text="Description *").pack(anchor="w", pady=(10, 5))
        self.text_description = ctk.CTkTextbox(self.form_frame, height=80, width=450)
        self.text_description.pack(anchor="w")

        # Sévérité
        ctk.CTkLabel(self.form_frame, text="Severity").pack(anchor="w", pady=(10, 5))
        self.combo_severity = ctk.CTkComboBox(
            self.form_frame,
            values=["Mild", "Moderate", "Severe"],
            width=150
        )
        self.combo_severity.pack(anchor="w")

        # Sérieux (EIG)
        self.var_serious = ctk.BooleanVar(value=False)
        self.check_serious = ctk.CTkCheckBox(
            self.form_frame,
            text="Serious Adverse Event (SAE)",
            variable=self.var_serious,
            command=self._on_serious_change
        )
        self.check_serious.pack(anchor="w", pady=(15, 5))

        # Critères de gravité (si SAE)
        self.seriousness_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.seriousness_frame.pack(anchor="w", fill="x")

        ctk.CTkLabel(self.seriousness_frame, text="Seriousness Criteria").pack(anchor="w", pady=(5, 5))
        self.combo_seriousness = ctk.CTkComboBox(
            self.seriousness_frame,
            values=[
                "Death",
                "Life-threatening",
                "Hospitalization",
                "Prolonged hospitalization",
                "Disability",
                "Congenital anomaly",
                "Other medically important"
            ],
            width=250
        )
        self.combo_seriousness.pack(anchor="w")

        # Date de déclaration SAE
        ctk.CTkLabel(self.seriousness_frame, text="Reporting Date (YYYY-MM-DD)").pack(anchor="w", pady=(10, 5))
        self.entry_reporting = ctk.CTkEntry(self.seriousness_frame, width=150)
        self.entry_reporting.pack(anchor="w")

        # Indicateur délai
        self.delay_label = ctk.CTkLabel(self.seriousness_frame, text="", text_color="gray")
        self.delay_label.pack(anchor="w", pady=5)
        self.entry_reporting.bind("<KeyRelease>", self._check_reporting_delay)

        self.seriousness_frame.pack_forget()  # Caché par défaut

        # Causalité
        ctk.CTkLabel(self.form_frame, text="Causality").pack(anchor="w", pady=(10, 5))
        self.combo_causality = ctk.CTkComboBox(
            self.form_frame,
            values=["Not related", "Unlikely", "Possible", "Probable", "Definite"],
            width=150
        )
        self.combo_causality.pack(anchor="w")

        # Action prise
        ctk.CTkLabel(self.form_frame, text="Action Taken").pack(anchor="w", pady=(10, 5))
        self.combo_action = ctk.CTkComboBox(
            self.form_frame,
            values=[
                "None",
                "Dose reduced",
                "Drug interrupted",
                "Drug withdrawn",
                "Concomitant medication",
                "Other"
            ],
            width=200
        )
        self.combo_action.pack(anchor="w")

        # Issue
        ctk.CTkLabel(self.form_frame, text="Outcome").pack(anchor="w", pady=(10, 5))
        self.combo_outcome = ctk.CTkComboBox(
            self.form_frame,
            values=[
                "Ongoing",
                "Recovered",
                "Recovered with sequelae",
                "Not recovered",
                "Fatal",
                "Unknown"
            ],
            width=200
        )
        self.combo_outcome.pack(anchor="w")

        # Boutons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="transparent",
            border_width=1
        ).pack(side="left")

        ctk.CTkButton(
            btn_frame,
            text="Save",
            command=self._save
        ).pack(side="right")

    def _on_serious_change(self) -> None:
        """Affiche/cache les critères de gravité."""
        if self.var_serious.get():
            self.seriousness_frame.pack(anchor="w", fill="x", after=self.check_serious)
        else:
            self.seriousness_frame.pack_forget()

    def _check_reporting_delay(self, event=None) -> None:
        """Vérifie le délai de déclaration SAE (< 24h requis)."""
        start_str = self.entry_start.get().strip()
        report_str = self.entry_reporting.get().strip()

        start_date = parse_date(start_str)
        report_date = parse_date(report_str)

        if start_date and report_date:
            delta = (report_date - start_date).days
            if delta <= 1:
                self.delay_label.configure(
                    text=f"Reported within 24h (Day {delta})",
                    text_color="#5cb85c"
                )
            else:
                self.delay_label.configure(
                    text=f"ALERT: Reported after {delta} days (> 24h)",
                    text_color="#d9534f"
                )
        else:
            self.delay_label.configure(text="", text_color="gray")

    def _fill_form(self, data: Dict) -> None:
        """Remplit le formulaire avec les données existantes."""
        if data.get("start_date"):
            self.entry_start.insert(0, str(data["start_date"]))
        if data.get("end_date"):
            self.entry_end.insert(0, str(data["end_date"]))
        if data.get("description"):
            self.text_description.insert("1.0", data["description"])
        if data.get("severity"):
            self.combo_severity.set(data["severity"])
        if data.get("is_serious"):
            self.var_serious.set(True)
            self._on_serious_change()
        if data.get("seriousness"):
            self.combo_seriousness.set(data["seriousness"])
        if data.get("reporting_date"):
            self.entry_reporting.insert(0, str(data["reporting_date"]))
            self._check_reporting_delay()
        if data.get("causality"):
            self.combo_causality.set(data["causality"])
        if data.get("action_taken"):
            self.combo_action.set(data["action_taken"])
        if data.get("outcome"):
            self.combo_outcome.set(data["outcome"])

    def _save(self) -> None:
        """Sauvegarde l'EI."""
        start_date = parse_date(self.entry_start.get().strip())
        if not start_date:
            messagebox.showerror("Error", "Start date is required (YYYY-MM-DD)")
            return

        description = self.text_description.get("1.0", "end-1c").strip()
        if not description:
            messagebox.showerror("Error", "Description is required")
            return

        self.result = {
            "patient_id": self.patient["id"],
            "start_date": start_date,
            "end_date": parse_date(self.entry_end.get().strip()),
            "description": description,
            "severity": self.combo_severity.get() or None,
            "seriousness": self.combo_seriousness.get() if self.var_serious.get() else None,
            "reporting_date": parse_date(self.entry_reporting.get().strip()) if self.var_serious.get() else None,
            "causality": self.combo_causality.get() or None,
            "action_taken": self.combo_action.get() or None,
            "outcome": self.combo_outcome.get() or None,
            "is_serious": self.var_serious.get()
        }

        self.destroy()


class AdverseEventsFrame(ctk.CTkFrame):
    """Frame de gestion des événements indésirables."""

    def __init__(self, parent, patient_queries, ae_queries):
        super().__init__(parent, fg_color="transparent")

        self.patient_queries = patient_queries
        self.ae_queries = ae_queries
        self.selected_patient = None
        self.patients: List[Dict] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Row 3 pour la liste (après stats)

        self._create_header()
        self._create_controls()
        self._create_stats_bar()
        self._create_ae_list()

    def _create_header(self) -> None:
        """Crée l'en-tête."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="Adverse Events",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        # Légende
        legend_frame = ctk.CTkFrame(header, fg_color="transparent")
        legend_frame.grid(row=0, column=2, sticky="e")

        legends = [
            ("Mild", "#5cb85c"),
            ("Moderate", "#f0ad4e"),
            ("Severe", "#d9534f"),
            ("SAE", "#d9534f"),
            ("Ongoing", "#5bc0de"),
            ("Recovered", "#5cb85c"),
        ]

        for text, color in legends:
            lf = ctk.CTkFrame(legend_frame, fg_color="transparent")
            lf.pack(side="left", padx=6)
            ctk.CTkLabel(lf, text="●", text_color=color, width=12).pack(side="left")
            ctk.CTkLabel(lf, text=text, font=ctk.CTkFont(size=11)).pack(side="left")

    def _create_controls(self) -> None:
        """Crée les contrôles."""
        controls = ctk.CTkFrame(self)
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Recherche patient
        ctk.CTkLabel(controls, text="Patient:").pack(side="left", padx=(10, 5))

        self.search_entry = ctk.CTkEntry(
            controls,
            placeholder_text="Search...",
            width=100
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self._on_search)

        # Sélecteur patient
        self.patients = self.patient_queries.get_all()
        patient_list = ["All patients"] + [f"{p['patient_number']}" for p in self.patients]

        self.patient_combo = ctk.CTkComboBox(
            controls,
            values=patient_list,
            command=self._on_patient_change,
            width=150
        )
        self.patient_combo.pack(side="left", padx=5)
        self.patient_combo.set("All patients")

        # Filtre SAE
        self.var_sae_only = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            controls,
            text="SAE only",
            variable=self.var_sae_only,
            command=self._refresh_list
        ).pack(side="left", padx=15)

        # Filtre Outcome
        ctk.CTkLabel(controls, text="Outcome:").pack(side="left", padx=(10, 5))
        self.outcome_filter = ctk.CTkComboBox(
            controls,
            values=["All", "Ongoing", "Recovered", "Recovered with sequelae", "Not recovered", "Fatal"],
            command=self._on_outcome_change,
            width=150
        )
        self.outcome_filter.pack(side="left", padx=5)
        self.outcome_filter.set("All")

        # Bouton nouveau
        self.btn_new = ctk.CTkButton(
            controls,
            text="+ New AE",
            command=self._new_ae,
            width=100
        )
        self.btn_new.pack(side="right", padx=10)

    def _create_stats_bar(self) -> None:
        """Crée la barre de statistiques."""
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        self.stats_labels = {}

        stats_config = [
            ("total", "Total AE", "white"),
            ("serious", "SAE", "#d9534f"),
            ("ongoing", "Ongoing", "#5bc0de"),
            ("recovered", "Recovered", "#5cb85c"),
            ("fatal", "Fatal", "#d9534f"),
        ]

        for key, label, color in stats_config:
            card = ctk.CTkFrame(self.stats_frame, width=110)
            card.pack(side="left", padx=10, pady=10)
            card.pack_propagate(False)

            ctk.CTkLabel(
                card,
                text="0",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=color
            ).pack(pady=(10, 0))

            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=11),
                text_color="gray"
            ).pack(pady=(0, 10))

            self.stats_labels[key] = card.winfo_children()[0]

    def _create_ae_list(self) -> None:
        """Crée la liste des EI."""
        self.list_container = ctk.CTkFrame(self, corner_radius=10)
        self.list_container.grid(row=3, column=0, sticky="nsew")
        self.list_container.grid_columnconfigure(0, weight=1)
        self.list_container.grid_rowconfigure(1, weight=1)

        # En-tête
        header = ctk.CTkFrame(self.list_container, fg_color=("gray80", "gray25"))
        header.grid(row=0, column=0, sticky="ew")

        columns = [
            ("Patient", 90), ("AE#", 40), ("Start", 90), ("Description", 180),
            ("Severity", 70), ("SAE", 40), ("Outcome", 90), ("Reporting", 70), ("Actions", 100)
        ]

        for i, (name, width) in enumerate(columns):
            ctk.CTkLabel(header, text=name, font=ctk.CTkFont(weight="bold"), width=width).grid(
                row=0, column=i, padx=3, pady=8
            )

        # Liste
        self.ae_list = ctk.CTkScrollableFrame(self.list_container, fg_color="transparent")
        self.ae_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self._refresh_list()

    def _update_stats(self, events: List[Dict] = None) -> None:
        """Met à jour les stats basées sur les événements affichés."""
        if events is None:
            events = []

        stats = {
            "total": len(events),
            "serious": sum(1 for e in events if e.get("is_serious")),
            "ongoing": sum(1 for e in events if e.get("outcome") in ("Ongoing", None, "")),
            "recovered": sum(1 for e in events if e.get("outcome") in ("Recovered", "Recovered with sequelae")),
            "fatal": sum(1 for e in events if e.get("outcome") == "Fatal"),
        }

        for key, label in self.stats_labels.items():
            label.configure(text=str(stats.get(key, 0)))

    def _on_search(self, event=None) -> None:
        """Filtre la liste des patients selon la recherche."""
        query = self.search_entry.get().strip().lower()

        if query:
            filtered = [p for p in self.patients
                       if query in p['patient_number'].lower()]
        else:
            filtered = self.patients

        patient_list = ["All patients"] + [f"{p['patient_number']}" for p in filtered]
        self.patient_combo.configure(values=patient_list)

        if patient_list:
            self.patient_combo.set(patient_list[0])
            self._on_patient_change(patient_list[0])

    def _on_outcome_change(self, value: str) -> None:
        """Callback changement filtre outcome."""
        self._refresh_list()

    def _refresh_list(self) -> None:
        """Rafraîchit la liste."""
        for widget in self.ae_list.winfo_children():
            widget.destroy()

        # Récupérer les EI
        if self.var_sae_only.get():
            events = self.ae_queries.get_all_serious()
        elif self.selected_patient:
            events = self.ae_queries.get_by_patient(self.selected_patient["id"])
            # Ajouter patient_number
            for ae in events:
                ae["patient_number"] = self.selected_patient["patient_number"]
        else:
            # Tous les EI de tous les patients
            events = []
            for patient in self.patient_queries.get_all():
                patient_aes = self.ae_queries.get_by_patient(patient["id"])
                for ae in patient_aes:
                    ae["patient_number"] = patient["patient_number"]
                events.extend(patient_aes)

        # Filtre outcome
        outcome_filter = self.outcome_filter.get()
        if outcome_filter != "All":
            events = [e for e in events if e.get("outcome") == outcome_filter]

        # Mettre à jour les stats
        self._update_stats(events)

        if not events:
            ctk.CTkLabel(
                self.ae_list,
                text="No adverse events",
                text_color="gray"
            ).grid(row=0, column=0, columnspan=9, pady=50)
            return

        for i, ae in enumerate(events):
            self._add_ae_row(i, ae)

    def _add_ae_row(self, row: int, ae: Dict) -> None:
        """Ajoute une ligne d'EI."""
        row_frame = ctk.CTkFrame(self.ae_list, fg_color=("gray90", "gray17"))
        row_frame.grid(row=row, column=0, sticky="ew", pady=2, padx=5)

        # Patient
        patient_num = ae.get("patient_number", "")
        if not patient_num and ae.get("patient_id"):
            patient = self.patient_queries.get_by_id(ae["patient_id"])
            patient_num = patient.get("patient_number", "") if patient else ""

        ctk.CTkLabel(row_frame, text=patient_num, width=90).grid(row=0, column=0, padx=3, pady=8)

        # AE#
        ctk.CTkLabel(row_frame, text=str(ae.get("ae_number", "")), width=40).grid(row=0, column=1, padx=3)

        # Date début
        start_date = ae.get("start_date", "")
        if start_date and hasattr(start_date, 'strftime'):
            start_date = start_date.strftime("%Y-%m-%d")
        ctk.CTkLabel(row_frame, text=str(start_date), width=90).grid(row=0, column=2, padx=3)

        # Description (tronquée)
        desc = ae.get("description", "")[:25]
        if len(ae.get("description", "")) > 25:
            desc += "..."
        ctk.CTkLabel(row_frame, text=desc, width=180, anchor="w").grid(row=0, column=3, padx=3)

        # Sévérité
        severity = ae.get("severity", "")
        severity_colors = {"Mild": "#5cb85c", "Moderate": "#f0ad4e", "Severe": "#d9534f"}
        ctk.CTkLabel(
            row_frame,
            text=severity,
            text_color=severity_colors.get(severity, "white"),
            width=70
        ).grid(row=0, column=4, padx=3)

        # SAE
        is_sae = "Yes" if ae.get("is_serious") else "-"
        sae_color = "#d9534f" if ae.get("is_serious") else "gray"
        ctk.CTkLabel(row_frame, text=is_sae, text_color=sae_color, width=40).grid(row=0, column=5, padx=3)

        # Outcome
        outcome = ae.get("outcome", "")
        outcome_colors = {
            "Ongoing": "#5bc0de",
            "Recovered": "#5cb85c",
            "Recovered with sequelae": "#f0ad4e",
            "Not recovered": "#f0ad4e",
            "Fatal": "#d9534f",
        }
        ctk.CTkLabel(
            row_frame,
            text=outcome or "-",
            text_color=outcome_colors.get(outcome, "white"),
            width=90
        ).grid(row=0, column=6, padx=3)

        # Reporting delay (pour SAE)
        reporting_text = "-"
        reporting_color = "gray"
        if ae.get("is_serious"):
            start = ae.get("start_date")
            report = ae.get("reporting_date")
            if start and report:
                if isinstance(start, str):
                    start = parse_date(start)
                if isinstance(report, str):
                    report = parse_date(report)
                if start and report:
                    delta = (report - start).days
                    if delta <= 1:
                        reporting_text = f"<24h"
                        reporting_color = "#5cb85c"
                    else:
                        reporting_text = f"+{delta}d"
                        reporting_color = "#d9534f"
            else:
                reporting_text = "?"
                reporting_color = "#f0ad4e"

        ctk.CTkLabel(
            row_frame,
            text=reporting_text,
            text_color=reporting_color,
            width=70
        ).grid(row=0, column=7, padx=3)

        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=100)
        actions_frame.grid(row=0, column=8, padx=3)

        ctk.CTkButton(
            actions_frame,
            text="Edit",
            width=45,
            height=25,
            command=lambda a=ae: self._edit_ae(a)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions_frame,
            text="Del",
            width=45,
            height=25,
            fg_color="#d9534f",
            hover_color="#c9302c",
            command=lambda a=ae: self._delete_ae(a)
        ).pack(side="left", padx=2)

    def _on_patient_change(self, value: str) -> None:
        """Callback changement patient."""
        if value == "All patients":
            self.selected_patient = None
        else:
            self.selected_patient = self.patient_queries.get_by_number(value)
        self._refresh_list()

    def _new_ae(self) -> None:
        """Crée un nouvel EI."""
        # Sélectionner un patient d'abord
        if not self.selected_patient:
            patients = self.patient_queries.get_all()
            if not patients:
                messagebox.showerror("Error", "No patients available")
                return
            self.selected_patient = patients[0]

        dialog = AEDialog(self, self.selected_patient, self.ae_queries)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.ae_queries.create(**dialog.result)
                self._refresh_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create AE: {e}")

    def _edit_ae(self, ae: Dict) -> None:
        """Modifie un EI."""
        patient = self.patient_queries.get_by_id(ae["patient_id"])
        if not patient:
            messagebox.showerror("Error", "Patient not found")
            return

        dialog = AEDialog(self, patient, self.ae_queries, ae)
        self.wait_window(dialog)

        if dialog.result:
            try:
                # Supprimer patient_id car on ne le modifie pas
                update_data = {k: v for k, v in dialog.result.items() if k != "patient_id"}
                self.ae_queries.update(ae["id"], **update_data)
                self._refresh_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not update AE: {e}")

    def _delete_ae(self, ae: Dict) -> None:
        """Supprime un EI après confirmation."""
        patient_num = ae.get("patient_number", "")
        ae_num = ae.get("ae_number", "")

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete AE #{ae_num} for patient {patient_num}?\n\nThis action cannot be undone."
        )

        if confirm:
            try:
                # Supprimer via une requête directe
                cursor = self.ae_queries.conn.cursor()
                cursor.execute("DELETE FROM adverse_events WHERE id = ?", (ae["id"],))
                self.ae_queries.conn.commit()
                self._refresh_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete AE: {e}")
