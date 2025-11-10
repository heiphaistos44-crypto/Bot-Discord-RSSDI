# 🤖 Bot Discord RSSDI

Bot Discord multifonction complet avec économie, modération, jeux, tickets, logs et bien plus encore !

## 🚀 Fonctionnalités

### 💰 Système d'Économie
- `/balance` - Affiche ton solde ou celui d'un autre utilisateur
- `/daily` - Récupère tes pièces quotidiennes
- `/work` - Travaille pour gagner des pièces
- `/crime` - Tente un crime (risqué mais lucratif)
- `/rob` - Vole les pièces d'un autre utilisateur
- `/give` - Donne des pièces à quelqu'un
- `/leaderboard` - Classement des plus riches
- `/shop` - Boutique du serveur
- `/gamble` - Joue à pile ou face

### 🛡️ Modération
- `/kick` - Expulse un membre
- `/ban` - Bannit un membre
- `/unban` - Débannit un utilisateur
- `/timeout` - Met un membre en timeout
- `/untimeout` - Retire le timeout
- `/warn` - Avertit un membre
- `/warnings` - Affiche les avertissements
- `/clearwarnings` - Efface les avertissements
- `/automod` - Active/désactive l'auto-modération

### 🎮 Jeux
- `/rps` - Pierre-papier-ciseaux
- `/guess` - Devine le nombre
- `/trivia` - Questions de culture générale
- `/8ball` - Boule magique 8
- `/reaction_duel` - Duel de réaction
- `/game_stats` - Statistiques de jeu
- `/higher_lower` - Devine si la carte est plus haute ou plus basse
- `/word_chain` - Jeu de chaîne de mots

### 🎫 Système de Tickets
- `/ticket_setup` - Configure le système de tickets
- `/ticket_create` - Crée un ticket de support
- `/ticket_close` - Ferme un ticket
- `/ticket_add` - Ajoute un membre à un ticket
- `/ticket_list` - Liste tous les tickets ouverts

### 👋 Bienvenue & Au Revoir
- `/welcome_setup` - Configure les messages de bienvenue
- `/goodbye_setup` - Configure les messages d'au revoir
- `/welcome_toggle` - Active/désactive la bienvenue
- `/goodbye_toggle` - Active/désactive l'au revoir
- `/welcome_test` - Teste le message de bienvenue

### 📝 Logs Avancés
- `/log_setup` - Configure le canal de logs
- `/log_disable` - Désactive les logs
- Logs automatiques :
  - Messages supprimés/édités
  - Membres bannis/expulsés
  - Modifications de rôles
  - Création/suppression de canaux
  - Et plus encore...

### ℹ️ Commandes d'Information
- `/userinfo` - Informations sur un utilisateur
- `/serverinfo` - Informations sur le serveur
- `/roleinfo` - Informations sur un rôle
- `/avatar` - Affiche l'avatar d'un utilisateur
- `/channelinfo` - Informations sur un canal

### 📊 Sondages
- `/poll` - Crée un sondage (2-5 options)
- `/poll_results` - Affiche les résultats
- `/poll_end` - Termine un sondage

### ⏰ Rappels
- `/remind` - Programme un rappel
- `/reminders_list` - Liste tes rappels actifs
- `/reminder_delete` - Supprime un rappel

### 🎭 Reaction-Roles
- `/reactionrole_add` - Ajoute un reaction-role
- `/reactionrole_remove` - Retire un reaction-role
- `/reactionrole_list` - Liste les reaction-roles
- `/reactionrole_panel` - Crée un panneau de reaction-roles

### 🎉 Giveaways
- `/giveaway_start` - Démarre un giveaway
- `/giveaway_end` - Termine un giveaway immédiatement
- `/giveaway_reroll` - Tire de nouveaux gagnants

### 📋 Notes sur les Utilisateurs
- `/note_add` - Ajoute une note sur un utilisateur
- `/note_list` - Liste les notes d'un utilisateur
- `/note_delete` - Supprime une note
- `/note_clear` - Efface toutes les notes d'un utilisateur
- `/note_search` - Recherche des notes par mot-clé

### 🎪 Commandes Fun
- `/truth_or_dare` - Vérité ou action
- `/would_you_rather` - Tu préfères...
- `/ship` - Calculateur de compatibilité
- `/compliment` - Génère un compliment
- `/roast` - Génère une vanne
- `/membercount` - Nombre de membres
- `/random_member` - Sélectionne un membre au hasard

### 🔧 Utilitaires Avancés
- `/ascii` - Générateur d'art ASCII
- `/base64` - Encodeur/décodeur Base64
- `/hash` - Hachage MD5/SHA256
- `/reverse` - Inverse un texte
- `/leet` - Convertit en l33t speak
- `/morse` - Convertit en code Morse
- `/password` - Générateur de mot de passe sécurisé
- `/uuid` - Générateur d'UUID
- `/color` - Générateur de couleur aléatoire
- `/convert_temp` - Conversion de température
- `/calculate_age` - Calculateur d'âge
- `/math` - Résolveur d'expressions mathématiques
- `/timestamp` - Générateur de timestamp Discord
- `/countdown` - Compte à rebours
- `/analyze_text` - Analyse de texte
- `/qrcode` - Générateur de QR code
- `/flip` - Simulateur de pile ou face
- `/random_choice` - Sélecteur aléatoire

### 🎯 Commandes Globales
- `/help` - Affiche l'aide du bot
- `/ping` - Affiche la latence
- `/botinfo` - Informations sur le bot

