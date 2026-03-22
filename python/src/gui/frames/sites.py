"""
Gestion des sites/centres investigateurs.
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict, List
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


class SiteDialog(ctk.CTkToplevel):
    """Dialogue pour ajouter/modifier un site."""

    def __init__(self, parent, db, site_data: Optional[Dict] = None):
        super().__init__(parent)

        self.db = db
        self.site_data = site_data
        self.result = None

        self.title("Edit Site" if site_data else "New Site")
        self.geometry("500x550")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 550) // 2
        self.geometry(f"+{x}+{y}")

        self._create_form()

        if site_data:
            self._fill_form(site_data)

    def _create_form(self) -> None:
        """Crée le formulaire."""
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Numéro de site
        ctk.CTkLabel(scroll_frame, text="Site Number *").pack(anchor="w", pady=(0, 5))
        self.entry_number = ctk.CTkEntry(scroll_frame, width=150, placeholder_text="e.g., 001")
        self.entry_number.pack(anchor="w", pady=(0, 10))

        # Nom du site
        ctk.CTkLabel(scroll_frame, text="Site Name").pack(anchor="w", pady=(0, 5))
        self.entry_name = ctk.CTkEntry(scroll_frame, width=400)
        self.entry_name.pack(anchor="w", pady=(0, 10))

        # Adresse
        ctk.CTkLabel(scroll_frame, text="Address").pack(anchor="w", pady=(0, 5))
        self.entry_address = ctk.CTkEntry(scroll_frame, width=400)
        self.entry_address.pack(anchor="w", pady=(0, 10))

        # Ville et Pays sur la même ligne
        row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=(0, 10))

        city_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        city_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(city_frame, text="City").pack(anchor="w", pady=(0, 5))
        self.entry_city = ctk.CTkEntry(city_frame, width=180)
        self.entry_city.pack(anchor="w")

        country_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        country_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(country_frame, text="Country").pack(anchor="w", pady=(0, 5))
        self.entry_country = ctk.CTkEntry(country_frame, width=180)
        self.entry_country.pack(anchor="w")

        # Téléphone et Email
        row_frame2 = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        row_frame2.pack(fill="x", pady=(0, 10))

        phone_frame = ctk.CTkFrame(row_frame2, fg_color="transparent")
        phone_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(phone_frame, text="Phone").pack(anchor="w", pady=(0, 5))
        self.entry_phone = ctk.CTkEntry(phone_frame, width=180)
        self.entry_phone.pack(anchor="w")

        email_frame = ctk.CTkFrame(row_frame2, fg_color="transparent")
        email_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(email_frame, text="Email").pack(anchor="w", pady=(0, 5))
        self.entry_email = ctk.CTkEntry(email_frame, width=180)
        self.entry_email.pack(anchor="w")

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
        self.entry_number.insert(0, data.get("site_number", "") or "")
        self.entry_name.insert(0, data.get("site_name", "") or "")
        self.entry_address.insert(0, data.get("address", "") or "")
        self.entry_city.insert(0, data.get("city", "") or "")
        self.entry_country.insert(0, data.get("country", "") or "")
        self.entry_phone.insert(0, data.get("phone", "") or "")
        self.entry_email.insert(0, data.get("email", "") or "")

    def _save(self) -> None:
        """Sauvegarde le site."""
        site_number = self.entry_number.get().strip()
        if not site_number:
            messagebox.showerror("Error", "Site number is required")
            return

        self.result = {
            "site_number": site_number,
            "site_name": self.entry_name.get().strip(),
            "address": self.entry_address.get().strip(),
            "city": self.entry_city.get().strip(),
            "country": self.entry_country.get().strip(),
            "phone": self.entry_phone.get().strip(),
            "email": self.entry_email.get().strip()
        }

        self.destroy()


class StudySiteDialog(ctk.CTkToplevel):
    """Dialogue pour modifier les infos spécifiques à l'étude pour un site."""

    def __init__(self, parent, db, study_site_data: Dict):
        super().__init__(parent)

        self.db = db
        self.study_site_data = study_site_data
        self.result = None

        site_number = study_site_data.get("site_number", "")
        self.title(f"Site {site_number} - Study Details")
        self.geometry("500x500")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 500) // 2
        self.geometry(f"+{x}+{y}")

        self._create_form()
        self._fill_form(study_site_data)

    def _create_form(self) -> None:
        """Crée le formulaire."""
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Info site (lecture seule)
        info_frame = ctk.CTkFrame(scroll_frame, fg_color=("gray85", "gray20"))
        info_frame.pack(fill="x", pady=(0, 15))

        site_info = f"{self.study_site_data.get('site_number', '')} - {self.study_site_data.get('site_name', '')}"
        ctk.CTkLabel(
            info_frame,
            text=site_info,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(padx=15, pady=10)

        city = self.study_site_data.get("city", "") or ""
        country = self.study_site_data.get("country", "") or ""
        location = f"{city}, {country}" if city and country else city or country
        if location:
            ctk.CTkLabel(info_frame, text=location, text_color="gray").pack(padx=15, pady=(0, 10))

        # Statut
        ctk.CTkLabel(scroll_frame, text="Status").pack(anchor="w", pady=(0, 5))
        self.combo_status = ctk.CTkComboBox(
            scroll_frame,
            values=["Active", "On Hold", "Closed"],
            width=150
        )
        self.combo_status.pack(anchor="w", pady=(0, 15))

        # Investigateur principal (spécifique à l'étude)
        ctk.CTkLabel(scroll_frame, text="Principal Investigator (for this study)").pack(anchor="w", pady=(0, 5))
        self.entry_pi = ctk.CTkEntry(scroll_frame, width=400, placeholder_text="Dr. Name")
        self.entry_pi.pack(anchor="w", pady=(0, 15))

        # Date d'activation
        ctk.CTkLabel(scroll_frame, text="Activation Date").pack(anchor="w", pady=(0, 5))
        self.entry_activation = ctk.CTkEntry(scroll_frame, width=150, placeholder_text="YYYY-MM-DD")
        self.entry_activation.pack(anchor="w", pady=(0, 15))

        # Date première inclusion
        ctk.CTkLabel(scroll_frame, text="First Patient Date").pack(anchor="w", pady=(0, 5))
        self.entry_first_patient = ctk.CTkEntry(scroll_frame, width=150, placeholder_text="YYYY-MM-DD")
        self.entry_first_patient.pack(anchor="w", pady=(0, 15))

        # Objectif de recrutement
        ctk.CTkLabel(scroll_frame, text="Recruitment Target").pack(anchor="w", pady=(0, 5))
        self.entry_target = ctk.CTkEntry(scroll_frame, width=100, placeholder_text="0")
        self.entry_target.pack(anchor="w", pady=(0, 15))

        # Commentaires
        ctk.CTkLabel(scroll_frame, text="Comments").pack(anchor="w", pady=(0, 5))
        self.text_comments = ctk.CTkTextbox(scroll_frame, width=400, height=80)
        self.text_comments.pack(anchor="w", pady=(0, 10))

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
        self.combo_status.set(data.get("status", "Active") or "Active")

        pi = data.get("principal_investigator", "") or ""
        if pi:
            self.entry_pi.insert(0, pi)

        activation = data.get("activation_date", "") or ""
        if activation:
            self.entry_activation.insert(0, str(activation)[:10])

        first_patient = data.get("first_patient_date", "") or ""
        if first_patient:
            self.entry_first_patient.insert(0, str(first_patient)[:10])

        target = data.get("target_patients", 0) or 0
        self.entry_target.insert(0, str(target))

        comments = data.get("comments", "") or ""
        if comments:
            self.text_comments.insert("1.0", comments)

    def _save(self) -> None:
        """Sauvegarde les modifications."""
        try:
            target = int(self.entry_target.get() or 0)
        except ValueError:
            target = 0

        activation_date = self.entry_activation.get().strip() or None
        first_patient_date = self.entry_first_patient.get().strip() or None

        self.result = {
            "status": self.combo_status.get(),
            "principal_investigator": self.entry_pi.get().strip(),
            "activation_date": activation_date,
            "first_patient_date": first_patient_date,
            "target_patients": target,
            "comments": self.text_comments.get("1.0", "end-1c").strip()
        }

        self.destroy()


class SelectOrCreateSiteDialog(ctk.CTkToplevel):
    """Dialogue pour sélectionner un site existant ou en créer un nouveau."""

    def __init__(self, parent, db, study_id: int):
        super().__init__(parent)

        self.db = db
        self.study_id = study_id
        self.result = None
        self.selected_site_ids = []

        self.title("Add Site to Study")
        self.geometry("600x400")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 600) // 2
        y = (self.winfo_screenheight() - 400) // 2
        self.geometry(f"+{x}+{y}")

        # Sites disponibles (non encore dans l'étude)
        self.available_sites = self.db.get_sites_not_in_study(study_id)

        self._create_ui()

    def _create_ui(self) -> None:
        """Crée l'interface."""
        # En-tête
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text="Select a site",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="+ Create New Site",
            command=self._create_new_site,
            width=140
        ).pack(side="right")

        # Liste des sites disponibles
        list_frame = ctk.CTkFrame(self, corner_radius=10)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # En-tête de liste
        list_header = ctk.CTkFrame(list_frame, fg_color=("gray80", "gray25"))
        list_header.pack(fill="x")

        ctk.CTkLabel(list_header, text="Site #", width=80, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=8)
        ctk.CTkLabel(list_header, text="Name", width=250, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=8)
        ctk.CTkLabel(list_header, text="City", width=150, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=8)

        # Liste scrollable
        self.sites_list = ctk.CTkScrollableFrame(list_frame, fg_color="transparent")
        self.sites_list.pack(fill="both", expand=True, padx=5, pady=5)

        self._refresh_sites_list()

        # Boutons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="transparent",
            border_width=1
        ).pack(side="left", padx=5)

        self.btn_add = ctk.CTkButton(
            btn_frame,
            text="Add Selected Site",
            command=self._save,
            state="disabled"
        )
        self.btn_add.pack(side="right", padx=5)

    def _refresh_sites_list(self) -> None:
        """Rafraîchit la liste des sites."""
        for widget in self.sites_list.winfo_children():
            widget.destroy()

        self.available_sites = self.db.get_sites_not_in_study(self.study_id)

        if not self.available_sites:
            ctk.CTkLabel(
                self.sites_list,
                text="No available sites. Create a new one.",
                text_color="gray"
            ).pack(pady=30)
            return

        self.site_checkboxes = {}

        for site in self.available_sites:
            row = ctk.CTkFrame(self.sites_list, fg_color="transparent")
            row.pack(fill="x", pady=2)

            # Checkbox
            var = ctk.BooleanVar(value=False)
            checkbox = ctk.CTkCheckBox(
                row,
                text="",
                variable=var,
                command=self._on_site_selected,
                width=20
            )
            checkbox.pack(side="left", padx=5)

            # Infos du site
            ctk.CTkLabel(row, text=site.get("site_number", "") or "-", width=70).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=site.get("site_name", "") or "-", width=240, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=site.get("city", "") or "-", width=140).pack(side="left", padx=5)

            self.site_checkboxes[site["id"]] = var

    def _on_site_selected(self) -> None:
        """Callback quand un site est sélectionné."""
        selected_ids = [sid for sid, var in self.site_checkboxes.items() if var.get()]
        if selected_ids:
            self.selected_site_ids = selected_ids
            count = len(selected_ids)
            self.btn_add.configure(state="normal", text=f"Add {count} Site{'s' if count > 1 else ''}")
        else:
            self.selected_site_ids = []
            self.btn_add.configure(state="disabled", text="Add Selected Site")

    def _create_new_site(self) -> None:
        """Ouvre le dialogue de création de site."""
        dialog = SiteDialog(self, self.db)
        self.wait_window(dialog)

        if dialog.result:
            try:
                site_id = self.db.create_site(**dialog.result)
                # Rafraîchir la liste et cocher le nouveau site
                self._refresh_sites_list()
                if site_id in self.site_checkboxes:
                    self.site_checkboxes[site_id].set(True)
                    self._on_site_selected()
            except Exception as e:
                if "UNIQUE constraint" in str(e):
                    messagebox.showerror("Error", "A site with this number already exists")
                else:
                    messagebox.showerror("Error", f"Could not create site: {e}")

    def _save(self) -> None:
        """Sauvegarde."""
        if not self.selected_site_ids:
            messagebox.showerror("Error", "Please select at least one site")
            return

        self.result = {
            "site_ids": self.selected_site_ids
        }

        self.destroy()


