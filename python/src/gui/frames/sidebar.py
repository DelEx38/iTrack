"""
Barre latérale de navigation.
"""

import customtkinter as ctk
from typing import Callable, Optional, List, Dict


class SidebarFrame(ctk.CTkFrame):
    """Barre latérale avec les boutons de navigation."""

    def __init__(
        self,
        parent,
        on_home: Callable,
        on_dashboard: Callable,
        on_sites: Callable,
        on_patients: Callable,
        on_visits: Callable,
        on_adverse_events: Callable,
        on_documents: Callable,
        on_monitoring: Callable,
        on_export: Callable,
        on_settings: Callable,
        on_study_change: Callable,
        studies: List[Dict],
        current_study: Optional[Dict] = None
    ):
        super().__init__(parent, width=200, corner_radius=0)
        self.grid_rowconfigure(12, weight=1)
        self.on_study_change = on_study_change

        # Logo / Titre
        self.logo_label = ctk.CTkLabel(
            self,
            text="Clinical Study\nTracker",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Sélecteur d'étude
        self.study_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.study_frame.grid(row=1, column=0, padx=10, pady=(0, 20), sticky="ew")

        ctk.CTkLabel(
            self.study_frame,
            text="Study:",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=5)

        study_names = [s.get("study_number") or s.get("study_name") or "No name" for s in studies] if studies else ["No study"]
        self.study_combo = ctk.CTkComboBox(
            self.study_frame,
            values=study_names,
            command=self._on_study_selected,
            width=170
        )
        self.study_combo.pack(padx=5, pady=5)

        if current_study:
            self.study_combo.set(current_study.get("study_number") or current_study.get("study_name") or "")
        elif study_names:
            self.study_combo.set(study_names[0])

        # Boutons de navigation
        self.nav_buttons = []

        # Home (Landing page)
        self.btn_home = ctk.CTkButton(
            self,
            text="Home",
            command=on_home,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            height=40
        )
        self.btn_home.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.nav_buttons.append(self.btn_home)

        # Dashboard
        self.btn_dashboard = ctk.CTkButton(
            self,
            text="Dashboard",
            command=on_dashboard,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            height=40
        )
        self.btn_dashboard.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        self.nav_buttons.append(self.btn_dashboard)

        # Sites
        self.btn_sites = ctk.CTkButton(
            self,
            text="Sites",
            command=on_sites,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            height=40
        )
        self.btn_sites.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        self.nav_buttons.append(self.btn_sites)

        # Patients
        self.btn_patients = ctk.CTkButton(
            self,
            text="Patients",
            command=on_patients,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            height=40
        )
        self.btn_patients.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        self.nav_buttons.append(self.btn_patients)

        # Visites
        self.btn_visits = ctk.CTkButton(
            self,
            text="Visites",
            command=on_visits,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            height=40
        )
        self.btn_visits.grid(row=6, column=0, padx=10, pady=5, sticky="ew")
        self.nav_buttons.append(self.btn_visits)

        # Événements indésirables
        self.btn_ae = ctk.CTkButton(
            self,
            text="Adverse Events",
            command=on_adverse_events,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            height=40
        )
        self.btn_ae.grid(row=7, column=0, padx=10, pady=5, sticky="ew")
        self.nav_buttons.append(self.btn_ae)

        # Documents / Consentements
        self.btn_documents = ctk.CTkButton(
            self,
            text="Documents",
            command=on_documents,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            height=40
        )
        self.btn_documents.grid(row=8, column=0, padx=10, pady=5, sticky="ew")
        self.nav_buttons.append(self.btn_documents)

        # Monitoring
        self.btn_monitoring = ctk.CTkButton(
            self,
            text="Monitoring",
            command=on_monitoring,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            height=40
        )
        self.btn_monitoring.grid(row=9, column=0, padx=10, pady=5, sticky="ew")
        self.nav_buttons.append(self.btn_monitoring)

        # Séparateur
        self.separator = ctk.CTkFrame(self, height=2, fg_color="gray50")
        self.separator.grid(row=10, column=0, padx=20, pady=20, sticky="ew")

        # Export Excel
        self.btn_export = ctk.CTkButton(
            self,
            text="Export Excel",
            command=on_export,
            fg_color=("#3a7ebf", "#1f538d"),
            hover_color=("#325882", "#14375e"),
            height=40
        )
        self.btn_export.grid(row=11, column=0, padx=10, pady=5, sticky="ew")

        # Espace flexible
        self.spacer = ctk.CTkFrame(self, fg_color="transparent")
        self.spacer.grid(row=12, column=0, sticky="nsew")

        # Paramètres (en bas)
        self.btn_settings = ctk.CTkButton(
            self,
            text="Settings",
            command=on_settings,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            height=40
        )
        self.btn_settings.grid(row=13, column=0, padx=10, pady=(5, 20), sticky="ew")

    def _on_study_selected(self, study_name: str) -> None:
        """Callback quand une étude est sélectionnée."""
        self.on_study_change(study_name)

    def update_studies(self, studies: List[Dict], current_study: Optional[Dict] = None) -> None:
        """Met à jour la liste des études."""
        study_names = [s.get("study_number") or s.get("study_name") or "No name" for s in studies] if studies else ["No study"]
        self.study_combo.configure(values=study_names)
        if current_study:
            self.study_combo.set(current_study.get("study_number") or current_study.get("study_name") or "")

    def set_active(self, button_name: str) -> None:
        """Met en surbrillance le bouton actif."""
        for btn in self.nav_buttons:
            btn.configure(fg_color="transparent")

        button_map = {
            "home": self.btn_home,
            "dashboard": self.btn_dashboard,
            "sites": self.btn_sites,
            "patients": self.btn_patients,
            "visits": self.btn_visits,
            "adverse_events": self.btn_ae,
            "documents": self.btn_documents,
            "monitoring": self.btn_monitoring
        }

        if button_name in button_map:
            button_map[button_name].configure(fg_color=("gray75", "gray25"))
