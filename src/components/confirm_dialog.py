# -*- coding: utf-8 -*-
"""
Dialog de confirmation standardisé.
"""

from typing import Callable
import flet as ft
from src.theme import AppColors, Typography, Spacing, Radius


class ConfirmDialog(ft.AlertDialog):
    """Dialog de confirmation avec mode danger optionnel."""

    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        on_confirm: Callable[[], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
        danger: bool = False,
    ):
        """
        Crée un dialog de confirmation.

        Args:
            title: Titre du dialog
            message: Message de confirmation
            confirm_text: Texte du bouton confirmer (défaut: "Confirm")
            cancel_text: Texte du bouton annuler (défaut: "Cancel")
            on_confirm: Callback appelé si confirmé
            on_cancel: Callback appelé si annulé
            danger: Si True, bouton confirmer en rouge
        """
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel
        self._page: ft.Page | None = None

        # Couleur du bouton de confirmation
        confirm_color = AppColors.ERROR if danger else AppColors.PRIMARY

        super().__init__(
            modal=True,
            title=ft.Text(title, **Typography.H4),
            content=ft.Text(
                message,
                **Typography.BODY,
                color=AppColors.TEXT_SECONDARY,
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text(cancel_text),
                    on_click=self._handle_cancel,
                ),
                ft.Button(
                    content=ft.Text(confirm_text),
                    bgcolor=confirm_color,
                    color=AppColors.TEXT_ON_PRIMARY,
                    on_click=self._handle_confirm,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def _handle_confirm(self, e: ft.ControlEvent) -> None:
        """Gère le clic sur Confirm."""
        self.close()
        if self._on_confirm:
            self._on_confirm()

    def _handle_cancel(self, e: ft.ControlEvent) -> None:
        """Gère le clic sur Cancel."""
        self.close()
        if self._on_cancel:
            self._on_cancel()

    def show(self, page: ft.Page) -> None:
        """Affiche le dialog."""
        self._page = page
        page.overlay.append(self)
        self.open = True
        page.update()

    def close(self) -> None:
        """Ferme le dialog."""
        self.open = False
        if self._page:
            if self in self._page.overlay:
                self._page.overlay.remove(self)
            self._page.update()
