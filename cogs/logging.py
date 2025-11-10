"""
Système de logs avancés pour le bot Discord
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
from utils.security import require_permissions

class LoggingCog(commands.Cog):
    """Système de logs des événements du serveur"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        """Chargement du cog"""
        bot_logger.logger.info("Module logging avancé chargé")

    async def send_log(self, guild_id: int, embed: discord.Embed):
        """Envoie un log dans le canal configuré"""
        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT log_channel_id FROM logging_config WHERE guild_id = ?
            """, (guild_id,)) as cursor:
                config = await cursor.fetchone()

        if not config or not config['log_channel_id']:
            return

        guild = self.bot.get_guild(guild_id)
        if not guild:
            return

        channel = guild.get_channel(config['log_channel_id'])
        if not channel:
            return

        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            bot_logger.logger.warning(f"Impossible d'envoyer des logs dans {channel.name}")

    @app_commands.command(name="log_setup", description="Configure le système de logs")
    @require_permissions("admin")
    async def log_setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Configure le canal de logs"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        async with aiosqlite.connect(db_manager.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO logging_config (guild_id, log_channel_id)
                VALUES (?, ?)
            """, (interaction.guild.id, channel.id))
            await db.commit()

        embed = discord.Embed(
            title="✅ Logs configurés",
            description=f"Les logs seront envoyés dans {channel.mention}",
            color=discord.Color.green()
        )
        embed.add_field(
            name="📋 Événements loggés",
            value="• Messages supprimés\n• Messages édités\n• Membres bannis/expulsés\n• Rôles modifiés\n• Canaux modifiés\n• Et plus encore...",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Log des messages supprimés"""
        if message.author.bot or not message.guild:
            return

        embed = discord.Embed(
            title="🗑️ Message Supprimé",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="👤 Auteur", value=message.author.mention, inline=True)
        embed.add_field(name="📍 Canal", value=message.channel.mention, inline=True)
        embed.add_field(name="📝 Contenu", value=message.content[:1000] or "*Message vide ou embed*", inline=False)

        if message.attachments:
            embed.add_field(
                name="📎 Pièces jointes",
                value=f"{len(message.attachments)} fichier(s)",
                inline=True
            )

        embed.set_footer(text=f"ID Message: {message.id} | ID Auteur: {message.author.id}")

        await self.send_log(message.guild.id, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Log des messages édités"""
        if before.author.bot or not before.guild or before.content == after.content:
            return

        embed = discord.Embed(
            title="✏️ Message Édité",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        embed.add_field(name="👤 Auteur", value=before.author.mention, inline=True)
        embed.add_field(name="📍 Canal", value=before.channel.mention, inline=True)
        embed.add_field(name="📝 Avant", value=before.content[:500] or "*Vide*", inline=False)
        embed.add_field(name="📝 Après", value=after.content[:500] or "*Vide*", inline=False)
        embed.add_field(name="🔗 Lien", value=f"[Aller au message]({after.jump_url})", inline=False)

        embed.set_footer(text=f"ID Message: {before.id}")

        await self.send_log(before.guild.id, embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        """Log des bans"""
        embed = discord.Embed(
            title="🔨 Membre Banni",
            description=f"**{user}** a été banni du serveur",
            color=discord.Color.dark_red(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        embed.add_field(name="👤 Utilisateur", value=user.mention, inline=True)
        embed.add_field(name="🆔 ID", value=user.id, inline=True)
        embed.set_footer(text=f"Compte créé le: {user.created_at.strftime('%d/%m/%Y')}")

        await self.send_log(guild.id, embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        """Log des débans"""
        embed = discord.Embed(
            title="🔓 Membre Débanni",
            description=f"**{user}** a été débanni du serveur",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        embed.add_field(name="👤 Utilisateur", value=user.mention, inline=True)
        embed.add_field(name="🆔 ID", value=user.id, inline=True)

        await self.send_log(guild.id, embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Log des modifications de membres"""
        if before.roles != after.roles:
            # Rôles modifiés
            added_roles = [role for role in after.roles if role not in before.roles]
            removed_roles = [role for role in before.roles if role not in after.roles]

            if added_roles or removed_roles:
                embed = discord.Embed(
                    title="👥 Rôles Modifiés",
                    description=f"Modifications des rôles de **{after}**",
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                embed.set_thumbnail(url=after.avatar.url if after.avatar else after.default_avatar.url)

                if added_roles:
                    embed.add_field(
                        name="➕ Rôles ajoutés",
                        value=", ".join([role.mention for role in added_roles]),
                        inline=False
                    )

                if removed_roles:
                    embed.add_field(
                        name="➖ Rôles retirés",
                        value=", ".join([role.mention for role in removed_roles]),
                        inline=False
                    )

                embed.set_footer(text=f"ID: {after.id}")

                await self.send_log(after.guild.id, embed)

        elif before.nick != after.nick:
            # Pseudo modifié
            embed = discord.Embed(
                title="✏️ Pseudo Modifié",
                description=f"Modification du pseudo de **{after}**",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.add_field(name="📝 Ancien pseudo", value=before.nick or before.name, inline=True)
            embed.add_field(name="📝 Nouveau pseudo", value=after.nick or after.name, inline=True)
            embed.set_footer(text=f"ID: {after.id}")

            await self.send_log(after.guild.id, embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Log de création de canaux"""
        embed = discord.Embed(
            title="📝 Canal Créé",
            description=f"Un nouveau canal a été créé: {channel.mention}",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="📌 Nom", value=channel.name, inline=True)
        embed.add_field(name="🔖 Type", value=str(channel.type), inline=True)
        embed.add_field(name="🆔 ID", value=channel.id, inline=True)

        await self.send_log(channel.guild.id, embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Log de suppression de canaux"""
        embed = discord.Embed(
            title="🗑️ Canal Supprimé",
            description=f"Le canal **{channel.name}** a été supprimé",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="📌 Nom", value=channel.name, inline=True)
        embed.add_field(name="🔖 Type", value=str(channel.type), inline=True)
        embed.add_field(name="🆔 ID", value=channel.id, inline=True)

        await self.send_log(channel.guild.id, embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        """Log de création de rôles"""
        embed = discord.Embed(
            title="🎨 Rôle Créé",
            description=f"Un nouveau rôle a été créé: {role.mention}",
            color=role.color,
            timestamp=datetime.now()
        )
        embed.add_field(name="📌 Nom", value=role.name, inline=True)
        embed.add_field(name="🎨 Couleur", value=str(role.color), inline=True)
        embed.add_field(name="🆔 ID", value=role.id, inline=True)

        await self.send_log(role.guild.id, embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        """Log de suppression de rôles"""
        embed = discord.Embed(
            title="🗑️ Rôle Supprimé",
            description=f"Le rôle **{role.name}** a été supprimé",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="📌 Nom", value=role.name, inline=True)
        embed.add_field(name="🆔 ID", value=role.id, inline=True)

        await self.send_log(role.guild.id, embed)

    @app_commands.command(name="log_disable", description="Désactive le système de logs")
    @require_permissions("admin")
    async def log_disable(self, interaction: discord.Interaction):
        """Désactive les logs"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        async with aiosqlite.connect(db_manager.db_path) as db:
            await db.execute("""
                DELETE FROM logging_config WHERE guild_id = ?
            """, (interaction.guild.id,))
            await db.commit()

        embed = discord.Embed(
            title="✅ Logs désactivés",
            description="Le système de logs a été désactivé.",
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
