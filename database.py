"""
Gestionnaire de base de données SQLite pour le bot Discord
"""
import sqlite3
import json
import asyncio
import aiosqlite
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import logging

from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestionnaire principal de la base de données"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Config.DATA_DIR / "bot.db"
        self.connection_pool = {}
        
    async def init_database(self):
        """Initialise la base de données avec toutes les tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript("""
                -- Guildes
                CREATE TABLE IF NOT EXISTS guilds (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    owner_id INTEGER,
                    prefix TEXT DEFAULT '!',
                    settings TEXT DEFAULT '{}',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Utilisateurs
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    discriminator TEXT,
                    avatar_url TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Membres (relation user-guild)
                CREATE TABLE IF NOT EXISTS members (
                    user_id INTEGER,
                    guild_id INTEGER,
                    nickname TEXT,
                    joined_at DATETIME,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    coins INTEGER DEFAULT 0,
                    last_daily DATETIME,
                    last_work DATETIME,
                    warnings INTEGER DEFAULT 0,
                    is_banned BOOLEAN DEFAULT FALSE,
                    ban_reason TEXT,
                    PRIMARY KEY (user_id, guild_id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (guild_id) REFERENCES guilds(id)
                );
                
                -- Tags
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    name TEXT,
                    content TEXT,
                    author_id INTEGER,
                    usage_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id),
                    FOREIGN KEY (author_id) REFERENCES users(id),
                    UNIQUE(guild_id, name)
                );
                
                -- Auto-réactions
                CREATE TABLE IF NOT EXISTS auto_reactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    trigger_word TEXT,
                    emoji TEXT,
                    created_by INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id),
                    FOREIGN KEY (created_by) REFERENCES users(id),
                    UNIQUE(guild_id, trigger_word)
                );
                
                -- Suggestions
                CREATE TABLE IF NOT EXISTS suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    author_id INTEGER,
                    content TEXT,
                    status TEXT DEFAULT 'open',
                    admin_response TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id),
                    FOREIGN KEY (author_id) REFERENCES users(id)
                );
                
                -- Citations
                CREATE TABLE IF NOT EXISTS quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    content TEXT,
                    author_id INTEGER,
                    added_by INTEGER,
                    usage_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id),
                    FOREIGN KEY (author_id) REFERENCES users(id),
                    FOREIGN KEY (added_by) REFERENCES users(id)
                );
                
                -- Avertissements
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    moderator_id INTEGER,
                    reason TEXT,
                    active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (moderator_id) REFERENCES users(id)
                );
                
                -- Statuts AFK
                CREATE TABLE IF NOT EXISTS afk_status (
                    user_id INTEGER,
                    guild_id INTEGER,
                    reason TEXT,
                    set_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (guild_id) REFERENCES guilds(id)
                );
                
                -- Flux RSS
                CREATE TABLE IF NOT EXISTS rss_feeds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    name TEXT,
                    url TEXT,
                    channel_id INTEGER,
                    webhook_url TEXT,
                    last_update DATETIME,
                    active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id)
                );
                
                -- Articles RSS vus (pour éviter les doublons)
                CREATE TABLE IF NOT EXISTS rss_seen_articles (
                    feed_id INTEGER,
                    article_guid TEXT,
                    seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (feed_id, article_guid),
                    FOREIGN KEY (feed_id) REFERENCES rss_feeds(id)
                );
                
                -- Logs d'activité
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    action_type TEXT,
                    action_data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
                
                -- Économie - Transactions
                CREATE TABLE IF NOT EXISTS economy_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    amount INTEGER,
                    transaction_type TEXT,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
                
                -- Boutique d'objets
                CREATE TABLE IF NOT EXISTS shop_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    name TEXT,
                    description TEXT,
                    price INTEGER,
                    category TEXT,
                    stock INTEGER DEFAULT -1,
                    active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id)
                );
                
                -- Inventaire utilisateurs
                CREATE TABLE IF NOT EXISTS user_inventory (
                    user_id INTEGER,
                    guild_id INTEGER,
                    item_id INTEGER,
                    quantity INTEGER DEFAULT 1,
                    acquired_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id, item_id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (guild_id) REFERENCES guilds(id),
                    FOREIGN KEY (item_id) REFERENCES shop_items(id)
                );
                
                -- Configuration des tickets
                CREATE TABLE IF NOT EXISTS ticket_config (
                    guild_id INTEGER PRIMARY KEY,
                    category_id INTEGER,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id)
                );

                -- Tickets de support
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    channel_id INTEGER,
                    user_id INTEGER,
                    subject TEXT,
                    status TEXT DEFAULT 'open',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    closed_at DATETIME,
                    closed_by INTEGER,
                    close_reason TEXT,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                -- Configuration bienvenue/au revoir
                CREATE TABLE IF NOT EXISTS welcome_config (
                    guild_id INTEGER PRIMARY KEY,
                    welcome_enabled BOOLEAN DEFAULT FALSE,
                    welcome_channel_id INTEGER,
                    welcome_message TEXT,
                    goodbye_enabled BOOLEAN DEFAULT FALSE,
                    goodbye_channel_id INTEGER,
                    goodbye_message TEXT,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id)
                );

                -- Configuration des logs
                CREATE TABLE IF NOT EXISTS logging_config (
                    guild_id INTEGER PRIMARY KEY,
                    log_channel_id INTEGER,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id)
                );

                -- Sondages
                CREATE TABLE IF NOT EXISTS polls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    channel_id INTEGER,
                    message_id INTEGER,
                    question TEXT,
                    options TEXT,
                    author_id INTEGER,
                    end_time DATETIME,
                    active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id),
                    FOREIGN KEY (author_id) REFERENCES users(id)
                );

                -- Rappels
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    guild_id INTEGER,
                    channel_id INTEGER,
                    message TEXT,
                    remind_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    sent BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (guild_id) REFERENCES guilds(id)
                );

                -- Reaction-roles
                CREATE TABLE IF NOT EXISTS reaction_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    channel_id INTEGER,
                    message_id INTEGER,
                    emoji TEXT,
                    role_id INTEGER,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id),
                    UNIQUE(guild_id, message_id, emoji)
                );

                -- Giveaways
                CREATE TABLE IF NOT EXISTS giveaways (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    channel_id INTEGER,
                    message_id INTEGER,
                    prize TEXT,
                    winners_count INTEGER,
                    end_time DATETIME,
                    host_id INTEGER,
                    ended BOOLEAN DEFAULT FALSE,
                    winner_ids TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id),
                    FOREIGN KEY (host_id) REFERENCES users(id)
                );

                -- Notes sur les utilisateurs
                CREATE TABLE IF NOT EXISTS user_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    moderator_id INTEGER,
                    note TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guilds(id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (moderator_id) REFERENCES users(id)
                );

                -- Statistiques des jeux
                CREATE TABLE IF NOT EXISTS game_stats (
                    user_id INTEGER,
                    guild_id INTEGER,
                    game_name TEXT,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    draws INTEGER DEFAULT 0,
                    total_played INTEGER DEFAULT 0,
                    last_played DATETIME,
                    PRIMARY KEY (user_id, guild_id, game_name),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (guild_id) REFERENCES guilds(id)
                );

                -- Index pour optimiser les performances
                CREATE INDEX IF NOT EXISTS idx_members_guild_xp ON members(guild_id, xp DESC);
                CREATE INDEX IF NOT EXISTS idx_warnings_user_guild ON warnings(user_id, guild_id, active);
                CREATE INDEX IF NOT EXISTS idx_activity_logs_guild_time ON activity_logs(guild_id, timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_tags_guild_name ON tags(guild_id, name);
                CREATE INDEX IF NOT EXISTS idx_auto_reactions_guild ON auto_reactions(guild_id);
                CREATE INDEX IF NOT EXISTS idx_tickets_guild_status ON tickets(guild_id, status);
                CREATE INDEX IF NOT EXISTS idx_reminders_user_time ON reminders(user_id, remind_at);
                CREATE INDEX IF NOT EXISTS idx_reaction_roles_message ON reaction_roles(message_id);
                CREATE INDEX IF NOT EXISTS idx_giveaways_guild_ended ON giveaways(guild_id, ended);
                CREATE INDEX IF NOT EXISTS idx_user_notes_user ON user_notes(guild_id, user_id);
            """)
            await db.commit()
            logger.info("Base de données initialisée avec succès")
    
    async def migrate_from_json(self, json_file: Path):
        """Migre les données depuis l'ancien fichier JSON"""
        if not json_file.exists():
            logger.warning(f"Fichier JSON {json_file} introuvable pour la migration")
            return
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Migration des tags
                for guild_id, tags in data.get('tags_store', {}).items():
                    for tag_name, content in tags.items():
                        await db.execute("""
                            INSERT OR REPLACE INTO tags (guild_id, name, content, author_id)
                            VALUES (?, ?, ?, ?)
                        """, (int(guild_id), tag_name, content, 0))
                
                # Migration des auto-réactions
                for guild_id, reacts in data.get('auto_react_store', {}).items():
                    for trigger, emoji in reacts.items():
                        await db.execute("""
                            INSERT OR REPLACE INTO auto_reactions (guild_id, trigger_word, emoji, created_by)
                            VALUES (?, ?, ?, ?)
                        """, (int(guild_id), trigger, emoji, 0))
                
                # Migration des suggestions
                for guild_id, suggestions in data.get('suggestions_store', {}).items():
                    for suggestion in suggestions:
                        await db.execute("""
                            INSERT INTO suggestions (guild_id, author_id, content, status)
                            VALUES (?, ?, ?, ?)
                        """, (int(guild_id), suggestion.get('author_id', 0), 
                             suggestion.get('content', ''), suggestion.get('status', 'open')))
                
                # Migration des citations
                for guild_id, quotes in data.get('quotes_store', {}).items():
                    for quote in quotes:
                        await db.execute("""
                            INSERT INTO quotes (guild_id, content, added_by)
                            VALUES (?, ?, ?)
                        """, (int(guild_id), quote, 0))
                
                # Migration de l'XP
                for guild_id, users_xp in data.get('xp_store', {}).items():
                    for user_id, xp in users_xp.items():
                        level = self.calculate_level_from_xp(xp)
                        await db.execute("""
                            INSERT OR REPLACE INTO members (user_id, guild_id, xp, level)
                            VALUES (?, ?, ?, ?)
                        """, (int(user_id), int(guild_id), xp, level))
                
                await db.commit()
                logger.info("Migration depuis JSON terminée avec succès")
                
        except Exception as e:
            logger.error(f"Erreur lors de la migration JSON: {e}")
    
    @staticmethod
    def calculate_level_from_xp(xp: int) -> int:
        """Calcule le niveau basé sur l'XP"""
        return int((xp / 100) ** 0.5) + 1
    
    @staticmethod
    def calculate_xp_for_level(level: int) -> int:
        """Calcule l'XP nécessaire pour un niveau"""
        return ((level - 1) ** 2) * 100

# Classes pour gérer chaque aspect de la base de données

class UserManager:
    """Gestionnaire des utilisateurs et membres"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
    
    async def get_or_create_user(self, user_id: int, username: Optional[str] = None) -> Dict:
        """Récupère ou crée un utilisateur"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
                user = await cursor.fetchone()
                
            if not user:
                await db.execute("""
                    INSERT INTO users (id, username) VALUES (?, ?)
                """, (user_id, username or f"User{user_id}"))
                await db.commit()
                
                async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
                    user = await cursor.fetchone()
                
        return dict(user) if user else {}
    
    async def get_member_data(self, user_id: int, guild_id: int) -> Dict:
        """Récupère les données d'un membre"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            async with db.execute("""
                SELECT * FROM members WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id)) as cursor:
                member = await cursor.fetchone()
                
            if not member:
                await db.execute("""
                    INSERT INTO members (user_id, guild_id) VALUES (?, ?)
                """, (user_id, guild_id))
                await db.commit()
                
                async with db.execute("""
                    SELECT * FROM members WHERE user_id = ? AND guild_id = ?
                """, (user_id, guild_id)) as cursor:
                    member = await cursor.fetchone()
                    
        return dict(member) if member else {}
    
    async def add_xp(self, user_id: int, guild_id: int, xp_amount: int) -> Dict:
        """Ajoute de l'XP à un utilisateur"""
        await self.get_member_data(user_id, guild_id)  # S'assurer que le membre existe
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Récupérer l'XP actuel
            async with db.execute("""
                SELECT xp, level FROM members WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id)) as cursor:
                current = await cursor.fetchone()
                
            current_xp = current['xp'] if current else 0
            current_level = current['level'] if current else 1
            new_xp = current_xp + xp_amount
            new_level = DatabaseManager.calculate_level_from_xp(new_xp)
            
            await db.execute("""
                UPDATE members SET xp = ?, level = ? WHERE user_id = ? AND guild_id = ?
            """, (new_xp, new_level, user_id, guild_id))
            await db.commit()
            
            return {
                'old_xp': current_xp,
                'new_xp': new_xp,
                'old_level': current_level,
                'new_level': new_level,
                'level_up': new_level > current_level
            }

class EconomyManager:
    """Gestionnaire de l'économie"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
    
    async def get_balance(self, user_id: int, guild_id: int) -> int:
        """Récupère le solde d'un utilisateur"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            async with db.execute("""
                SELECT coins FROM members WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id)) as cursor:
                result = await cursor.fetchone()
                return result['coins'] if result else 0
    
    async def add_coins(self, user_id: int, guild_id: int, amount: int, reason: str = "Unknown") -> int:
        """Ajoute des pièces à un utilisateur"""
        # S'assurer que l'utilisateur existe dans members
        user_mgr = UserManager(self.db_path)
        await user_mgr.get_member_data(user_id, guild_id)
        
        async with aiosqlite.connect(self.db_path) as db:
            # Mettre à jour le solde
            await db.execute("""
                UPDATE members SET coins = coins + ? WHERE user_id = ? AND guild_id = ?
            """, (amount, user_id, guild_id))
            
            # Enregistrer la transaction
            await db.execute("""
                INSERT INTO economy_transactions (guild_id, user_id, amount, transaction_type, description)
                VALUES (?, ?, ?, ?, ?)
            """, (guild_id, user_id, amount, "add", reason))
            
            await db.commit()
            return await self.get_balance(user_id, guild_id)
    
    async def can_daily(self, user_id: int, guild_id: int) -> bool:
        """Vérifie si l'utilisateur peut récupérer ses pièces quotidiennes"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            async with db.execute("""
                SELECT last_daily FROM members WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id)) as cursor:
                result = await cursor.fetchone()
                
            if not result or not result['last_daily']:
                return True
                
            last_daily = datetime.fromisoformat(result['last_daily'])
            return datetime.now() - last_daily >= timedelta(days=1)
    
    async def claim_daily(self, user_id: int, guild_id: int) -> int:
        """Permet à l'utilisateur de récupérer ses pièces quotidiennes"""
        if not await self.can_daily(user_id, guild_id):
            return 0
            
        amount = Config.DAILY_COINS
        await self.add_coins(user_id, guild_id, amount, "Daily reward")
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE members SET last_daily = ? WHERE user_id = ? AND guild_id = ?
            """, (datetime.now().isoformat(), user_id, guild_id))
            await db.commit()
            
        return amount

# Instance globale
db_manager = DatabaseManager()
user_manager = UserManager(Config.DATA_DIR / "bot.db")
economy_manager = EconomyManager(Config.DATA_DIR / "bot.db")