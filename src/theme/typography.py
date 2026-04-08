# -*- coding: utf-8 -*-
"""
Typographie centralisée pour l'application.

Utilisation:
    from src.theme import Typography

    ft.Text("Titre", **Typography.H1)
    ft.Text("Sous-titre", **Typography.H2)
"""

import flet as ft


class Typography:
    """Styles typographiques de l'application."""

    # ═══════════════════════════════════════════════════════════════
    # TITRES
    # ═══════════════════════════════════════════════════════════════

    H1 = {
        "size": 32,
        "weight": ft.FontWeight.BOLD,
    }

    H2 = {
        "size": 24,
        "weight": ft.FontWeight.BOLD,
    }

    H3 = {
        "size": 20,
        "weight": ft.FontWeight.W_600,
    }

    H4 = {
        "size": 18,
        "weight": ft.FontWeight.W_600,
    }

    H5 = {
        "size": 16,
        "weight": ft.FontWeight.W_500,
    }

    H6 = {
        "size": 14,
        "weight": ft.FontWeight.W_500,
    }

    # ═══════════════════════════════════════════════════════════════
    # CORPS DE TEXTE
    # ═══════════════════════════════════════════════════════════════

    BODY_LARGE = {
        "size": 16,
        "weight": ft.FontWeight.NORMAL,
    }

    BODY = {
        "size": 14,
        "weight": ft.FontWeight.NORMAL,
    }

    BODY_SMALL = {
        "size": 12,
        "weight": ft.FontWeight.NORMAL,
    }

    # ═══════════════════════════════════════════════════════════════
    # LABELS ET CAPTIONS
    # ═══════════════════════════════════════════════════════════════

    LABEL = {
        "size": 12,
        "weight": ft.FontWeight.W_500,
    }

    LABEL_LARGE = {
        "size": 14,
        "weight": ft.FontWeight.W_500,
    }

    CAPTION = {
        "size": 11,
        "weight": ft.FontWeight.NORMAL,
    }

    OVERLINE = {
        "size": 10,
        "weight": ft.FontWeight.W_500,
    }

    # ═══════════════════════════════════════════════════════════════
    # BOUTONS
    # ═══════════════════════════════════════════════════════════════

    BUTTON = {
        "size": 14,
        "weight": ft.FontWeight.W_500,
    }

    BUTTON_SMALL = {
        "size": 12,
        "weight": ft.FontWeight.W_500,
    }

    # ═══════════════════════════════════════════════════════════════
    # TABLEAU
    # ═══════════════════════════════════════════════════════════════

    TABLE_HEADER = {
        "size": 13,
        "weight": ft.FontWeight.BOLD,
    }

    TABLE_CELL = {
        "size": 13,
        "weight": ft.FontWeight.NORMAL,
    }

    # ═══════════════════════════════════════════════════════════════
    # STATISTIQUES
    # ═══════════════════════════════════════════════════════════════

    STAT_VALUE = {
        "size": 28,
        "weight": ft.FontWeight.BOLD,
    }

    STAT_LABEL = {
        "size": 12,
        "weight": ft.FontWeight.W_500,
    }

    # ═══════════════════════════════════════════════════════════════
    # BADGES
    # ═══════════════════════════════════════════════════════════════

    BADGE = {
        "size": 11,
        "weight": ft.FontWeight.W_600,
    }

    CHIP = {
        "size": 12,
        "weight": ft.FontWeight.W_500,
    }


# Fonctions utilitaires pour créer des textes stylés
def title(text: str, level: int = 1, **kwargs) -> ft.Text:
    """Crée un titre avec le style approprié.

    Args:
        text: Le texte à afficher
        level: Niveau du titre (1-6)
        **kwargs: Arguments supplémentaires pour ft.Text
    """
    styles = {
        1: Typography.H1,
        2: Typography.H2,
        3: Typography.H3,
        4: Typography.H4,
        5: Typography.H5,
        6: Typography.H6,
    }
    style = styles.get(level, Typography.H1)
    return ft.Text(text, **{**style, **kwargs})


def body(text: str, size: str = "normal", **kwargs) -> ft.Text:
    """Crée un texte corps avec le style approprié.

    Args:
        text: Le texte à afficher
        size: "large", "normal", ou "small"
        **kwargs: Arguments supplémentaires pour ft.Text
    """
    styles = {
        "large": Typography.BODY_LARGE,
        "normal": Typography.BODY,
        "small": Typography.BODY_SMALL,
    }
    style = styles.get(size, Typography.BODY)
    return ft.Text(text, **{**style, **kwargs})


def label(text: str, large: bool = False, **kwargs) -> ft.Text:
    """Crée un label avec le style approprié."""
    style = Typography.LABEL_LARGE if large else Typography.LABEL
    return ft.Text(text, **{**style, **kwargs})


def caption(text: str, **kwargs) -> ft.Text:
    """Crée une caption avec le style approprié."""
    return ft.Text(text, **{**Typography.CAPTION, **kwargs})
