"""
Bot Discord principal - Version restructurée et améliorée
"""
import os
import asyncio
import logging
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands
import aiosqlite

from config import Config
from database import db_manager
from utils.logger import setup_logging, bot_logger
from utils.security import SecurityError

# Configuration du logging
logger = setup_logging()

class DiscordBot(commands.Bot):
    """Classe principale du bot Discord"""
    
    def __init__(self):
        # Configuration des intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.reactions = True
        
        super().__init__(
            command_prefix=self._get_prefix,
            intents=intents,
            help_command=None,  # On utilise notre propre commande help
            case_insensitive=True,
            strip_after_prefix=True
        )
        
        # État du bot
        self.startup_time = None
        self.database_ready = False
        
    async def _get_prefix(self, bot, message):
        """Récupère le préfixe pour un serveur"""
        if not message.guild:
            return Config.COMMAND_PREFIX
        
        # TODO: Récupérer le préfixe personnalisé depuis la base de données
        return Config.COMMAND_PREFIX
    
    async def setup_hook(self):
        """Configuration initiale du bot"""
        logger.info("🚀 Démarrage du bot...")
        
        # Initialiser la base de données
        await self._setup_database()
        
        # Charger les cogs
        await self._load_cogs()
        
        # Synchroniser les commandes slash
        await self._sync_commands()
        
        logger.info("✅ Configuration terminée")
    
    async def _setup_database(self):
        """Configure la base de données"""
        try:
            await db_manager.init_database()
            
            # Migrer les anciennes données JSON si elles existent
            old_data_file = Path("data.json")
            if old_data_file.exists():
                logger.info("📦 Migration des anciennes données...")
                await db_manager.migrate_from_json(old_data_file)
                
                # Faire une sauvegarde de l'ancien fichier
                backup_file = Path("data.json.backup")
                if not backup_file.exists():
                    old_data_file.rename(backup_file)
                    logger.info(f"💾 Sauvegarde créée: {backup_file}")
            
            self.database_ready = True
            logger.info("✅ Base de données initialisée")
            
        except Exception as e:
            logger.error(f"❌ Erreur d'initialisation de la base de données: {e}")
            raise
    
    async def _load_cogs(self):
        """Charge tous les cogs"""
        cogs = [
            # Modules de base
            'cogs.economy',
            'cogs.moderation',
            'cogs.games',
            'cogs.legacy_commands',
            'cogs.advanced_utils',
            'cogs.fun_extras',

            # Systèmes de gestion
            'cogs.tickets',
            'cogs.welcome',
            'cogs.logging',
            'cogs.polls',
            'cogs.reminders',
            'cogs.reactionroles',
            'cogs.giveaways',
            'cogs.notes',
            'cogs.suggestions_system',

            # Information et statistiques
            'cogs.info',
            'cogs.statistics',
            'cogs.leveling',

            # Divertissement et social
            'cogs.entertainment',
            'cogs.social',
            'cogs.minigames',

            # Musique et médias
            'cogs.music',
            'cogs.images',

            # Recherche et API
            'cogs.search',

            # Gestion serveur et configuration
            'cogs.server_management',
            'cogs.configuration',

            # Utilitaires supplémentaires
            'cogs.utilities_extra'
        ]
        
        loaded_count = 0
        for cog in cogs:
            try:
                await self.load_extension(cog)
                loaded_count += 1
                logger.info(f"✅ Cog chargé: {cog}")
            except Exception as e:
                logger.error(f"❌ Erreur chargement {cog}: {e}")
        
        logger.info(f"📦 {loaded_count}/{len(cogs)} cogs chargés")
    
    async def _sync_commands(self):
        """Synchronise les commandes slash"""
        try:
            synced = await self.tree.sync()
            logger.info(f"🔄 {len(synced)} commandes slash synchronisées")
        except Exception as e:
            logger.error(f"❌ Erreur synchronisation commandes: {e}")
    
    async def on_ready(self):
        """Événement de connexion réussie"""
        self.startup_time = discord.utils.utcnow()
        
        logger.info(f"🤖 {self.user} connecté sur {len(self.guilds)} serveur(s)")
        logger.info(f"📊 {len(self.users)} utilisateurs visibles")
        
        # Définir le statut
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} serveurs | /help"
        )
        await self.change_presence(activity=activity)
        
        bot_logger.logger.info("Bot démarré avec succès")
    
    async def on_guild_join(self, guild):
        """Événement d'ajout à un serveur"""
        logger.info(f"➕ Ajouté au serveur: {guild.name} ({guild.id})")
        
        # Initialiser les données du serveur en base
        try:
            async with aiosqlite.connect(db_manager.db_path) as db:
                await db.execute("""
                    INSERT OR IGNORE INTO guilds (id, name, owner_id)
                    VALUES (?, ?, ?)
                """, (guild.id, guild.name, guild.owner_id))
                await db.commit()
        except Exception as e:
            logger.error(f"Erreur initialisation serveur {guild.id}: {e}")
        
        bot_logger.logger.info(f"Ajouté au serveur {guild.name}")
    
    async def on_guild_remove(self, guild):
        """Événement de retrait d'un serveur"""
        logger.info(f"➖ Retiré du serveur: {guild.name} ({guild.id})")
        bot_logger.logger.info(f"Retiré du serveur {guild.name}")
    
    async def on_member_join(self, member):
        """Événement d'arrivée d'un membre"""
        if member.bot:
            return
        
        logger.debug(f"👋 {member} a rejoint {member.guild.name}")
        
        # Log en base
        try:
            async with aiosqlite.connect(db_manager.db_path) as db:
                await db.execute("""
                    INSERT INTO activity_logs (guild_id, user_id, action_type, action_data)
                    VALUES (?, ?, ?, ?)
                """, (member.guild.id, member.id, "MEMBER_JOIN", f"Rejoint {member.guild.name}"))
                await db.commit()
        except Exception as e:
            logger.error(f"Erreur log member_join: {e}")
    
    async def on_member_remove(self, member):
        """Événement de départ d'un membre"""
        if member.bot:
            return
        
        logger.debug(f"👋 {member} a quitté {member.guild.name}")
        
        # Log en base
        try:
            async with aiosqlite.connect(db_manager.db_path) as db:
                await db.execute("""
                    INSERT INTO activity_logs (guild_id, user_id, action_type, action_data)
                    VALUES (?, ?, ?, ?)
                """, (member.guild.id, member.id, "MEMBER_LEAVE", f"Quitté {member.guild.name}"))
                await db.commit()
        except Exception as e:
            logger.error(f"Erreur log member_leave: {e}")
    
    async def on_message(self, message):
        """Événement de message"""
        # Ignorer les bots
        if message.author.bot:
            return
        
        # Traiter les commandes
        await self.process_commands(message)
        
        # Pas d'XP/économie en DM
        if not message.guild:
            return
        
        # Gain d'XP pour l'activité (si le module économie est chargé)
        if Config.ENABLE_ECONOMY and self.database_ready:
            try:
                # Importer dynamiquement pour éviter les imports circulaires
                from database import user_manager
                
                # S'assurer que l'utilisateur existe
                await user_manager.get_or_create_user(message.author.id, message.author.display_name)
                
                # Ajouter de l'XP (1-5 points par message, max 1 fois par minute)
                xp_gain = min(len(message.content) // 10, Config.MAX_XP_PER_MESSAGE)
                if xp_gain > 0:
                    result = await user_manager.add_xp(message.author.id, message.guild.id, xp_gain)
                    
                    # Notifier si montée de niveau
                    if result['level_up']:
                        embed = discord.Embed(
                            title="🎉 Montée de niveau !",
                            description=f"{message.author.mention} est maintenant niveau **{result['new_level']}** !",
                            color=discord.Color.gold()
                        )
                        await message.channel.send(embed=embed, delete_after=10)
                        
                        bot_logger.logger.info(f"Level up: {message.author.id} reached level {result['new_level']}")
            
            except Exception as e:
                logger.error(f"Erreur traitement XP: {e}")
    
    async def on_command_error(self, ctx, error):
        """Gestionnaire d'erreurs des commandes"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignorer les commandes inexistantes
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Tu n'as pas les permissions nécessaires pour cette commande.")
            return
        
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Je n'ai pas les permissions nécessaires pour exécuter cette commande.")
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏱️ Commande en cooldown. Réessaye dans {error.retry_after:.1f}s.")
            return
        
        if isinstance(error, SecurityError):
            await ctx.send(f"🔒 Erreur de sécurité: {error}")
            return
        
        # Erreurs non gérées
        logger.error(f"Erreur commande non gérée: {error}", exc_info=True)
        bot_logger.logger.error(f"Command error in {ctx.command}: {error}")
        
        await ctx.send("❌ Une erreur inattendue s'est produite. L'incident a été signalé.")
    
    async def on_application_command_error(self, interaction, error):
        """Gestionnaire d'erreurs des commandes slash"""
        if isinstance(error, SecurityError):
            await interaction.response.send_message(f"🔒 Erreur de sécurité: {error}", ephemeral=True)
            return
        
        # Erreurs non gérées
        logger.error(f"Erreur commande slash non gérée: {error}", exc_info=True)
        
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Une erreur inattendue s'est produite. L'incident a été signalé.", 
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ Une erreur inattendue s'est produite. L'incident a été signalé.", 
                    ephemeral=True
                )
        except Exception:
            pass  # Éviter les erreurs en cascade
    
    async def close(self):
        """Nettoyage à la fermeture"""
        logger.info("🛑 Arrêt du bot...")
        await super().close()

