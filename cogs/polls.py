"""
Système de sondages pour le bot Discord
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List
import aiosqlite
from datetime import datetime, timedelta

from config import Config
from database import db_manager
from utils.logger import bot_logger
from utils.security import input_validator

class PollsCog(commands.Cog):
    """Système de création et gestion de sondages"""

    def __init__(self, bot):
        self.bot = bot
        self.number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    async def cog_load(self):
        """Chargement du cog"""
        bot_logger.logger.info("Module sondages chargé")

    @app_commands.command(name="poll", description="Crée un sondage")
    async def poll(self, interaction: discord.Interaction,
                   question: str,
                   option1: str,
                   option2: str,
                   option3: Optional[str] = None,
                   option4: Optional[str] = None,
                   option5: Optional[str] = None,
                   duree_minutes: Optional[int] = None):
        """Crée un sondage avec 2 à 5 options"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        # Valider les entrées
        question = input_validator.sanitize_text(question, 250)
        options = [option1, option2]

        if option3:
            options.append(option3)
        if option4:
            options.append(option4)
        if option5:
            options.append(option5)

        options = [input_validator.sanitize_text(opt, 100) for opt in options]

        if len(options) > 10:
            await interaction.response.send_message("❌ Maximum 10 options pour un sondage.", ephemeral=True)
            return

        # Créer l'embed du sondage
        embed = discord.Embed(
            title="📊 " + question,
            description="Votez en réagissant avec les emojis ci-dessous !",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )

        for i, option in enumerate(options):
            embed.add_field(
                name=f"{self.number_emojis[i]} Option {i+1}",
                value=option,
                inline=False
            )

        if duree_minutes:
            end_time = datetime.now() + timedelta(minutes=duree_minutes)
            embed.add_field(
                name="⏰ Fin du sondage",
                value=discord.utils.format_dt(end_time, 'R'),
                inline=False
            )

        embed.set_footer(text=f"Sondage créé par {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()

        # Ajouter les réactions
        for i in range(len(options)):
            await message.add_reaction(self.number_emojis[i])

        # Sauvegarder le sondage dans la base de données
        async with aiosqlite.connect(db_manager.db_path) as db:
            end_time_iso = (datetime.now() + timedelta(minutes=duree_minutes)).isoformat() if duree_minutes else None
            await db.execute("""
                INSERT INTO polls (guild_id, channel_id, message_id, question, options, author_id, end_time, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (interaction.guild.id, message.channel.id, message.id, question,
                  "|".join(options), interaction.user.id, end_time_iso, True))
            await db.commit()

        bot_logger.logger.info(f"Sondage créé par {interaction.user.id}: {question}")

    @app_commands.command(name="poll_results", description="Affiche les résultats d'un sondage")
    async def poll_results(self, interaction: discord.Interaction, message_id: str):
        """Affiche les résultats d'un sondage"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        try:
            msg_id = int(message_id)
        except ValueError:
            await interaction.response.send_message("❌ ID de message invalide.", ephemeral=True)
            return

        # Récupérer le sondage
        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM polls WHERE guild_id = ? AND message_id = ?
            """, (interaction.guild.id, msg_id)) as cursor:
                poll = await cursor.fetchone()

        if not poll:
            await interaction.response.send_message("❌ Sondage introuvable.", ephemeral=True)
            return

        # Récupérer le message
        try:
            channel = interaction.guild.get_channel(poll['channel_id'])
            if not channel:
                await interaction.response.send_message("❌ Canal introuvable.", ephemeral=True)
                return

            message = await channel.fetch_message(poll['message_id'])
        except discord.NotFound:
            await interaction.response.send_message("❌ Message du sondage introuvable.", ephemeral=True)
            return

        # Compter les votes
        options = poll['options'].split('|')
        results = []
        total_votes = 0

        for i, option in enumerate(options):
            reaction = discord.utils.get(message.reactions, emoji=self.number_emojis[i])
            count = (reaction.count - 1) if reaction else 0  # -1 pour enlever le bot
            results.append((option, count))
            total_votes += count

        # Créer l'embed des résultats
        embed = discord.Embed(
            title="📊 Résultats: " + poll['question'],
            description=f"**Total des votes:** {total_votes}",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )

        # Trier par nombre de votes
        results.sort(key=lambda x: x[1], reverse=True)

        for i, (option, count) in enumerate(results):
            percentage = (count / total_votes * 100) if total_votes > 0 else 0
            bar_length = int(percentage / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)

            embed.add_field(
                name=f"{self.number_emojis[i]} {option}",
                value=f"`{bar}` {count} votes ({percentage:.1f}%)",
                inline=False
            )

        embed.set_footer(text=f"Sondage créé par l'utilisateur ID: {poll['author_id']}")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="poll_end", description="Termine un sondage et affiche les résultats")
    async def poll_end(self, interaction: discord.Interaction, message_id: str):
        """Termine un sondage"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        try:
            msg_id = int(message_id)
        except ValueError:
            await interaction.response.send_message("❌ ID de message invalide.", ephemeral=True)
            return

        # Récupérer le sondage
        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM polls WHERE guild_id = ? AND message_id = ?
            """, (interaction.guild.id, msg_id)) as cursor:
                poll = await cursor.fetchone()

        if not poll:
            await interaction.response.send_message("❌ Sondage introuvable.", ephemeral=True)
            return

        # Vérifier les permissions
        from utils.security import permission_manager
        is_author = interaction.user.id == poll['author_id']
        is_mod = permission_manager.has_moderator_permissions(interaction.user)

        if not (is_author or is_mod):
            await interaction.response.send_message("❌ Seul l'auteur du sondage ou un modérateur peut le terminer.", ephemeral=True)
            return

        # Marquer comme terminé
        async with aiosqlite.connect(db_manager.db_path) as db:
            await db.execute("""
                UPDATE polls SET active = 0 WHERE message_id = ?
            """, (msg_id,))
            await db.commit()

        # Afficher les résultats
        await interaction.response.send_message("✅ Sondage terminé ! Voici les résultats:", ephemeral=True)
        await self.poll_results(interaction, message_id)

async def setup(bot):
    await bot.add_cog(PollsCog(bot))
