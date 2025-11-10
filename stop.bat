@echo off
REM ========================================
REM Arrêt du bot Discord
REM ========================================

title Arrêt - Bot Discord RSSDI

echo.
echo ================================================
echo    ARRET DU BOT DISCORD
echo ================================================
echo.

echo Arret en cours...

REM Arrêter les processus Python liés au bot
tasklist /FI "WINDOWTITLE eq Bot Discord RSSDI*" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    taskkill /FI "WINDOWTITLE eq Bot Discord RSSDI*" /F >nul 2>&1
    echo Bot Discord arrete!
) else (
    echo Bot Discord non trouve.
)

REM Arrêter l'interface web
tasklist /FI "WINDOWTITLE eq Interface Web*" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    taskkill /FI "WINDOWTITLE eq Interface Web*" /F >nul 2>&1
    echo Interface Web arretee!
) else (
    echo Interface Web non trouvee.
)

echo.
echo ================================================
echo   ARRET TERMINE !
echo ================================================
echo.
echo Tous les processus du bot ont ete arretes.
echo.
pause
