"""
Excel Generator - Génération de fichiers Excel via openpyxl.
"""

# Fonctions de base
from .generator import (
    create_workbook,
    save_workbook,
    add_sheet,
    write_row,
    write_data,
    style_header,
    auto_column_width,
)

# Mise en forme avancée
from .styles import (
    # Bordures
    create_border,
    apply_border,
    apply_border_range,
    # Fusion
    merge_cells,
    merge_range,
    # Formats de nombres
    NUMBER_FORMATS,
    apply_number_format,
    format_column,
    # Alignement
    apply_alignment,
    # Mise en forme conditionnelle
    add_color_scale,
    add_data_bars,
    add_icon_set,
    add_highlight_rule,
    # Styles prédéfinis
    apply_style_preset,
)

# Templates
from .templates import (
    # Classes de base
    ExcelTemplate,
    TableTemplate,
    # Templates prédéfinis
    InvoiceTemplate,
    BudgetTemplate,
    PlanningTemplate,
    # Utilitaires
    TEMPLATES,
    get_template,
    list_templates,
    create_from_dict,
    create_from_json,
)

__all__ = [
    # Base
    "create_workbook",
    "save_workbook",
    "add_sheet",
    "write_row",
    "write_data",
    "style_header",
    "auto_column_width",
    # Styles
    "create_border",
    "apply_border",
    "apply_border_range",
    "merge_cells",
    "merge_range",
    "NUMBER_FORMATS",
    "apply_number_format",
    "format_column",
    "apply_alignment",
    "add_color_scale",
    "add_data_bars",
    "add_icon_set",
    "add_highlight_rule",
    "apply_style_preset",
    # Templates
    "ExcelTemplate",
    "TableTemplate",
    "InvoiceTemplate",
    "BudgetTemplate",
    "PlanningTemplate",
    "TEMPLATES",
    "get_template",
    "list_templates",
    "create_from_dict",
    "create_from_json",
    # Clinical
    "create_visit_tracking",
]

# Clinical / Recherche clinique
from .clinical import (
    create_visit_tracking,
)
