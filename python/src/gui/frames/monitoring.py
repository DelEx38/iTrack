"""
Gestion des visites de monitoring.
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict, List
from datetime import date, timedelta
import sqlite3


def count_business_days(start_date: date, end_date: date) -> int:
    """Compte les jours ouvrés entre deux dates."""
    if not start_date or not end_date:
        return 0

    days = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # Lundi à Vendredi
            days += 1
        current += timedelta(days=1)
    return days


def add_business_days(start_date: date, days: int) -> date:
    """Ajoute des jours ouvrés à une date."""
    current = start_date
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


class MonitoringDialog(ctk.CTkToplevel):
    """Dialogue pour ajouter/modifier une visite de monitoring."""

    def __init__(self, parent, study_id: int, conn: sqlite3.Connection, visit_data: Optional[Dict] = None):
        super().__init__(parent)

        self.study_id = study_id
        self.conn = conn
        self.visit_data = visit_data
        self.result = None

        self.title("Edit Monitoring Visit" if visit_data else "New Monitoring Visit")
        self.geometry("500x650")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 650) // 2
        self.geometry(f"+{x}+{y}")

        self._create_form()

        if visit_data:
            self._fill_form(visit_data)

    def _create_form(self) -> None:
        """Crée le formulaire."""
        form = ctk.CTkScrollableFrame(self, height=520)
        form.pack(fill="both", expand=True, padx=20, pady=20)

        # Type de visite
        ctk.CTkLabel(form, text="Visit Type").pack(anchor="w", pady=(0, 5))
        self.combo_type = ctk.CTkComboBox(
            form,
            values=["Site Initiation Visit", "Interim Monitoring Visit", "Close-out Visit", "Other"],
            width=250
        )
        self.combo_type.pack(anchor="w", pady=(0, 15))

        # Date de début
        ctk.CTkLabel(form, text="Start Date (YYYY-MM-DD) *").pack(anchor="w", pady=(0, 5))
        self.entry_start = ctk.CTkEntry(form, width=150)
        self.entry_start.pack(anchor="w", pady=(0, 15))

        # Date de fin
        ctk.CTkLabel(form, text="End Date (YYYY-MM-DD)").pack(anchor="w", pady=(0, 5))
        self.entry_end = ctk.CTkEntry(form, width=150)
        self.entry_end.pack(anchor="w", pady=(0, 15))

        # Date lettre de confirmation
        ctk.CTkLabel(form, text="Confirmation Letter Date").pack(anchor="w", pady=(0, 5))
        self.entry_confirmation = ctk.CTkEntry(form, width=150)
        self.entry_confirmation.pack(anchor="w", pady=(0, 15))

        # Date soumission rapport
        ctk.CTkLabel(form, text="Report Submission Date").pack(anchor="w", pady=(0, 5))
        self.entry_report = ctk.CTkEntry(form, width=150)
        self.entry_report.pack(anchor="w", pady=(0, 15))

        # Nombre de turnover
        ctk.CTkLabel(form, text="Turnover Count").pack(anchor="w", pady=(0, 5))
        self.entry_turnover = ctk.CTkEntry(form, width=80)
        self.entry_turnover.insert(0, "0")
        self.entry_turnover.pack(anchor="w", pady=(0, 15))

        # Date approbation rapport
        ctk.CTkLabel(form, text="Report Approval Date").pack(anchor="w", pady=(0, 5))
        self.entry_approval = ctk.CTkEntry(form, width=150)
        self.entry_approval.pack(anchor="w", pady=(0, 15))

        # Date follow-up letter
        ctk.CTkLabel(form, text="Follow-up Letter Date").pack(anchor="w", pady=(0, 5))
        self.entry_followup = ctk.CTkEntry(form, width=150)
        self.entry_followup.pack(anchor="w", pady=(0, 15))

        # Date expenses
        ctk.CTkLabel(form, text="Expenses Submission Date").pack(anchor="w", pady=(0, 5))
        self.entry_expenses = ctk.CTkEntry(form, width=150)
        self.entry_expenses.pack(anchor="w", pady=(0, 15))

        # Commentaires
        ctk.CTkLabel(form, text="Comments").pack(anchor="w", pady=(0, 5))
        self.text_comments = ctk.CTkTextbox(form, height=60, width=400)
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

    def _fill_form(self, data: Dict) -> None:
        """Remplit le formulaire."""
        if data.get("visit_type"):
            self.combo_type.set(data["visit_type"])
        if data.get("start_date"):
            self.entry_start.insert(0, str(data["start_date"]))
        if data.get("end_date"):
            self.entry_end.insert(0, str(data["end_date"]))
        if data.get("confirmation_letter_date"):
            self.entry_confirmation.insert(0, str(data["confirmation_letter_date"]))
        if data.get("report_submission_date"):
            self.entry_report.insert(0, str(data["report_submission_date"]))
        if data.get("turnover_count") is not None:
            self.entry_turnover.delete(0, "end")
            self.entry_turnover.insert(0, str(data["turnover_count"]))
        if data.get("report_approval_date"):
            self.entry_approval.insert(0, str(data["report_approval_date"]))
        if data.get("followup_letter_date"):
            self.entry_followup.insert(0, str(data["followup_letter_date"]))
        if data.get("expenses_submission_date"):
            self.entry_expenses.insert(0, str(data["expenses_submission_date"]))
        if data.get("comments"):
            self.text_comments.insert("1.0", data["comments"])

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse une date."""
        date_str = date_str.strip()
        if not date_str:
            return None
        try:
            parts = date_str.split("-")
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            return None

    def _save(self) -> None:
        """Sauvegarde."""
        start_date = self._parse_date(self.entry_start.get())
        if not start_date:
            messagebox.showerror("Error", "Start date is required (YYYY-MM-DD)")
            return

        try:
            turnover = int(self.entry_turnover.get() or 0)
        except ValueError:
            turnover = 0

        self.result = {
            "study_id": self.study_id,
            "visit_type": self.combo_type.get() or None,
            "start_date": start_date,
            "end_date": self._parse_date(self.entry_end.get()),
            "confirmation_letter_date": self._parse_date(self.entry_confirmation.get()),
            "report_submission_date": self._parse_date(self.entry_report.get()),
            "turnover_count": turnover,
            "report_approval_date": self._parse_date(self.entry_approval.get()),
            "followup_letter_date": self._parse_date(self.entry_followup.get()),
            "expenses_submission_date": self._parse_date(self.entry_expenses.get()),
            "comments": self.text_comments.get("1.0", "end-1c").strip() or None
        }

        self.destroy()


