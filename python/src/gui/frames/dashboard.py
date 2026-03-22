"""
Dashboard avec statistiques et vue d'ensemble.
"""

import customtkinter as ctk
from typing import Optional


class StatCard(ctk.CTkFrame):
    """Carte de statistique."""

    def __init__(self, parent, title: str, value: str, color: str = "#1f538d"):
        super().__init__(parent, corner_radius=10)

        self.grid_columnconfigure(0, weight=1)

        # Valeur
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=color
        )
        self.value_label.grid(row=0, column=0, padx=20, pady=(20, 5))

        # Titre
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.title_label.grid(row=1, column=0, padx=20, pady=(0, 20))

    def update_value(self, value: str) -> None:
        """Met à jour la valeur."""
        self.value_label.configure(text=value)


class DashboardFrame(ctk.CTkFrame):
    """Frame du tableau de bord."""

    def __init__(self, parent, patient_queries, visit_queries, ae_queries):
        super().__init__(parent, fg_color="transparent")

        self.patient_queries = patient_queries
        self.visit_queries = visit_queries
        self.ae_queries = ae_queries

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Titre
        self.title = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title.grid(row=0, column=0, columnspan=4, padx=20, pady=(0, 20), sticky="w")

        # Cartes de statistiques
        self._create_stat_cards()

        # Section des visites à venir
        self._create_upcoming_visits()

        # Section des alertes
        self._create_alerts()

        # Charger les données
        self.refresh_data()

    def _create_stat_cards(self) -> None:
        """Crée les cartes de statistiques."""
        # Total patients
        self.card_total = StatCard(self, "Total Patients", "0", "#3a7ebf")
        self.card_total.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # En screening
        self.card_screening = StatCard(self, "Screening", "0", "#f0ad4e")
        self.card_screening.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Inclus
        self.card_included = StatCard(self, "Included", "0", "#5cb85c")
        self.card_included.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        # Adverse Events
        self.card_ae = StatCard(self, "Adverse Events", "0", "#d9534f")
        self.card_ae.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")

    def _create_upcoming_visits(self) -> None:
        """Crée la section des visites à venir."""
        self.visits_frame = ctk.CTkFrame(self, corner_radius=10)
        self.visits_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.visits_frame.grid_columnconfigure(0, weight=1)
        self.visits_frame.grid_rowconfigure(1, weight=1)

        # Titre
        visits_title = ctk.CTkLabel(
            self.visits_frame,
            text="Upcoming Visits",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        visits_title.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        # Liste des visites
        self.visits_list = ctk.CTkScrollableFrame(self.visits_frame)
        self.visits_list.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.visits_list.grid_columnconfigure(0, weight=1)

        # Placeholder
        self.no_visits_label = ctk.CTkLabel(
            self.visits_list,
            text="No upcoming visits",
            text_color="gray"
        )
        self.no_visits_label.grid(row=0, column=0, pady=20)

    def _create_alerts(self) -> None:
        """Crée la section des alertes."""
        self.alerts_frame = ctk.CTkFrame(self, corner_radius=10)
        self.alerts_frame.grid(row=2, column=2, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.alerts_frame.grid_columnconfigure(0, weight=1)
        self.alerts_frame.grid_rowconfigure(1, weight=1)

        # Titre
        alerts_title = ctk.CTkLabel(
            self.alerts_frame,
            text="Alerts & Notifications",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        alerts_title.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        # Liste des alertes
        self.alerts_list = ctk.CTkScrollableFrame(self.alerts_frame)
        self.alerts_list.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.alerts_list.grid_columnconfigure(0, weight=1)

        # Placeholder
        self.no_alerts_label = ctk.CTkLabel(
            self.alerts_list,
            text="No alerts",
            text_color="gray"
        )
        self.no_alerts_label.grid(row=0, column=0, pady=20)

    def refresh_data(self) -> None:
        """Rafraîchit les données du dashboard."""
        # Compter les patients par statut
        status_counts = self.patient_queries.count_by_status()
        total = sum(status_counts.values())

        self.card_total.update_value(str(total))
        self.card_screening.update_value(str(status_counts.get("Screening", 0)))
        self.card_included.update_value(str(status_counts.get("Included", 0)))

        # Compter les EI
        ae_counts = self.ae_queries.count_by_status()
        self.card_ae.update_value(str(ae_counts.get("total", 0)))

    def add_visit_item(self, patient: str, visit: str, date: str, status: str = "Planned") -> None:
        """Ajoute une visite à la liste."""
        self.no_visits_label.grid_forget()

        item_frame = ctk.CTkFrame(self.visits_list, fg_color="transparent")
        item_frame.grid(sticky="ew", pady=2)
        item_frame.grid_columnconfigure(1, weight=1)

        # Patient
        patient_label = ctk.CTkLabel(item_frame, text=patient, font=ctk.CTkFont(weight="bold"))
        patient_label.grid(row=0, column=0, padx=5, sticky="w")

        # Visite
        visit_label = ctk.CTkLabel(item_frame, text=visit)
        visit_label.grid(row=0, column=1, padx=5, sticky="w")

        # Date
        date_label = ctk.CTkLabel(item_frame, text=date, text_color="gray")
        date_label.grid(row=0, column=2, padx=5, sticky="e")

    def add_alert(self, message: str, alert_type: str = "warning") -> None:
        """Ajoute une alerte."""
        self.no_alerts_label.grid_forget()

        colors = {
            "warning": "#f0ad4e",
            "danger": "#d9534f",
            "info": "#5bc0de",
            "success": "#5cb85c"
        }

        item_frame = ctk.CTkFrame(self.alerts_list, fg_color="transparent")
        item_frame.grid(sticky="ew", pady=2)

        indicator = ctk.CTkLabel(
            item_frame,
            text="●",
            text_color=colors.get(alert_type, "#5bc0de")
        )
        indicator.grid(row=0, column=0, padx=5)

        message_label = ctk.CTkLabel(item_frame, text=message, anchor="w")
        message_label.grid(row=0, column=1, padx=5, sticky="w")
