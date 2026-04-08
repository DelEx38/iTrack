# -*- coding: utf-8 -*-
"""
Wrapper pour TextField avec label, helper et validation.
"""

import flet as ft
from src.theme import AppColors, Typography, Spacing, Radius


class FormField(ft.Column):
    """Wrapper pour TextField avec label, helper, error et required."""

    def __init__(
        self,
        label: str,
        helper: str | None = None,
        error: str | None = None,
        required: bool = False,
        **textfield_kwargs,
    ):
        """
        Crée un champ de formulaire.

        Args:
            label: Label au-dessus du champ (obligatoire)
            helper: Texte d'aide sous le champ
            error: Message d'erreur (rouge, remplace helper si présent)
            required: Ajoute un indicateur * rouge au label
            **textfield_kwargs: Arguments passés au TextField
        """
        self._required = required
        self._helper_text = helper
        self._error_text = error

        # Label avec indicateur required
        label_controls = [
            ft.Text(label, **Typography.LABEL, color=AppColors.TEXT_SECONDARY)
        ]
        if required:
            label_controls.append(
                ft.Text(" *", **Typography.LABEL, color=AppColors.ERROR)
            )

        self._label_row = ft.Row(
            label_controls,
            spacing=Spacing.NONE,
        )

        # TextField
        self._textfield = ft.TextField(
            border_radius=Radius.INPUT,
            border_color=AppColors.BORDER,
            focused_border_color=AppColors.PRIMARY,
            **textfield_kwargs,
        )

        # Helper/Error text
        self._helper_control = ft.Text(
            error if error else (helper if helper else ""),
            **Typography.CAPTION,
            color=AppColors.ERROR if error else AppColors.TEXT_DISABLED,
            visible=bool(error or helper),
        )

        super().__init__(
            controls=[
                self._label_row,
                self._textfield,
                self._helper_control,
            ],
            spacing=Spacing.XXS,
        )

    @property
    def value(self) -> str:
        """Retourne la valeur du TextField."""
        return self._textfield.value or ""

    @value.setter
    def value(self, val: str) -> None:
        """Définit la valeur du TextField."""
        self._textfield.value = val
        if self.page:
            self._textfield.update()

    @property
    def textfield(self) -> ft.TextField:
        """Retourne le TextField interne pour configuration avancée."""
        return self._textfield

    def set_error(self, message: str | None) -> None:
        """
        Affiche ou masque un message d'erreur.

        Args:
            message: Message d'erreur à afficher, ou None pour masquer
        """
        self._error_text = message
        if message:
            self._helper_control.value = message
            self._helper_control.color = AppColors.ERROR
            self._helper_control.visible = True
            self._textfield.border_color = AppColors.ERROR
        else:
            self._helper_control.value = self._helper_text or ""
            self._helper_control.color = AppColors.TEXT_DISABLED
            self._helper_control.visible = bool(self._helper_text)
            self._textfield.border_color = AppColors.BORDER

        if self.page:
            self.update()

    def validate(self) -> bool:
        """
        Valide le champ (vérifie required).

        Returns:
            True si valide, False sinon
        """
        if self._required and not self.value.strip():
            self.set_error("Ce champ est requis")
            return False
        self.set_error(None)
        return True

    def focus(self) -> None:
        """Met le focus sur le TextField."""
        self._textfield.focus()
        if self.page:
            self._textfield.update()
