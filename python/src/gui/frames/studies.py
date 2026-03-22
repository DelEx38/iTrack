"""
Gestion des études cliniques.
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict, List


class VendorDialog(ctk.CTkToplevel):
    """Dialogue pour ajouter/modifier un vendor."""

    def __init__(self, parent, vendor_types: List[Dict], vendor_data: Optional[Dict] = None):
        super().__init__(parent)

        self.vendor_types = vendor_types
        self.vendor_data = vendor_data
        self.result = None

        # Configuration de la fenêtre
        self.title("Modifier Vendor" if vendor_data else "Ajouter Vendor")
        self.geometry("400x300")
        self.resizable(False, False)

        # Rendre modale
        self.transient(parent)
        self.grab_set()

        # Centrer
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 400) // 2
        y = (self.winfo_screenheight() - 300) // 2
        self.geometry(f"+{x}+{y}")

        self._create_form()

        if vendor_data:
            self._fill_form(vendor_data)

    def _create_form(self) -> None:
        """Crée le formulaire."""
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Type de vendor
        ctk.CTkLabel(form_frame, text="Type de vendor *").pack(anchor="w", pady=(0, 5))
        type_names = [vt["type_name"] for vt in self.vendor_types]
        self.combo_type = ctk.CTkComboBox(form_frame, values=type_names, width=300)
        self.combo_type.pack(anchor="w", pady=(0, 15))
        if type_names:
            self.combo_type.set(type_names[0])

        # Nom du vendor
        ctk.CTkLabel(form_frame, text="Nom du vendor *").pack(anchor="w", pady=(0, 5))
        self.entry_name = ctk.CTkEntry(form_frame, width=300)
        self.entry_name.pack(anchor="w", pady=(0, 15))

        # Contact
        ctk.CTkLabel(form_frame, text="Contact").pack(anchor="w", pady=(0, 5))
        self.entry_contact = ctk.CTkEntry(form_frame, width=300)
        self.entry_contact.pack(anchor="w", pady=(0, 15))

        # Boutons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Annuler",
            command=self.destroy,
            fg_color="transparent",
            border_width=1
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Enregistrer",
            command=self._save
        ).pack(side="right", padx=5)

    def _fill_form(self, data: Dict) -> None:
        """Remplit le formulaire avec les données existantes."""
        if data.get("type_name"):
            self.combo_type.set(data["type_name"])
        self.entry_name.insert(0, data.get("vendor_name", ""))
        self.entry_contact.insert(0, data.get("contact", "") or "")

    def _save(self) -> None:
        """Sauvegarde le vendor."""
        vendor_name = self.entry_name.get().strip()
        type_name = self.combo_type.get()

        if not vendor_name:
            messagebox.showerror("Erreur", "Le nom du vendor est requis")
            return

        if not type_name:
            messagebox.showerror("Erreur", "Le type de vendor est requis")
            return

        # Trouver l'ID du type
        vendor_type_id = None
        for vt in self.vendor_types:
            if vt["type_name"] == type_name:
                vendor_type_id = vt["id"]
                break

        self.result = {
            "vendor_type_id": vendor_type_id,
            "type_name": type_name,
            "vendor_name": vendor_name,
            "contact": self.entry_contact.get().strip()
        }

        self.destroy()


class StudyDialog(ctk.CTkToplevel):
    """Dialogue pour ajouter/modifier une étude."""

    def __init__(self, parent, db, study_data: Optional[Dict] = None):
        super().__init__(parent)

        self.db = db
        self.study_data = study_data
        self.result = None
        self.vendors_to_add = []  # Nouveaux vendors à ajouter
        self.vendors_to_delete = []  # Vendors à supprimer
        self.existing_vendors = []  # Vendors existants (pour affichage)

        # Configuration de la fenêtre
        self.title("Modifier Étude" if study_data else "Nouvelle Étude")
        self.geometry("700x700")
        self.resizable(True, True)
        self.minsize(600, 500)

        # Rendre modale
        self.transient(parent)
        self.grab_set()

        # Centrer
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 700) // 2
        y = (self.winfo_screenheight() - 700) // 2
        self.geometry(f"+{x}+{y}")

        self._create_tabs()

        if study_data:
            self._fill_form(study_data)
            self._load_vendors()

    def _create_tabs(self) -> None:
        """Crée les onglets."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(20, 10))

        # Onglet Informations
        self.tab_info = self.tabview.add("Informations")
        self._create_info_tab()

        # Onglet Vendors
        self.tab_vendors = self.tabview.add("Vendors")
        self._create_vendors_tab()

        # Boutons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkButton(
            btn_frame,
            text="Annuler",
            command=self.destroy,
            fg_color="transparent",
            border_width=1
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Enregistrer",
            command=self._save
        ).pack(side="right", padx=5)

    def _create_info_tab(self) -> None:
        """Crée l'onglet des informations."""
        scroll_frame = ctk.CTkScrollableFrame(self.tab_info, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True)

        # Numéro d'étude
        ctk.CTkLabel(scroll_frame, text="Numéro d'étude *").pack(anchor="w", pady=(10, 5))
        self.entry_study_number = ctk.CTkEntry(scroll_frame, width=400)
        self.entry_study_number.pack(anchor="w", pady=(0, 10))

        # Nom de l'étude
        ctk.CTkLabel(scroll_frame, text="Nom de l'étude").pack(anchor="w", pady=(0, 5))
        self.entry_study_name = ctk.CTkEntry(scroll_frame, width=400)
        self.entry_study_name.pack(anchor="w", pady=(0, 10))

        # Numéro EU CT
        ctk.CTkLabel(scroll_frame, text="Numéro EU CT").pack(anchor="w", pady=(0, 5))
        self.entry_eu_ct = ctk.CTkEntry(scroll_frame, width=400)
        self.entry_eu_ct.pack(anchor="w", pady=(0, 10))

        # Numéro NCT
        ctk.CTkLabel(scroll_frame, text="Numéro NCT").pack(anchor="w", pady=(0, 5))
        self.entry_nct = ctk.CTkEntry(scroll_frame, width=400)
        self.entry_nct.pack(anchor="w", pady=(0, 10))

        # Phase
        ctk.CTkLabel(scroll_frame, text="Phase").pack(anchor="w", pady=(0, 5))
        self.combo_phase = ctk.CTkComboBox(
            scroll_frame,
            values=["", "I", "I/II", "II", "II/III", "III", "III/IV", "IV"],
            width=150
        )
        self.combo_phase.pack(anchor="w", pady=(0, 10))
        self.combo_phase.set("")

        # Produit à l'étude
        ctk.CTkLabel(scroll_frame, text="Produit à l'étude").pack(anchor="w", pady=(0, 5))
        self.entry_product = ctk.CTkEntry(scroll_frame, width=400)
        self.entry_product.pack(anchor="w", pady=(0, 10))

        # Comparateur
        ctk.CTkLabel(scroll_frame, text="Comparateur").pack(anchor="w", pady=(0, 5))
        self.entry_comparator = ctk.CTkEntry(scroll_frame, width=400)
        self.entry_comparator.pack(anchor="w", pady=(0, 10))

        # Pathologie
        ctk.CTkLabel(scroll_frame, text="Pathologie").pack(anchor="w", pady=(0, 5))
        self.entry_pathology = ctk.CTkEntry(scroll_frame, width=400)
        self.entry_pathology.pack(anchor="w", pady=(0, 10))

        # Titre de l'étude
        ctk.CTkLabel(scroll_frame, text="Titre de l'étude").pack(anchor="w", pady=(0, 5))
        self.entry_title = ctk.CTkEntry(scroll_frame, width=400)
        self.entry_title.pack(anchor="w", pady=(0, 10))

        # Sponsor
        ctk.CTkLabel(scroll_frame, text="Sponsor").pack(anchor="w", pady=(0, 5))
        self.entry_sponsor = ctk.CTkEntry(scroll_frame, width=400)
        self.entry_sponsor.pack(anchor="w", pady=(0, 10))

    def _create_vendors_tab(self) -> None:
        """Crée l'onglet des vendors."""
        # Frame principal
        main_frame = ctk.CTkFrame(self.tab_vendors, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Liste des vendors
        self.vendors_list_frame = ctk.CTkScrollableFrame(main_frame)
        self.vendors_list_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        # En-tête
        header = ctk.CTkFrame(self.vendors_list_frame, fg_color=("gray80", "gray25"))
        header.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(header, text="Type", width=180, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(header, text="Vendor", width=200, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(header, text="Contact", width=150, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(header, text="Actions", width=80, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5, pady=5)

        # Container pour les lignes de vendors
        self.vendors_rows_frame = ctk.CTkFrame(self.vendors_list_frame, fg_color="transparent")
        self.vendors_rows_frame.pack(fill="both", expand=True)

        # Bouton ajouter
        add_btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        add_btn_frame.grid(row=1, column=0, sticky="ew")

        ctk.CTkButton(
            add_btn_frame,
            text="+ Ajouter un vendor",
            command=self._add_vendor
        ).pack(side="right")

    def _refresh_vendors_list(self) -> None:
        """Rafraîchit la liste des vendors."""
        # Effacer les lignes existantes
        for widget in self.vendors_rows_frame.winfo_children():
            widget.destroy()

        # Afficher les vendors existants
        all_vendors = self.existing_vendors + self.vendors_to_add

        if not all_vendors:
            no_data = ctk.CTkLabel(
                self.vendors_rows_frame,
                text="Aucun vendor",
                text_color="gray"
            )
            no_data.pack(pady=20)
            return

        for i, vendor in enumerate(all_vendors):
            self._add_vendor_row(vendor, is_new=(vendor in self.vendors_to_add))

    def _add_vendor_row(self, vendor: Dict, is_new: bool = False) -> None:
        """Ajoute une ligne de vendor."""
        row_frame = ctk.CTkFrame(self.vendors_rows_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)

        # Type
        ctk.CTkLabel(row_frame, text=vendor.get("type_name", ""), width=180).pack(side="left", padx=5)

        # Nom
        ctk.CTkLabel(row_frame, text=vendor.get("vendor_name", ""), width=200).pack(side="left", padx=5)

        # Contact
        ctk.CTkLabel(row_frame, text=vendor.get("contact", "") or "-", width=150).pack(side="left", padx=5)

        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=80)
        actions_frame.pack(side="left", padx=5)

        # Bouton supprimer
        del_btn = ctk.CTkButton(
            actions_frame,
            text="X",
            width=30,
            height=25,
            fg_color="#d9534f",
            hover_color="#c9302c",
            command=lambda v=vendor, n=is_new: self._delete_vendor(v, n)
        )
        del_btn.pack(side="left", padx=2)

    def _add_vendor(self) -> None:
        """Ouvre le dialogue pour ajouter un vendor."""
        vendor_types = self.db.get_vendor_types()
        dialog = VendorDialog(self, vendor_types)
        self.wait_window(dialog)

        if dialog.result:
            self.vendors_to_add.append(dialog.result)
            self._refresh_vendors_list()

    def _delete_vendor(self, vendor: Dict, is_new: bool) -> None:
        """Supprime un vendor."""
        if is_new:
            self.vendors_to_add.remove(vendor)
        else:
            self.existing_vendors.remove(vendor)
            if vendor.get("id"):
                self.vendors_to_delete.append(vendor["id"])
        self._refresh_vendors_list()

    def _fill_form(self, data: Dict) -> None:
        """Remplit le formulaire avec les données existantes."""
        self.entry_study_number.insert(0, data.get("study_number", "") or "")
        self.entry_study_name.insert(0, data.get("study_name", "") or "")
        self.entry_eu_ct.insert(0, data.get("eu_ct_number", "") or "")
        self.entry_nct.insert(0, data.get("nct_number", "") or "")
        if data.get("phase"):
            self.combo_phase.set(data["phase"])
        self.entry_product.insert(0, data.get("investigational_product", "") or "")
        self.entry_comparator.insert(0, data.get("comparator", "") or "")
        self.entry_pathology.insert(0, data.get("pathology", "") or "")
        self.entry_title.insert(0, data.get("study_title", "") or "")
        self.entry_sponsor.insert(0, data.get("sponsor", "") or "")

    def _load_vendors(self) -> None:
        """Charge les vendors de l'étude."""
        if self.study_data and self.study_data.get("id"):
            self.existing_vendors = self.db.get_study_vendors(self.study_data["id"])
        self._refresh_vendors_list()

    def _save(self) -> None:
        """Sauvegarde l'étude."""
        study_number = self.entry_study_number.get().strip()
        if not study_number:
            messagebox.showerror("Erreur", "Le numéro d'étude est requis")
            return

        self.result = {
            "study_number": study_number,
            "study_name": self.entry_study_name.get().strip(),
            "eu_ct_number": self.entry_eu_ct.get().strip(),
            "nct_number": self.entry_nct.get().strip(),
            "phase": self.combo_phase.get(),
            "investigational_product": self.entry_product.get().strip(),
            "comparator": self.entry_comparator.get().strip(),
            "pathology": self.entry_pathology.get().strip(),
            "study_title": self.entry_title.get().strip(),
            "sponsor": self.entry_sponsor.get().strip(),
            "vendors_to_add": self.vendors_to_add,
            "vendors_to_delete": self.vendors_to_delete
        }

        self.destroy()


class StudiesFrame(ctk.CTkFrame):
    """Frame de gestion des études."""

    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")

        self.db = db

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # En-tête
        self._create_header()

        # Barre de recherche
        self._create_search_bar()

        # Liste des études
        self._create_study_list()

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
            text="Études",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w")

        # Bouton Nouveau
        self.btn_new = ctk.CTkButton(
            header_frame,
            text="+ Nouvelle Étude",
            command=self._new_study,
            width=160
        )
        self.btn_new.grid(row=0, column=2, sticky="e")

    def _create_search_bar(self) -> None:
        """Crée la barre de recherche."""
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Rechercher une étude...",
            width=300
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self._on_search)

    def _create_study_list(self) -> None:
        """Crée la liste des études."""
        # Frame conteneur
        self.list_container = ctk.CTkFrame(self, corner_radius=10)
        self.list_container.grid(row=2, column=0, sticky="nsew")
        self.list_container.grid_columnconfigure(0, weight=1)
        self.list_container.grid_rowconfigure(1, weight=1)

        # En-tête du tableau
        header = ctk.CTkFrame(self.list_container, fg_color=("gray80", "gray25"), corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")

        columns = [
            ("N° Étude", 120),
            ("Nom", 150),
            ("Phase", 60),
            ("Sponsor", 150),
            ("Pathologie", 150),
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
        self.study_list = ctk.CTkScrollableFrame(self.list_container, fg_color="transparent")
        self.study_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def refresh_data(self, search: str = "") -> None:
        """Rafraîchit la liste des études."""
        # Effacer la liste actuelle
        for widget in self.study_list.winfo_children():
            widget.destroy()

        # Récupérer les études
        studies = self.db.get_studies()

        # Filtrer par recherche
        if search:
            search_lower = search.lower()
            studies = [s for s in studies if
                       search_lower in (s.get("study_number", "") or "").lower() or
                       search_lower in (s.get("study_name", "") or "").lower() or
                       search_lower in (s.get("sponsor", "") or "").lower() or
                       search_lower in (s.get("pathology", "") or "").lower()]

        # Afficher les études
        if not studies:
            no_data = ctk.CTkLabel(
                self.study_list,
                text="Aucune étude trouvée",
                text_color="gray"
            )
            no_data.grid(row=0, column=0, columnspan=6, pady=50)
            return

        for i, study in enumerate(studies):
            self._add_study_row(i, study)

    def _add_study_row(self, row: int, study: Dict) -> None:
        """Ajoute une ligne d'étude."""
        row_frame = ctk.CTkFrame(self.study_list, fg_color="transparent")
        row_frame.grid(row=row, column=0, sticky="ew", pady=2)

        # Numéro d'étude
        ctk.CTkLabel(row_frame, text=study.get("study_number", "") or "-", width=120).grid(row=0, column=0, padx=5)

        # Nom
        ctk.CTkLabel(row_frame, text=study.get("study_name", "") or "-", width=150).grid(row=0, column=1, padx=5)

        # Phase
        ctk.CTkLabel(row_frame, text=study.get("phase", "") or "-", width=60).grid(row=0, column=2, padx=5)

        # Sponsor
        ctk.CTkLabel(row_frame, text=study.get("sponsor", "") or "-", width=150).grid(row=0, column=3, padx=5)

        # Pathologie
        ctk.CTkLabel(row_frame, text=study.get("pathology", "") or "-", width=150).grid(row=0, column=4, padx=5)

        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=100)
        actions_frame.grid(row=0, column=5, padx=5)

        # Edit button
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="Edit",
            width=40,
            height=25,
            command=lambda s=study: self._edit_study(s)
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
            command=lambda s=study: self._delete_study(s)
        )
        del_btn.pack(side="left", padx=2)

    def _new_study(self) -> None:
        """Ouvre le dialogue pour une nouvelle étude."""
        dialog = StudyDialog(self, self.db)
        self.wait_window(dialog)

        if dialog.result:
            try:
                # Créer l'étude
                vendors_to_add = dialog.result.pop("vendors_to_add", [])
                dialog.result.pop("vendors_to_delete", [])

                study_id = self.db.create_study(**dialog.result)

                # Ajouter les vendors
                for vendor in vendors_to_add:
                    self.db.add_study_vendor(
                        study_id,
                        vendor["vendor_type_id"],
                        vendor["vendor_name"],
                        vendor.get("contact", "")
                    )

                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de créer l'étude: {e}")

    def _edit_study(self, study: Dict) -> None:
        """Ouvre le dialogue pour modifier une étude."""
        dialog = StudyDialog(self, self.db, study)
        self.wait_window(dialog)

        if dialog.result:
            try:
                vendors_to_add = dialog.result.pop("vendors_to_add", [])
                vendors_to_delete = dialog.result.pop("vendors_to_delete", [])

                # Mettre à jour l'étude
                self.db.update_study(study["id"], **dialog.result)

                # Supprimer les vendors
                for vendor_id in vendors_to_delete:
                    self.db.delete_study_vendor(vendor_id)

                # Ajouter les nouveaux vendors
                for vendor in vendors_to_add:
                    self.db.add_study_vendor(
                        study["id"],
                        vendor["vendor_type_id"],
                        vendor["vendor_name"],
                        vendor.get("contact", "")
                    )

                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de modifier l'étude: {e}")

    def _delete_study(self, study: Dict) -> None:
        """Supprime une étude."""
        confirm = messagebox.askyesno(
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer l'étude {study.get('study_number')} ?"
        )

        if confirm:
            try:
                self.db.delete_study(study["id"])
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de supprimer l'étude: {e}")

    def _on_search(self, event=None) -> None:
        """Callback pour la recherche."""
        search = self.search_entry.get()
        self.refresh_data(search)
