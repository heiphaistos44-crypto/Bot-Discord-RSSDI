# 🚀 Scripts de Gestion du Bot

Ce dossier contient plusieurs scripts `.bat` pour faciliter la gestion du bot Discord sous Windows.

## 📋 Scripts Disponibles

### 🎯 `start.bat` - Lanceur Principal
**Lance le bot et l'interface web automatiquement**

- Vérifie Python et les dépendances
- Crée les dossiers nécessaires (data, logs, backups)
- Lance le bot Discord en arrière-plan
- Lance l'interface web sur http://localhost:5000
- Ouvre automatiquement le navigateur

**Usage:**
```batch
start.bat
```

**Première utilisation:**
1. Le script détectera l'absence de `.env`
2. Il copiera `.env.example` vers `.env`
3. Vous devrez éditer `.env` pour ajouter votre token Discord
4. Relancez ensuite `start.bat`

---

### 🔧 `setup.bat` - Configuration Initiale
**Configure le bot pour la première fois**

- Crée le fichier `.env` à partir de `.env.example`
- Demande votre token Discord
- Configure le préfixe des commandes
- Crée les dossiers nécessaires

**Usage:**
```batch
setup.bat
```

**Étapes:**
1. Le script copiera `.env.example` vers `.env`
2. Vous serez invité à entrer votre token Discord
3. Vous pourrez choisir le préfixe (par défaut: `!`)
4. Les dossiers seront créés automatiquement

---

### 📦 `install.bat` - Installation des Dépendances
**Installe toutes les dépendances Python nécessaires**

- Met à jour pip
- Installe toutes les dépendances depuis `requirements_new.txt`
- Vérifie l'installation

**Usage:**
```batch
install.bat
```

**Dépendances installées:**
- discord.py (API Discord)
- aiosqlite (Base de données)
- flask (Interface web)
- pillow (Traitement d'images)
- Et bien d'autres...

---

### 🛑 `stop.bat` - Arrêt du Bot
**Arrête proprement le bot et l'interface web**

- Ferme le processus du bot Discord
- Ferme le processus de l'interface web
- Libère toutes les ressources

**Usage:**
```batch
stop.bat
```

---

### 🧹 `clean.bat` - Nettoyage
**Nettoie les fichiers temporaires et cache**

- Supprime le cache Python (`__pycache__`, `*.pyc`)
- Supprime les logs de plus de 7 jours
- Supprime les fichiers temporaires
- Optimise la base de données (VACUUM)

**Usage:**
```batch
clean.bat
```

---

### 💾 `backup.bat` - Sauvegarde
**Sauvegarde la base de données**

- Crée une copie de `data/bot.db`
- Nomme la sauvegarde avec date et heure
- Crée une archive ZIP (si 7-Zip est installé)
- Garde les 10 dernières sauvegardes

**Usage:**
```batch
backup.bat
```

**Emplacement des sauvegardes:**
```
backups/
├── bot_backup_2025-01-10_14-30-00.db
├── bot_backup_2025-01-10_14-30-00.zip
└── ...
```

---

### 🔄 `update.bat` - Mise à Jour
**Met à jour le bot depuis Git**

- Arrête le bot automatiquement
- Sauvegarde la base de données
- Récupère les dernières mises à jour (git pull)
- Met à jour les dépendances
- Nettoie le cache

**Usage:**
```batch
update.bat
```

**Prérequis:** Git doit être installé et le projet doit être un dépôt Git.

---

## 🎬 Guide de Démarrage Rapide

### Première Installation

1. **Configuration initiale:**
   ```batch
   setup.bat
   ```
   - Suivez les instructions à l'écran
   - Entrez votre token Discord

2. **Installation des dépendances:**
   ```batch
   install.bat
   ```
   - Attendez la fin de l'installation (quelques minutes)

3. **Lancement du bot:**
   ```batch
   start.bat
   ```
   - Le bot démarre automatiquement
   - L'interface web s'ouvre sur http://localhost:5000

### Usage Quotidien

**Démarrer le bot:**
```batch
start.bat
```

**Arrêter le bot:**
```batch
stop.bat
```

**Faire une sauvegarde:**
```batch
backup.bat
```

**Nettoyer le projet:**
```batch
clean.bat
```

---

## 🔧 Configuration Avancée

### Variables d'Environnement (.env)

Le fichier `.env` contient toutes les configurations:

```env
# Token Discord (OBLIGATOIRE)
DISCORD_TOKEN=votre_token_ici

# Préfixe des commandes
COMMAND_PREFIX=!

# Base de données
DATABASE_URL=sqlite:///data/bot.db

# Interface web
INTERFACE_HOST=127.0.0.1
INTERFACE_PORT=5000
INTERFACE_PASSWORD=admin123

# Modules
ENABLE_ECONOMY=true
ENABLE_GAMES=true
ENABLE_AUTOMOD=true

# Économie
DAILY_COINS=100
WORK_COINS_MIN=10
WORK_COINS_MAX=50
```

Éditez ce fichier pour personnaliser votre bot.

---

## 📊 Structure du Projet

```
Bot-Discord-RSSDI/
├── start.bat          ⭐ Script principal
├── setup.bat          🔧 Configuration
├── install.bat        📦 Installation
├── stop.bat           🛑 Arrêt
├── clean.bat          🧹 Nettoyage
├── backup.bat         💾 Sauvegarde
├── update.bat         🔄 Mise à jour
│
├── bot.py             🤖 Bot Discord
├── web_interface.py   🌐 Interface web
├── config.py          ⚙️ Configuration
├── database.py        💾 Base de données
│
├── cogs/              📁 Modules du bot (27 fichiers)
│   ├── economy.py
│   ├── moderation.py
│   ├── music.py
│   └── ...
│
├── utils/             🔧 Utilitaires
│   ├── logger.py
│   └── security.py
│
├── templates/         🎨 Templates HTML
├── data/              💾 Données (créé automatiquement)
├── logs/              📝 Logs (créé automatiquement)
└── backups/           💾 Sauvegardes (créé automatiquement)
```

---

## ❓ Résolution de Problèmes

### Le bot ne démarre pas

1. **Vérifier Python:**
   ```batch
   python --version
   ```
   Python 3.8+ requis

2. **Vérifier le token:**
   - Ouvrez `.env`
   - Vérifiez que `DISCORD_TOKEN` est correct

3. **Réinstaller les dépendances:**
   ```batch
   install.bat
   ```

### Erreur "Module not found"

Réinstallez les dépendances:
```batch
install.bat
```

### L'interface web ne s'ouvre pas

1. Vérifiez que le port 5000 n'est pas utilisé
2. Ouvrez manuellement: http://localhost:5000
3. Vérifiez les logs dans `logs/bot.log`

### Base de données corrompue

Restaurez une sauvegarde:
```batch
copy backups\bot_backup_XXXX.db data\bot.db
```

---

## 🆘 Support

- **Documentation:** README.md
- **Liste des commandes:** COMMANDS_LIST.md
- **Logs:** `logs/bot.log`
- **Configuration:** `.env`

---

## 📝 Notes

- Les scripts sont conçus pour Windows uniquement
- Python 3.8+ est requis
- Git est optionnel (nécessaire seulement pour `update.bat`)
- 7-Zip est optionnel (pour les archives ZIP dans `backup.bat`)

---

**Fait avec ❤️ pour faciliter la gestion du bot Discord**
