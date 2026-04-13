# -*- coding: utf-8 -*-
"""
Carte de statistique réutilisable.
"""

import flet as ft
from src.theme import AppColors, Spacing, Radius


class StatCard(ft.Container):
    """
    Carte affichant une statistique avec titre, valeur et icône.

    Design :
    - Barre colorée de 3px en haut
    - Valeur grande + label à gauche
    - Icône dans un cercle teinté à droite
    - Bordure subtile
    """

    def __init__(
        self,
        title: str,
        value: str = "0",
        color: str = AppColors.PRIMARY,
        icon: str = None,
    ):
        self.value_text = ft.Text(
            value,
            size=28,
            weight=ft.FontWeight.BOLD,
            color=color,
        )
        self.title_text = ft.Text(
            title,
            size=12,
            weight=ft.FontWeight.W_500,
            color=AppColors.TEXT_SECONDARY,
        )

        icon_widget = ft.Container(
            content=ft.Icon(icon, color=color, size=22),
            width=42,
            height=42,
            border_radius=21,
            bgcolor=ft.Colors.with_opacity(0.12, color),
            alignment=ft.Alignment.CENTER,
        ) if icon else ft.Container(width=0)

        body = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [self.value_text, self.title_text],
                        spacing=Spacing.XXXS,
                        expand=True,
                    ),
                    icon_widget,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(left=Spacing.MD, right=Spacing.MD, top=Spacing.SM, bottom=Spacing.MD),
        )

        super().__init__(
            content=ft.Column(
                [
                    # Barre colorée en haut
                    ft.Container(height=3, bgcolor=color),
                    body,
                ],
                spacing=0,
            ),
            border_radius=Radius.CARD,
            bgcolor=AppColors.SURFACE_VARIANT,
            border=ft.border.all(1, AppColors.BORDER),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            expand=True,
        )

    def update_value(self, value: str) -> None:
        """Met à jour la valeur affichée."""
        self.value_text.value = value
        if self.page:
            self.update()
