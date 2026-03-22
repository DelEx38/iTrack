"""
Gestion des documents et consentements.
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict, List, Any
from datetime import date


def parse_date(date_str: str) -> Optional[date]:
    """Parse une date au format YYYY-MM-DD."""
    if not date_str or len(date_str) < 10:
        return None
    try:
        parts = date_str.split("-")
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        return None


class ManageTypesDialog(ctk.CTkToplevel):
    """Dialogue pour gérer les types et versions de consentements."""

    def __init__(self, parent, consent_queries):
        super().__init__(parent)

        self.consent_queries = consent_queries

        self.title("Manage Consent Types & Versions")
        self.geometry("600x500")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 600) // 2
        y = (self.winfo_screenheight() - 500) // 2
        self.geometry(f"+{x}+{y}")

        self._create_ui()
        self._refresh_types()

    def _create_ui(self) -> None:
        """Crée l'interface."""
        # Frame gauche : Types
        left_frame = ctk.CTkFrame(self)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(left_frame, text="Consent Types", font=ctk.CTkFont(weight="bold")).pack(pady=10)

        # Liste des types
        self.types_list = ctk.CTkScrollableFrame(left_frame, height=300)
        self.types_list.pack(fill="both", expand=True, padx=5)

        # Ajouter type
        add_type_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        add_type_frame.pack(fill="x", pady=10, padx=5)

        self.entry_new_type = ctk.CTkEntry(add_type_frame, placeholder_text="New type name...", width=150)
        self.entry_new_type.pack(side="left", padx=5)

        ctk.CTkButton(add_type_frame, text="+ Add", width=60, command=self._add_type).pack(side="left")

        # Frame droite : Versions
        right_frame = ctk.CTkFrame(self)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(right_frame, text="Versions", font=ctk.CTkFont(weight="bold")).pack(pady=10)

        self.selected_type_label = ctk.CTkLabel(right_frame, text="Select a type", text_color="gray")
        self.selected_type_label.pack()

        # Liste des versions
        self.versions_list = ctk.CTkScrollableFrame(right_frame, height=250)
        self.versions_list.pack(fill="both", expand=True, padx=5)

        # Ajouter version
        add_version_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        add_version_frame.pack(fill="x", pady=10, padx=5)

        self.entry_version = ctk.CTkEntry(add_version_frame, placeholder_text="Version", width=80)
        self.entry_version.pack(side="left", padx=2)

        self.entry_version_date = ctk.CTkEntry(add_version_frame, placeholder_text="YYYY-MM-DD", width=100)
        self.entry_version_date.pack(side="left", padx=2)

        ctk.CTkButton(add_version_frame, text="+ Add", width=60, command=self._add_version).pack(side="left", padx=2)

        self.selected_type_id = None

    def _refresh_types(self) -> None:
        """Rafraîchit la liste des types."""
        for widget in self.types_list.winfo_children():
            widget.destroy()

        types = self.consent_queries.get_types()

        for ct in types:
            row = ctk.CTkFrame(self.types_list, fg_color="transparent")
            row.pack(fill="x", pady=2)

            btn = ctk.CTkButton(
                row,
                text=ct["type_name"],
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray30"),
                anchor="w",
                command=lambda t=ct: self._select_type(t)
            )
            btn.pack(side="left", fill="x", expand=True)

    def _select_type(self, consent_type: Dict) -> None:
        """Sélectionne un type et affiche ses versions."""
        self.selected_type_id = consent_type["id"]
        self.selected_type_label.configure(text=consent_type["type_name"])
        self._refresh_versions()

    def _refresh_versions(self) -> None:
        """Rafraîchit la liste des versions."""
        for widget in self.versions_list.winfo_children():
            widget.destroy()

        if not self.selected_type_id:
            return

        versions = self.consent_queries.get_versions(self.selected_type_id)

        for v in versions:
            row = ctk.CTkFrame(self.versions_list, fg_color=("gray90", "gray17"))
            row.pack(fill="x", pady=2, padx=5)

            ctk.CTkLabel(row, text=v["version"], width=80).pack(side="left", padx=5, pady=5)
            ctk.CTkLabel(row, text=str(v.get("version_date", "")), width=100).pack(side="left", padx=5)

    def _add_type(self) -> None:
        """Ajoute un nouveau type."""
        type_name = self.entry_new_type.get().strip()
        if not type_name:
            return

        try:
            self.consent_queries.add_type(type_name)
            self.entry_new_type.delete(0, "end")
            self._refresh_types()
        except Exception as e:
            messagebox.showerror("Error", f"Could not add type: {e}")

    def _add_version(self) -> None:
        """Ajoute une nouvelle version."""
        if not self.selected_type_id:
            messagebox.showerror("Error", "Select a type first")
            return

        version = self.entry_version.get().strip()
        if not version:
            return

        version_date = parse_date(self.entry_version_date.get().strip())

        try:
            self.consent_queries.add_version(self.selected_type_id, version, version_date)
            self.entry_version.delete(0, "end")
            self.entry_version_date.delete(0, "end")
            self._refresh_versions()
        except Exception as e:
            messagebox.showerror("Error", f"Could not add version: {e}")


