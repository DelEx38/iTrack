"""
Génération de rapports PDF pour le suivi d'étude clinique.

Produit un rapport complet incluant : résumé, patients, visites, AE, queries.
"""

from datetime import date
from typing import Dict, List, Any, Optional


# Couleurs
_BLUE_DARK  = (30,  80, 140)
_BLUE_LIGHT = (70, 130, 200)
_GREY_HEAD  = (240, 240, 245)
_GREY_ROW   = (250, 250, 252)
_RED        = (200,  50,  50)
_ORANGE     = (220, 130,  30)
_GREEN      = (40,  140,  70)
_WHITE      = (255, 255, 255)
_BLACK      = (30,   30,  30)


class ReportGenerator:
    """
    Génère un rapport PDF de suivi d'étude clinique.

    Usage :
        gen = ReportGenerator(study, patient_queries, visit_queries, ae_queries, query_queries)
        gen.generate("output/rapport.pdf")
    """

    def __init__(
        self,
        study: Dict[str, Any],
        patient_queries,
        visit_queries,
        ae_queries,
        query_queries,
    ):
        self.study = study
        self.patient_queries = patient_queries
        self.visit_queries = visit_queries
        self.ae_queries = ae_queries
        self.query_queries = query_queries

    # ------------------------------------------------------------------
    # Point d'entrée
    # ------------------------------------------------------------------

    def generate(self, output_path: str) -> None:
        """
        Génère le rapport PDF et l'enregistre à output_path.

        Raises:
            ImportError: si fpdf2 n'est pas installé
        """
        try:
            from fpdf import FPDF
        except ImportError:
            raise ImportError(
                "fpdf2 est requis pour générer des rapports PDF. "
                "Installez-le avec : pip install fpdf2"
            )

        pdf = _ClinicalPDF(self.study)

        # Charger les données
        patients  = self.patient_queries.get_all()
        ae_list   = self.ae_queries.get_all()
        queries   = self.query_queries.get_all()
        visit_configs = self.visit_queries.get_configs()

        # --- Page de garde ---
        pdf.add_page()
        self._page_garde(pdf)

        # --- Résumé ---
        pdf.add_page()
        self._section_resume(pdf, patients, ae_list, queries)

        # --- Patients ---
        pdf.add_page()
        self._section_patients(pdf, patients)

        # --- Visites ---
        if visit_configs and patients:
            pdf.add_page()
            self._section_visites(pdf, patients, visit_configs)

        # --- Événements indésirables ---
        if ae_list:
            pdf.add_page()
            self._section_ae(pdf, ae_list)

        # --- Queries ouvertes ---
        open_queries = [q for q in queries if q.get("status", "").lower() != "closed"]
        if open_queries:
            pdf.add_page()
            self._section_queries(pdf, open_queries)

        pdf.output(output_path)

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def _page_garde(self, pdf: "FPDF") -> None:
        """Page de garde avec titre de l'étude."""
        pdf.ln(30)
        pdf.set_fill_color(*_BLUE_DARK)
        pdf.rect(10, pdf.get_y(), 190, 60, "F")

        pdf.set_xy(10, pdf.get_y() + 10)
        pdf.set_text_color(*_WHITE)
        pdf.set_font("Helvetica", "B", 22)
        pdf.multi_cell(190, 10, "Clinical Study Report", align="C")
        pdf.ln(4)
        pdf.set_font("Helvetica", "", 14)
        study_name = self.study.get("study_name") or self.study.get("study_number", "—")
        pdf.multi_cell(190, 8, study_name, align="C")

        pdf.set_text_color(*_BLACK)
        pdf.ln(20)
        pdf.set_font("Helvetica", "", 11)

        infos = [
            ("Study Number",    self.study.get("study_number", "—")),
            ("Sponsor",         self.study.get("sponsor", "—")),
            ("Protocol Version",self.study.get("protocol_version", "—")),
            ("Report Date",     date.today().strftime("%d-%b-%Y")),
        ]
        for label, value in infos:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(55, 8, f"{label}:", border=0)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 8, str(value or "—"), border=0, new_x="LMARGIN", new_y="NEXT")

    def _section_resume(self, pdf: "FPDF", patients: List, ae_list: List, queries: List) -> None:
        """Section résumé avec statistiques clés."""
        _section_title(pdf, "Summary")

        # Comptages patients
        by_status: Dict[str, int] = {}
        for p in patients:
            s = p.get("status", "Unknown")
            by_status[s] = by_status.get(s, 0) + 1

        total    = len(patients)
        ae_total = len(ae_list)
        ae_sae   = sum(1 for a in ae_list if a.get("is_serious"))
        open_q   = sum(1 for q in queries if q.get("status", "").lower() != "closed")

        # Blocs de stats (2 colonnes)
        stats = [
            ("Total Patients",     str(total),    _BLUE_LIGHT),
            ("Screening",          str(by_status.get("Screening", 0)), (100, 150, 220)),
            ("Included",           str(by_status.get("Included", 0)),  _GREEN),
            ("Completed",          str(by_status.get("Completed", 0)), (60, 160, 90)),
            ("Withdrawn",          str(by_status.get("Withdrawn", 0)), _ORANGE),
            ("Adverse Events",     str(ae_total), _ORANGE),
            ("Serious AE (SAE)",   str(ae_sae),   _RED),
            ("Open Queries",       str(open_q),   (180, 100, 30)),
        ]

        col_w, box_h, margin = 90, 20, 5
        x_start = pdf.l_margin
        for i, (label, value, color) in enumerate(stats):
            col = i % 2
            x = x_start + col * (col_w + margin)
            if col == 0 and i > 0:
                pdf.ln(box_h + margin)
            y = pdf.get_y()

            pdf.set_fill_color(*color)
            pdf.rect(x, y, col_w, box_h, "F")
            pdf.set_xy(x, y + 2)
            pdf.set_text_color(*_WHITE)
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(col_w, 7, value, align="C")
            pdf.set_xy(x, y + 10)
            pdf.set_font("Helvetica", "", 8)
            pdf.cell(col_w, 6, label, align="C")
            pdf.set_text_color(*_BLACK)

            if col == 1:
                pass  # nouvelle ligne gérée au prochain tour

        pdf.ln(box_h + margin + 5)

        # Tableau patients par statut
        _section_subtitle(pdf, "Patients by Status")
        _table(pdf,
               headers=["Status", "Count", "%"],
               col_widths=[80, 40, 40],
               rows=[
                   [s, str(c), f"{c/total*100:.1f}%" if total else "0%"]
                   for s, c in sorted(by_status.items())
               ] or [["No patients", "0", "—"]])

    def _section_patients(self, pdf: "FPDF", patients: List) -> None:
        """Tableau de tous les patients."""
        _section_title(pdf, "Patients")
        _table(pdf,
               headers=["#", "Patient No.", "Initials", "Site", "Status", "Birth Date"],
               col_widths=[10, 35, 25, 30, 30, 30],
               rows=[
                   [
                       str(i + 1),
                       p.get("patient_number", ""),
                       p.get("initials", ""),
                       p.get("site_id", ""),
                       p.get("status", ""),
                       str(p.get("birth_date", "") or ""),
                   ]
                   for i, p in enumerate(patients)
               ] or [["—", "No patients", "", "", "", ""]])

    def _section_visites(self, pdf: "FPDF", patients: List, visit_configs: List) -> None:
        """Grille des visites par patient (X = réalisée, · = non réalisée)."""
        _section_title(pdf, "Visit Tracking")

        # Limiter à 8 configs max pour tenir en largeur
        configs = visit_configs[:8]
        visit_names = [vc.get("visit_name", f"V{i+1}") for i, vc in enumerate(configs)]

        headers = ["Patient"] + visit_names
        col_w_patient = 35
        col_w_visit   = max(12, int((190 - col_w_patient) / len(configs)))
        col_widths     = [col_w_patient] + [col_w_visit] * len(configs)

        rows = []
        for patient in patients:
            pid = patient["id"]
            recorded = {
                v["visit_config_id"]: v
                for v in self.visit_queries.get_patient_visits(pid)
            }
            row = [patient.get("patient_number", "")]
            for vc in configs:
                row.append("X" if vc["id"] in recorded else "-")
            rows.append(row)

        _table(pdf, headers=headers, col_widths=col_widths, rows=rows or [["No data"] + [""] * len(configs)])

        if len(visit_configs) > 8:
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 5, f"  * {len(visit_configs) - 8} additional visit(s) not shown.", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(*_BLACK)

    def _section_ae(self, pdf: "FPDF", ae_list: List) -> None:
        """Tableau des événements indésirables."""
        _section_title(pdf, f"Adverse Events ({len(ae_list)} total)")

        def _severity_indicator(sev: str) -> str:
            return {"Mild": "+", "Moderate": "++", "Severe": "+++"}.get(sev, sev)

        rows = [
            [
                a.get("patient_number", ""),
                a.get("ae_term", ""),
                _severity_indicator(a.get("severity", "")),
                "SAE" if a.get("is_serious") else "AE",
                a.get("outcome", ""),
                str(a.get("start_date", "") or ""),
            ]
            for a in ae_list
        ]
        _table(pdf,
               headers=["Patient", "AE Term", "Severity", "Type", "Outcome", "Start Date"],
               col_widths=[28, 55, 22, 16, 30, 30],
               rows=rows or [["—", "No adverse events", "", "", "", ""]])

    def _section_queries(self, pdf: "FPDF", queries: List) -> None:
        """Tableau des queries ouvertes."""
        _section_title(pdf, f"Open Queries ({len(queries)})")
        rows = [
            [
                q.get("patient_number", ""),
                q.get("field_name", ""),
                (q.get("description", "") or "")[:50],
                q.get("priority", ""),
                q.get("status", ""),
            ]
            for q in queries
        ]
        _table(pdf,
               headers=["Patient", "Field", "Description", "Priority", "Status"],
               col_widths=[28, 35, 75, 22, 22],
               rows=rows or [["—", "No open queries", "", "", ""]])


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _section_title(pdf, title: str) -> None:
    """Titre de section principal."""
    pdf.set_fill_color(*_BLUE_DARK)
    pdf.set_text_color(*_WHITE)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*_BLACK)
    pdf.ln(4)


