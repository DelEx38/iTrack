"""
Gestion des visites.
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, List, Dict, Any
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


class VisitDialog(ctk.CTkToplevel):
    """Dialogue pour enregistrer une visite."""

    def __init__(self, parent, patient: Dict, visit_config: Dict, visit_queries, existing_visit: Optional[Dict] = None):
        super().__init__(parent)

        self.patient = patient
        self.visit_config = visit_config
        self.visit_queries = visit_queries
        self.existing_visit = existing_visit
        self.result = None

        # Configuration
        self.title(f"Visit {visit_config['visit_name']} - {patient['patient_number']}")
        self.geometry("450x400")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 450) // 2
        y = (self.winfo_screenheight() - 400) // 2
        self.geometry(f"+{x}+{y}")

        self._create_form()

        if existing_visit:
            self._fill_form(existing_visit)

    def _create_form(self) -> None:
        """Crée le formulaire."""
        # Info patient
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            info_frame,
            text=f"Patient: {self.patient['patient_number']}",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=5)

        ctk.CTkLabel(
            info_frame,
            text=f"Visit: {self.visit_config['visit_name']} (Day {self.visit_config['target_day']})"
        ).pack(anchor="w")

        # Fenêtre de visite
        window_text = f"Window: [{self.visit_config['window_before']}, +{self.visit_config['window_after']}] days"
        ctk.CTkLabel(info_frame, text=window_text, text_color="gray").pack(anchor="w")

        # Formulaire
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20)

        # Date de visite
        ctk.CTkLabel(form_frame, text="Visit Date (YYYY-MM-DD) *").pack(anchor="w", pady=(10, 5))
        self.entry_date = ctk.CTkEntry(form_frame, width=150)
        self.entry_date.pack(anchor="w")

        # Indicateur de fenêtre
        self.window_label = ctk.CTkLabel(form_frame, text="", text_color="gray")
        self.window_label.pack(anchor="w", pady=5)
        self.entry_date.bind("<KeyRelease>", self._check_window)

        # Statut
        ctk.CTkLabel(form_frame, text="Status").pack(anchor="w", pady=(15, 5))
        self.combo_status = ctk.CTkComboBox(
            form_frame,
            values=["Completed", "Missed", "Not Done", "Pending"],
            width=150
        )
        self.combo_status.pack(anchor="w")
        self.combo_status.set("Completed")

        # Commentaires
        ctk.CTkLabel(form_frame, text="Comments").pack(anchor="w", pady=(15, 5))
        self.text_comments = ctk.CTkTextbox(form_frame, height=80, width=350)
        self.text_comments.pack(anchor="w")

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

    def _fill_form(self, visit: Dict) -> None:
        """Remplit le formulaire avec les données existantes."""
        if visit.get("visit_date"):
            self.entry_date.insert(0, str(visit["visit_date"]))
        if visit.get("status"):
            self.combo_status.set(visit["status"])
        if visit.get("comments"):
            self.text_comments.insert("1.0", visit["comments"])

    def _check_window(self, event=None) -> None:
        """Vérifie si la date est dans la fenêtre."""
        date_str = self.entry_date.get().strip()
        if not date_str or len(date_str) < 10:
            self.window_label.configure(text="", text_color="gray")
            return

        try:
            parts = date_str.split("-")
            visit_date = date(int(parts[0]), int(parts[1]), int(parts[2]))

            result = self.visit_queries.check_window(
                self.patient["id"],
                self.visit_config["id"],
                visit_date
            )

            if result.get("valid"):
                if result.get("delta_days") is not None:
                    delta = result["delta_days"]
                    sign = "+" if delta >= 0 else ""
                    self.window_label.configure(
                        text=f"In window ({sign}{delta} days)",
                        text_color="#5cb85c"
                    )
                else:
                    self.window_label.configure(text=result.get("message", ""), text_color="gray")
            else:
                delta = result.get("delta_days", 0)
                sign = "+" if delta >= 0 else ""
                self.window_label.configure(
                    text=f"Out of window ({sign}{delta} days)",
                    text_color="#d9534f"
                )

        except (ValueError, IndexError):
            self.window_label.configure(text="Invalid date format", text_color="#f0ad4e")

    def _save(self) -> None:
        """Sauvegarde la visite."""
        date_str = self.entry_date.get().strip()
        if not date_str:
            messagebox.showerror("Error", "Visit date is required")
            return

        try:
            parts = date_str.split("-")
            visit_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return

        self.result = {
            "patient_id": self.patient["id"],
            "visit_config_id": self.visit_config["id"],
            "visit_date": visit_date,
            "status": self.combo_status.get(),
            "comments": self.text_comments.get("1.0", "end-1c").strip()
        }

        self.destroy()


class VisitsFrame(ctk.CTkFrame):
    """Frame de gestion des visites."""

    def __init__(self, parent, patient_queries, visit_queries):
        super().__init__(parent, fg_color="transparent")

        self.patient_queries = patient_queries
        self.visit_queries = visit_queries
        self.selected_patient = None
        self.v1_date: Optional[date] = None  # Date de V1 pour calculs

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Row 3 pour la grille (après stats)

        self._create_header()
        self._create_patient_selector()
        self._create_stats_bar()
        self._create_visits_grid()

    def _create_header(self) -> None:
        """Crée l'en-tête."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="Visit Management",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        # Légende des statuts
        legend_frame = ctk.CTkFrame(header, fg_color="transparent")
        legend_frame.grid(row=0, column=2, sticky="e")

        legends = [
            ("Completed", "#5cb85c"),
            ("Missed", "#d9534f"),
            ("Pending", "#5bc0de"),
            ("In window", "#5cb85c"),
            ("Out of window", "#d9534f"),
        ]

        for text, color in legends:
            lf = ctk.CTkFrame(legend_frame, fg_color="transparent")
            lf.pack(side="left", padx=8)
            ctk.CTkLabel(lf, text="●", text_color=color, width=15).pack(side="left")
            ctk.CTkLabel(lf, text=text, font=ctk.CTkFont(size=11)).pack(side="left")

    def _create_patient_selector(self) -> None:
        """Crée le sélecteur de patient avec recherche."""
        selector_frame = ctk.CTkFrame(self)
        selector_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(selector_frame, text="Patient:").pack(side="left", padx=(10, 5))

        # Champ de recherche
        self.search_entry = ctk.CTkEntry(
            selector_frame,
            placeholder_text="Search patient...",
            width=150
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self._on_search)

        # Liste des patients
        self.patients = self.patient_queries.get_all()
        patient_list = [f"{p['patient_number']} - {p.get('initials', '')}" for p in self.patients]

        self.patient_combo = ctk.CTkComboBox(
            selector_frame,
            values=patient_list if patient_list else ["No patients"],
            command=self._on_patient_selected,
            width=250
        )
        self.patient_combo.pack(side="left", padx=10)

        self.btn_refresh = ctk.CTkButton(
            selector_frame,
            text="Refresh",
            command=self._refresh_all,
            width=80
        )
        self.btn_refresh.pack(side="left", padx=10)

        # Info patient sélectionné
        self.patient_info_label = ctk.CTkLabel(
            selector_frame,
            text="",
            text_color="gray"
        )
        self.patient_info_label.pack(side="left", padx=20)

    def _create_stats_bar(self) -> None:
        """Crée la barre de statistiques du patient."""
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        # Sera rempli dynamiquement
        self.stats_labels = {}

        stats_config = [
            ("total", "Total Visits", "white"),
            ("completed", "Completed", "#5cb85c"),
            ("in_window", "In Window", "#5cb85c"),
            ("out_window", "Out of Window", "#d9534f"),
            ("pending", "Pending", "#5bc0de"),
            ("missed", "Missed", "#d9534f"),
        ]

        for key, label, color in stats_config:
            card = ctk.CTkFrame(self.stats_frame, width=120)
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

    def _create_visits_grid(self) -> None:
        """Crée la grille des visites."""
        self.visits_container = ctk.CTkFrame(self, corner_radius=10)
        self.visits_container.grid(row=3, column=0, sticky="nsew")
        self.visits_container.grid_columnconfigure(0, weight=1)
        self.visits_container.grid_rowconfigure(1, weight=1)

        # En-tête du tableau
        header = ctk.CTkFrame(self.visits_container, fg_color=("gray80", "gray25"), corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")

        columns = [
            ("Visit", 60),
            ("Target Day", 80),
            ("Window", 100),
            ("Target Date", 100),
            ("Actual Date", 100),
            ("Status", 90),
            ("Window Check", 100),
            ("Action", 70),
        ]

        for i, (name, width) in enumerate(columns):
            ctk.CTkLabel(
                header,
                text=name,
                font=ctk.CTkFont(weight="bold"),
                width=width
            ).grid(row=0, column=i, padx=5, pady=8)

        self.visits_scroll = ctk.CTkScrollableFrame(self.visits_container, fg_color="transparent")
        self.visits_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Message initial
        self.no_patient_label = ctk.CTkLabel(
            self.visits_scroll,
            text="Select a patient to view visits",
            text_color="gray"
        )
        self.no_patient_label.grid(row=0, column=0, columnspan=8, pady=50)

    def _on_search(self, event=None) -> None:
        """Filtre la liste des patients selon la recherche."""
        query = self.search_entry.get().strip().lower()

        if query:
            filtered = [p for p in self.patients
                       if query in p['patient_number'].lower()
                       or query in (p.get('initials', '') or '').lower()]
        else:
            filtered = self.patients

        patient_list = [f"{p['patient_number']} - {p.get('initials', '')}" for p in filtered]
        self.patient_combo.configure(values=patient_list if patient_list else ["No patients"])

        if patient_list:
            self.patient_combo.set(patient_list[0])

    def _refresh_all(self) -> None:
        """Rafraîchit la liste des patients et les visites."""
        self.patients = self.patient_queries.get_all()
        patient_list = [f"{p['patient_number']} - {p.get('initials', '')}" for p in self.patients]
        self.patient_combo.configure(values=patient_list if patient_list else ["No patients"])

        if self.selected_patient:
            self._refresh_visits()

    def _on_patient_selected(self, value: str) -> None:
        """Callback quand un patient est sélectionné."""
        if value == "No patients":
            self.selected_patient = None
            self.v1_date = None
            self._update_patient_info()
            self._refresh_visits()
            return

        patient_number = value.split(" - ")[0]
        self.selected_patient = self.patient_queries.get_by_number(patient_number)

        if self.selected_patient:
            # Récupérer la date de V1
            self._fetch_v1_date()
            self._update_patient_info()
            self._refresh_visits()

    def _fetch_v1_date(self) -> None:
        """Récupère la date de V1 pour le patient sélectionné."""
        self.v1_date = None
        if not self.selected_patient:
            return

        visits = self.visit_queries.get_patient_visits(self.selected_patient["id"])
        for v in visits:
            if v.get("visit_name") == "V1" and v.get("visit_date"):
                self.v1_date = v["visit_date"]
                if isinstance(self.v1_date, str):
                    self.v1_date = parse_date(self.v1_date)
                break

    def _update_patient_info(self) -> None:
        """Met à jour les infos du patient sélectionné."""
        if self.selected_patient:
            status = self.selected_patient.get('status', '')
            v1_text = f" | V1: {self.v1_date}" if self.v1_date else " | V1: Not recorded"
            self.patient_info_label.configure(text=f"Status: {status}{v1_text}")
        else:
            self.patient_info_label.configure(text="")

    def _refresh_visits(self) -> None:
        """Rafraîchit la grille des visites."""
        # Effacer
        for widget in self.visits_scroll.winfo_children():
            widget.destroy()

        # Réinitialiser les stats
        stats = {
            "total": 0,
            "completed": 0,
            "in_window": 0,
            "out_window": 0,
            "pending": 0,
            "missed": 0,
        }

        if not self.selected_patient:
            self.no_patient_label = ctk.CTkLabel(
                self.visits_scroll,
                text="Select a patient to view visits",
                text_color="gray"
            )
            self.no_patient_label.grid(row=0, column=0, columnspan=8, pady=50)
            self._update_stats(stats)
            return

        # Récupérer config et visites
        visit_configs = self.visit_queries.get_config()
        patient_visits = self.visit_queries.get_patient_visits(self.selected_patient["id"])

        # Créer un dict pour accès rapide
        visits_dict = {v["visit_config_id"]: v for v in patient_visits}

        stats["total"] = len(visit_configs)

        # Afficher les visites
        for i, config in enumerate(visit_configs):
            visit_data = visits_dict.get(config["id"])
            window_status = self._create_visit_row(i, config, visit_data)

            # Compter les stats
            if visit_data:
                status = visit_data.get("status", "")
                if status == "Completed":
                    stats["completed"] += 1
                elif status == "Pending":
                    stats["pending"] += 1
                elif status == "Missed":
                    stats["missed"] += 1

                if window_status == "in":
                    stats["in_window"] += 1
                elif window_status == "out":
                    stats["out_window"] += 1

        self._update_stats(stats)

    def _update_stats(self, stats: Dict[str, int]) -> None:
        """Met à jour les labels de statistiques."""
        for key, label in self.stats_labels.items():
            label.configure(text=str(stats.get(key, 0)))

    def _create_visit_row(self, row: int, config: Dict, visit_data: Optional[Dict]) -> Optional[str]:
        """Crée une ligne de visite. Retourne 'in', 'out' ou None pour le statut fenêtre."""
        row_frame = ctk.CTkFrame(self.visits_scroll, fg_color=("gray90", "gray17"))
        row_frame.grid(row=row, column=0, sticky="ew", pady=2, padx=5)

        window_status = None
        status_colors = {
            "Completed": "#5cb85c",
            "Missed": "#d9534f",
            "Not Done": "#f0ad4e",
            "Pending": "#5bc0de"
        }

        # Col 0: Nom de la visite
        ctk.CTkLabel(
            row_frame,
            text=config["visit_name"],
            font=ctk.CTkFont(weight="bold"),
            width=60
        ).grid(row=0, column=0, padx=10, pady=10)

        # Col 1: Target Day
        ctk.CTkLabel(
            row_frame,
            text=f"J{config['target_day']}" if config['target_day'] > 0 else "J0",
            width=80
        ).grid(row=0, column=1, padx=5)

        # Col 2: Fenêtre
        if config['window_before'] != 0 or config['window_after'] != 0:
            window_text = f"[{config['window_before']}, +{config['window_after']}]"
        else:
            window_text = "-"
        ctk.CTkLabel(row_frame, text=window_text, width=100).grid(row=0, column=2, padx=5)

        # Col 3: Date cible (calculée depuis V1)
        target_date_text = "-"
        target_date = None
        if self.v1_date and config['target_day'] > 0:
            target_date = self.v1_date + timedelta(days=config['target_day'])
            target_date_text = target_date.strftime("%Y-%m-%d")
        elif config['visit_name'] == "V1" and self.v1_date:
            target_date_text = self.v1_date.strftime("%Y-%m-%d")
            target_date = self.v1_date

        ctk.CTkLabel(row_frame, text=target_date_text, width=100).grid(row=0, column=3, padx=5)

        # Col 4: Date réelle
        if visit_data and visit_data.get("visit_date"):
            actual_date = visit_data["visit_date"]
            if isinstance(actual_date, str):
                actual_date = parse_date(actual_date)
            date_text = actual_date.strftime("%Y-%m-%d") if actual_date else "-"
        else:
            date_text = "-"
            actual_date = None

        ctk.CTkLabel(row_frame, text=date_text, width=100).grid(row=0, column=4, padx=5)

        # Col 5: Statut
        if visit_data:
            status = visit_data.get("status", "")
            ctk.CTkLabel(
                row_frame,
                text=status,
                text_color=status_colors.get(status, "white"),
                width=90
            ).grid(row=0, column=5, padx=5)
        else:
            ctk.CTkLabel(
                row_frame,
                text="Not recorded",
                text_color="gray",
                width=90
            ).grid(row=0, column=5, padx=5)

        # Col 6: Window Check (dans/hors fenêtre)
        window_check_text = "-"
        window_check_color = "gray"

        if visit_data and actual_date and target_date:
            # Calculer si dans la fenêtre
            min_date = target_date - timedelta(days=abs(config['window_before']))
            max_date = target_date + timedelta(days=config['window_after'])
            delta = (actual_date - target_date).days

            if min_date <= actual_date <= max_date:
                sign = "+" if delta >= 0 else ""
                window_check_text = f"OK ({sign}{delta}d)"
                window_check_color = "#5cb85c"
                window_status = "in"
            else:
                sign = "+" if delta >= 0 else ""
                window_check_text = f"OUT ({sign}{delta}d)"
                window_check_color = "#d9534f"
                window_status = "out"
        elif config['visit_name'] == "V1" and visit_data:
            window_check_text = "REF"
            window_check_color = "#5bc0de"
            window_status = "in"  # V1 est toujours "dans la fenêtre" (référence)

        ctk.CTkLabel(
            row_frame,
            text=window_check_text,
            text_color=window_check_color,
            width=100
        ).grid(row=0, column=6, padx=5)

        # Col 7: Bouton
        btn_text = "Edit" if visit_data else "Record"
        ctk.CTkButton(
            row_frame,
            text=btn_text,
            width=70,
            height=28,
            command=lambda c=config, v=visit_data: self._open_visit_dialog(c, v)
        ).grid(row=0, column=7, padx=10, pady=5)

        return window_status

    def _open_visit_dialog(self, config: Dict, visit_data: Optional[Dict]) -> None:
        """Ouvre le dialogue de visite."""
        dialog = VisitDialog(
            self,
            self.selected_patient,
            config,
            self.visit_queries,
            visit_data
        )
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.visit_queries.record_visit(**dialog.result)
                self._refresh_visits()
            except Exception as e:
                messagebox.showerror("Error", f"Could not save visit: {e}")
