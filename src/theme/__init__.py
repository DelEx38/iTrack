# -*- coding: utf-8 -*-
"""
Module de thème pour Clinical Study Tracker.

Centralise toutes les constantes visuelles de l'application :
- Couleurs (AppColors)
- Typographie (Typography)
- Espacement (Spacing, Radius, Elevation)

Utilisation:
    from src.theme import AppColors, Typography, Spacing, Radius

    # Couleurs
    ft.Container(bgcolor=AppColors.SUCCESS)
    color = AppColors.get_patient_status_color("Included")

    # Typographie
    ft.Text("Titre", **Typography.H1)

    # Espacement
    ft.Container(padding=Spacing.MD, border_radius=Radius.CARD)
"""

from .colors import AppColors
from .typography import Typography, title, body, label, caption
from .spacing import Spacing, Radius, Elevation

__all__ = [
    # Couleurs
    "AppColors",

    # Typographie
    "Typography",
    "title",
    "body",
    "label",
    "caption",

    # Espacement
    "Spacing",
    "Radius",
    "Elevation",
]
