# -*- coding: utf-8 -*-
"""
En-tête de section avec divider optionnel.
"""

import flet as ft
from src.theme import AppColors, Typography, Spacing


class SectionHeader(ft.Column):
    """Titre de section avec icône optionnelle et divider."""

    def __init__(
        self,
        title: str,
        icon: str | None = None,
        action_button: ft.Control | None = None,
        show_divider: bool = True,
    ):
        """
        Crée un en-tête de section.

        Args:
            title: Texte du titre (obligatoire)
            icon: Icône à gauche du titre
            action_button: Bouton/lien à droite (ex: "Voir tout")
            show_divider: Afficher le divider horizontal (défaut: True)
        """
        # Construction du header
        header_left = []
        if icon:
            header_left.append(
                ft.Icon(icon, color=AppColors.TEXT_SECONDARY, size=20)
            )
        header_left.append(
            ft.Text(title, **Typography.H5, color=AppColors.TEXT_PRIMARY)
        )

        # Row avec titre à gauche et action à droite
        header_row = ft.Row(
            [
                ft.Row(header_left, spacing=Spacing.XS),
                action_button if action_button else ft.Container(),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Éléments de la colonne
        elements = [header_row]

        if show_divider:
            elements.append(
                ft.Divider(height=1, color=AppColors.BORDER)
            )

        super().__init__(
            controls=elements,
            spacing=Spacing.XS,
        )