## 📦 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le repository**
   ```bash
   git clone <url-du-repo>
   cd Bot-Discord-RSSDI
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements_new.txt
   ```

3. **Configuration**
   - Copier `.env.example` vers `.env`
   - Éditer `.env` et remplir les valeurs requises :
     ```env
     DISCORD_TOKEN=votre_token_discord
     COMMAND_PREFIX=!
     ```

4. **Lancer le bot**
   ```bash
   python bot.py
   ```

## ⚙️ Configuration

### Variables d'environnement (.env)

#### Obligatoire
- `DISCORD_TOKEN` - Token du bot Discord

#### Optionnel
- `COMMAND_PREFIX` - Préfixe des commandes (défaut: `!`)
- `DATABASE_URL` - URL de la base de données (défaut: SQLite local)
- `INTERFACE_SECRET` - Clé secrète pour l'interface web
- `INTERFACE_PASSWORD` - Mot de passe admin de l'interface web
- `INTERFACE_HOST` - Host de l'interface web (défaut: `127.0.0.1`)
- `INTERFACE_PORT` - Port de l'interface web (défaut: `5000`)

#### Fonctionnalités
- `ENABLE_RSS` - Activer le module RSS (défaut: `true`)
- `ENABLE_ECONOMY` - Activer l'économie (défaut: `true`)
- `ENABLE_GAMES` - Activer les jeux (défaut: `true`)
- `ENABLE_AUTOMOD` - Activer l'auto-modération (défaut: `true`)

#### Limites
- `MAX_WARNINGS` - Nombre d'avertissements avant ban (défaut: `5`)
- `MAX_XP_PER_MESSAGE` - XP maximum par message (défaut: `5`)
- `COOLDOWN_SECONDS` - Cooldown général (défaut: `60`)

#### Économie
- `DAILY_COINS` - Pièces quotidiennes (défaut: `100`)
- `WORK_COINS_MIN` - Pièces minimales pour /work (défaut: `10`)
- `WORK_COINS_MAX` - Pièces maximales pour /work (défaut: `50`)

## 📊 Base de Données

Le bot utilise SQLite par défaut. La base de données est automatiquement créée au premier lancement.

### Tables principales
- `guilds` - Serveurs Discord
- `users` - Utilisateurs
- `members` - Relation utilisateurs-serveurs (XP, pièces, etc.)
- `tickets` - Système de tickets
- `polls` - Sondages
- `reminders` - Rappels
- `giveaways` - Concours
- `user_notes` - Notes sur les utilisateurs
- Et bien d'autres...

## 🔒 Sécurité

Le bot inclut plusieurs couches de sécurité :
- Validation des entrées utilisateur
- Filtrage de contenu
- Rate limiting
- Système de permissions
- Calculateur mathématique sécurisé (pas d'eval())
- Sessions sécurisées pour l'interface web

## 🌐 Interface Web

Une interface web est disponible pour gérer le bot :
- Dashboard avec statistiques
- Gestion de l'économie
- Consultation des logs de modération
- Configuration des serveurs
- Et plus encore...

Accès : `http://localhost:5000` (par défaut)

## 📝 Logs

Le bot génère plusieurs types de logs :
- `logs/bot.log` - Logs généraux (format texte)
- `logs/bot.json` - Logs structurés (format JSON)
- Logs en base de données pour l'activité des utilisateurs

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Améliorer la documentation
- Soumettre des pull requests

## 📜 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🆘 Support

Pour obtenir de l'aide :
1. Consultez la documentation ci-dessus
2. Utilisez `/help` dans Discord
3. Ouvrez une issue sur GitHub

## 🎯 Roadmap

Fonctionnalités prévues :
- [ ] Système de niveaux avec récompenses de rôles automatiques
- [ ] Module de musique (lecture YouTube/Spotify)
- [ ] Système de backup automatique
- [ ] API REST pour l'intégration externe
- [ ] Commandes de recherche (Wikipedia, Google)
- [ ] Système de suggestions amélioré
- [ ] Dashboard web amélioré avec graphiques

## 👨‍💻 Développement

### Structure du projet
```
Bot-Discord-RSSDI/
├── bot.py              # Point d'entrée principal
├── config.py           # Configuration centralisée
├── database.py         # Gestionnaire de base de données
├── cogs/               # Modules du bot
│   ├── economy.py
│   ├── moderation.py
│   ├── games.py
│   ├── tickets.py
│   ├── welcome.py
│   ├── logging.py
│   ├── info.py
│   ├── polls.py
│   ├── reminders.py
│   ├── reactionroles.py
│   ├── giveaways.py
│   ├── notes.py
│   └── ...
├── utils/              # Utilitaires
│   ├── logger.py
│   └── security.py
├── templates/          # Templates HTML (interface web)
└── data/              # Données (base de données, logs)
```

### Tests
```bash
pytest
```

### Formatage du code
```bash
black .
isort .
```

## ⚡ Performance

Le bot est optimisé pour :
- Gérer plusieurs serveurs simultanément
- Traiter des milliers de commandes par jour
- Base de données indexée pour des requêtes rapides
- Opérations asynchrones avec asyncio
- Rate limiting pour éviter les abus

## 🔧 Maintenance

### Backup de la base de données
```bash
cp data/bot.db data/bot.db.backup
```

### Mise à jour
```bash
git pull
pip install -r requirements_new.txt --upgrade
```

---

**Fait avec ❤️ pour la communauté Discord**