class MonitoringFrame(ctk.CTkFrame):
    """Frame de gestion du monitoring."""

    def __init__(self, parent, study_id: int, db_connection: sqlite3.Connection):
        super().__init__(parent, fg_color="transparent")

        self.study_id = study_id
        self.conn = db_connection

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._create_header()
        self._create_kpis()
        self._create_visit_list()
        self._refresh_data()

    def _create_header(self) -> None:
        """Crée l'en-tête."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="Monitoring Visits",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header,
            text="+ New Visit",
            command=self._new_visit,
            width=100
        ).grid(row=0, column=2, sticky="e")

    def _create_kpis(self) -> None:
        """Crée les KPIs."""
        kpi_frame = ctk.CTkFrame(self)
        kpi_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        # KPI 1: Reports dans les 5 jours
        self.kpi_report_frame = ctk.CTkFrame(kpi_frame, corner_radius=10)
        self.kpi_report_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        self.kpi_report_value = ctk.CTkLabel(
            self.kpi_report_frame,
            text="0/0",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#5cb85c"
        )
        self.kpi_report_value.pack(pady=(15, 5))

        ctk.CTkLabel(
            self.kpi_report_frame,
            text="Reports ≤5 BD",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(0, 15))

        # KPI 2: Follow-up letters dans les 15 jours
        self.kpi_followup_frame = ctk.CTkFrame(kpi_frame, corner_radius=10)
        self.kpi_followup_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        self.kpi_followup_value = ctk.CTkLabel(
            self.kpi_followup_frame,
            text="0/0",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#5bc0de"
        )
        self.kpi_followup_value.pack(pady=(15, 5))

        ctk.CTkLabel(
            self.kpi_followup_frame,
            text="Follow-up ≤15 BD",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(0, 15))

        # KPI 3: Expenses dans les 5 jours
        self.kpi_expenses_frame = ctk.CTkFrame(kpi_frame, corner_radius=10)
        self.kpi_expenses_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        self.kpi_expenses_value = ctk.CTkLabel(
            self.kpi_expenses_frame,
            text="0/0",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#f0ad4e"
        )
        self.kpi_expenses_value.pack(pady=(15, 5))

        ctk.CTkLabel(
            self.kpi_expenses_frame,
            text="Expenses ≤5 BD",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(0, 15))

    def _create_visit_list(self) -> None:
        """Crée la liste des visites."""
        self.list_container = ctk.CTkFrame(self, corner_radius=10)
        self.list_container.grid(row=2, column=0, sticky="nsew")
        self.list_container.grid_columnconfigure(0, weight=1)
        self.list_container.grid_rowconfigure(1, weight=1)

        # En-tête
        header = ctk.CTkFrame(self.list_container, fg_color=("gray80", "gray25"))
        header.grid(row=0, column=0, sticky="ew")

        columns = [
            ("#", 30), ("Type", 80), ("Start", 85), ("End", 85), ("Days", 40),
            ("Confirm", 85), ("Report", 85), ("Approv.", 85), ("F-Up", 85), ("Exp.", 85), ("", 50)
        ]

        for i, (name, width) in enumerate(columns):
            ctk.CTkLabel(header, text=name, font=ctk.CTkFont(size=11, weight="bold"), width=width).grid(
                row=0, column=i, padx=2, pady=8
            )

        # Liste
        self.visit_list = ctk.CTkScrollableFrame(self.list_container, fg_color="transparent")
        self.visit_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def _get_visits(self) -> List[Dict]:
        """Récupère les visites de monitoring."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM monitoring_visits
            WHERE study_id = ?
            ORDER BY start_date DESC
        """, (self.study_id,))
        return [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    def _calculate_kpis(self, visits: List[Dict]) -> Dict:
        """Calcule les KPIs."""
        total_with_end = 0
        reports_on_time = 0
        followup_on_time = 0
        expenses_on_time = 0

        total_reports = 0
        total_followup = 0
        total_expenses = 0

        for visit in visits:
            end_date = visit.get("end_date")
            if not end_date:
                continue

            if isinstance(end_date, str):
                parts = end_date.split("-")
                end_date = date(int(parts[0]), int(parts[1]), int(parts[2]))

            total_with_end += 1

            # Report submission
            report_date = visit.get("report_submission_date")
            if report_date:
                if isinstance(report_date, str):
                    parts = report_date.split("-")
                    report_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
                total_reports += 1
                bd = count_business_days(end_date, report_date) - 1
                if bd <= 5:
                    reports_on_time += 1

            # Follow-up letter
            followup_date = visit.get("followup_letter_date")
            if followup_date:
                if isinstance(followup_date, str):
                    parts = followup_date.split("-")
                    followup_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
                total_followup += 1
                bd = count_business_days(end_date, followup_date) - 1
                if bd <= 15:
                    followup_on_time += 1

            # Expenses
            expenses_date = visit.get("expenses_submission_date")
            if expenses_date:
                if isinstance(expenses_date, str):
                    parts = expenses_date.split("-")
                    expenses_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
                total_expenses += 1
                bd = count_business_days(end_date, expenses_date) - 1
                if bd <= 5:
                    expenses_on_time += 1

        return {
            "reports_on_time": reports_on_time,
            "total_reports": total_reports,
            "followup_on_time": followup_on_time,
            "total_followup": total_followup,
            "expenses_on_time": expenses_on_time,
            "total_expenses": total_expenses
        }

    def _refresh_data(self) -> None:
        """Rafraîchit les données."""
        visits = self._get_visits()

        # Mettre à jour les KPIs
        kpis = self._calculate_kpis(visits)

        # Calcul des pourcentages
        report_pct = (kpis['reports_on_time'] / kpis['total_reports'] * 100) if kpis['total_reports'] > 0 else 0
        followup_pct = (kpis['followup_on_time'] / kpis['total_followup'] * 100) if kpis['total_followup'] > 0 else 0
        expenses_pct = (kpis['expenses_on_time'] / kpis['total_expenses'] * 100) if kpis['total_expenses'] > 0 else 0

        self.kpi_report_value.configure(
            text=f"{kpis['reports_on_time']}/{kpis['total_reports']} ({report_pct:.0f}%)"
        )
        self.kpi_followup_value.configure(
            text=f"{kpis['followup_on_time']}/{kpis['total_followup']} ({followup_pct:.0f}%)"
        )
        self.kpi_expenses_value.configure(
            text=f"{kpis['expenses_on_time']}/{kpis['total_expenses']} ({expenses_pct:.0f}%)"
        )

        # Rafraîchir la liste
        for widget in self.visit_list.winfo_children():
            widget.destroy()

        if not visits:
            ctk.CTkLabel(
                self.visit_list,
                text="No monitoring visits recorded",
                text_color="gray"
            ).grid(row=0, column=0, columnspan=11, pady=50)
            return

        for i, visit in enumerate(visits):
            self._add_visit_row(i, visit)

    def _add_visit_row(self, row: int, visit: Dict) -> None:
        """Ajoute une ligne de visite."""
        row_frame = ctk.CTkFrame(self.visit_list, fg_color="transparent")
        row_frame.grid(row=row, column=0, sticky="ew", pady=2)

        # Numéro
        ctk.CTkLabel(row_frame, text=str(visit.get("visit_number", row + 1)), width=30).grid(row=0, column=0, padx=2)

        # Type (abrégé)
        vtype = visit.get("visit_type", "")
        if vtype == "Site Initiation Visit":
            vtype = "SIV"
        elif vtype == "Interim Monitoring Visit":
            vtype = "IMV"
        elif vtype == "Close-out Visit":
            vtype = "COV"
        ctk.CTkLabel(row_frame, text=vtype, width=80).grid(row=0, column=1, padx=2)

        # Dates
        start = str(visit.get("start_date", ""))[-10:] if visit.get("start_date") else "-"
        end = str(visit.get("end_date", ""))[-10:] if visit.get("end_date") else "-"

        ctk.CTkLabel(row_frame, text=start, width=85, font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=2)
        ctk.CTkLabel(row_frame, text=end, width=85, font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=2)

        # Nombre de jours
        days = "-"
        if visit.get("start_date") and visit.get("end_date"):
            try:
                s = visit["start_date"]
                e = visit["end_date"]
                if isinstance(s, str):
                    parts = s.split("-")
                    s = date(int(parts[0]), int(parts[1]), int(parts[2]))
                if isinstance(e, str):
                    parts = e.split("-")
                    e = date(int(parts[0]), int(parts[1]), int(parts[2]))
                days = str((e - s).days + 1)
            except:
                pass
        ctk.CTkLabel(row_frame, text=days, width=40).grid(row=0, column=4, padx=2)

        # Confirmation letter
        conf = str(visit.get("confirmation_letter_date", ""))[-10:] if visit.get("confirmation_letter_date") else "-"
        ctk.CTkLabel(row_frame, text=conf, width=85, font=ctk.CTkFont(size=11)).grid(row=0, column=5, padx=2)

        # Report submission
        report = str(visit.get("report_submission_date", ""))[-10:] if visit.get("report_submission_date") else "-"
        ctk.CTkLabel(row_frame, text=report, width=85, font=ctk.CTkFont(size=11)).grid(row=0, column=6, padx=2)

        # Approval
        approv = str(visit.get("report_approval_date", ""))[-10:] if visit.get("report_approval_date") else "-"
        ctk.CTkLabel(row_frame, text=approv, width=85, font=ctk.CTkFont(size=11)).grid(row=0, column=7, padx=2)

        # Follow-up
        fup = str(visit.get("followup_letter_date", ""))[-10:] if visit.get("followup_letter_date") else "-"
        ctk.CTkLabel(row_frame, text=fup, width=85, font=ctk.CTkFont(size=11)).grid(row=0, column=8, padx=2)

        # Expenses
        exp = str(visit.get("expenses_submission_date", ""))[-10:] if visit.get("expenses_submission_date") else "-"
        ctk.CTkLabel(row_frame, text=exp, width=85, font=ctk.CTkFont(size=11)).grid(row=0, column=9, padx=2)

        # Edit button
        ctk.CTkButton(
            row_frame,
            text="Edit",
            width=45,
            height=24,
            command=lambda v=visit: self._edit_visit(v)
        ).grid(row=0, column=10, padx=2)

    def _new_visit(self) -> None:
        """Crée une nouvelle visite."""
        dialog = MonitoringDialog(self, self.study_id, self.conn)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self._create_visit(dialog.result)
                self._refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create visit: {e}")

    def _create_visit(self, data: Dict) -> None:
        """Crée une visite en base."""
        cursor = self.conn.cursor()

        # Prochain numéro
        cursor.execute(
            "SELECT COALESCE(MAX(visit_number), 0) + 1 FROM monitoring_visits WHERE study_id = ?",
            (self.study_id,)
        )
        visit_number = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO monitoring_visits (
                study_id, visit_number, visit_type, start_date, end_date,
                confirmation_letter_date, report_submission_date, turnover_count,
                report_approval_date, followup_letter_date, expenses_submission_date, comments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["study_id"], visit_number, data["visit_type"], data["start_date"],
            data["end_date"], data["confirmation_letter_date"], data["report_submission_date"],
            data["turnover_count"], data["report_approval_date"], data["followup_letter_date"],
            data["expenses_submission_date"], data["comments"]
        ))
        self.conn.commit()

    def _edit_visit(self, visit: Dict) -> None:
        """Modifie une visite."""
        dialog = MonitoringDialog(self, self.study_id, self.conn, visit)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self._update_visit(visit["id"], dialog.result)
                self._refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Could not update visit: {e}")

    def _update_visit(self, visit_id: int, data: Dict) -> None:
        """Met à jour une visite."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE monitoring_visits SET
                visit_type = ?, start_date = ?, end_date = ?,
                confirmation_letter_date = ?, report_submission_date = ?, turnover_count = ?,
                report_approval_date = ?, followup_letter_date = ?, expenses_submission_date = ?,
                comments = ?
            WHERE id = ?
        """, (
            data["visit_type"], data["start_date"], data["end_date"],
            data["confirmation_letter_date"], data["report_submission_date"], data["turnover_count"],
            data["report_approval_date"], data["followup_letter_date"], data["expenses_submission_date"],
            data["comments"], visit_id
        ))
        self.conn.commit()
