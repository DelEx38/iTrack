"""
Landing page - Liste des études disponibles.
"""

import customtkinter as ctk
from typing import Callable, List, Dict, Optional


class StudyCard(ctk.CTkFrame):
    """Carte représentant une étude."""

    def __init__(
        self,
        parent,
        study: Dict,
        on_click: Callable,
        stats: Optional[Dict] = None
    ):
        super().__init__(parent, corner_radius=10, fg_color=("gray90", "gray17"))

        self.study = study
        self.on_click = on_click

        self.grid_columnconfigure(0, weight=1)

        # En-tête : Numéro + Phase
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))

        study_number = study.get("study_number") or "N/A"
        ctk.CTkLabel(
            header_frame,
            text=study_number,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray30", "gray70")
        ).pack(side="left")

        phase = study.get("phase")
        if phase:
            phase_colors = {
                "I": "#17a2b8",
                "I/II": "#17a2b8",
                "II": "#28a745",
                "II/III": "#28a745",
                "III": "#ffc107",
                "III/IV": "#ffc107",
                "IV": "#dc3545"
            }
            ctk.CTkLabel(
                header_frame,
                text=f"Phase {phase}",
                font=ctk.CTkFont(size=12),
                text_color=phase_colors.get(phase, "gray")
            ).pack(side="right")

        # Nom de l'étude (lien cliquable)
        study_name = study.get("study_name") or study.get("study_number") or "Unnamed Study"
        self.name_btn = ctk.CTkButton(
            self,
            text=study_name,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="transparent",
            text_color=("#1a73e8", "#8ab4f8"),
            hover_color=("gray85", "gray25"),
            anchor="w",
            command=self._on_name_click
        )
        self.name_btn.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        # Infos supplémentaires
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=5)

        sponsor = study.get("sponsor")
        if sponsor:
            ctk.CTkLabel(
                info_frame,
                text=f"Sponsor: {sponsor}",
                font=ctk.CTkFont(size=12),
                text_color=("gray40", "gray60")
            ).pack(anchor="w")

        pathology = study.get("pathology")
        if pathology:
            ctk.CTkLabel(
                info_frame,
                text=f"Pathologie: {pathology}",
                font=ctk.CTkFont(size=12),
                text_color=("gray40", "gray60")
            ).pack(anchor="w")

        # Statistiques
        stats_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray25"), corner_radius=5)
        stats_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=(10, 15))

        if stats:
            patients = stats.get("patients", 0)
            visits = stats.get("visits", 0)
            ae = stats.get("ae", 0)
        else:
            patients = visits = ae = 0

        stats_text = f"{patients} Patients  |  {visits} Visites  |  {ae} AE"
        ctk.CTkLabel(
            stats_frame,
            text=stats_text,
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray70")
        ).pack(pady=8, padx=10)

    def _on_name_click(self) -> None:
        """Callback quand on clique sur le nom."""
        self.on_click(self.study)


class LandingFrame(ctk.CTkFrame):
    """Landing page avec liste des études."""

    def __init__(
        self,
        parent,
        db,
        on_study_select: Callable,
        on_new_study: Callable
    ):
        super().__init__(parent, fg_color="transparent")

        self.db = db
        self.on_study_select = on_study_select
        self.on_new_study = on_new_study

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._create_header()
        self._create_search_bar()
        self._create_studies_grid()

        self.refresh_data()

    def _create_header(self) -> None:
        """Crée l'en-tête."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure(1, weight=1)

        # Titre
        ctk.CTkLabel(
            header,
            text="My Studies",
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        # Sous-titre
        ctk.CTkLabel(
            header,
            text="Select a study to access its dashboard",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray60")
        ).grid(row=1, column=0, sticky="w", pady=(5, 0))

        # Bouton nouvelle étude
        ctk.CTkButton(
            header,
            text="+ New Study",
            command=self.on_new_study,
            width=120,
            height=35
        ).grid(row=0, column=2, rowspan=2, sticky="e", padx=(10, 0))

    def _create_search_bar(self) -> None:
        """Crée la barre de recherche."""
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search studies...",
            width=350,
            height=35
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self._on_search)

        # Stats globales
        self.global_stats = ctk.CTkLabel(
            search_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        self.global_stats.pack(side="right", padx=10)

    def _create_studies_grid(self) -> None:
        """Crée la grille des études."""
        self.studies_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.studies_scroll.grid(row=2, column=0, sticky="nsew")

        # Configurer 3 colonnes
        self.studies_scroll.grid_columnconfigure(0, weight=1)
        self.studies_scroll.grid_columnconfigure(1, weight=1)
        self.studies_scroll.grid_columnconfigure(2, weight=1)

    def refresh_data(self, search: str = "") -> None:
        """Rafraîchit la liste des études."""
        # Nettoyer la grille
        for widget in self.studies_scroll.winfo_children():
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

        # Mettre à jour les stats globales
        self.global_stats.configure(text=f"{len(studies)} study(ies)")

        # Afficher message si aucune étude
        if not studies:
            no_data_frame = ctk.CTkFrame(self.studies_scroll, fg_color="transparent")
            no_data_frame.grid(row=0, column=0, columnspan=3, pady=50)

            ctk.CTkLabel(
                no_data_frame,
                text="No studies found",
                font=ctk.CTkFont(size=18),
                text_color="gray"
            ).pack(pady=10)

            ctk.CTkLabel(
                no_data_frame,
                text="Create your first study to get started",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            ).pack()

            ctk.CTkButton(
                no_data_frame,
                text="+ Create Study",
                command=self.on_new_study,
                width=140
            ).pack(pady=20)

            return

        # Afficher les études en grille (3 colonnes)
        for i, study in enumerate(studies):
            row = i // 3
            col = i % 3

            # Récupérer les stats de l'étude
            stats = self._get_study_stats(study["id"])

            card = StudyCard(
                self.studies_scroll,
                study=study,
                on_click=self._on_study_click,
                stats=stats
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def _get_study_stats(self, study_id: int) -> Dict:
        """Récupère les statistiques d'une étude."""
        try:
            cursor = self.db.connection.cursor()

            # Nombre de patients
            cursor.execute(
                "SELECT COUNT(*) FROM patients WHERE study_id = ?",
                (study_id,)
            )
            patients = cursor.fetchone()[0]

            # Nombre de visites enregistrées
            cursor.execute("""
                SELECT COUNT(*) FROM visits v
                JOIN patients p ON v.patient_id = p.id
                WHERE p.study_id = ? AND v.visit_date IS NOT NULL
            """, (study_id,))
            visits = cursor.fetchone()[0]

            # Nombre d'AE
            cursor.execute(
                "SELECT COUNT(*) FROM adverse_events WHERE study_id = ?",
                (study_id,)
            )
            ae = cursor.fetchone()[0]

            return {"patients": patients, "visits": visits, "ae": ae}
        except Exception:
            return {"patients": 0, "visits": 0, "ae": 0}

    def _on_study_click(self, study: Dict) -> None:
        """Callback quand une étude est cliquée."""
        self.on_study_select(study)

    def _on_search(self, event=None) -> None:
        """Callback pour la recherche."""
        search = self.search_entry.get()
        self.refresh_data(search)
