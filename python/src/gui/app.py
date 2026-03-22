"""
Application principale de suivi d'étude clinique.
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict
from pathlib import Path

from database.models import Database
from database.queries import PatientQueries, VisitQueries, ConsentQueries, AdverseEventQueries
from gui.frames.sidebar import SidebarFrame
from gui.frames.patients import PatientsFrame
from gui.frames.dashboard import DashboardFrame
from gui.frames.studies import StudiesFrame, StudyDialog
from gui.frames.visits import VisitsFrame
from gui.frames.adverse_events import AdverseEventsFrame
from gui.frames.documents import DocumentsFrame
from gui.frames.settings import SettingsFrame
from gui.frames.monitoring import MonitoringFrame
from gui.frames.landing import LandingFrame
from gui.frames.sites import SitesFrame


class ClinicalStudyApp(ctk.CTk):
    """Application principale."""

    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre
        self.title("Clinical Study Tracker")
        self.geometry("1270x760")
        self.minsize(1270, 760)

        # Thème
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Base de données
        self.db = Database()
        self.db.connect()
        self.db.init_schema()
        self.db.init_default_data(num_visits=25)

        # Étude courante
        self.current_study: Optional[Dict] = None
        self.studies = self.db.get_studies()

        # Si aucune étude, en créer une par défaut
        if not self.studies:
            study_id = self.db.create_study(study_number="STUDY-001", study_name="My First Study")
            self.studies = self.db.get_studies()
            self.current_study = self.db.get_study_by_id(study_id)
        else:
            self.current_study = self.studies[0]

        # Requêtes
        study_id = self.current_study["id"] if self.current_study else None
        self.patient_queries = PatientQueries(self.db.connection, study_id)
        self.visit_queries = VisitQueries(self.db.connection)
        self.consent_queries = ConsentQueries(self.db.connection)
        self.ae_queries = AdverseEventQueries(self.db.connection, study_id)

        # Configuration du grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Frame actuelle
        self.current_frame: Optional[ctk.CTkFrame] = None

        # Création des widgets
        self._create_sidebar()
        self._show_landing()

    def _create_sidebar(self) -> None:
        """Crée la barre latérale de navigation."""
        self.sidebar = SidebarFrame(
            self,
            on_home=self._show_landing,
            on_dashboard=self._show_dashboard,
            on_sites=self._show_sites,
            on_patients=self._show_patients,
            on_visits=self._show_visits,
            on_adverse_events=self._show_adverse_events,
            on_documents=self._show_documents,
            on_monitoring=self._show_monitoring,
            on_export=self._export_excel,
            on_settings=self._show_settings,
            on_study_change=self._on_study_change,
            studies=self.studies,
            current_study=self.current_study
        )
        self.sidebar.grid(row=0, column=0, sticky="nsw")

    def _on_study_change(self, study_identifier: str) -> None:
        """Callback quand l'étude change."""
        for study in self.studies:
            # Chercher par study_number ou study_name
            if (study.get("study_number") == study_identifier or
                study.get("study_name") == study_identifier):
                self.current_study = study
                self.patient_queries.set_study(study["id"])
                self.ae_queries.set_study(study["id"])
                self._update_title()
                self._show_dashboard()
                break

    def _refresh_studies(self) -> None:
        """Rafraîchit la liste des études."""
        self.studies = self.db.get_studies()
        self.sidebar.update_studies(self.studies, self.current_study)

    def _update_title(self) -> None:
        """Met à jour le titre de la fenêtre."""
        if self.current_study:
            study_label = self.current_study.get('study_number') or self.current_study.get('study_name') or ''
            self.title(f"Clinical Study Tracker - {study_label}")
        else:
            self.title("Clinical Study Tracker")

    def _switch_frame(self, frame_class, **kwargs) -> None:
        """Change le frame principal."""
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = frame_class(self, **kwargs)
        self.current_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def _show_landing(self) -> None:
        """Affiche la landing page avec la liste des études."""
        # Masquer la sidebar sur la landing
        self.sidebar.grid_remove()

        self._switch_frame(
            LandingFrame,
            db=self.db,
            on_study_select=self._on_study_select_from_landing,
            on_new_study=self._new_study_from_landing
        )

    def _on_study_select_from_landing(self, study: Dict) -> None:
        """Callback quand une étude est sélectionnée depuis la landing page."""
        self.current_study = study
        self.patient_queries.set_study(study["id"])
        self.ae_queries.set_study(study["id"])
        self._update_title()

        # Afficher la sidebar
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.update_studies(self.studies, self.current_study)

        # Afficher les sites de l'étude
        self._show_sites()

    def _new_study_from_landing(self) -> None:
        """Ouvre le dialogue pour créer une nouvelle étude depuis la landing."""
        dialog = StudyDialog(self, self.db)
        self.wait_window(dialog)

        if dialog.result:
            try:
                vendors_to_add = dialog.result.pop("vendors_to_add", [])
                dialog.result.pop("vendors_to_delete", [])

                study_id = self.db.create_study(**dialog.result)

                for vendor in vendors_to_add:
                    self.db.add_study_vendor(
                        study_id,
                        vendor["vendor_type_id"],
                        vendor["vendor_name"],
                        vendor.get("contact", "")
                    )

                # Rafraîchir les données
                self._refresh_studies()
                self._show_landing()

            except Exception as e:
                messagebox.showerror("Error", f"Could not create study: {e}")

    def _show_dashboard(self) -> None:
        """Affiche le tableau de bord."""
        self._switch_frame(
            DashboardFrame,
            patient_queries=self.patient_queries,
            visit_queries=self.visit_queries,
            ae_queries=self.ae_queries
        )
        self.sidebar.set_active("dashboard")

    def _show_studies(self) -> None:
        """Affiche la gestion des études."""
        self._switch_frame(StudiesFrame, db=self.db)
        self.sidebar.set_active("studies")

    def _show_patients(self) -> None:
        """Affiche la liste des patients."""
        self._switch_frame(
            PatientsFrame,
            patient_queries=self.patient_queries,
            visit_queries=self.visit_queries,
            consent_queries=self.consent_queries
        )

    def _show_visits(self) -> None:
        """Affiche la gestion des visites."""
        self._switch_frame(
            VisitsFrame,
            patient_queries=self.patient_queries,
            visit_queries=self.visit_queries
        )

    def _show_adverse_events(self) -> None:
        """Affiche les événements indésirables."""
        self._switch_frame(
            AdverseEventsFrame,
            patient_queries=self.patient_queries,
            ae_queries=self.ae_queries
        )

    def _show_documents(self) -> None:
        """Affiche les documents."""
        self._switch_frame(
            DocumentsFrame,
            patient_queries=self.patient_queries,
            consent_queries=self.consent_queries
        )

    def _show_monitoring(self) -> None:
        """Affiche le monitoring."""
        study_id = self.current_study["id"] if self.current_study else None
        if study_id:
            self._switch_frame(
                MonitoringFrame,
                study_id=study_id,
                db_connection=self.db.connection
            )

    def _show_sites(self) -> None:
        """Affiche la gestion des sites."""
        self._switch_frame(
            SitesFrame,
            db=self.db,
            current_study=self.current_study
        )
        self.sidebar.set_active("sites")

    def _show_settings(self) -> None:
        """Affiche les paramètres."""
        self._switch_frame(
            SettingsFrame,
            visit_queries=self.visit_queries,
            consent_queries=self.consent_queries,
            db_connection=self.db.connection
        )

    def _export_excel(self) -> None:
        """Exporte les données en Excel."""
        from tkinter import filedialog
        from excel_generator import create_visit_tracking

        study_name = self.current_study["study_name"] if self.current_study else "study"
        default_name = f"suivi_{study_name.replace(' ', '_')}.xlsx"

        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfilename=default_name
        )

        if filepath:
            try:
                # TODO: Générer depuis la base de données
                wb = create_visit_tracking(num_visits=25, num_patients=50)
                wb.save(filepath)
                messagebox.showinfo("Export réussi", f"Fichier exporté :\n{filepath}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export :\n{str(e)}")

    def on_closing(self) -> None:
        """Appelé à la fermeture de l'application."""
        self.db.close()
        self.destroy()


def main():
    """Point d'entrée de l'application."""
    app = ClinicalStudyApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