def _section_subtitle(pdf, title: str) -> None:
    """Sous-titre de section."""
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*_BLUE_LIGHT)
    pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*_BLACK)
    pdf.ln(2)


def _table(pdf, headers: List[str], col_widths: List[int], rows: List[List[str]]) -> None:
    """
    Dessine un tableau avec en-tête colorée et alternance de lignes.
    Gère le saut de page automatique.
    """
    row_h = 7

    # En-tête
    pdf.set_fill_color(*_GREY_HEAD)
    pdf.set_font("Helvetica", "B", 8)
    for i, (header, w) in enumerate(zip(headers, col_widths)):
        pdf.cell(w, row_h, _truncate(header, w), border=1, fill=True, align="C")
    pdf.ln()

    # Lignes de données
    pdf.set_font("Helvetica", "", 8)
    for row_idx, row in enumerate(rows):
        # Saut de page si nécessaire
        if pdf.get_y() + row_h > pdf.page_break_trigger:
            pdf.add_page()
            # Ré-afficher l'en-tête
            pdf.set_fill_color(*_GREY_HEAD)
            pdf.set_font("Helvetica", "B", 8)
            for header, w in zip(headers, col_widths):
                pdf.cell(w, row_h, _truncate(header, w), border=1, fill=True, align="C")
            pdf.ln()
            pdf.set_font("Helvetica", "", 8)

        fill = row_idx % 2 == 1
        pdf.set_fill_color(*_GREY_ROW)
        for cell, w in zip(row, col_widths):
            pdf.cell(w, row_h, _truncate(str(cell or ""), w), border=1, fill=fill)
        pdf.ln()

    pdf.ln(4)


