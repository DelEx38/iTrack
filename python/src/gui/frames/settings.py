"""
Paramètres de l'étude.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import Dict, List, Optional, Any
from datetime import date
import json


def parse_date(date_str: str) -> Optional[date]:
    """Parse une date au format YYYY-MM-DD."""
    if not date_str or len(date_str) < 10:
        return None
    try:
        parts = date_str.split("-")
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        return None


class SettingsFrame(ctk.CTkFrame):
    """Frame des paramètres."""

    def __init__(self, parent, visit_queries, consent_queries, db_connection):
        super().__init__(parent, fg_color="transparent")

        self.visit_queries = visit_queries
        self.consent_queries = consent_queries
        self.conn = db_connection

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_header()
        self._create_visit_settings()
        self._create_consent_settings()

    def _create_header(self) -> None:
        """Crée l'en-tête."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(
            header,
            text="Study Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")

        # Boutons Export/Import
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(
            btn_frame,
            text="Export JSON",
            command=self._export_config,
            width=100,
            fg_color="transparent",
            border_width=1
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Import JSON",
            command=self._import_config,
            width=100,
            fg_color="transparent",
            border_width=1
        ).pack(side="left", padx=5)

    def _create_visit_settings(self) -> None:
        """Crée les paramètres de visites."""
        visit_frame = ctk.CTkFrame(self, corner_radius=10)
        visit_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        visit_frame.grid_columnconfigure(0, weight=1)
        visit_frame.grid_rowconfigure(1, weight=1)

        # Titre
        title_frame = ctk.CTkFrame(visit_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)

        ctk.CTkLabel(
            title_frame,
            text="Visit Windows",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            title_frame,
            text="Save All",
            command=self._save_visit_settings,
            width=80
        ).pack(side="right")

        ctk.CTkButton(
            title_frame,
            text="Reset",
            command=self._reset_visit_defaults,
            width=60,
            fg_color="transparent",
            border_width=1
        ).pack(side="right", padx=5)

        # Stats
        self.visit_stats_label = ctk.CTkLabel(
            title_frame,
            text="",
            text_color="gray"
        )
        self.visit_stats_label.pack(side="right", padx=15)

        # Liste des visites
        self.visit_list = ctk.CTkScrollableFrame(visit_frame)
        self.visit_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # En-tête
        header_frame = ctk.CTkFrame(self.visit_list, fg_color=("gray80", "gray25"))
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        ctk.CTkLabel(header_frame, text="Visit", width=60, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(header_frame, text="Target Day", width=80, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(header_frame, text="Window -", width=70, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkLabel(header_frame, text="Window +", width=70, font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5)

        # Charger les visites
        self.visit_entries = {}
        self._load_visits()

    def _load_visits(self) -> None:
        """Charge les visites."""
        # Nettoyer les anciennes entrées
        for widget in self.visit_list.winfo_children():
            if hasattr(widget, '_is_header') and widget._is_header:
                continue
            widget.destroy()

        visits = self.visit_queries.get_config()

        # Stats
        self.visit_stats_label.configure(text=f"{len(visits)} visits configured")

        for i, visit in enumerate(visits):
            # Vérifier si fenêtre valide
            is_valid = visit["window_before"] <= visit["target_day"]
            row_color = "transparent" if is_valid else ("#ffcccc", "#4a2020")

            row_frame = ctk.CTkFrame(self.visit_list, fg_color=row_color)
            row_frame.grid(row=i+1, column=0, sticky="ew", pady=2)

            # Nom avec indicateur V1
            visit_text = visit["visit_name"]
            if visit["visit_name"] == "V1":
                visit_text += " (REF)"
            ctk.CTkLabel(row_frame, text=visit_text, width=70).grid(row=0, column=0, padx=5)

            # Target day
            entry_target = ctk.CTkEntry(row_frame, width=70)
            entry_target.insert(0, str(visit["target_day"]))
            entry_target.grid(row=0, column=1, padx=5)

            # Window before (négatif)
            entry_before = ctk.CTkEntry(row_frame, width=60)
            entry_before.insert(0, str(visit["window_before"]))
            entry_before.grid(row=0, column=2, padx=5)

            # Window after
            entry_after = ctk.CTkEntry(row_frame, width=60)
            entry_after.insert(0, str(visit["window_after"]))
            entry_after.grid(row=0, column=3, padx=5)

            # Indicateur de validation
            if not is_valid:
                ctk.CTkLabel(
                    row_frame,
                    text="!",
                    text_color="#d9534f",
                    font=ctk.CTkFont(weight="bold")
                ).grid(row=0, column=4, padx=5)

            self.visit_entries[visit["id"]] = {
                "target": entry_target,
                "before": entry_before,
                "after": entry_after,
                "name": visit["visit_name"]
            }

    def _save_visit_settings(self) -> None:
        """Sauvegarde les paramètres de visites."""
        try:
            warnings = []
            for visit_id, entries in self.visit_entries.items():
                target = int(entries["target"].get())
                before = int(entries["before"].get())
                after = int(entries["after"].get())

                # Validation
                if before > target:
                    warnings.append(f"{entries['name']}: window_before ({before}) > target_day ({target})")

                self.visit_queries.update_config(visit_id, target, before, after)

            if warnings:
                messagebox.showwarning(
                    "Saved with warnings",
                    "Settings saved but some windows are invalid:\n\n" + "\n".join(warnings)
                )
            else:
                messagebox.showinfo("Success", "Visit settings saved successfully")

            self._load_visits()  # Rafraîchir pour montrer indicateurs

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save settings: {e}")

    def _reset_visit_defaults(self) -> None:
        """Réinitialise les fenêtres par défaut."""
        if not messagebox.askyesno("Confirm", "Reset all visit windows to defaults?"):
            return

        # Valeurs par défaut standard
        defaults = {
            1: (0, 0, 0),      # V1 - pas de fenêtre
            2: (7, 3, 3),      # V2
            3: (14, 3, 3),
            4: (28, 5, 5),
            5: (56, 7, 7),
            6: (84, 7, 7),
            7: (112, 7, 7),
            8: (140, 7, 7),
            9: (168, 7, 7),
            10: (196, 7, 7),
        }

        try:
            for visit_id, entries in self.visit_entries.items():
                if visit_id in defaults:
                    target, before, after = defaults[visit_id]
                else:
                    # Pour les visites au-delà de 10, calculer
                    target = (visit_id - 1) * 28
                    before = 7
                    after = 7

                self.visit_queries.update_config(visit_id, target, before, after)

            self._reload_visits()
            messagebox.showinfo("Success", "Visit windows reset to defaults")
        except Exception as e:
            messagebox.showerror("Error", f"Could not reset: {e}")

    def _reload_visits(self) -> None:
        """Recharge les entrées de visites."""
        self.visit_entries = {}
        for widget in self.visit_list.winfo_children():
            widget.destroy()

        # Recréer l'en-tête
        header_frame = ctk.CTkFrame(self.visit_list, fg_color=("gray80", "gray25"))
        header_frame._is_header = True
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        ctk.CTkLabel(header_frame, text="Visit", width=70, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(header_frame, text="Target Day", width=80, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(header_frame, text="Window -", width=70, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkLabel(header_frame, text="Window +", width=70, font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5)

        self._load_visits()

    def _export_config(self) -> None:
        """Exporte la configuration en JSON."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Configuration"
        )
        if not file_path:
            return

        try:
            config = {
                "visits": [],
                "consent_types": []
            }

            # Visites
            visits = self.visit_queries.get_config()
            for v in visits:
                config["visits"].append({
                    "visit_name": v["visit_name"],
                    "target_day": v["target_day"],
                    "window_before": v["window_before"],
                    "window_after": v["window_after"]
                })

            # Consentements
            consent_types = self.consent_queries.get_types()
            for ct in consent_types:
                versions = self.consent_queries.get_versions(ct["id"])
                config["consent_types"].append({
                    "type_name": ct["type_name"],
                    "versions": [
                        {
                            "version": v["version"],
                            "version_date": v.get("version_date", "")
                        } for v in versions
                    ]
                })

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("Success", f"Configuration exported to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Could not export: {e}")

    def _import_config(self) -> None:
        """Importe la configuration depuis JSON."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Configuration"
        )
        if not file_path:
            return

        if not messagebox.askyesno("Confirm", "This will overwrite current settings. Continue?"):
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Importer visites
            if "visits" in config:
                visits = self.visit_queries.get_config()
                visit_map = {v["visit_name"]: v["id"] for v in visits}

                for v in config["visits"]:
                    if v["visit_name"] in visit_map:
                        self.visit_queries.update_config(
                            visit_map[v["visit_name"]],
                            v["target_day"],
                            v["window_before"],
                            v["window_after"]
                        )

            self._reload_visits()
            self._load_consents()
            messagebox.showinfo("Success", "Configuration imported successfully")

        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON file")
        except Exception as e:
            messagebox.showerror("Error", f"Could not import: {e}")

    def _create_consent_settings(self) -> None:
        """Crée les paramètres de consentements."""
        consent_frame = ctk.CTkFrame(self, corner_radius=10)
        consent_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        consent_frame.grid_columnconfigure(0, weight=1)
        consent_frame.grid_rowconfigure(2, weight=1)

        # Titre
        title_frame = ctk.CTkFrame(consent_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)

        ctk.CTkLabel(
            title_frame,
            text="Consent Types & Versions",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        # Boutons d'ajout
        btn_frame = ctk.CTkFrame(consent_frame, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="+ Type",
            command=self._add_consent_type,
            width=80
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="+ Version",
            command=self._add_consent_version,
            width=80
        ).pack(side="left", padx=5)

        # Liste
        self.consent_list = ctk.CTkScrollableFrame(consent_frame)
        self.consent_list.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self._load_consents()

    def _load_consents(self) -> None:
        """Charge les types et versions de consentement."""
        for widget in self.consent_list.winfo_children():
            widget.destroy()

        consent_types = self.consent_queries.get_types()

        for i, ct in enumerate(consent_types):
            type_frame = ctk.CTkFrame(self.consent_list, fg_color=("gray85", "gray20"))
            type_frame.grid(row=i, column=0, sticky="ew", pady=5, padx=5)
            type_frame.grid_columnconfigure(0, weight=1)

            # En-tête du type
            type_header = ctk.CTkFrame(type_frame, fg_color="transparent")
            type_header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
            type_header.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                type_header,
                text=ct["type_name"],
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=0, sticky="w")

            # Bouton supprimer type
            ctk.CTkButton(
                type_header,
                text="×",
                width=25,
                height=25,
                fg_color="#d9534f",
                hover_color="#c9302c",
                command=lambda tid=ct["id"], tname=ct["type_name"]: self._delete_consent_type(tid, tname)
            ).grid(row=0, column=1, sticky="e")

            # Versions
            versions = self.consent_queries.get_versions(ct["id"])

            for j, version in enumerate(versions):
                version_frame = ctk.CTkFrame(type_frame, fg_color="transparent")
                version_frame.grid(row=j+1, column=0, sticky="ew", padx=20, pady=2)
                version_frame.grid_columnconfigure(0, weight=1)

                version_text = f"{version['version']}"
                if version.get("version_date"):
                    version_text += f" ({version['version_date']})"

                ctk.CTkLabel(version_frame, text=version_text).grid(row=0, column=0, sticky="w")

                # Bouton supprimer version
                ctk.CTkButton(
                    version_frame,
                    text="×",
                    width=20,
                    height=20,
                    fg_color="transparent",
                    text_color="#d9534f",
                    hover_color=("gray80", "gray30"),
                    command=lambda vid=version["id"], vname=version["version"]: self._delete_consent_version(vid, vname)
                ).grid(row=0, column=1, sticky="e")

            if not versions:
                ctk.CTkLabel(
                    type_frame,
                    text="No versions",
                    text_color="gray"
                ).grid(row=1, column=0, sticky="w", padx=20, pady=5)

    def _delete_consent_type(self, type_id: int, type_name: str) -> None:
        """Supprime un type de consentement."""
        if not messagebox.askyesno(
            "Confirm",
            f"Delete consent type '{type_name}' and all its versions?"
        ):
            return

        try:
            self.consent_queries.delete_type(type_id)
            self._load_consents()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete: {e}")

    def _delete_consent_version(self, version_id: int, version_name: str) -> None:
        """Supprime une version de consentement."""
        if not messagebox.askyesno(
            "Confirm",
            f"Delete version '{version_name}'?"
        ):
            return

        try:
            self.consent_queries.delete_version(version_id)
            self._load_consents()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete: {e}")

    def _add_consent_type(self) -> None:
        """Ajoute un type de consentement."""
        dialog = ctk.CTkInputDialog(
            text="Enter consent type name:",
            title="New Consent Type"
        )
        type_name = dialog.get_input()

        if type_name and type_name.strip():
            try:
                self.consent_queries.add_type(type_name.strip())
                self._load_consents()
            except Exception as e:
                messagebox.showerror("Error", f"Could not add type: {e}")

    def _add_consent_version(self) -> None:
        """Ajoute une version de consentement."""
        # Sélectionner le type
        consent_types = self.consent_queries.get_types()
        if not consent_types:
            messagebox.showerror("Error", "Create a consent type first")
            return

        # Dialogue de sélection
        select_dialog = SelectTypeDialog(self, consent_types)
        self.wait_window(select_dialog)

        if select_dialog.result:
            type_id = select_dialog.result["type_id"]
            version = select_dialog.result["version"]
            version_date = select_dialog.result.get("version_date")

            try:
                self.consent_queries.add_version(type_id, version, version_date)
                self._load_consents()
            except Exception as e:
                messagebox.showerror("Error", f"Could not add version: {e}")


class SelectTypeDialog(ctk.CTkToplevel):
    """Dialogue de sélection de type et version."""

    def __init__(self, parent, consent_types: List[Dict]):
        super().__init__(parent)

        self.consent_types = consent_types
        self.result = None

        self.title("Add Version")
        self.geometry("350x280")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 350) // 2
        y = (self.winfo_screenheight() - 280) // 2
        self.geometry(f"+{x}+{y}")

        # Type
        ctk.CTkLabel(self, text="Consent Type:").pack(anchor="w", padx=20, pady=(20, 5))
        type_names = [ct["type_name"] for ct in consent_types]
        self.combo_type = ctk.CTkComboBox(self, values=type_names, width=250)
        self.combo_type.pack(anchor="w", padx=20)
        if type_names:
            self.combo_type.set(type_names[0])

        # Version
        ctk.CTkLabel(self, text="Version:").pack(anchor="w", padx=20, pady=(15, 5))
        self.entry_version = ctk.CTkEntry(self, width=150, placeholder_text="e.g., 1.0")
        self.entry_version.pack(anchor="w", padx=20)

        # Date de version
        ctk.CTkLabel(self, text="Version Date (optional):").pack(anchor="w", padx=20, pady=(15, 5))
        self.entry_date = ctk.CTkEntry(self, width=150, placeholder_text="YYYY-MM-DD")
        self.entry_date.pack(anchor="w", padx=20)

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
            text="Add",
            command=self._save
        ).pack(side="right")

    def _save(self) -> None:
        """Sauvegarde."""
        version = self.entry_version.get().strip()
        if not version:
            messagebox.showerror("Error", "Version is required")
            return

        version_date = self.entry_date.get().strip()
        if version_date:
            # Valider le format de date
            parsed = parse_date(version_date)
            if not parsed:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return

        type_name = self.combo_type.get()
        type_id = None
        for ct in self.consent_types:
            if ct["type_name"] == type_name:
                type_id = ct["id"]
                break

        if type_id:
            self.result = {
                "type_id": type_id,
                "version": version,
                "version_date": version_date if version_date else None
            }
            self.destroy()
