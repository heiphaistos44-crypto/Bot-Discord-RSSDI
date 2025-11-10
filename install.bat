@echo off
REM ========================================
REM Installation des dépendances
REM ========================================

title Installation - Bot Discord RSSDI

echo.
echo ================================================
echo    INSTALLATION DES DEPENDANCES
echo ================================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe!
    pause
    exit /b 1
)

echo Version de Python:
python --version
echo.

REM Mettre à jour pip
echo [1/3] Mise a jour de pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERREUR] Mise a jour de pip echouee!
    pause
    exit /b 1
)
echo.

REM Installer les dépendances
echo [2/3] Installation des dependances...
echo Cela peut prendre quelques minutes...
echo.
python -m pip install -r requirements_new.txt
if errorlevel 1 (
    echo.
    echo [ERREUR] Installation des dependances echouee!
    echo.
    echo Verifiez votre connexion internet et reessayez.
    pause
    exit /b 1
)
echo.

REM Vérifier l'installation
echo [3/3] Verification de l'installation...
python -c "import discord; import aiosqlite; import flask; print('Toutes les dependances sont installees!')"
if errorlevel 1 (
    echo.
    echo [AVERTISSEMENT] Certaines dependances n'ont pas pu etre verifiees.
    echo Le bot pourrait ne pas fonctionner correctement.
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo   INSTALLATION TERMINEE AVEC SUCCES !
echo ================================================
echo.
echo Vous pouvez maintenant lancer le bot avec start.bat
echo.
pause
