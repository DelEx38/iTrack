"""
Service de parsing des Schedule of Assessments (SoA) depuis fichiers PDF.

Utilise pdfplumber pour extraire les tableaux et applique les mêmes patterns
regex que SoaParserService pour détecter visites, jours cibles et fenêtres.
"""

import re
from typing import List, Optional, Tuple, Dict
from io import BytesIO

from src.services.soa_parser import VisitConfig, SoaParserService


class SoaPdfParser:
    """
    Parser de SoA depuis fichiers PDF.

    Stratégie :
    1. Extraire tous les tableaux du PDF via pdfplumber
    2. Identifier le tableau SoA (contient des en-têtes de visites)
    3. Réutiliser les patterns regex de SoaParserService pour le parsing
    """

    def __init__(self):
        self._helper = SoaParserService()
        self.visits: List[VisitConfig] = []

    def parse_file(self, file_bytes: bytes) -> List[VisitConfig]:
        """
        Parse un fichier PDF et extrait les configurations de visites.

        Args:
            file_bytes: Contenu du fichier PDF en bytes

        Returns:
            Liste des VisitConfig extraites

        Raises:
            ImportError: si pdfplumber n'est pas installé
            ValueError: si aucun tableau SoA n'est trouvé
        """
        try:
            import pdfplumber
        except ImportError:
            raise ImportError(
                "pdfplumber est requis pour lire les PDF. "
                "Installez-le avec : pip install pdfplumber"
            )

        self.visits = []

        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            soa_table = self._find_soa_table(pdf)
            if not soa_table:
                raise ValueError("Aucun tableau SoA trouvé dans le PDF")

            self._parse_table(soa_table)

        return self.visits

    # ------------------------------------------------------------------
    # Recherche du tableau SoA
    # ------------------------------------------------------------------

    def _find_soa_table(self, pdf) -> Optional[List[List]]:
        """
        Parcourt toutes les pages et retourne le premier tableau contenant
        au moins 3 colonnes reconnues comme visites.
        """
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if self._is_soa_table(table):
                    return table
        return None

    def _is_soa_table(self, table: List[List]) -> bool:
        """Vérifie qu'un tableau contient suffisamment de headers de visites."""
        for row in table[:10]:  # Chercher dans les 10 premières lignes
            visit_count = sum(
                1 for cell in row
                if cell and self._helper._is_visit_header(str(cell).strip())
            )
            if visit_count >= 3:
                return True
        return False

    # ------------------------------------------------------------------
    # Parsing du tableau
    # ------------------------------------------------------------------

    def _parse_table(self, table: List[List]) -> None:
        """Extrait les visites depuis un tableau brut pdfplumber."""
        header_row_idx, visit_cols = self._find_visit_header(table)
        if header_row_idx is None:
            raise ValueError("Impossible de trouver la ligne des visites dans le tableau PDF")

        for col_idx, visit_info in visit_cols.items():
            target_day, window_before, window_after = self._extract_day_window(
                table, header_row_idx, col_idx, visit_info
            )
            self.visits.append(VisitConfig(
                visit_name=visit_info["name"],
                target_day=target_day,
                window_before=window_before,
                window_after=window_after,
            ))

    def _find_visit_header(self, table: List[List]) -> Tuple[Optional[int], Dict]:
        """
        Trouve la ligne contenant les headers de visites.

        Returns:
            Tuple (index de ligne, dict {col_idx: {"name": ..., "raw": ...}})
        """
        for row_idx, row in enumerate(table):
            visit_cols = {}
            for col_idx, cell in enumerate(row):
                if not cell:
                    continue
                text = str(cell).strip()
                if self._helper._is_visit_header(text):
                    visit_cols[col_idx] = {
                        "name": self._helper._extract_visit_name(text),
                        "raw": text,
                    }
            if len(visit_cols) >= 3:
                return row_idx, visit_cols
        return None, {}

    def _extract_day_window(
        self,
        table: List[List],
        header_row_idx: int,
        col_idx: int,
        visit_info: Dict,
    ) -> Tuple[int, int, int]:
        """
        Extrait le jour cible et les fenêtres pour une colonne de visite.

        Cherche d'abord dans le texte du header (Format 2),
        puis dans les lignes suivantes (Format 1).
        """
        raw_text = visit_info["raw"]
        target_day = 0
        window_before = 0
        window_after = 0

        # 1. Extraire depuis le header (Format 2 : "V1 D0", "V2 D7±2")
        for pattern in self._helper.DAY_PATTERNS:
            m = re.search(pattern, raw_text, re.IGNORECASE)
            if m:
                target_day = int(m.group(1))
                break

        window = self._helper._parse_window(raw_text)
        if window:
            window_before, window_after = window

        # 2. Lignes suivantes (Format 1 : lignes Day / Window séparées)
        for row_idx in range(header_row_idx + 1, min(header_row_idx + 5, len(table))):
            row = table[row_idx]
            if col_idx >= len(row):
                continue

            cell_text = str(row[col_idx] or "").strip()
            if not cell_text:
                continue

            # Jour non encore trouvé
            if target_day == 0:
                for pattern in self._helper.DAY_PATTERNS:
                    m = re.search(pattern, cell_text, re.IGNORECASE)
                    if m:
                        target_day = int(m.group(1))
                        break
                # Peut-être un nombre brut (ex: "0", "7", "-28")
                if target_day == 0:
                    m = re.match(r"^(-?\d+)$", cell_text)
                    if m:
                        target_day = int(m.group(1))

            # Fenêtre non encore trouvée
            if window_before == 0 and window_after == 0:
                window = self._helper._parse_window(cell_text)
                if window:
                    window_before, window_after = window

            # Vérifier le label de la ligne (première colonne)
            label = str(row[0] or "").strip().lower() if row else ""
            if "window" in label or "fenêtre" in label:
                window = self._helper._parse_window(cell_text)
                if window:
                    window_before, window_after = window
            elif "day" in label or "jour" in label:
                if target_day == 0:
                    for pattern in self._helper.DAY_PATTERNS:
                        m = re.search(pattern, cell_text, re.IGNORECASE)
                        if m:
                            target_day = int(m.group(1))
                            break

        return target_day, window_before, window_after
