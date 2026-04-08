# -*- coding: utf-8 -*-
"""
Composant d'état vide pour afficher quand aucune donnée n'est disponible.
"""

import flet as ft
from src.theme import AppColors, Typography, Spacing


class EmptyState(ft.Container):
    """Affichage quand aucune donnée n'est disponible."""

    def __init__(
        self,
        title: str,
        description: str | None = None,
        icon: str = ft.Icons.INBOX,
        action_button: ft.Control | None = None,
    ):
        """
        Crée un état vide.

        Args:
            title: Titre principal (ex: "Aucun patient")
            description: Description secondaire optionnelle
            icon: Icône affichée au-dessus (défaut: INBOX)
            action_button: Bouton d'action optionnel (ex: "Ajouter")
        """
        elements = []

        # Icône grande
        elements.append(
            ft.Icon(
                icon,
                size=48,
                color=AppColors.TEXT_DISABLED,
            )
        )

        # Titre
        elements.append(
            ft.Text(
                title,
                **Typography.H5,
                color=AppColors.TEXT_SECONDARY,
                text_align=ft.TextAlign.CENTER,
            )
        )

        # Description optionnelle
        if description:
            elements.append(
                ft.Text(
                    description,
                    **Typography.BODY_SMALL,
                    color=AppColors.TEXT_DISABLED,
                    text_align=ft.TextAlign.CENTER,
                )
            )

        # Bouton d'action optionnel
        if action_button:
            elements.append(ft.Container(height=Spacing.SM))
            elements.append(action_button)

        content = ft.Column(
            elements,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.XS,
        )

        super().__init__(
            content=content,
            alignment=ft.alignment.center,
            padding=Spacing.XXL,
            expand=True,
        )
