@echo off
REM ========================================
REM Mise à jour du bot
REM ========================================

title Mise à jour - Bot Discord RSSDI

echo.
echo ================================================
echo    MISE A JOUR DU BOT
echo ================================================
echo.

REM Vérifier si Git est installé
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Git n'est pas installe!
    echo Telechargez Git sur https://git-scm.com/
    pause
    exit /b 1
)

REM Arrêter le bot
echo [1/5] Arret du bot...
call stop.bat >nul 2>&1

REM Sauvegarder la base de données
echo [2/5] Sauvegarde de la base de donnees...
if exist data\bot.db (
    call backup.bat >nul 2>&1
    echo Sauvegarde effectuee!
) else (
    echo Pas de base de donnees a sauvegarder.
)

REM Récupérer les mises à jour
echo [3/5] Recuperation des mises a jour...
git pull
if errorlevel 1 (
    echo.
    echo [ERREUR] Mise a jour echouee!
    echo Verifiez votre connexion internet et reessayez.
    pause
    exit /b 1
)

REM Mettre à jour les dépendances
echo [4/5] Mise a jour des dependances...
python -m pip install --upgrade -r requirements_new.txt
if errorlevel 1 (
    echo.
    echo [AVERTISSEMENT] Certaines dependances n'ont pas pu etre mises a jour.
    pause
)

REM Nettoyer le cache
echo [5/5] Nettoyage du cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1

echo.
echo ================================================
echo   MISE A JOUR TERMINEE !
echo ================================================
echo.
echo Vous pouvez relancer le bot avec start.bat
echo.
pause