def _truncate(text: str, width_mm: int, char_w: float = 1.8) -> str:
    """Tronque un texte selon la largeur de colonne estimée."""
    max_chars = int(width_mm / char_w)
    return text if len(text) <= max_chars else text[: max_chars - 3] + "..."


class _ClinicalPDF:
    """Sous-classe FPDF avec en-tête et pied de page personnalisés."""

    def __new__(cls, study: Dict) -> "FPDF":
        try:
            from fpdf import FPDF

            class _PDF(FPDF):
                def __init__(self, study):
                    super().__init__()
                    self._study = study
                    self.set_auto_page_break(auto=True, margin=15)
                    self.set_margins(10, 15, 10)

                def header(self):
                    self.set_font("Helvetica", "B", 8)
                    self.set_text_color(*_BLUE_DARK)
                    study_ref = self._study.get("study_number") or self._study.get("study_name", "")
                    self.cell(0, 6, f"iTrack | {study_ref}", align="L")
                    self.set_text_color(*_BLACK)
                    self.ln(1)
                    self.set_draw_color(*_BLUE_LIGHT)
                    self.set_line_width(0.4)
                    self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
                    self.ln(4)

                def footer(self):
                    self.set_y(-12)
                    self.set_font("Helvetica", "I", 7)
                    self.set_text_color(150, 150, 150)
                    gen_date = date.today().strftime("%d-%b-%Y")
                    self.cell(0, 5, f"Generated by iTrack on {gen_date}  |  Page {self.page_no()}", align="C")

            return _PDF(study)
        except ImportError:
            raise ImportError("fpdf2 est requis. Installez-le avec : pip install fpdf2")