class ConsentDialog(ctk.CTkToplevel):
    """Dialogue pour enregistrer un consentement."""

    def __init__(self, parent, patient: Dict, consent_queries, consent_data: Optional[Dict] = None):
        super().__init__(parent)

        self.patient = patient
        self.consent_queries = consent_queries
        self.consent_data = consent_data
        self.result = None

        self.title("Edit Consent" if consent_data else "New Consent")
        self.geometry("450x400")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 450) // 2
        y = (self.winfo_screenheight() - 400) // 2
        self.geometry(f"+{x}+{y}")

        self._create_form()

        if consent_data:
            self._fill_form(consent_data)

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

        # Formulaire
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20)

        # Type de consentement
        ctk.CTkLabel(form_frame, text="Consent Type *").pack(anchor="w", pady=(10, 5))

        consent_types = self.consent_queries.get_types()
        type_names = [ct["type_name"] for ct in consent_types]

        self.combo_type = ctk.CTkComboBox(
            form_frame,
            values=type_names if type_names else ["No types available"],
            command=self._on_type_change,
            width=250
        )
        self.combo_type.pack(anchor="w")

        # Version
        ctk.CTkLabel(form_frame, text="Version *").pack(anchor="w", pady=(15, 5))
        self.combo_version = ctk.CTkComboBox(form_frame, values=["Select type first"], width=250)
        self.combo_version.pack(anchor="w")

        # Charger les versions du premier type
        if type_names:
            self._on_type_change(type_names[0])

        # Date de signature
        ctk.CTkLabel(form_frame, text="Signature Date (YYYY-MM-DD) *").pack(anchor="w", pady=(15, 5))
        self.entry_date = ctk.CTkEntry(form_frame, width=150)
        self.entry_date.pack(anchor="w")

        # Commentaires
        ctk.CTkLabel(form_frame, text="Comments").pack(anchor="w", pady=(15, 5))
        self.text_comments = ctk.CTkTextbox(form_frame, height=60, width=350)
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

    def _on_type_change(self, type_name: str) -> None:
        """Charge les versions pour le type sélectionné."""
        consent_types = self.consent_queries.get_types()
        type_id = None
        for ct in consent_types:
            if ct["type_name"] == type_name:
                type_id = ct["id"]
                break

        if type_id:
            versions = self.consent_queries.get_versions(type_id)
            version_names = [f"{v['version']} ({v.get('version_date', '')})" for v in versions]
            self.combo_version.configure(values=version_names if version_names else ["No versions"])
            if version_names:
                self.combo_version.set(version_names[0])

    def _fill_form(self, data: Dict) -> None:
        """Remplit le formulaire."""
        if data.get("type_name"):
            self.combo_type.set(data["type_name"])
            self._on_type_change(data["type_name"])
        if data.get("version"):
            version_str = f"{data['version']} ({data.get('version_date', '')})"
            self.combo_version.set(version_str)
        if data.get("signature_date"):
            self.entry_date.insert(0, str(data["signature_date"]))
        if data.get("comments"):
            self.text_comments.insert("1.0", data["comments"])

    def _save(self) -> None:
        """Sauvegarde le consentement."""
        date_str = self.entry_date.get().strip()
        if not date_str:
            messagebox.showerror("Error", "Signature date is required")
            return

        try:
            parts = date_str.split("-")
            signature_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return

        # Trouver l'ID de la version
        type_name = self.combo_type.get()
        version_str = self.combo_version.get()

        consent_types = self.consent_queries.get_types()
        type_id = None
        for ct in consent_types:
            if ct["type_name"] == type_name:
                type_id = ct["id"]
                break

        if not type_id:
            messagebox.showerror("Error", "Invalid consent type")
            return

        versions = self.consent_queries.get_versions(type_id)
        version_id = None
        for v in versions:
            if version_str.startswith(v["version"]):
                version_id = v["id"]
                break

        if not version_id:
            messagebox.showerror("Error", "Invalid version")
            return

        self.result = {
            "patient_id": self.patient["id"],
            "consent_version_id": version_id,
            "signature_date": signature_date,
            "comments": self.text_comments.get("1.0", "end-1c").strip()
        }

        self.destroy()


