# -*- coding: utf-8 -*-
"""
Carte générique réutilisable avec variantes.
"""

from enum import Enum
import flet as ft
from src.theme import AppColors, Typography, Spacing, Radius, Elevation


class CardVariant(Enum):
    """Variantes de style pour GenericCard."""

    DEFAULT = "default"      # SURFACE_VARIANT, pas de bordure
    ELEVATED = "elevated"    # SURFACE_ELEVATED, ombre
    OUTLINED = "outlined"    # SURFACE, bordure


class GenericCard(ft.Container):
    """Carte générique réutilisable avec titre optionnel et actions."""

    def __init__(
        self,
        content: ft.Control,
        title: str | None = None,
        icon: str | None = None,
        actions: list[ft.Control] | None = None,
        variant: CardVariant = CardVariant.DEFAULT,
        padding: int = Spacing.CARD_PADDING,
        expand: bool = False,
        accent_color: str | None = None,
    ):
        """
        Crée une carte générique.

        Args:
            content:       Contenu principal de la carte (obligatoire)
            title:         Titre optionnel affiché en haut
            icon:          Icône à côté du titre
            actions:       Liste de boutons en bas de la carte
            variant:       Style de la carte (DEFAULT, ELEVATED, OUTLINED)
            padding:       Padding interne (défaut: Spacing.CARD_PADDING)
            expand:        Si la carte doit s'étendre pour remplir l'espace
            accent_color:  Couleur de la barre d'accent gauche (None = pas de barre)
        """
        bgcolor, border, shadow = self._get_variant_styles(variant)
        card_content = self._build_content(content, title, icon, actions)

        if accent_color:
            # Barre colorée de 3px à gauche
            inner = ft.Container(
                content=card_content,
                padding=padding,
                expand=expand,
            )
            wrapped = ft.Row(
                [
                    ft.Container(
                        width=3,
                        bgcolor=accent_color,
                        border_radius=ft.BorderRadius(
                            top_left=Radius.CARD, top_right=0,
                            bottom_left=Radius.CARD, bottom_right=0,
                        ),
                    ),
                    inner,
                ],
                spacing=0,
                expand=expand,
            )
            super().__init__(
                content=wrapped,
                border_radius=Radius.CARD,
                bgcolor=bgcolor,
                border=border,
                shadow=shadow,
                expand=expand,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            )
        else:
            super().__init__(
                content=card_content,
                padding=padding,
                border_radius=Radius.CARD,
                bgcolor=bgcolor,
                border=border,
                shadow=shadow,
                expand=expand,
            )

    def _get_variant_styles(
        self, variant: CardVariant
    ) -> tuple[str, ft.Border | None, ft.BoxShadow | None]:
        """Retourne les styles selon la variante."""
        if variant == CardVariant.ELEVATED:
            return (
                AppColors.SURFACE_ELEVATED,
                None,
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=8,
                    color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
            )
        elif variant == CardVariant.OUTLINED:
            return (
                AppColors.SURFACE,
                ft.border.all(1, AppColors.BORDER),
                None,
            )
        else:  # DEFAULT
            return (
                AppColors.SURFACE_VARIANT,
                None,
                None,
            )

    def _build_content(
        self,
        content: ft.Control,
        title: str | None,
        icon: str | None,
        actions: list[ft.Control] | None,
    ) -> ft.Control:
        """Construit le contenu complet de la carte."""
        elements = []

        # Header avec titre et icône
        if title:
            header_controls = []
            if icon:
                header_controls.append(
                    ft.Icon(icon, color=AppColors.TEXT_SECONDARY, size=20)
                )
            header_controls.append(
                ft.Text(title, **Typography.H5, color=AppColors.TEXT_PRIMARY)
            )
            elements.append(
                ft.Row(
                    header_controls,
                    spacing=Spacing.XS,
                )
            )
            elements.append(ft.Container(height=Spacing.SM))  # Espace après le titre

        # Contenu principal
        elements.append(content)

        # Actions en bas
        if actions:
            elements.append(ft.Container(height=Spacing.SM))  # Espace avant les actions
            elements.append(
                ft.Row(
                    actions,
                    alignment=ft.MainAxisAlignment.END,
                    spacing=Spacing.XS,
                )
            )

        # Si un seul élément, le retourner directement
        if len(elements) == 1:
            return elements[0]

        return ft.Column(
            elements,
            spacing=Spacing.NONE,
        )
