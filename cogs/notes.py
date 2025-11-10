"""
Système de notes sur les utilisateurs pour le bot Discord
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

class NotesCog(commands.Cog):
    """Système de notes pour les modérateurs"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        """Chargement du cog"""
        bot_logger.logger.info("Module notes chargé")

    @app_commands.command(name="note_add", description="Ajoute une note sur un utilisateur")
    @require_permissions("moderator")
    async def note_add(self, interaction: discord.Interaction,
                      membre: discord.Member,
                      note: str):
        """Ajoute une note sur un utilisateur"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        note = input_validator.sanitize_text(note, 1000)

        async with aiosqlite.connect(db_manager.db_path) as db:
            await db.execute("""
                INSERT INTO user_notes (guild_id, user_id, moderator_id, note, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (interaction.guild.id, membre.id, interaction.user.id, note, datetime.now().isoformat()))
            await db.commit()

        embed = discord.Embed(
            title="✅ Note Ajoutée",
            description=f"Note ajoutée sur {membre.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="📝 Contenu", value=note, inline=False)
        embed.set_footer(text=f"Par {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.response.send_message(embed=embed, ephemeral=True)
        bot_logger.logger.info(f"Note ajoutée sur {membre.id} par {interaction.user.id}")

    @app_commands.command(name="note_list", description="Liste les notes d'un utilisateur")
    @require_permissions("moderator")
    async def note_list(self, interaction: discord.Interaction, membre: discord.Member):
        """Liste toutes les notes d'un utilisateur"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM user_notes
                WHERE guild_id = ? AND user_id = ?
                ORDER BY created_at DESC
            """, (interaction.guild.id, membre.id)) as cursor:
                notes = await cursor.fetchall()

        if not notes:
            await interaction.response.send_message(f"📭 Aucune note sur {membre.mention}.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📋 Notes sur {membre}",
            description=f"{len(notes)} note(s) enregistrée(s)",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=membre.avatar.url if membre.avatar else membre.default_avatar.url)

        for note in notes[:10]:  # Limiter à 10
            created_at = datetime.fromisoformat(note['created_at'])
            moderator = interaction.guild.get_member(note['moderator_id'])
            mod_name = moderator.name if moderator else f"ID: {note['moderator_id']}"

            embed.add_field(
                name=f"#{note['id']} - {discord.utils.format_dt(created_at, 'R')}",
                value=f"**Par:** {mod_name}\n**Note:** {note['note'][:200]}",
                inline=False
            )

        if len(notes) > 10:
            embed.set_footer(text=f"... et {len(notes) - 10} autre(s) note(s)")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="note_delete", description="Supprime une note")
    @require_permissions("moderator")
    async def note_delete(self, interaction: discord.Interaction, note_id: int):
        """Supprime une note"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        async with aiosqlite.connect(db_manager.db_path) as db:
            # Vérifier que la note existe
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM user_notes WHERE id = ? AND guild_id = ?
            """, (note_id, interaction.guild.id)) as cursor:
                note = await cursor.fetchone()

            if not note:
                await interaction.response.send_message("❌ Note introuvable.", ephemeral=True)
                return

            # Supprimer la note
            await db.execute("""
                DELETE FROM user_notes WHERE id = ?
            """, (note_id,))
            await db.commit()

        embed = discord.Embed(
            title="✅ Note Supprimée",
            description=f"La note #{note_id} a été supprimée.",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)
        bot_logger.logger.info(f"Note {note_id} supprimée par {interaction.user.id}")

    @app_commands.command(name="note_clear", description="Efface toutes les notes d'un utilisateur")
    @require_permissions("admin")
    async def note_clear(self, interaction: discord.Interaction, membre: discord.Member):
        """Efface toutes les notes d'un utilisateur"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        async with aiosqlite.connect(db_manager.db_path) as db:
            cursor = await db.execute("""
                DELETE FROM user_notes WHERE guild_id = ? AND user_id = ?
            """, (interaction.guild.id, membre.id))
            await db.commit()

            deleted_count = cursor.rowcount

        if deleted_count == 0:
            await interaction.response.send_message(f"📭 Aucune note à supprimer pour {membre.mention}.", ephemeral=True)
            return

        embed = discord.Embed(
            title="✅ Notes Effacées",
            description=f"{deleted_count} note(s) supprimée(s) pour {membre.mention}",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)
        bot_logger.logger.info(f"{deleted_count} notes effacées pour {membre.id} par {interaction.user.id}")

    @app_commands.command(name="note_search", description="Recherche des notes par mot-clé")
    @require_permissions("moderator")
    async def note_search(self, interaction: discord.Interaction, mot_cle: str):
        """Recherche des notes contenant un mot-clé"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        mot_cle = input_validator.sanitize_text(mot_cle, 100)

        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM user_notes
                WHERE guild_id = ? AND note LIKE ?
                ORDER BY created_at DESC
                LIMIT 20
            """, (interaction.guild.id, f"%{mot_cle}%")) as cursor:
                notes = await cursor.fetchall()

        if not notes:
            await interaction.response.send_message(f"📭 Aucune note trouvée avec le mot-clé '{mot_cle}'.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"🔍 Résultats pour '{mot_cle}'",
            description=f"{len(notes)} note(s) trouvée(s)",
            color=discord.Color.blue()
        )

        for note in notes[:10]:
            created_at = datetime.fromisoformat(note['created_at'])
            user = interaction.guild.get_member(note['user_id'])
            user_name = user.name if user else f"ID: {note['user_id']}"

            embed.add_field(
                name=f"#{note['id']} - {user_name}",
                value=f"{note['note'][:150]}\n*{discord.utils.format_dt(created_at, 'R')}*",
                inline=False
            )

        if len(notes) > 10:
            embed.set_footer(text=f"... et {len(notes) - 10} autre(s) résultat(s)")

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(NotesCog(bot))