class DocumentsFrame(ctk.CTkFrame):
    """Frame de gestion des documents/consentements."""

    def __init__(self, parent, patient_queries, consent_queries):
        super().__init__(parent, fg_color="transparent")

        self.patient_queries = patient_queries
        self.consent_queries = consent_queries
        self.selected_patient = None
        self.patients: List[Dict] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Row 3 pour la liste

        self._create_header()
        self._create_controls()
        self._create_stats_bar()
        self._create_consent_list()

    def _create_header(self) -> None:
        """Crée l'en-tête."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="Documents & Consents",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        # Légende
        legend_frame = ctk.CTkFrame(header, fg_color="transparent")
        legend_frame.grid(row=0, column=2, sticky="e")

        legends = [
            ("Signed", "#5cb85c"),
            ("Missing", "#d9534f"),
            ("New version", "#f0ad4e"),
        ]

        for text, color in legends:
            lf = ctk.CTkFrame(legend_frame, fg_color="transparent")
            lf.pack(side="left", padx=8)
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
        patient_list = [f"{p['patient_number']}" for p in self.patients]

        self.patient_combo = ctk.CTkComboBox(
            controls,
            values=patient_list if patient_list else ["No patients"],
            command=self._on_patient_change,
            width=150
        )
        self.patient_combo.pack(side="left", padx=5)

        # Filtre par type
        ctk.CTkLabel(controls, text="Type:").pack(side="left", padx=(15, 5))

        consent_types = self.consent_queries.get_types()
        type_names = ["All"] + [ct["type_name"] for ct in consent_types]

        self.type_filter = ctk.CTkComboBox(
            controls,
            values=type_names,
            command=self._on_type_filter_change,
            width=150
        )
        self.type_filter.pack(side="left", padx=5)
        self.type_filter.set("All")

        # Indicateur de complétude patient
        self.completeness_label = ctk.CTkLabel(controls, text="", text_color="gray")
        self.completeness_label.pack(side="left", padx=15)

        # Bouton Manage Types
        ctk.CTkButton(
            controls,
            text="Manage Types",
            command=self._manage_types,
            width=100,
            fg_color="transparent",
            border_width=1
        ).pack(side="right", padx=5)

        # Bouton nouveau
        self.btn_new = ctk.CTkButton(
            controls,
            text="+ New Consent",
            command=self._new_consent,
            width=120
        )
        self.btn_new.pack(side="right", padx=10)

    def _create_stats_bar(self) -> None:
        """Crée la barre de statistiques par type d'ICF."""
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        self.stats_labels = {}

        # Les stats seront créées dynamiquement selon les types
        consent_types = self.consent_queries.get_types()

        for ct in consent_types:
            card = ctk.CTkFrame(self.stats_frame, width=130)
            card.pack(side="left", padx=10, pady=10)
            card.pack_propagate(False)

            count_label = ctk.CTkLabel(
                card,
                text="-",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="gray"
            )
            count_label.pack(pady=(10, 0))

            ctk.CTkLabel(
                card,
                text=ct["type_name"][:15],
                font=ctk.CTkFont(size=10),
                text_color="gray"
            ).pack(pady=(0, 10))

            self.stats_labels[ct["id"]] = count_label

    def _create_consent_list(self) -> None:
        """Crée la liste des consentements."""
        self.list_container = ctk.CTkFrame(self, corner_radius=10)
        self.list_container.grid(row=3, column=0, sticky="nsew")
        self.list_container.grid_columnconfigure(0, weight=1)
        self.list_container.grid_rowconfigure(1, weight=1)

        # En-tête
        header = ctk.CTkFrame(self.list_container, fg_color=("gray80", "gray25"))
        header.grid(row=0, column=0, sticky="ew")

        columns = [
            ("Type", 140), ("Version", 80), ("Version Date", 90),
            ("Signature", 90), ("Status", 80), ("Comments", 150), ("Actions", 100)
        ]

        for i, (name, width) in enumerate(columns):
            ctk.CTkLabel(header, text=name, font=ctk.CTkFont(weight="bold"), width=width).grid(
                row=0, column=i, padx=3, pady=8
            )

        # Liste
        self.consent_list = ctk.CTkScrollableFrame(self.list_container, fg_color="transparent")
        self.consent_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Message initial
        self.no_data_label = ctk.CTkLabel(
            self.consent_list,
            text="Select a patient to view consents",
            text_color="gray"
        )
        self.no_data_label.grid(row=0, column=0, columnspan=7, pady=50)

    def _on_search(self, event=None) -> None:
        """Filtre la liste des patients."""
        query = self.search_entry.get().strip().lower()

        if query:
            filtered = [p for p in self.patients if query in p['patient_number'].lower()]
        else:
            filtered = self.patients

        patient_list = [f"{p['patient_number']}" for p in filtered]
        self.patient_combo.configure(values=patient_list if patient_list else ["No patients"])

        if patient_list:
            self.patient_combo.set(patient_list[0])
            self._on_patient_change(patient_list[0])

    def _on_type_filter_change(self, value: str) -> None:
        """Callback changement filtre type."""
        self._refresh_list()

    def _manage_types(self) -> None:
        """Ouvre le dialogue de gestion des types."""
        dialog = ManageTypesDialog(self, self.consent_queries)
        self.wait_window(dialog)
        # Rafraîchir les filtres
        consent_types = self.consent_queries.get_types()
        type_names = ["All"] + [ct["type_name"] for ct in consent_types]
        self.type_filter.configure(values=type_names)
        self._refresh_list()

    def _on_patient_change(self, value: str) -> None:
        """Callback changement patient."""
        if value == "No patients":
            self.selected_patient = None
        else:
            self.selected_patient = self.patient_queries.get_by_number(value)
        self._refresh_list()
        self._update_completeness()

    def _update_completeness(self) -> None:
        """Met à jour l'indicateur de complétude."""
        if not self.selected_patient:
            self.completeness_label.configure(text="", text_color="gray")
            return

        consent_types = self.consent_queries.get_types()
        consents = self.consent_queries.get_patient_consents(self.selected_patient["id"])

        signed_types = set(c.get("type_name") for c in consents)
        all_types = set(ct["type_name"] for ct in consent_types)

        missing = all_types - signed_types

        if not missing:
            self.completeness_label.configure(
                text="All consents signed",
                text_color="#5cb85c"
            )
        else:
            self.completeness_label.configure(
                text=f"Missing: {', '.join(missing)}",
                text_color="#d9534f"
            )

    def _update_stats(self, consents: List[Dict]) -> None:
        """Met à jour les stats par type."""
        # Compter par type
        type_counts = {}
        for c in consents:
            type_name = c.get("type_name", "")
            # Trouver l'ID du type
            for ct in self.consent_queries.get_types():
                if ct["type_name"] == type_name:
                    type_counts[ct["id"]] = type_counts.get(ct["id"], 0) + 1
                    break

        # Mettre à jour les labels
        for type_id, label in self.stats_labels.items():
            count = type_counts.get(type_id, 0)
            if count > 0:
                label.configure(text=str(count), text_color="#5cb85c")
            else:
                label.configure(text="-", text_color="gray")

    def _check_new_version(self, consent: Dict) -> bool:
        """Vérifie si une nouvelle version est disponible."""
        type_name = consent.get("type_name")
        current_version = consent.get("version")

        # Trouver l'ID du type
        consent_types = self.consent_queries.get_types()
        type_id = None
        for ct in consent_types:
            if ct["type_name"] == type_name:
                type_id = ct["id"]
                break

        if not type_id:
            return False

        # Récupérer toutes les versions
        versions = self.consent_queries.get_versions(type_id)
        if not versions:
            return False

        # Comparer avec la dernière version
        latest = versions[-1]["version"]
        return current_version != latest

    def _refresh_list(self) -> None:
        """Rafraîchit la liste."""
        for widget in self.consent_list.winfo_children():
            widget.destroy()

        # Réinitialiser les stats
        for label in self.stats_labels.values():
            label.configure(text="-", text_color="gray")

        if not self.selected_patient:
            self.no_data_label = ctk.CTkLabel(
                self.consent_list,
                text="Select a patient to view consents",
                text_color="gray"
            )
            self.no_data_label.grid(row=0, column=0, columnspan=7, pady=50)
            return

        consents = self.consent_queries.get_patient_consents(self.selected_patient["id"])

        # Filtre par type
        type_filter = self.type_filter.get()
        if type_filter != "All":
            consents = [c for c in consents if c.get("type_name") == type_filter]

        # Mettre à jour les stats
        all_consents = self.consent_queries.get_patient_consents(self.selected_patient["id"])
        self._update_stats(all_consents)

        if not consents:
            ctk.CTkLabel(
                self.consent_list,
                text="No consents recorded",
                text_color="gray"
            ).grid(row=0, column=0, columnspan=7, pady=50)
            return

        for i, consent in enumerate(consents):
            self._add_consent_row(i, consent)

    def _add_consent_row(self, row: int, consent: Dict) -> None:
        """Ajoute une ligne de consentement."""
        row_frame = ctk.CTkFrame(self.consent_list, fg_color=("gray90", "gray17"))
        row_frame.grid(row=row, column=0, sticky="ew", pady=2, padx=5)

        # Type
        ctk.CTkLabel(row_frame, text=consent.get("type_name", ""), width=140).grid(row=0, column=0, padx=3, pady=8)

        # Version
        ctk.CTkLabel(row_frame, text=consent.get("version", ""), width=80).grid(row=0, column=1, padx=3)

        # Version date
        version_date = consent.get("version_date", "")
        if version_date and hasattr(version_date, 'strftime'):
            version_date = version_date.strftime("%Y-%m-%d")
        ctk.CTkLabel(row_frame, text=str(version_date), width=90).grid(row=0, column=2, padx=3)

        # Signature date
        sig_date = consent.get("signature_date", "")
        if sig_date and hasattr(sig_date, 'strftime'):
            sig_date = sig_date.strftime("%Y-%m-%d")
        ctk.CTkLabel(row_frame, text=str(sig_date), width=90).grid(row=0, column=3, padx=3)

        # Status (nouvelle version disponible?)
        has_new_version = self._check_new_version(consent)
        if has_new_version:
            status_text = "Update"
            status_color = "#f0ad4e"
        else:
            status_text = "Current"
            status_color = "#5cb85c"

        ctk.CTkLabel(
            row_frame,
            text=status_text,
            text_color=status_color,
            width=80
        ).grid(row=0, column=4, padx=3)

        # Comments
        comments = consent.get("comments", "") or ""
        if len(comments) > 20:
            comments = comments[:20] + "..."
        ctk.CTkLabel(row_frame, text=comments, width=150, anchor="w").grid(row=0, column=5, padx=3)

        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=100)
        actions_frame.grid(row=0, column=6, padx=3)

        ctk.CTkButton(
            actions_frame,
            text="Edit",
            width=45,
            height=25,
            command=lambda c=consent: self._edit_consent(c)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions_frame,
            text="Del",
            width=45,
            height=25,
            fg_color="#d9534f",
            hover_color="#c9302c",
            command=lambda c=consent: self._delete_consent(c)
        ).pack(side="left", padx=2)

    def _new_consent(self) -> None:
        """Ajoute un nouveau consentement."""
        if not self.selected_patient:
            messagebox.showerror("Error", "Please select a patient first")
            return

        dialog = ConsentDialog(self, self.selected_patient, self.consent_queries)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.consent_queries.record_consent(**dialog.result)
                self._refresh_list()
                self._update_completeness()
            except Exception as e:
                messagebox.showerror("Error", f"Could not save consent: {e}")

    def _edit_consent(self, consent: Dict) -> None:
        """Modifie un consentement existant."""
        dialog = ConsentDialog(self, self.selected_patient, self.consent_queries, consent)
        self.wait_window(dialog)

        if dialog.result:
            try:
                # Mettre à jour le consentement
                cursor = self.consent_queries.conn.cursor()
                cursor.execute("""
                    UPDATE patient_consents
                    SET consent_version_id = ?, signature_date = ?, comments = ?
                    WHERE id = ?
                """, (
                    dialog.result["consent_version_id"],
                    dialog.result["signature_date"],
                    dialog.result["comments"],
                    consent["id"]
                ))
                self.consent_queries.conn.commit()
                self._refresh_list()
                self._update_completeness()
            except Exception as e:
                messagebox.showerror("Error", f"Could not update consent: {e}")

    def _delete_consent(self, consent: Dict) -> None:
        """Supprime un consentement."""
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete {consent.get('type_name')} consent for this patient?\n\nThis action cannot be undone."
        )

        if confirm:
            try:
                cursor = self.consent_queries.conn.cursor()
                cursor.execute("DELETE FROM patient_consents WHERE id = ?", (consent["id"],))
                self.consent_queries.conn.commit()
                self._refresh_list()
                self._update_completeness()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete consent: {e}")
