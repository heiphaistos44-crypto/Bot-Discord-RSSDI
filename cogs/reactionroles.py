"""
Système de réaction-roles pour le bot Discord
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import aiosqlite

from config import Config
from database import db_manager
from utils.logger import bot_logger
from utils.security import require_permissions

class ReactionRolesCog(commands.Cog):
    """Système d'attribution de rôles par réaction"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        """Chargement du cog"""
        bot_logger.logger.info("Module reaction-roles chargé")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Ajoute un rôle quand une réaction est ajoutée"""
        if payload.user_id == self.bot.user.id:
            return

        # Récupérer la configuration de reaction-role
        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT role_id FROM reaction_roles
                WHERE guild_id = ? AND message_id = ? AND emoji = ?
            """, (payload.guild_id, payload.message_id, str(payload.emoji))) as cursor:
                config = await cursor.fetchone()

        if not config:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        role = guild.get_role(config['role_id'])
        if not role:
            return

        try:
            await member.add_roles(role, reason="Reaction role")
            bot_logger.logger.info(f"Rôle {role.name} ajouté à {member} via reaction-role")
        except discord.Forbidden:
            bot_logger.logger.warning(f"Impossible d'ajouter le rôle {role.name} à {member}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Retire un rôle quand une réaction est retirée"""
        if payload.user_id == self.bot.user.id:
            return

        # Récupérer la configuration de reaction-role
        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT role_id FROM reaction_roles
                WHERE guild_id = ? AND message_id = ? AND emoji = ?
            """, (payload.guild_id, payload.message_id, str(payload.emoji))) as cursor:
                config = await cursor.fetchone()

        if not config:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        role = guild.get_role(config['role_id'])
        if not role:
            return

        try:
            await member.remove_roles(role, reason="Reaction role removed")
            bot_logger.logger.info(f"Rôle {role.name} retiré de {member} via reaction-role")
        except discord.Forbidden:
            bot_logger.logger.warning(f"Impossible de retirer le rôle {role.name} de {member}")

    @app_commands.command(name="reactionrole_add", description="Ajoute un reaction-role")
    @require_permissions("admin")
    async def reactionrole_add(self, interaction: discord.Interaction,
                               message_id: str,
                               emoji: str,
                               role: discord.Role):
        """Ajoute une configuration de reaction-role"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        try:
            msg_id = int(message_id)
        except ValueError:
            await interaction.response.send_message("❌ ID de message invalide.", ephemeral=True)
            return

        # Vérifier que le message existe
        try:
            message = await interaction.channel.fetch_message(msg_id)
        except discord.NotFound:
            await interaction.response.send_message("❌ Message introuvable dans ce canal.", ephemeral=True)
            return

        # Vérifier la hiérarchie des rôles
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ Je ne peux pas gérer ce rôle (hiérarchie).", ephemeral=True)
            return

        # Ajouter la réaction au message
        try:
            await message.add_reaction(emoji)
        except discord.HTTPException:
            await interaction.response.send_message("❌ Emoji invalide ou impossible à ajouter.", ephemeral=True)
            return

        # Sauvegarder dans la base de données
        async with aiosqlite.connect(db_manager.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO reaction_roles (guild_id, channel_id, message_id, emoji, role_id)
                VALUES (?, ?, ?, ?, ?)
            """, (interaction.guild.id, message.channel.id, message.id, emoji, role.id))
            await db.commit()

        embed = discord.Embed(
            title="✅ Reaction-Role configuré",
            description=f"Les utilisateurs qui réagissent avec {emoji} au message recevront le rôle {role.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="📝 Message", value=f"[Aller au message]({message.jump_url})", inline=False)

        await interaction.response.send_message(embed=embed)
        bot_logger.logger.info(f"Reaction-role configuré: {emoji} -> {role.name}")

    @app_commands.command(name="reactionrole_remove", description="Retire un reaction-role")
    @require_permissions("admin")
    async def reactionrole_remove(self, interaction: discord.Interaction,
                                  message_id: str,
                                  emoji: str):
        """Retire une configuration de reaction-role"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        try:
            msg_id = int(message_id)
        except ValueError:
            await interaction.response.send_message("❌ ID de message invalide.", ephemeral=True)
            return

        # Supprimer de la base de données
        async with aiosqlite.connect(db_manager.db_path) as db:
            cursor = await db.execute("""
                DELETE FROM reaction_roles
                WHERE guild_id = ? AND message_id = ? AND emoji = ?
            """, (interaction.guild.id, msg_id, emoji))
            await db.commit()

            if cursor.rowcount == 0:
                await interaction.response.send_message("❌ Aucune configuration trouvée pour ce message et cet emoji.", ephemeral=True)
                return

        embed = discord.Embed(
            title="✅ Reaction-Role supprimé",
            description=f"La configuration pour {emoji} a été supprimée.",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="reactionrole_list", description="Liste les reaction-roles configurés")
    @require_permissions("admin")
    async def reactionrole_list(self, interaction: discord.Interaction):
        """Liste tous les reaction-roles"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM reaction_roles WHERE guild_id = ?
            """, (interaction.guild.id,)) as cursor:
                configs = await cursor.fetchall()

        if not configs:
            await interaction.response.send_message("📭 Aucun reaction-role configuré.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎭 Reaction-Roles Configurés",
            description=f"{len(configs)} configuration(s)",
            color=discord.Color.blue()
        )

        for config in configs[:25]:  # Limiter à 25 (limite Discord)
            role = interaction.guild.get_role(config['role_id'])
            role_name = role.mention if role else f"Rôle inconnu ({config['role_id']})"

            embed.add_field(
                name=f"{config['emoji']} → {role_name}",
                value=f"Message ID: `{config['message_id']}`\nCanal: <#{config['channel_id']}>",
                inline=False
            )

        if len(configs) > 25:
            embed.set_footer(text=f"... et {len(configs) - 25} autre(s)")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="reactionrole_panel", description="Crée un panneau de reaction-roles")
    @require_permissions("admin")
    async def reactionrole_panel(self, interaction: discord.Interaction,
                                 title: str,
                                 description: str):
        """Crée un message panneau pour les reaction-roles"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        from utils.security import input_validator
        title = input_validator.sanitize_text(title, 250)
        description = input_validator.sanitize_text(description, 2000)

        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Réagis avec les emojis pour obtenir les rôles correspondants !")

        await interaction.response.send_message("✅ Panneau créé ci-dessous !")
        message = await interaction.channel.send(embed=embed)

        await interaction.followup.send(
            f"✅ Panneau créé ! ID du message: `{message.id}`\n"
            f"Utilise `/reactionrole_add {message.id} <emoji> <role>` pour ajouter des rôles.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(ReactionRolesCog(bot))
