@echo off
REM Script de build PyInstaller pour Clinical Study Tracker
REM Usage: build.bat

echo ========================================
echo  Clinical Study Tracker - Build
echo ========================================
echo.

REM Activer le venv
call .venv\Scripts\activate.bat

REM Installer PyInstaller si nécessaire
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installation de PyInstaller...
    pip install pyinstaller
)

REM Nettoyer les anciens builds
echo Nettoyage...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Build
echo.
echo Build en cours (peut prendre quelques minutes)...
pyinstaller clinical_tracker.spec --noconfirm

echo.
if exist "dist\ClinicalStudyTracker.exe" (
    echo ========================================
    echo  BUILD REUSSI !
    echo ========================================
    echo.
    echo Executable: dist\ClinicalStudyTracker.exe
    echo.
    echo DISTRIBUTION:
    echo   1. Copiez ClinicalStudyTracker.exe ou vous voulez
    echo   2. Au premier lancement, le dossier data\ sera cree
    echo   3. La base etude.db contient toutes vos donnees
    echo.
    echo BACKUP: Pour sauvegarder, copiez le dossier data\
    echo.
) else (
    echo ========================================
    echo  ERREUR DE BUILD
    echo ========================================
    echo Verifiez les erreurs ci-dessus.
)

pause
