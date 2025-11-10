@echo off
REM ========================================
REM Sauvegarde de la base de données
REM ========================================

title Sauvegarde - Bot Discord RSSDI

echo.
echo ================================================
echo    SAUVEGARDE DE LA BASE DE DONNEES
echo ================================================
echo.

REM Créer le dossier backups s'il n'existe pas
if not exist backups mkdir backups

REM Générer un nom avec la date et l'heure
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "BACKUP_NAME=bot_backup_%YYYY%-%MM%-%DD%_%HH%-%Min%-%Sec%"

echo Date: %YYYY%-%MM%-%DD% %HH%:%Min%:%Sec%
echo.

REM Vérifier si la base de données existe
if not exist data\bot.db (
    echo [ERREUR] La base de donnees n'existe pas!
    echo Emplacement attendu: data\bot.db
    echo.
    pause
    exit /b 1
)

REM Copier la base de données
echo [1/2] Sauvegarde de la base de donnees...
copy data\bot.db backups\%BACKUP_NAME%.db >nul
if errorlevel 1 (
    echo [ERREUR] Sauvegarde echouee!
    pause
    exit /b 1
)
echo Base de donnees sauvegardee!

REM Créer une archive ZIP (si 7-Zip est installé)
echo [2/2] Creation de l'archive...
where 7z >nul 2>&1
if not errorlevel 1 (
    7z a -tzip backups\%BACKUP_NAME%.zip data\bot.db logs\*.log .env >nul 2>&1
    echo Archive ZIP creee: %BACKUP_NAME%.zip
) else (
    echo 7-Zip non installe - archive ZIP non creee.
    echo Installez 7-Zip pour activer cette fonctionnalite.
)

REM Afficher les infos
echo.
echo ================================================
echo   SAUVEGARDE TERMINEE !
echo ================================================
echo.
echo Fichier: backups\%BACKUP_NAME%.db
for %%A in (backups\%BACKUP_NAME%.db) do echo Taille: %%~zA octets
echo.

REM Nettoyer les anciennes sauvegardes (garder les 10 dernières)
echo Nettoyage des anciennes sauvegardes...
for /f "skip=10 delims=" %%F in ('dir /b /o-d backups\bot_backup_*.db 2^>nul') do (
    del "backups\%%F" >nul 2>&1
    echo Supprime: %%F
)

echo.
pause
