"""
Gestion des queries (data management).
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict, List, Any
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


def get_query_age(open_date) -> int:
    """Calcule l'âge d'une query en jours."""
    if not open_date:
        return 0
    if isinstance(open_date, str):
        open_date = parse_date(open_date)
    if open_date:
        return (date.today() - open_date).days
    return 0


class QueryDialog(ctk.CTkToplevel):
    """Dialogue pour créer/modifier une query."""

    def __init__(self, parent, patient: Dict, db_connection, query_data: Optional[Dict] = None):
        super().__init__(parent)

        self.patient = patient
        self.conn = db_connection
        self.query_data = query_data
        self.result = None

        self.title("Edit Query" if query_data else "New Query")
        self.geometry("500x500")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 500) // 2
        self.geometry(f"+{x}+{y}")

        self._create_form()

        if query_data:
            self._fill_form(query_data)

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
        form_frame = ctk.CTkScrollableFrame(self, height=350)
        form_frame.pack(fill="both", expand=True, padx=20)

        # Champ CRF
        ctk.CTkLabel(form_frame, text="CRF Field").pack(anchor="w", pady=(10, 5))
        self.entry_field = ctk.CTkEntry(form_frame, width=300)
        self.entry_field.pack(anchor="w")

        # Description
        ctk.CTkLabel(form_frame, text="Description *").pack(anchor="w", pady=(10, 5))
        self.text_description = ctk.CTkTextbox(form_frame, height=80, width=400)
        self.text_description.pack(anchor="w")

        # Date d'ouverture
        ctk.CTkLabel(form_frame, text="Open Date (YYYY-MM-DD) *").pack(anchor="w", pady=(10, 5))
        self.entry_open_date = ctk.CTkEntry(form_frame, width=150)
        self.entry_open_date.pack(anchor="w")
        # Pré-remplir avec aujourd'hui
        self.entry_open_date.insert(0, str(date.today()))

        # Statut
        ctk.CTkLabel(form_frame, text="Status").pack(anchor="w", pady=(10, 5))
        self.combo_status = ctk.CTkComboBox(
            form_frame,
            values=["Open", "Answered", "Closed"],
            width=150
        )
        self.combo_status.pack(anchor="w")
        self.combo_status.set("Open")

        # Réponse site
        ctk.CTkLabel(form_frame, text="Site Response").pack(anchor="w", pady=(10, 5))
        self.text_response = ctk.CTkTextbox(form_frame, height=60, width=400)
        self.text_response.pack(anchor="w")

        # Date de réponse
        ctk.CTkLabel(form_frame, text="Response Date (YYYY-MM-DD)").pack(anchor="w", pady=(10, 5))
        self.entry_response_date = ctk.CTkEntry(form_frame, width=150)
        self.entry_response_date.pack(anchor="w")

        # Date de résolution
        ctk.CTkLabel(form_frame, text="Resolution Date (YYYY-MM-DD)").pack(anchor="w", pady=(10, 5))
        self.entry_resolution_date = ctk.CTkEntry(form_frame, width=150)
        self.entry_resolution_date.pack(anchor="w")

        # Commentaires DM
        ctk.CTkLabel(form_frame, text="DM Comments").pack(anchor="w", pady=(10, 5))
        self.text_dm_comments = ctk.CTkTextbox(form_frame, height=60, width=400)
        self.text_dm_comments.pack(anchor="w")

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

    def _fill_form(self, data: Dict) -> None:
        """Remplit le formulaire."""
        if data.get("crf_field"):
            self.entry_field.insert(0, data["crf_field"])
        if data.get("description"):
            self.text_description.insert("1.0", data["description"])
        if data.get("open_date"):
            self.entry_open_date.delete(0, "end")
            self.entry_open_date.insert(0, str(data["open_date"]))
        if data.get("status"):
            self.combo_status.set(data["status"])
        if data.get("site_response"):
            self.text_response.insert("1.0", data["site_response"])
        if data.get("response_date"):
            self.entry_response_date.insert(0, str(data["response_date"]))
        if data.get("resolution_date"):
            self.entry_resolution_date.insert(0, str(data["resolution_date"]))
        if data.get("dm_comments"):
            self.text_dm_comments.insert("1.0", data["dm_comments"])

    def _save(self) -> None:
        """Sauvegarde la query."""
        open_date = parse_date(self.entry_open_date.get().strip())
        if not open_date:
            messagebox.showerror("Error", "Open date is required (YYYY-MM-DD)")
            return

        description = self.text_description.get("1.0", "end-1c").strip()
        if not description:
            messagebox.showerror("Error", "Description is required")
            return

        self.result = {
            "patient_id": self.patient["id"],
            "crf_field": self.entry_field.get().strip() or None,
            "description": description,
            "open_date": open_date,
            "status": self.combo_status.get(),
            "site_response": self.text_response.get("1.0", "end-1c").strip() or None,
            "response_date": parse_date(self.entry_response_date.get().strip()),
            "resolution_date": parse_date(self.entry_resolution_date.get().strip()),
            "dm_comments": self.text_dm_comments.get("1.0", "end-1c").strip() or None
        }

        self.destroy()


class QueriesFrame(ctk.CTkFrame):
    """Frame de gestion des queries."""

    def __init__(self, parent, patient_queries, db_connection):
        super().__init__(parent, fg_color="transparent")

        self.patient_queries = patient_queries
        self.conn = db_connection
        self.selected_patient = None
        self.patients: List[Dict] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Row 3 pour la liste

        self._create_header()
        self._create_controls()
        self._create_stats_bar()
        self._create_query_list()

    def _create_header(self) -> None:
        """Crée l'en-tête."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="Queries",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        # Légende
        legend_frame = ctk.CTkFrame(header, fg_color="transparent")
        legend_frame.grid(row=0, column=2, sticky="e")

        legends = [
            ("Open", "#d9534f"),
            ("Answered", "#f0ad4e"),
            ("Closed", "#5cb85c"),
            (">7 days", "#d9534f"),
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
        patient_list = ["All patients"] + [f"{p['patient_number']}" for p in self.patients]

        self.patient_combo = ctk.CTkComboBox(
            controls,
            values=patient_list,
            command=self._on_patient_change,
            width=140
        )
        self.patient_combo.pack(side="left", padx=5)
        self.patient_combo.set("All patients")

        # Filtre statut
        ctk.CTkLabel(controls, text="Status:").pack(side="left", padx=(15, 5))
        self.status_combo = ctk.CTkComboBox(
            controls,
            values=["All", "Open", "Answered", "Closed"],
            command=self._on_filter_change,
            width=100
        )
        self.status_combo.pack(side="left", padx=5)
        self.status_combo.set("All")

        # Filtre par âge
        ctk.CTkLabel(controls, text="Age:").pack(side="left", padx=(15, 5))
        self.age_combo = ctk.CTkComboBox(
            controls,
            values=["All", ">7 days", ">30 days"],
            command=self._on_filter_change,
            width=100
        )
        self.age_combo.pack(side="left", padx=5)
        self.age_combo.set("All")

        # Bouton nouveau
        self.btn_new = ctk.CTkButton(
            controls,
            text="+ New Query",
            command=self._new_query,
            width=100
        )
        self.btn_new.pack(side="right", padx=10)

    def _create_stats_bar(self) -> None:
        """Crée la barre de statistiques."""
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        self.stats_labels = {}

        stats_config = [
            ("total", "Total", "white"),
            ("open", "Open", "#d9534f"),
            ("answered", "Answered", "#f0ad4e"),
            ("closed", "Closed", "#5cb85c"),
            ("overdue", ">7 days", "#d9534f"),
        ]

        for key, label, color in stats_config:
            card = ctk.CTkFrame(self.stats_frame, width=100)
            card.pack(side="left", padx=10, pady=10)
            card.pack_propagate(False)

            ctk.CTkLabel(
                card,
                text="0",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=color
            ).pack(pady=(10, 0))

            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=10),
                text_color="gray"
            ).pack(pady=(0, 10))

            self.stats_labels[key] = card.winfo_children()[0]

    def _create_query_list(self) -> None:
        """Crée la liste des queries."""
        self.list_container = ctk.CTkFrame(self, corner_radius=10)
        self.list_container.grid(row=3, column=0, sticky="nsew")
        self.list_container.grid_columnconfigure(0, weight=1)
        self.list_container.grid_rowconfigure(1, weight=1)

        # En-tête
        header = ctk.CTkFrame(self.list_container, fg_color=("gray80", "gray25"))
        header.grid(row=0, column=0, sticky="ew")

        columns = [
            ("Patient", 75), ("Q#", 35), ("Field", 90), ("Description", 150),
            ("Open", 80), ("Age", 50), ("Status", 70), ("Response", 75), ("Actions", 130)
        ]

        for i, (name, width) in enumerate(columns):
            ctk.CTkLabel(header, text=name, font=ctk.CTkFont(weight="bold"), width=width).grid(
                row=0, column=i, padx=2, pady=8
            )

        # Liste
        self.query_list = ctk.CTkScrollableFrame(self.list_container, fg_color="transparent")
        self.query_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self._refresh_list()

    def _update_stats(self, queries: List[Dict] = None) -> None:
        """Met à jour les stats basées sur les queries affichées."""
        if queries is None:
            queries = []

        today = date.today()
        stats = {
            "total": len(queries),
            "open": sum(1 for q in queries if q.get("status") == "Open"),
            "answered": sum(1 for q in queries if q.get("status") == "Answered"),
            "closed": sum(1 for q in queries if q.get("status") == "Closed"),
            "overdue": 0,
        }

        # Compter les queries > 7 jours
        for q in queries:
            if q.get("status") == "Open":
                age = get_query_age(q.get("open_date"))
                if age > 7:
                    stats["overdue"] += 1

        for key, label in self.stats_labels.items():
            label.configure(text=str(stats.get(key, 0)))

    def _on_search(self, event=None) -> None:
        """Filtre la liste des patients."""
        query = self.search_entry.get().strip().lower()

        if query:
            filtered = [p for p in self.patients if query in p['patient_number'].lower()]
        else:
            filtered = self.patients

        patient_list = ["All patients"] + [f"{p['patient_number']}" for p in filtered]
        self.patient_combo.configure(values=patient_list)

        if patient_list:
            self.patient_combo.set(patient_list[0])
            self._on_patient_change(patient_list[0])

    def _get_queries(self) -> List[Dict]:
        """Récupère les queries."""
        cursor = self.conn.cursor()

        sql = """
            SELECT q.*, p.patient_number
            FROM queries q
            JOIN patients p ON q.patient_id = p.id
            WHERE 1=1
        """
        params = []

        if self.selected_patient:
            sql += " AND q.patient_id = ?"
            params.append(self.selected_patient["id"])

        status_filter = self.status_combo.get()
        if status_filter != "All":
            sql += " AND q.status = ?"
            params.append(status_filter)

        sql += " ORDER BY q.open_date DESC"

        cursor.execute(sql, params)
        queries = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

        # Filtre par âge (côté Python car SQLite n'a pas de bonne gestion des dates)
        age_filter = self.age_combo.get()
        if age_filter == ">7 days":
            queries = [q for q in queries if get_query_age(q.get("open_date")) > 7]
        elif age_filter == ">30 days":
            queries = [q for q in queries if get_query_age(q.get("open_date")) > 30]

        return queries

    def _refresh_list(self) -> None:
        """Rafraîchit la liste."""
        for widget in self.query_list.winfo_children():
            widget.destroy()

        queries = self._get_queries()

        # Mettre à jour les stats
        self._update_stats(queries)

        if not queries:
            ctk.CTkLabel(
                self.query_list,
                text="No queries found",
                text_color="gray"
            ).grid(row=0, column=0, columnspan=9, pady=50)
            return

        for i, query in enumerate(queries):
            self._add_query_row(i, query)

    def _add_query_row(self, row: int, query: Dict) -> None:
        """Ajoute une ligne de query."""
        row_frame = ctk.CTkFrame(self.query_list, fg_color=("gray90", "gray17"))
        row_frame.grid(row=row, column=0, sticky="ew", pady=2, padx=5)

        # Patient
        ctk.CTkLabel(row_frame, text=query.get("patient_number", ""), width=75).grid(row=0, column=0, padx=2, pady=8)

        # Query #
        ctk.CTkLabel(row_frame, text=str(query.get("query_number", "")), width=35).grid(row=0, column=1, padx=2)

        # Field
        field = (query.get("crf_field") or "-")[:12]
        ctk.CTkLabel(row_frame, text=field, width=90).grid(row=0, column=2, padx=2)

        # Description
        desc = query.get("description", "")[:20]
        if len(query.get("description", "")) > 20:
            desc += "..."
        ctk.CTkLabel(row_frame, text=desc, width=150, anchor="w").grid(row=0, column=3, padx=2)

        # Open Date
        open_date = query.get("open_date", "")
        if open_date and hasattr(open_date, 'strftime'):
            open_date = open_date.strftime("%Y-%m-%d")
        ctk.CTkLabel(row_frame, text=str(open_date), width=80).grid(row=0, column=4, padx=2)

        # Age (jours depuis ouverture)
        age = get_query_age(query.get("open_date"))
        age_color = "#d9534f" if age > 7 else ("#f0ad4e" if age > 3 else "white")
        if query.get("status") == "Closed":
            age_color = "gray"
            age_text = "-"
        else:
            age_text = f"{age}d"

        ctk.CTkLabel(
            row_frame,
            text=age_text,
            text_color=age_color,
            width=50
        ).grid(row=0, column=5, padx=2)

        # Status
        status = query.get("status", "")
        status_colors = {"Open": "#d9534f", "Answered": "#f0ad4e", "Closed": "#5cb85c"}
        ctk.CTkLabel(
            row_frame,
            text=status,
            text_color=status_colors.get(status, "white"),
            width=70
        ).grid(row=0, column=6, padx=2)

        # Response date
        resp_date = query.get("response_date", "")
        if resp_date and hasattr(resp_date, 'strftime'):
            resp_date = resp_date.strftime("%Y-%m-%d")
        ctk.CTkLabel(row_frame, text=str(resp_date) if resp_date else "-", width=75).grid(row=0, column=7, padx=2)

        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=130)
        actions_frame.grid(row=0, column=8, padx=2)

        # Quick actions selon le statut
        if status == "Open":
            ctk.CTkButton(
                actions_frame,
                text="Ans",
                width=35,
                height=24,
                fg_color="#f0ad4e",
                hover_color="#ec971f",
                command=lambda q=query: self._quick_answer(q)
            ).pack(side="left", padx=1)

        if status != "Closed":
            ctk.CTkButton(
                actions_frame,
                text="Close",
                width=40,
                height=24,
                fg_color="#5cb85c",
                hover_color="#449d44",
                command=lambda q=query: self._quick_close(q)
            ).pack(side="left", padx=1)

        ctk.CTkButton(
            actions_frame,
            text="Edit",
            width=35,
            height=24,
            command=lambda q=query: self._edit_query(q)
        ).pack(side="left", padx=1)

        ctk.CTkButton(
            actions_frame,
            text="Del",
            width=30,
            height=24,
            fg_color="#d9534f",
            hover_color="#c9302c",
            command=lambda q=query: self._delete_query(q)
        ).pack(side="left", padx=1)

    def _on_patient_change(self, value: str) -> None:
        """Callback changement patient."""
        if value == "All patients":
            self.selected_patient = None
        else:
            self.selected_patient = self.patient_queries.get_by_number(value)
        self._refresh_list()

    def _on_filter_change(self, value: str) -> None:
        """Callback changement filtre."""
        self._refresh_list()

    def _new_query(self) -> None:
        """Crée une nouvelle query."""
        if not self.selected_patient:
            patients = self.patient_queries.get_all()
            if not patients:
                messagebox.showerror("Error", "No patients available")
                return
            self.selected_patient = patients[0]

        dialog = QueryDialog(self, self.selected_patient, self.conn)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self._create_query(dialog.result)
                self._refresh_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create query: {e}")

    def _create_query(self, data: Dict) -> None:
        """Crée une query en base."""
        cursor = self.conn.cursor()

        # Prochain numéro
        cursor.execute(
            "SELECT COALESCE(MAX(query_number), 0) + 1 FROM queries WHERE patient_id = ?",
            (data["patient_id"],)
        )
        query_number = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO queries (patient_id, query_number, crf_field, description, open_date,
                                status, site_response, response_date, dm_comments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["patient_id"], query_number, data["crf_field"], data["description"],
            data["open_date"], data["status"], data["site_response"],
            data["response_date"], data["dm_comments"]
        ))
        self.conn.commit()

    def _edit_query(self, query: Dict) -> None:
        """Modifie une query."""
        patient = self.patient_queries.get_by_id(query["patient_id"])
        if not patient:
            messagebox.showerror("Error", "Patient not found")
            return

        dialog = QueryDialog(self, patient, self.conn, query)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self._update_query(query["id"], dialog.result)
                self._refresh_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not update query: {e}")

    def _update_query(self, query_id: int, data: Dict) -> None:
        """Met à jour une query."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE queries SET
                crf_field = ?, description = ?, status = ?,
                site_response = ?, response_date = ?, resolution_date = ?, dm_comments = ?
            WHERE id = ?
        """, (
            data["crf_field"], data["description"], data["status"],
            data["site_response"], data["response_date"], data.get("resolution_date"),
            data["dm_comments"], query_id
        ))
        self.conn.commit()

    def _quick_answer(self, query: Dict) -> None:
        """Marque une query comme répondue."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE queries SET status = 'Answered', response_date = ?
                WHERE id = ?
            """, (date.today(), query["id"]))
            self.conn.commit()
            self._refresh_list()
        except Exception as e:
            messagebox.showerror("Error", f"Could not update query: {e}")

    def _quick_close(self, query: Dict) -> None:
        """Ferme une query."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE queries SET status = 'Closed', resolution_date = ?
                WHERE id = ?
            """, (date.today(), query["id"]))
            self.conn.commit()
            self._refresh_list()
        except Exception as e:
            messagebox.showerror("Error", f"Could not close query: {e}")

    def _delete_query(self, query: Dict) -> None:
        """Supprime une query."""
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete Query #{query.get('query_number')} for patient {query.get('patient_number')}?\n\nThis action cannot be undone."
        )

        if confirm:
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM queries WHERE id = ?", (query["id"],))
                self.conn.commit()
                self._refresh_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete query: {e}")
