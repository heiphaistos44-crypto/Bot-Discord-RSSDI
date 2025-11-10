@echo off
REM ========================================
REM Bot Discord RSSDI - Lanceur Principal
REM ========================================

title Bot Discord RSSDI - Lanceur

echo.
echo ================================================
echo    BOT DISCORD RSSDI - LANCEUR AUTOMATIQUE
echo ================================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH!
    echo Telechargez Python sur https://www.python.org/
    pause
    exit /b 1
)

REM Vérifier si .env existe
if not exist .env (
    echo [AVERTISSEMENT] Fichier .env non trouve!
    echo.
    echo Copie de .env.example vers .env...
    copy .env.example .env
    echo.
    echo [ACTION REQUISE] Editez le fichier .env et ajoutez votre token Discord!
    echo.
    echo Appuyez sur une touche une fois que c'est fait...
    pause
    notepad .env
)

REM Vérifier si les dépendances sont installées
echo [1/4] Verification des dependances...
python -c "import discord" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Les dependances ne sont pas installees!
    echo Installation automatique...
    echo.
    call install.bat
    if errorlevel 1 (
        echo.
        echo [ERREUR] Installation des dependances echouee!
        pause
        exit /b 1
    )
)

REM Créer les dossiers nécessaires
echo [2/4] Creation des dossiers...
if not exist data mkdir data
if not exist logs mkdir logs
if not exist backups mkdir backups

REM Lancer le bot et l'interface web en parallèle
echo [3/4] Demarrage du bot Discord...
echo.
echo ================================================
echo   Bot Discord en cours de demarrage...
echo   Interface Web: http://localhost:5000
echo   Logs: logs/bot.log
echo ================================================
echo.
echo Pour arreter: Fermez cette fenetre ou Ctrl+C
echo.

REM Lancer le bot en arrière-plan et l'interface web
start "Bot Discord RSSDI" /MIN python bot.py

REM Attendre 3 secondes
timeout /t 3 /nobreak >nul

REM Lancer l'interface web
echo [4/4] Demarrage de l'interface web...
start "Interface Web - Bot Discord" /MIN python web_interface.py

echo.
echo ================================================
echo   TOUT EST LANCE !
echo ================================================
echo.
echo   - Bot Discord: En cours d'execution
echo   - Interface Web: http://localhost:5000
echo.
echo Appuyez sur une touche pour ouvrir l'interface web...
pause >nul

REM Ouvrir le navigateur
start http://localhost:5000

echo.
echo Pour arreter le bot, fermez les fenetres "Bot Discord RSSDI"
echo et "Interface Web - Bot Discord"
echo.
pause
