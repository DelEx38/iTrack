"""
Gestion des patients.
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, List, Dict, Any
from datetime import date


class PatientDialog(ctk.CTkToplevel):
    """Dialogue pour ajouter/modifier un patient."""

    def __init__(self, parent, patient_queries, consent_queries, patient_data: Optional[Dict] = None):
        super().__init__(parent)

        self.patient_queries = patient_queries
        self.consent_queries = consent_queries
        self.patient_data = patient_data
        self.result = None

        # Configuration de la fenêtre
        self.title("Edit Patient" if patient_data else "New Patient")
        self.geometry("500x600")
        self.resizable(False, False)

        # Rendre modale
        self.transient(parent)
        self.grab_set()

        # Centrer la fenêtre
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 600) // 2
        self.geometry(f"+{x}+{y}")

        self._create_form()

        if patient_data:
            self._fill_form(patient_data)

    def _create_form(self) -> None:
        """Crée le formulaire."""
        # Frame principal
        self.form_frame = ctk.CTkScrollableFrame(self)
        self.form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Patient Number
        ctk.CTkLabel(self.form_frame, text="Patient Number *").pack(anchor="w", pady=(0, 5))
        self.entry_number = ctk.CTkEntry(self.form_frame, width=300)
        self.entry_number.pack(anchor="w", pady=(0, 15))

        # Initials
        ctk.CTkLabel(self.form_frame, text="Initials").pack(anchor="w", pady=(0, 5))
        self.entry_initials = ctk.CTkEntry(self.form_frame, width=100)
        self.entry_initials.pack(anchor="w", pady=(0, 15))

        # Site ID
        ctk.CTkLabel(self.form_frame, text="Site ID").pack(anchor="w", pady=(0, 5))
        self.entry_site = ctk.CTkEntry(self.form_frame, width=150)
        self.entry_site.pack(anchor="w", pady=(0, 15))

        # Birth Date
        ctk.CTkLabel(self.form_frame, text="Birth Date (YYYY-MM-DD)").pack(anchor="w", pady=(0, 5))
        self.entry_birth = ctk.CTkEntry(self.form_frame, width=150)
        self.entry_birth.pack(anchor="w", pady=(0, 15))

        # Status
        ctk.CTkLabel(self.form_frame, text="Status").pack(anchor="w", pady=(0, 5))
        self.combo_status = ctk.CTkComboBox(
            self.form_frame,
            values=["Screening", "Screen Failure", "Included", "Completed", "Withdrawn", "Lost to Follow-up"],
            width=200
        )
        self.combo_status.pack(anchor="w", pady=(0, 15))
        self.combo_status.set("Screening")

        # Randomization Number
        ctk.CTkLabel(self.form_frame, text="Randomization Number").pack(anchor="w", pady=(0, 5))
        self.entry_randomization = ctk.CTkEntry(self.form_frame, width=150)
        self.entry_randomization.pack(anchor="w", pady=(0, 15))

        # Randomization Arm
        ctk.CTkLabel(self.form_frame, text="Randomization Arm").pack(anchor="w", pady=(0, 5))
        self.entry_arm = ctk.CTkEntry(self.form_frame, width=200)
        self.entry_arm.pack(anchor="w", pady=(0, 15))

        # Boutons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="transparent",
            border_width=1
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Save",
            command=self._save
        ).pack(side="right", padx=5)

    def _fill_form(self, data: Dict) -> None:
        """Remplit le formulaire avec les données existantes."""
        self.entry_number.insert(0, data.get("patient_number", ""))
        self.entry_initials.insert(0, data.get("initials", ""))
        self.entry_site.insert(0, data.get("site_id", ""))
        if data.get("birth_date"):
            self.entry_birth.insert(0, str(data["birth_date"]))
        if data.get("status"):
            self.combo_status.set(data["status"])
        self.entry_randomization.insert(0, data.get("randomization_number", "") or "")
        self.entry_arm.insert(0, data.get("randomization_arm", "") or "")

    def _save(self) -> None:
        """Sauvegarde le patient."""
        patient_number = self.entry_number.get().strip()
        if not patient_number:
            messagebox.showerror("Error", "Patient number is required")
            return

        birth_date = None
        birth_str = self.entry_birth.get().strip()
        if birth_str:
            try:
                parts = birth_str.split("-")
                birth_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Invalid birth date format. Use YYYY-MM-DD")
                return

        self.result = {
            "patient_number": patient_number,
            "initials": self.entry_initials.get().strip(),
            "site_id": self.entry_site.get().strip(),
            "birth_date": birth_date,
            "status": self.combo_status.get(),
            "randomization_number": self.entry_randomization.get().strip() or None,
            "randomization_arm": self.entry_arm.get().strip() or None
        }

        self.destroy()


class PatientsFrame(ctk.CTkFrame):
    """Frame de gestion des patients."""

    def __init__(self, parent, patient_queries, visit_queries, consent_queries):
        super().__init__(parent, fg_color="transparent")

        self.patient_queries = patient_queries
        self.visit_queries = visit_queries
        self.consent_queries = consent_queries

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # En-tête
        self._create_header()

        # Barre de recherche
        self._create_search_bar()

        # Liste des patients
        self._create_patient_list()

        # Charger les données
        self.refresh_data()

    def _create_header(self) -> None:
        """Crée l'en-tête."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)

        # Titre
        title = ctk.CTkLabel(
            header_frame,
            text="Patients",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w")

        # Bouton Nouveau
        self.btn_new = ctk.CTkButton(
            header_frame,
            text="+ New Patient",
            command=self._new_patient,
            width=140
        )
        self.btn_new.grid(row=0, column=2, sticky="e")

    def _create_search_bar(self) -> None:
        """Crée la barre de recherche."""
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search patients...",
            width=300
        )
        self.search_entry.grid(row=0, column=0, sticky="w")
        self.search_entry.bind("<KeyRelease>", self._on_search)

        # Filtre par statut
        self.filter_status = ctk.CTkComboBox(
            search_frame,
            values=["All", "Screening", "Screen Failure", "Included", "Completed", "Withdrawn"],
            command=self._on_filter_change,
            width=150
        )
        self.filter_status.grid(row=0, column=1, padx=(10, 0))
        self.filter_status.set("All")

    def _create_patient_list(self) -> None:
        """Crée la liste des patients."""
        # Frame conteneur avec scrollbar
        self.list_container = ctk.CTkFrame(self, corner_radius=10)
        self.list_container.grid(row=2, column=0, sticky="nsew")
        self.list_container.grid_columnconfigure(0, weight=1)
        self.list_container.grid_rowconfigure(1, weight=1)

        # En-tête du tableau
        header = ctk.CTkFrame(self.list_container, fg_color=("gray80", "gray25"), corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")

        columns = [
            ("Patient #", 120),
            ("Initials", 80),
            ("Site", 80),
            ("Status", 120),
            ("Screening", 100),
            ("Inclusion", 100),
            ("Actions", 100)
        ]

        for i, (name, width) in enumerate(columns):
            lbl = ctk.CTkLabel(
                header,
                text=name,
                font=ctk.CTkFont(weight="bold"),
                width=width
            )
            lbl.grid(row=0, column=i, padx=5, pady=10)

        # Liste scrollable
        self.patient_list = ctk.CTkScrollableFrame(self.list_container, fg_color="transparent")
        self.patient_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def refresh_data(self, search: str = "", status_filter: str = "All") -> None:
        """Rafraîchit la liste des patients."""
        # Effacer la liste actuelle
        for widget in self.patient_list.winfo_children():
            widget.destroy()

        # Récupérer les patients
        if search:
            patients = self.patient_queries.search(search)
        else:
            patients = self.patient_queries.get_all()

        # Filtrer par statut
        if status_filter != "All":
            patients = [p for p in patients if p.get("status") == status_filter]

        # Afficher les patients
        if not patients:
            no_data = ctk.CTkLabel(
                self.patient_list,
                text="No patients found",
                text_color="gray"
            )
            no_data.grid(row=0, column=0, columnspan=7, pady=50)
            return

        for i, patient in enumerate(patients):
            self._add_patient_row(i, patient)

    def _add_patient_row(self, row: int, patient: Dict) -> None:
        """Ajoute une ligne de patient."""
        row_frame = ctk.CTkFrame(self.patient_list, fg_color="transparent")
        row_frame.grid(row=row, column=0, sticky="ew", pady=2)

        # Patient Number
        ctk.CTkLabel(row_frame, text=patient.get("patient_number", ""), width=120).grid(row=0, column=0, padx=5)

        # Initials
        ctk.CTkLabel(row_frame, text=patient.get("initials", ""), width=80).grid(row=0, column=1, padx=5)

        # Site
        ctk.CTkLabel(row_frame, text=patient.get("site_id", ""), width=80).grid(row=0, column=2, padx=5)

        # Status avec couleur
        status = patient.get("status", "")
        status_colors = {
            "Screening": "#f0ad4e",
            "Screen Failure": "#d9534f",
            "Included": "#5cb85c",
            "Completed": "#5bc0de",
            "Withdrawn": "#777777"
        }
        status_label = ctk.CTkLabel(
            row_frame,
            text=status,
            width=120,
            text_color=status_colors.get(status, "white")
        )
        status_label.grid(row=0, column=3, padx=5)

        # Screening date
        screening = patient.get("screening_date", "")
        ctk.CTkLabel(row_frame, text=str(screening) if screening else "-", width=100).grid(row=0, column=4, padx=5)

        # Inclusion date
        inclusion = patient.get("inclusion_date", "")
        ctk.CTkLabel(row_frame, text=str(inclusion) if inclusion else "-", width=100).grid(row=0, column=5, padx=5)

        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=100)
        actions_frame.grid(row=0, column=6, padx=5)

        # Edit button
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="Edit",
            width=40,
            height=25,
            command=lambda p=patient: self._edit_patient(p)
        )
        edit_btn.pack(side="left", padx=2)

        # Delete button
        del_btn = ctk.CTkButton(
            actions_frame,
            text="Del",
            width=40,
            height=25,
            fg_color="#d9534f",
            hover_color="#c9302c",
            command=lambda p=patient: self._delete_patient(p)
        )
        del_btn.pack(side="left", padx=2)

    def _new_patient(self) -> None:
        """Ouvre le dialogue pour un nouveau patient."""
        dialog = PatientDialog(self, self.patient_queries, self.consent_queries)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.patient_queries.create(**dialog.result)
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create patient: {e}")

    def _edit_patient(self, patient: Dict) -> None:
        """Ouvre le dialogue pour modifier un patient."""
        dialog = PatientDialog(self, self.patient_queries, self.consent_queries, patient)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.patient_queries.update(patient["id"], **dialog.result)
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Could not update patient: {e}")

    def _delete_patient(self, patient: Dict) -> None:
        """Supprime un patient."""
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete patient {patient.get('patient_number')}?"
        )

        if confirm:
            try:
                self.patient_queries.delete(patient["id"])
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete patient: {e}")

    def _on_search(self, event=None) -> None:
        """Callback pour la recherche."""
        search = self.search_entry.get()
        status = self.filter_status.get()
        self.refresh_data(search, status)

    def _on_filter_change(self, value: str) -> None:
        """Callback pour le changement de filtre."""
        search = self.search_entry.get()
        self.refresh_data(search, value)
