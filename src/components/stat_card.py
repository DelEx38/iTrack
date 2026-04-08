# -*- coding: utf-8 -*-
"""
Carte de statistique réutilisable.
"""

import flet as ft
from src.theme import AppColors, Typography, Spacing, Radius


class StatCard(ft.Container):
    """Carte affichant une statistique avec titre et valeur."""

    def __init__(
        self,
        title: str,
        value: str = "0",
        color: str = AppColors.PRIMARY,
        icon: str = None,
    ):
        self.value_text = ft.Text(
            value,
            **Typography.STAT_VALUE,
            color=color,
        )
        self.title_text = ft.Text(
            title,
            **Typography.STAT_LABEL,
            color=AppColors.TEXT_SECONDARY,
        )

        row_controls = [self.value_text]
        if icon:
            row_controls.append(ft.Icon(icon, color=color, size=24))

        content = ft.Column(
            [
                ft.Row(
                    row_controls,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                self.title_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.XS,
        )

        super().__init__(
            content=content,
            padding=Spacing.CARD_PADDING,
            border_radius=Radius.CARD,
            bgcolor=AppColors.SURFACE_VARIANT,
            expand=True,
        )

    def update_value(self, value: str) -> None:
        """Met à jour la valeur affichée."""
        self.value_text.value = value
        if self.page:
            self.update()
