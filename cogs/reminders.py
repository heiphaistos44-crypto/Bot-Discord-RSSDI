"""
Système de rappels pour le bot Discord
"""
import discord
from discord.ext import commands, tasks
from discord import app_commands
from typing import Optional
import aiosqlite
from datetime import datetime, timedelta
import asyncio

from config import Config
from database import db_manager
from utils.logger import bot_logger
from utils.security import input_validator

class RemindersCog(commands.Cog):
    """Système de rappels programmés"""

    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()

    async def cog_load(self):
        """Chargement du cog"""
        bot_logger.logger.info("Module rappels chargé")

    def cog_unload(self):
        """Déchargement du cog"""
        self.check_reminders.cancel()

    @tasks.loop(seconds=30)
    async def check_reminders(self):
        """Vérifie et envoie les rappels dus"""
        try:
            async with aiosqlite.connect(db_manager.db_path) as db:
                db.row_factory = aiosqlite.Row
                now = datetime.now().isoformat()

                async with db.execute("""
                    SELECT * FROM reminders
                    WHERE remind_at <= ? AND sent = 0
                    ORDER BY remind_at
                """, (now,)) as cursor:
                    reminders = await cursor.fetchall()

                for reminder in reminders:
                    await self.send_reminder(reminder)

                    # Marquer comme envoyé
                    await db.execute("""
                        UPDATE reminders SET sent = 1
                        WHERE id = ?
                    """, (reminder['id'],))
                    await db.commit()

        except Exception as e:
            bot_logger.logger.error(f"Erreur vérification rappels: {e}")

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()

    async def send_reminder(self, reminder):
        """Envoie un rappel à l'utilisateur"""
        try:
            user = await self.bot.fetch_user(reminder['user_id'])
            if not user:
                return

            embed = discord.Embed(
                title="⏰ Rappel !",
                description=reminder['message'],
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.add_field(
                name="📅 Programmé pour",
                value=discord.utils.format_dt(datetime.fromisoformat(reminder['remind_at']), 'F'),
                inline=False
            )
            embed.set_footer(text="Rappel créé le " + datetime.fromisoformat(reminder['created_at']).strftime("%d/%m/%Y à %H:%M"))

            # Essayer d'envoyer dans le canal ou en DM
            if reminder['channel_id']:
                channel = self.bot.get_channel(reminder['channel_id'])
                if channel:
                    await channel.send(f"{user.mention}", embed=embed)
                    return

            # Sinon, envoyer en DM
            await user.send(embed=embed)

        except discord.Forbidden:
            bot_logger.logger.warning(f"Impossible d'envoyer un rappel à {reminder['user_id']}")
        except Exception as e:
            bot_logger.logger.error(f"Erreur envoi rappel: {e}")

    @app_commands.command(name="remind", description="Programme un rappel")
    async def remind(self, interaction: discord.Interaction,
                     duree: int,
                     unite: str,
                     message: str):
        """Programme un rappel

        Args:
            duree: Durée avant le rappel
            unite: 'minutes', 'heures', 'jours'
            message: Message du rappel
        """
        # Valider l'unité
        unite = unite.lower()
        if unite not in ['minutes', 'minute', 'heures', 'heure', 'jours', 'jour']:
            await interaction.response.send_message(
                "❌ Unité invalide. Utilisez 'minutes', 'heures' ou 'jours'.",
                ephemeral=True
            )
            return

        # Valider la durée
        if duree < 1:
            await interaction.response.send_message("❌ La durée doit être d'au moins 1.", ephemeral=True)
            return

        if duree > 365 and 'jour' in unite:
            await interaction.response.send_message("❌ Maximum 365 jours.", ephemeral=True)
            return

        # Calculer le temps du rappel
        if 'minute' in unite:
            delta = timedelta(minutes=duree)
        elif 'heure' in unite:
            delta = timedelta(hours=duree)
        else:  # jours
            delta = timedelta(days=duree)

        remind_at = datetime.now() + delta
        message = input_validator.sanitize_text(message, 500)

        # Sauvegarder le rappel
        async with aiosqlite.connect(db_manager.db_path) as db:
            await db.execute("""
                INSERT INTO reminders (user_id, guild_id, channel_id, message, remind_at, created_at, sent)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            """, (interaction.user.id,
                  interaction.guild.id if interaction.guild else None,
                  interaction.channel.id,
                  message,
                  remind_at.isoformat(),
                  datetime.now().isoformat()))
            await db.commit()

        embed = discord.Embed(
            title="✅ Rappel programmé",
            description=f"Je te rappellerai dans {duree} {unite}.",
            color=discord.Color.green()
        )
        embed.add_field(name="📝 Message", value=message, inline=False)
        embed.add_field(
            name="⏰ Date",
            value=discord.utils.format_dt(remind_at, 'F') + f"\n({discord.utils.format_dt(remind_at, 'R')})",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)
        bot_logger.logger.info(f"Rappel créé pour {interaction.user.id}: {message}")

    @app_commands.command(name="reminders_list", description="Liste tes rappels actifs")
    async def reminders_list(self, interaction: discord.Interaction):
        """Liste les rappels actifs de l'utilisateur"""
        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM reminders
                WHERE user_id = ? AND sent = 0
                ORDER BY remind_at
            """, (interaction.user.id,)) as cursor:
                reminders = await cursor.fetchall()

        if not reminders:
            await interaction.response.send_message("📭 Tu n'as aucun rappel actif.", ephemeral=True)
            return

        embed = discord.Embed(
            title="⏰ Tes Rappels Actifs",
            description=f"Tu as {len(reminders)} rappel(s) programmé(s)",
            color=discord.Color.blue()
        )

        for reminder in reminders[:10]:  # Limiter à 10
            remind_at = datetime.fromisoformat(reminder['remind_at'])
            embed.add_field(
                name=f"ID {reminder['id']} - {discord.utils.format_dt(remind_at, 'R')}",
                value=reminder['message'][:100],
                inline=False
            )

        if len(reminders) > 10:
            embed.set_footer(text=f"... et {len(reminders) - 10} autre(s) rappel(s)")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="reminder_delete", description="Supprime un rappel")
    async def reminder_delete(self, interaction: discord.Interaction, reminder_id: int):
        """Supprime un rappel"""
        async with aiosqlite.connect(db_manager.db_path) as db:
            # Vérifier que le rappel appartient à l'utilisateur
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM reminders WHERE id = ? AND user_id = ?
            """, (reminder_id, interaction.user.id)) as cursor:
                reminder = await cursor.fetchone()

            if not reminder:
                await interaction.response.send_message("❌ Rappel introuvable ou non autorisé.", ephemeral=True)
                return

            # Supprimer le rappel
            await db.execute("""
                DELETE FROM reminders WHERE id = ?
            """, (reminder_id,))
            await db.commit()

        embed = discord.Embed(
            title="✅ Rappel supprimé",
            description=f"Le rappel #{reminder_id} a été supprimé.",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(RemindersCog(bot))