# Commandes globales (non dans un cog)
class GlobalCommands(commands.Cog):
    """Commandes globales du bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @discord.app_commands.command(name="help", description="Affiche l'aide du bot")
    async def help_command(self, interaction: discord.Interaction):
        """Commande d'aide principale"""
        embed = discord.Embed(
            title="🤖 Aide du Bot",
            description="Bot Discord multifonction avec économie, modération, jeux et plus !",
            color=discord.Color.blue()
        )
        
        # Modules disponibles
        modules = []
        if Config.ENABLE_ECONOMY:
            modules.append("💰 **Économie** - Pièces, travail, paris")
        
        modules.extend([
            "🛡️ **Modération** - Kick, ban, warn, automod",
            "🎮 **Jeux** - Pierre-papier-ciseaux, trivia, duels",
            "📊 **Niveaux** - Système d'XP et classements",
            "🔧 **Utilitaires** - Sondages, rappels, calculs"
        ])
        
        embed.add_field(
            name="📦 Modules",
            value="\n".join(modules),
            inline=False
        )
        
        embed.add_field(
            name="🔗 Liens utiles",
            value="• `/help` - Cette aide\n• `/commands` - Liste des commandes\n• `/botinfo` - Infos du bot",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Configuration",
            value="Utilise `/config` pour configurer le bot sur ton serveur",
            inline=False
        )
        
        embed.set_footer(text=f"Bot en ligne depuis: {discord.utils.format_dt(self.bot.startup_time, 'R')}")
        
        await interaction.response.send_message(embed=embed)
    
    @discord.app_commands.command(name="ping", description="Affiche la latence du bot")
    async def ping(self, interaction: discord.Interaction):
        """Commande ping"""
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong !",
            description=f"Latence: **{latency}ms**",
            color=discord.Color.green() if latency < 100 else discord.Color.orange() if latency < 200 else discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @discord.app_commands.command(name="botinfo", description="Informations sur le bot")
    async def botinfo(self, interaction: discord.Interaction):
        """Informations du bot"""
        embed = discord.Embed(
            title="🤖 Informations du Bot",
            color=discord.Color.blurple()
        )
        
        embed.add_field(name="👤 Nom", value=self.bot.user.name, inline=True)
        embed.add_field(name="🆔 ID", value=self.bot.user.id, inline=True)
        embed.add_field(name="📡 Latence", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        embed.add_field(name="🏠 Serveurs", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="👥 Utilisateurs", value=len(self.bot.users), inline=True)
        embed.add_field(name="⚙️ Commandes", value=len(self.bot.tree.get_commands()), inline=True)
        
        if self.bot.startup_time:
            embed.add_field(
                name="⏰ En ligne depuis", 
                value=discord.utils.format_dt(self.bot.startup_time, 'R'), 
                inline=False
            )
        
        import sys
        embed.add_field(
            name="🔧 Version",
            value=f"Discord.py {discord.__version__}\nPython {'.'.join(map(str, sys.version_info[:3]))}",
            inline=True
        )
        
        embed.add_field(
            name="💾 Base de données",
            value="✅ Connectée" if self.bot.database_ready else "❌ Erreur",
            inline=True
        )
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url)
        
        await interaction.response.send_message(embed=embed)

async def main():
    """Fonction principale"""
    try:
        # Créer et démarrer le bot
        bot = DiscordBot()
        
        # Ajouter les commandes globales
        await bot.add_cog(GlobalCommands(bot))
        
        # Démarrer le bot
        async with bot:
            if not Config.DISCORD_TOKEN:
                logger.error("❌ Le token Discord n'est pas défini dans la configuration.")
                raise ValueError("Le token Discord est requis pour démarrer le bot.")
            await bot.start(Config.DISCORD_TOKEN)
            
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur critique: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot arrêté")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")