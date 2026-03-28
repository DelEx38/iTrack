"""
Carte de statistique réutilisable.
"""

import flet as ft


class StatCard(ft.Container):
    """Carte affichant une statistique avec titre et valeur."""

    def __init__(
        self,
        title: str,
        value: str = "0",
        color: str = "#3a7ebf",
        icon: str = None,
    ):
        self.value_text = ft.Text(
            value,
            size=36,
            weight=ft.FontWeight.BOLD,
            color=color,
        )
        self.title_text = ft.Text(
            title,
            size=14,
            color=ft.Colors.GREY_500,
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
            spacing=5,
        )

        super().__init__(
            content=content,
            padding=20,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            expand=True,
        )

    def update_value(self, value: str) -> None:
        """Met à jour la valeur affichée."""
        self.value_text.value = value
        if self.page:
            self.update()
