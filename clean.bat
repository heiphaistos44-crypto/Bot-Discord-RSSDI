@echo off
REM ========================================
REM Nettoyage du projet
REM ========================================

title Nettoyage - Bot Discord RSSDI

echo.
echo ================================================
echo    NETTOYAGE DU PROJET
echo ================================================
echo.

echo Ce script va supprimer:
echo - Cache Python (__pycache__, *.pyc)
echo - Logs anciens (plus de 7 jours)
echo - Fichiers temporaires
echo.
set /p CONFIRM="Continuer? (O/N): "
if /i not "%CONFIRM%"=="O" (
    echo Nettoyage annule.
    pause
    exit /b 0
)

echo.
echo [1/4] Suppression du cache Python...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1
del /s /q *.pyo >nul 2>&1
echo Cache Python supprime!

echo [2/4] Suppression des logs anciens...
if exist logs (
    forfiles /p logs /s /m *.log /d -7 /c "cmd /c del @path" >nul 2>&1
    echo Logs anciens supprimes!
) else (
    echo Dossier logs inexistant.
)

echo [3/4] Suppression des fichiers temporaires...
del /q *.tmp >nul 2>&1
del /q *.temp >nul 2>&1
echo Fichiers temporaires supprimes!

echo [4/4] Optimisation de la base de donnees...
if exist data\bot.db (
    python -c "import sqlite3; conn = sqlite3.connect('data/bot.db'); conn.execute('VACUUM'); conn.close(); print('Base de donnees optimisee!')"
) else (
    echo Base de donnees inexistante.
)

echo.
echo ================================================
echo   NETTOYAGE TERMINE !
echo ================================================
echo.
pause
