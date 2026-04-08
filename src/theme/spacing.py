# -*- coding: utf-8 -*-
"""
Système d'espacement centralisé pour l'application.

Basé sur une échelle de 4px (Material Design).

Utilisation:
    from src.theme import Spacing

    ft.Container(padding=Spacing.MD)
    ft.Column(spacing=Spacing.SM)
"""

import flet as ft


class Spacing:
    """Constantes d'espacement (échelle 4px)."""

    # ═══════════════════════════════════════════════════════════════
    # ÉCHELLE DE BASE
    # ═══════════════════════════════════════════════════════════════

    NONE = 0
    XXXS = 2      # 0.5x
    XXS = 4       # 1x
    XS = 8        # 2x
    SM = 12       # 3x
    MD = 16       # 4x
    LG = 20       # 5x
    XL = 24       # 6x
    XXL = 32      # 8x
    XXXL = 48     # 12x

    # ═══════════════════════════════════════════════════════════════
    # ALIAS SÉMANTIQUES
    # ═══════════════════════════════════════════════════════════════

    # Padding de conteneurs
    CARD_PADDING = MD           # 16px - Padding interne des cartes
    DIALOG_PADDING = XL         # 24px - Padding des dialogues
    PAGE_PADDING = LG           # 20px - Padding des pages

    # Espacement entre éléments
    ELEMENT_GAP = SM            # 12px - Entre éléments liés
    SECTION_GAP = XL            # 24px - Entre sections
    GROUP_GAP = MD              # 16px - Entre groupes d'éléments

    # Espacement de listes
    LIST_ITEM_GAP = XS          # 8px - Entre items de liste
    TABLE_ROW_GAP = XXS         # 4px - Entre lignes de tableau

    # Marges
    CONTENT_MARGIN = LG         # 20px - Marge du contenu principal
    INLINE_GAP = XS             # 8px - Entre éléments inline

    # ═══════════════════════════════════════════════════════════════
    # PADDING SYMÉTRIQUE (horizontal, vertical)
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def symmetric(horizontal: int = 0, vertical: int = 0) -> ft.Padding:
        """Crée un padding symétrique."""
        return ft.padding.symmetric(horizontal=horizontal, vertical=vertical)

    @staticmethod
    def all(value: int) -> ft.Padding:
        """Crée un padding uniforme."""
        return ft.padding.all(value)

    @staticmethod
    def only(
        left: int = 0,
        top: int = 0,
        right: int = 0,
        bottom: int = 0
    ) -> ft.Padding:
        """Crée un padding personnalisé."""
        return ft.padding.only(left=left, top=top, right=right, bottom=bottom)

    # ═══════════════════════════════════════════════════════════════
    # PRESETS DE PADDING
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def card() -> ft.Padding:
        """Padding standard pour une carte."""
        return ft.padding.all(Spacing.CARD_PADDING)

    @staticmethod
    def dialog() -> ft.Padding:
        """Padding standard pour un dialogue."""
        return ft.padding.all(Spacing.DIALOG_PADDING)

    @staticmethod
    def page() -> ft.Padding:
        """Padding standard pour une page."""
        return ft.padding.all(Spacing.PAGE_PADDING)

    @staticmethod
    def button() -> ft.Padding:
        """Padding standard pour un bouton."""
        return ft.padding.symmetric(horizontal=Spacing.MD, vertical=Spacing.XS)

    @staticmethod
    def chip() -> ft.Padding:
        """Padding standard pour un chip/badge."""
        return ft.padding.symmetric(horizontal=Spacing.XS, vertical=Spacing.XXS)

    @staticmethod
    def badge() -> ft.Padding:
        """Padding standard pour un badge de statut."""
        return ft.padding.symmetric(horizontal=Spacing.XS, vertical=Spacing.XXXS)


class Radius:
    """Constantes de border radius."""

    NONE = 0
    XS = 4        # Badges, chips
    SM = 6        # Petits éléments
    MD = 8        # Boutons
    LG = 10       # Cartes
    XL = 12       # Dialogues
    XXL = 16      # Grandes cartes
    FULL = 999    # Cercle complet

    # Alias sémantiques
    CARD = LG             # 10px
    BUTTON = MD           # 8px
    BADGE = XS            # 4px
    CHIP = SM             # 6px
    DIALOG = XL           # 12px
    INPUT = SM            # 6px
    TABLE = LG            # 10px


class Elevation:
    """Niveaux d'élévation (ombres)."""

    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 4

    # Alias sémantiques
    CARD = LOW
    DIALOG = HIGH
    DROPDOWN = MEDIUM
    TOOLTIP = MEDIUM