class SitesFrame(ctk.CTkFrame):
    """Frame de gestion des sites."""

    def __init__(self, parent, db, current_study: Optional[Dict] = None):
        super().__init__(parent, fg_color="transparent")

        self.db = db
        self.current_study = current_study

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._create_header()
        self._create_stats_bar()
        self._create_search_bar()
        self._create_site_list()

        self.refresh_data()

    def _create_header(self) -> None:
        """Crée l'en-tête."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header.grid_columnconfigure(1, weight=1)

        # Titre
        ctk.CTkLabel(
            header,
            text="Sites",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        # Légende
        legend_frame = ctk.CTkFrame(header, fg_color="transparent")
        legend_frame.grid(row=0, column=1, sticky="e", padx=20)

        statuses = [
            ("Active", "#5cb85c"),
            ("On Hold", "#f0ad4e"),
            ("Closed", "#d9534f")
        ]
        for status, color in statuses:
            item = ctk.CTkFrame(legend_frame, fg_color="transparent")
            item.pack(side="left", padx=10)
            ctk.CTkFrame(item, width=12, height=12, fg_color=color, corner_radius=2).pack(side="left", padx=(0, 5))
            ctk.CTkLabel(item, text=status, font=ctk.CTkFont(size=11)).pack(side="left")

        # Bouton
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.grid(row=0, column=2, sticky="e")

        if self.current_study:
            ctk.CTkButton(
                btn_frame,
                text="+ Add Site",
                command=self._add_site_to_study,
                width=100
            ).pack(side="left", padx=5)
        else:
            ctk.CTkButton(
                btn_frame,
                text="+ New Site",
                command=self._new_site,
                width=100
            ).pack(side="left", padx=5)

    def _create_stats_bar(self) -> None:
        """Crée la barre de statistiques."""
        self.stats_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray17"), corner_radius=8)
        self.stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        self.stats_labels = {}
        stats = [
            ("total", "Total", "#6c757d"),
            ("active", "Active", "#5cb85c"),
            ("on_hold", "On Hold", "#f0ad4e"),
            ("closed", "Closed", "#d9534f"),
            ("patients", "Patients", "#17a2b8")
        ]

        for i, (key, label, color) in enumerate(stats):
            frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
            frame.pack(side="left", padx=20, pady=10)

            self.stats_labels[key] = ctk.CTkLabel(
                frame,
                text="0",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=color
            )
            self.stats_labels[key].pack()

            ctk.CTkLabel(
                frame,
                text=label,
                font=ctk.CTkFont(size=11),
                text_color="gray"
            ).pack()

    def _create_search_bar(self) -> None:
        """Crée la barre de recherche."""
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search sites...",
            width=300
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self._on_search)

        # Filtre statut
        ctk.CTkLabel(search_frame, text="Status:").pack(side="left", padx=(20, 5))
        self.filter_status = ctk.CTkComboBox(
            search_frame,
            values=["All", "Active", "On Hold", "Closed"],
            width=120,
            command=self._on_filter_change
        )
        self.filter_status.pack(side="left")
        self.filter_status.set("All")

    def _create_site_list(self) -> None:
        """Crée la liste des sites."""
        container = ctk.CTkFrame(self, corner_radius=10)
        container.grid(row=3, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)

        # En-tête
        header = ctk.CTkFrame(container, fg_color=("gray80", "gray25"), corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")

        # Colonnes différentes selon le contexte
        if self.current_study:
            columns = [
                ("Site #", 70),
                ("Name", 150),
                ("PI", 120),
                ("Status", 70),
                ("Activation", 90),
                ("Target", 55),
                ("Incl.", 50),
                ("Actions", 100)
            ]
        else:
            columns = [
                ("Site #", 80),
                ("Name", 220),
                ("City", 150),
                ("Status", 80),
                ("Patients", 70),
                ("Actions", 120)
            ]

        for i, (name, width) in enumerate(columns):
            ctk.CTkLabel(
                header,
                text=name,
                font=ctk.CTkFont(weight="bold"),
                width=width
            ).grid(row=0, column=i, padx=3, pady=10)

        # Liste scrollable
        self.site_list = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.site_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def refresh_data(self, search: str = "", status_filter: str = "All") -> None:
        """Rafraîchit la liste des sites."""
        for widget in self.site_list.winfo_children():
            widget.destroy()

        # Récupérer les sites
        if self.current_study:
            sites = self.db.get_study_sites(self.current_study["id"])
        else:
            sites = self.db.get_all_sites()
            # Ajouter patient_count = 0 pour les sites sans étude
            for s in sites:
                s["patient_count"] = 0
                s["status"] = "N/A"

        # Filtrer par recherche
        if search:
            search_lower = search.lower()
            sites = [s for s in sites if
                     search_lower in (s.get("site_number", "") or "").lower() or
                     search_lower in (s.get("site_name", "") or "").lower() or
                     search_lower in (s.get("principal_investigator", "") or "").lower() or
                     search_lower in (s.get("city", "") or "").lower()]

        # Filtrer par statut
        if status_filter != "All":
            sites = [s for s in sites if s.get("status") == status_filter]

        # Mettre à jour les stats
        self._update_stats(sites)

        # Afficher les sites
        if not sites:
            ctk.CTkLabel(
                self.site_list,
                text="No sites found",
                text_color="gray"
            ).grid(row=0, column=0, columnspan=7, pady=50)
            return

        for i, site in enumerate(sites):
            self._add_site_row(i, site)

    def _update_stats(self, sites: List[Dict]) -> None:
        """Met à jour les statistiques."""
        total = len(sites)
        active = len([s for s in sites if s.get("status") == "Active"])
        on_hold = len([s for s in sites if s.get("status") == "On Hold"])
        closed = len([s for s in sites if s.get("status") == "Closed"])
        patients = sum(s.get("patient_count", 0) or 0 for s in sites)

        self.stats_labels["total"].configure(text=str(total))
        self.stats_labels["active"].configure(text=str(active))
        self.stats_labels["on_hold"].configure(text=str(on_hold))
        self.stats_labels["closed"].configure(text=str(closed))
        self.stats_labels["patients"].configure(text=str(patients))

    def _add_site_row(self, row: int, site: Dict) -> None:
        """Ajoute une ligne de site."""
        status = site.get("status", "N/A")
        status_colors = {
            "Active": ("#e8f5e9", "#1b3d1b"),
            "On Hold": ("#fff8e1", "#3d3520"),
            "Closed": ("#ffebee", "#3d1b1b"),
            "N/A": ("gray90", "gray17")
        }
        row_color = status_colors.get(status, ("gray90", "gray17"))

        row_frame = ctk.CTkFrame(self.site_list, fg_color=row_color)
        row_frame.grid(row=row, column=0, sticky="ew", pady=2)

        status_badge_colors = {
            "Active": "#5cb85c",
            "On Hold": "#f0ad4e",
            "Closed": "#d9534f",
            "N/A": "#6c757d"
        }

        if self.current_study:
            # Affichage contexte étude (avec PI, activation, target, etc.)
            col = 0

            # Site number
            ctk.CTkLabel(
                row_frame,
                text=site.get("site_number", "") or "-",
                width=70
            ).grid(row=0, column=col, padx=3, pady=8)
            col += 1

            # Name
            ctk.CTkLabel(
                row_frame,
                text=site.get("site_name", "") or "-",
                width=150,
                anchor="w"
            ).grid(row=0, column=col, padx=3, pady=8)
            col += 1

            # PI
            pi = site.get("principal_investigator", "") or "-"
            if len(pi) > 15:
                pi = pi[:14] + "..."
            ctk.CTkLabel(
                row_frame,
                text=pi,
                width=120,
                anchor="w"
            ).grid(row=0, column=col, padx=3, pady=8)
            col += 1

            # Status badge
            ctk.CTkLabel(
                row_frame,
                text=status,
                font=ctk.CTkFont(size=11),
                text_color=status_badge_colors.get(status, "#6c757d"),
                width=70
            ).grid(row=0, column=col, padx=3, pady=8)
            col += 1

            # Activation date
            activation = site.get("activation_date", "") or ""
            if activation:
                activation = str(activation)[:10]
            ctk.CTkLabel(
                row_frame,
                text=activation or "-",
                width=90,
                font=ctk.CTkFont(size=11)
            ).grid(row=0, column=col, padx=3, pady=8)
            col += 1

            # Target
            target = site.get("target_patients", 0) or 0
            patient_count = site.get("patient_count", 0) or 0
            target_text = f"{patient_count}/{target}" if target > 0 else str(patient_count)
            # Couleur selon progression
            if target > 0:
                if patient_count >= target:
                    target_color = "#5cb85c"  # Vert - objectif atteint
                elif patient_count >= target * 0.5:
                    target_color = "#f0ad4e"  # Orange - en cours
                else:
                    target_color = "#6c757d"  # Gris - début
            else:
                target_color = "#6c757d"
            ctk.CTkLabel(
                row_frame,
                text=target_text,
                width=55,
                text_color=target_color,
                font=ctk.CTkFont(size=11)
            ).grid(row=0, column=col, padx=3, pady=8)
            col += 1

            # First patient date (FPI)
            fpi = site.get("first_patient_date", "") or ""
            if fpi:
                fpi = str(fpi)[:10]
            ctk.CTkLabel(
                row_frame,
                text=fpi or "-",
                width=50,
                font=ctk.CTkFont(size=11)
            ).grid(row=0, column=col, padx=3, pady=8)
            col += 1

            # Actions
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=100)
            actions_frame.grid(row=0, column=col, padx=3, pady=8)

            ctk.CTkButton(
                actions_frame,
                text="Edit",
                width=45,
                height=25,
                command=lambda s=site: self._edit_study_site(s)
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                actions_frame,
                text="Del",
                width=45,
                height=25,
                fg_color="#d9534f",
                hover_color="#c9302c",
                command=lambda s=site: self._delete_site(s)
            ).pack(side="left", padx=2)

        else:
            # Affichage global (tous les sites sans contexte étude)
            # Site number
            ctk.CTkLabel(
                row_frame,
                text=site.get("site_number", "") or "-",
                width=80
            ).grid(row=0, column=0, padx=5, pady=8)

            # Name
            ctk.CTkLabel(
                row_frame,
                text=site.get("site_name", "") or "-",
                width=220,
                anchor="w"
            ).grid(row=0, column=1, padx=5, pady=8)

            # City
            ctk.CTkLabel(
                row_frame,
                text=site.get("city", "") or "-",
                width=150
            ).grid(row=0, column=2, padx=5, pady=8)

            # Status badge
            ctk.CTkLabel(
                row_frame,
                text=status,
                font=ctk.CTkFont(size=11),
                text_color=status_badge_colors.get(status, "#6c757d"),
                width=80
            ).grid(row=0, column=3, padx=5, pady=8)

            # Patients count
            patient_count = site.get("patient_count", 0) or 0
            ctk.CTkLabel(
                row_frame,
                text=str(patient_count),
                width=70
            ).grid(row=0, column=4, padx=5, pady=8)

            # Actions
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=120)
            actions_frame.grid(row=0, column=5, padx=5, pady=8)

            ctk.CTkButton(
                actions_frame,
                text="Edit",
                width=50,
                height=25,
                command=lambda s=site: self._edit_site(s)
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                actions_frame,
                text="Del",
                width=50,
                height=25,
                fg_color="#d9534f",
                hover_color="#c9302c",
                command=lambda s=site: self._delete_site(s)
            ).pack(side="left", padx=2)

    def _new_site(self) -> None:
        """Crée un nouveau site (quand pas d'étude sélectionnée)."""
        dialog = SiteDialog(self, self.db)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.db.create_site(**dialog.result)
                self.refresh_data()
            except Exception as e:
                if "UNIQUE constraint" in str(e):
                    messagebox.showerror("Error", "A site with this number already exists")
                else:
                    messagebox.showerror("Error", f"Could not create site: {e}")

    def _add_site_to_study(self) -> None:
        """Ouvre le dialogue pour sélectionner ou créer un site."""
        if not self.current_study:
            return

        dialog = SelectOrCreateSiteDialog(self, self.db, self.current_study["id"])
        self.wait_window(dialog)

        if dialog.result:
            try:
                for site_id in dialog.result["site_ids"]:
                    self.db.add_site_to_study(
                        self.current_study["id"],
                        site_id,
                        status="Active"
                    )
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Could not add site: {e}")

    def _edit_site(self, site: Dict) -> None:
        """Modifie un site (informations générales)."""
        # Récupérer les données complètes du site
        site_data = self.db.get_site_by_id(site.get("site_id") or site.get("id"))
        if not site_data:
            messagebox.showerror("Error", "Site not found")
            return

        dialog = SiteDialog(self, self.db, site_data)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.db.update_site(site_data["id"], **dialog.result)
                self.refresh_data()
            except Exception as e:
                if "UNIQUE constraint" in str(e):
                    messagebox.showerror("Error", "A site with this number already exists")
                else:
                    messagebox.showerror("Error", f"Could not update site: {e}")

    def _edit_study_site(self, site: Dict) -> None:
        """Modifie les infos spécifiques à l'étude pour un site."""
        if not self.current_study:
            return

        # Récupérer les données complètes de la liaison study_site
        study_site_data = self.db.get_study_site_by_id(site["id"])
        if not study_site_data:
            messagebox.showerror("Error", "Study site not found")
            return

        dialog = StudySiteDialog(self, self.db, study_site_data)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.db.update_study_site(site["id"], **dialog.result)
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Could not update site: {e}")

    def _delete_site(self, site: Dict) -> None:
        """Supprime un site."""
        site_number = site.get("site_number", "")

        if self.current_study:
            # Retirer de l'étude seulement
            if not messagebox.askyesno(
                "Confirm",
                f"Remove site {site_number} from this study?"
            ):
                return

            try:
                self.db.remove_site_from_study(site["id"])
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Could not remove site: {e}")
        else:
            # Supprimer complètement
            if not messagebox.askyesno(
                "Confirm",
                f"Delete site {site_number} permanently?\nThis will remove it from all studies."
            ):
                return

            try:
                self.db.delete_site(site["id"])
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete site: {e}")

    def _on_search(self, event=None) -> None:
        """Callback pour la recherche."""
        self.refresh_data(
            search=self.search_entry.get(),
            status_filter=self.filter_status.get()
        )

    def _on_filter_change(self, value: str) -> None:
        """Callback pour le changement de filtre."""
        self.refresh_data(
            search=self.search_entry.get(),
            status_filter=value
        )
