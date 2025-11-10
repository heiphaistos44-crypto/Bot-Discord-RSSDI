"""
Système de bienvenue et d'au revoir pour le bot Discord
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import aiosqlite
from datetime import datetime

from config import Config
from database import db_manager
from utils.logger import bot_logger
from utils.security import require_permissions, input_validator

class WelcomeCog(commands.Cog):
    """Système de messages de bienvenue et d'au revoir"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        """Chargement du cog"""
        bot_logger.logger.info("Module bienvenue/au revoir chargé")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Événement quand un membre rejoint le serveur"""
        if member.bot:
            return

        # Récupérer la configuration
        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT welcome_enabled, welcome_channel_id, welcome_message
                FROM welcome_config
                WHERE guild_id = ?
            """, (member.guild.id,)) as cursor:
                config = await cursor.fetchone()

        if not config or not config['welcome_enabled']:
            return

        channel = member.guild.get_channel(config['welcome_channel_id'])
        if not channel:
            return

        # Variables disponibles pour le message
        message = config['welcome_message'] or "Bienvenue {user} sur **{server}** ! Tu es le membre n°{count} !"
        message = message.replace("{user}", member.mention)
        message = message.replace("{username}", member.name)
        message = message.replace("{server}", member.guild.name)
        message = message.replace("{count}", str(member.guild.member_count))

        embed = discord.Embed(
            title="👋 Nouveau Membre !",
            description=message,
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"ID: {member.id}")

        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            bot_logger.logger.warning(f"Impossible d'envoyer le message de bienvenue dans {channel.name}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Événement quand un membre quitte le serveur"""
        if member.bot:
            return

        # Récupérer la configuration
        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT goodbye_enabled, goodbye_channel_id, goodbye_message
                FROM welcome_config
                WHERE guild_id = ?
            """, (member.guild.id,)) as cursor:
                config = await cursor.fetchone()

        if not config or not config['goodbye_enabled']:
            return

        channel = member.guild.get_channel(config['goodbye_channel_id'])
        if not channel:
            return

        # Variables disponibles pour le message
        message = config['goodbye_message'] or "Au revoir {username}, nous espérons te revoir bientôt sur **{server}** !"
        message = message.replace("{user}", f"**{member.name}**")
        message = message.replace("{username}", member.name)
        message = message.replace("{server}", member.guild.name)
        message = message.replace("{count}", str(member.guild.member_count))

        embed = discord.Embed(
            title="👋 Membre Parti",
            description=message,
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"ID: {member.id}")

        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            bot_logger.logger.warning(f"Impossible d'envoyer le message d'au revoir dans {channel.name}")

    @app_commands.command(name="welcome_setup", description="Configure le système de bienvenue")
    @require_permissions("admin")
    async def welcome_setup(self, interaction: discord.Interaction,
                           channel: discord.TextChannel,
                           message: Optional[str] = None):
        """Configure le système de bienvenue"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        if message:
            message = input_validator.sanitize_text(message, 1000)

        async with aiosqlite.connect(db_manager.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO welcome_config
                (guild_id, welcome_enabled, welcome_channel_id, welcome_message)
                VALUES (?, ?, ?, ?)
            """, (interaction.guild.id, True, channel.id, message))
            await db.commit()

        embed = discord.Embed(
            title="✅ Bienvenue configurée",
            description=f"Les messages de bienvenue seront envoyés dans {channel.mention}",
            color=discord.Color.green()
        )

        if message:
            embed.add_field(
                name="📝 Message personnalisé",
                value=message,
                inline=False
            )
        else:
            embed.add_field(
                name="📝 Message par défaut",
                value="Bienvenue {user} sur **{server}** ! Tu es le membre n°{count} !",
                inline=False
            )

        embed.add_field(
            name="💡 Variables disponibles",
            value="`{user}` - Mention de l'utilisateur\n`{username}` - Nom de l'utilisateur\n`{server}` - Nom du serveur\n`{count}` - Nombre de membres",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="goodbye_setup", description="Configure le système d'au revoir")
    @require_permissions("admin")
    async def goodbye_setup(self, interaction: discord.Interaction,
                           channel: discord.TextChannel,
                           message: Optional[str] = None):
        """Configure le système d'au revoir"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        if message:
            message = input_validator.sanitize_text(message, 1000)

        async with aiosqlite.connect(db_manager.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO welcome_config
                (guild_id, goodbye_enabled, goodbye_channel_id, goodbye_message)
                VALUES (?, ?, ?, ?)
            """, (interaction.guild.id, True, channel.id, message))
            await db.commit()

        embed = discord.Embed(
            title="✅ Au revoir configuré",
            description=f"Les messages d'au revoir seront envoyés dans {channel.mention}",
            color=discord.Color.green()
        )

        if message:
            embed.add_field(
                name="📝 Message personnalisé",
                value=message,
                inline=False
            )
        else:
            embed.add_field(
                name="📝 Message par défaut",
                value="Au revoir {username}, nous espérons te revoir bientôt sur **{server}** !",
                inline=False
            )

        embed.add_field(
            name="💡 Variables disponibles",
            value="`{user}` - Nom de l'utilisateur (bold)\n`{username}` - Nom de l'utilisateur\n`{server}` - Nom du serveur\n`{count}` - Nombre de membres restants",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="welcome_toggle", description="Active/désactive le système de bienvenue")
    @require_permissions("admin")
    async def welcome_toggle(self, interaction: discord.Interaction, activer: bool):
        """Active ou désactive le système de bienvenue"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        async with aiosqlite.connect(db_manager.db_path) as db:
            await db.execute("""
                UPDATE welcome_config
                SET welcome_enabled = ?
                WHERE guild_id = ?
            """, (activer, interaction.guild.id))
            await db.commit()

        status = "activé" if activer else "désactivé"
        embed = discord.Embed(
            title=f"✅ Bienvenue {status}",
            description=f"Le système de bienvenue a été {status}.",
            color=discord.Color.green() if activer else discord.Color.red()
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="goodbye_toggle", description="Active/désactive le système d'au revoir")
    @require_permissions("admin")
    async def goodbye_toggle(self, interaction: discord.Interaction, activer: bool):
        """Active ou désactive le système d'au revoir"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        async with aiosqlite.connect(db_manager.db_path) as db:
            await db.execute("""
                UPDATE welcome_config
                SET goodbye_enabled = ?
                WHERE guild_id = ?
            """, (activer, interaction.guild.id))
            await db.commit()

        status = "activé" if activer else "désactivé"
        embed = discord.Embed(
            title=f"✅ Au revoir {status}",
            description=f"Le système d'au revoir a été {status}.",
            color=discord.Color.green() if activer else discord.Color.red()
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="welcome_test", description="Teste le message de bienvenue")
    @require_permissions("admin")
    async def welcome_test(self, interaction: discord.Interaction):
        """Teste le message de bienvenue avec l'utilisateur actuel"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        await interaction.response.send_message("✅ Test du message de bienvenue...", ephemeral=True)
        await self.on_member_join(interaction.user)

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
