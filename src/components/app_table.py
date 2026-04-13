# -*- coding: utf-8 -*-
"""
Tableau avec colonnes de largeur égale qui remplit la largeur de la page.
"""

import flet as ft
from typing import List, Union, Dict
from src.theme import AppColors, Typography, Spacing, Radius


class AppTable(ft.Container):
    """Tableau avec colonnes de largeur égale, expansion automatique."""

    def __init__(self, columns: List[str]):
        self._columns = columns
        self._rows_container = ft.Column([], spacing=0)

        header = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(col, **Typography.TABLE_HEADER),
                        expand=1,
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        alignment=ft.Alignment(0, 0),
                        border=ft.border.only(right=ft.BorderSide(1, AppColors.BORDER)),
                    )
                    for col in columns
                ],
                spacing=0,
            ),
            bgcolor=AppColors.SURFACE_VARIANT,
            border=ft.border.only(bottom=ft.BorderSide(1, AppColors.BORDER)),
        )

        super().__init__(
            content=ft.Column(
                [header, self._rows_container],
                spacing=0,
            ),
            border=ft.border.all(1, AppColors.BORDER),
            border_radius=Radius.TABLE,
            expand=True,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

    def set_rows(self, rows: List[Union[List[ft.Control], Dict]]) -> None:
        """Met à jour les lignes.

        rows: liste de :
          - list[ft.Control] : cellules seules
          - dict avec 'cells' (list[ft.Control]) et optionnel 'bgcolor' (str)
        """
        self._rows_container.controls.clear()
        for row_data in rows:
            if isinstance(row_data, dict):
                cells = row_data["cells"]
                bgcolor = row_data.get("bgcolor")
            else:
                cells = row_data
                bgcolor = None

            row = ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=cell,
                            expand=1,
                            padding=ft.padding.symmetric(horizontal=16, vertical=10),
                            alignment=ft.Alignment(-1, 0),
                            border=ft.border.only(right=ft.BorderSide(1, AppColors.BORDER)),
                        )
                        for cell in cells
                    ],
                    spacing=0,
                ),
                bgcolor=bgcolor,
                border=ft.border.only(bottom=ft.BorderSide(1, AppColors.BORDER)),
            )
            self._rows_container.controls.append(row)

        try:
            if self.page:
                self._rows_container.update()
        except RuntimeError:
            pass
