@echo off
REM Active l'environnement virtuel Python
call .venv\Scripts\activate.bat

REM Lance le bot principal
start python bot.py

REM Lance l'interface web
start python web_interface.py

REM Lance la migration de la base de données
start python migrate.py

REM Lance le module économie
start python cogs\economy.py

REM Lance le module modération
start python cogs\moderation.py

REM Lance le module jeux
start python cogs\games.py

REM Lance le module commandes legacy
start python cogs\legacy_commands.py

REM Lance le module utilitaires avancés
start python cogs\advanced_utils.py

REM Lance le module fun extras
start python cogs\fun_extras.py

echo Tous les modules du bot sont lancés !
pause