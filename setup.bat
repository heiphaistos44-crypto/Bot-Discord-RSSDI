@echo off
REM ========================================
REM Configuration initiale du bot
REM ========================================

title Configuration - Bot Discord RSSDI

echo.
echo ================================================
echo    CONFIGURATION INITIALE DU BOT
echo ================================================
echo.

REM Vérifier si .env existe déjà
if exist .env (
    echo Le fichier .env existe deja.
    echo.
    set /p OVERWRITE="Voulez-vous le recreer? (O/N): "
    if /i not "%OVERWRITE%"=="O" (
        echo Configuration annulee.
        pause
        exit /b 0
    )
)

REM Créer .env à partir de l'exemple
echo [1/4] Copie de .env.example vers .env...
copy .env.example .env >nul
echo OK
echo.

REM Demander le token Discord
echo [2/4] Configuration du token Discord
echo.
echo Pour obtenir votre token:
echo 1. Allez sur https://discord.com/developers/applications
echo 2. Creez une nouvelle application
echo 3. Allez dans "Bot" et cliquez "Add Bot"
echo 4. Copiez le token
echo.
set /p TOKEN="Entrez votre token Discord: "

REM Remplacer le token dans .env
powershell -Command "(gc .env) -replace 'your_bot_token_here', '%TOKEN%' | Out-File -encoding ASCII .env"
echo Token configure!
echo.

REM Demander le préfixe
echo [3/4] Configuration du prefixe
set /p PREFIX="Prefixe des commandes (par defaut '!'): "
if "%PREFIX%"=="" set PREFIX=!
powershell -Command "(gc .env) -replace 'COMMAND_PREFIX=!', 'COMMAND_PREFIX=%PREFIX%' | Out-File -encoding ASCII .env"
echo Prefixe configure: %PREFIX%
echo.

REM Créer les dossiers
echo [4/4] Creation des dossiers...
if not exist data mkdir data
if not exist logs mkdir logs
if not exist backups mkdir backups
echo Dossiers crees!
echo.

echo ================================================
echo   CONFIGURATION TERMINEE !
echo ================================================
echo.
echo Fichier .env cree avec succes.
echo.
echo Prochaines etapes:
echo 1. Executez 'install.bat' pour installer les dependances
echo 2. Executez 'start.bat' pour lancer le bot
echo.
echo Voulez-vous ouvrir le fichier .env pour verification? (O/N)
set /p OPEN_ENV=""
if /i "%OPEN_ENV%"=="O" notepad .env
echo.
pause
