# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file pour Clinical Study Tracker avec Flet.

Usage:
    pyinstaller clinical_tracker.spec --noconfirm
"""

import sys
from pathlib import Path

block_cipher = None

# Chemin du projet
PROJECT_PATH = Path(SPECPATH)
SRC_PATH = PROJECT_PATH / 'src'

ASSETS_PATH = PROJECT_PATH / 'assets'

a = Analysis(
    [str(PROJECT_PATH / 'main.py')],
    pathex=[str(SRC_PATH)],
    binaries=[],
    datas=[
        (str(ASSETS_PATH), 'assets'),
    ],
    hiddenimports=[
        # Flet et ses dépendances
        'flet',
        'flet_core',
        'flet_runtime',
        'flet_runtime.app',
        'flet.fastapi',
        'flet.fastapi.flet_fastapi',
        'flet.fastapi.flet_app',
        'flet.fastapi.oauth_state',
        'flet.utils',
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.websockets_impl',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'httptools',
        'websockets',
        'watchfiles',
        'python_multipart',
        # Openpyxl
        'openpyxl',
        'openpyxl.cell',
        'openpyxl.styles',
        'openpyxl.utils',
        'openpyxl.workbook',
        'openpyxl.worksheet',
        # SQLite
        'sqlite3',
        # Modules de l'application
        'app',
        'database',
        'database.models',
        'database.queries',
        'components',
        'components.sidebar',
        'components.stat_card',
        'views',
        'views.landing',
        'views.dashboard',
        'views.patients',
        'views.sites',
        'views.visits',
        'views.adverse_events',
        'views.documents',
        'views.queries',
        'views.monitoring',
        'views.settings',
        'services',
        'services.soa_parser',
        'services.excel_importer',
        'excel_generator',
        'excel_generator.clinical',
        'excel_generator.generator',
        'excel_generator.styles',
        'excel_generator.templates',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ClinicalStudyTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Pas de console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ASSETS_PATH / 'icon.ico'),
)
