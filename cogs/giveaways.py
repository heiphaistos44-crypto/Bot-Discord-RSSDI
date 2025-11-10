"""
Système de giveaways (concours) pour le bot Discord
"""
import discord
from discord.ext import commands, tasks
from discord import app_commands
from typing import Optional
import aiosqlite
from datetime import datetime, timedelta
import random

from config import Config
from database import db_manager
from utils.logger import bot_logger
from utils.security import require_permissions, input_validator

class GiveawaysCog(commands.Cog):
    """Système de giveaways/concours"""

    def __init__(self, bot):
        self.bot = bot
        self.giveaway_emoji = "🎉"
        self.check_giveaways.start()

    async def cog_load(self):
        """Chargement du cog"""
        bot_logger.logger.info("Module giveaways chargé")

    def cog_unload(self):
        """Déchargement du cog"""
        self.check_giveaways.cancel()

    @tasks.loop(seconds=30)
    async def check_giveaways(self):
        """Vérifie et termine les giveaways expirés"""
        try:
            async with aiosqlite.connect(db_manager.db_path) as db:
                db.row_factory = aiosqlite.Row
                now = datetime.now().isoformat()

                async with db.execute("""
                    SELECT * FROM giveaways
                    WHERE end_time <= ? AND ended = 0
                """, (now,)) as cursor:
                    giveaways = await cursor.fetchall()

                for giveaway in giveaways:
                    await self.end_giveaway(giveaway)

        except Exception as e:
            bot_logger.logger.error(f"Erreur vérification giveaways: {e}")

    @check_giveaways.before_loop
    async def before_check_giveaways(self):
        await self.bot.wait_until_ready()

    async def end_giveaway(self, giveaway):
        """Termine un giveaway et choisit les gagnants"""
        try:
            guild = self.bot.get_guild(giveaway['guild_id'])
            if not guild:
                return

            channel = guild.get_channel(giveaway['channel_id'])
            if not channel:
                return

            message = await channel.fetch_message(giveaway['message_id'])
            if not message:
                return

            # Récupérer les participants (ceux qui ont réagi)
            participants = []
            for reaction in message.reactions:
                if str(reaction.emoji) == self.giveaway_emoji:
                    async for user in reaction.users():
                        if not user.bot:
                            participants.append(user)

            # Choisir les gagnants
            winners_count = giveaway['winners_count']
            if len(participants) == 0:
                winners_text = "Aucun participant !"
                winners = []
            elif len(participants) < winners_count:
                winners = participants
                winners_text = ", ".join([w.mention for w in winners])
            else:
                winners = random.sample(participants, winners_count)
                winners_text = ", ".join([w.mention for w in winners])

            # Créer l'embed des résultats
            embed = discord.Embed(
                title="🎉 Giveaway Terminé !",
                description=giveaway['prize'],
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )
            embed.add_field(
                name="🏆 Gagnant(s)",
                value=winners_text,
                inline=False
            )
            embed.add_field(
                name="📊 Participants",
                value=str(len(participants)),
                inline=True
            )
            embed.set_footer(text="Giveaway terminé")

            # Modifier le message original
            await message.edit(embed=embed)

            # Annoncer les gagnants
            if winners:
                congrats_msg = f"🎉 Félicitations {winners_text} ! Vous avez gagné **{giveaway['prize']}** !"
                await channel.send(congrats_msg)

            # Marquer comme terminé dans la base de données
            async with aiosqlite.connect(db_manager.db_path) as db:
                winner_ids = "|".join([str(w.id) for w in winners])
                await db.execute("""
                    UPDATE giveaways
                    SET ended = 1, winner_ids = ?
                    WHERE id = ?
                """, (winner_ids, giveaway['id']))
                await db.commit()

            bot_logger.logger.info(f"Giveaway terminé: {giveaway['prize']} - {len(winners)} gagnant(s)")

        except Exception as e:
            bot_logger.logger.error(f"Erreur fin de giveaway: {e}")

    @app_commands.command(name="giveaway_start", description="Démarre un giveaway")
    @require_permissions("admin")
    async def giveaway_start(self, interaction: discord.Interaction,
                            duree: int,
                            unite: str,
                            gagnants: int,
                            prix: str):
        """Démarre un nouveau giveaway

        Args:
            duree: Durée du giveaway
            unite: 'minutes', 'heures', 'jours'
            gagnants: Nombre de gagnants
            prix: Description du prix
        """
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        # Valider les paramètres
        unite = unite.lower()
        if unite not in ['minutes', 'minute', 'heures', 'heure', 'jours', 'jour']:
            await interaction.response.send_message(
                "❌ Unité invalide. Utilisez 'minutes', 'heures' ou 'jours'.",
                ephemeral=True
            )
            return

        if duree < 1:
            await interaction.response.send_message("❌ La durée doit être d'au moins 1.", ephemeral=True)
            return

        if gagnants < 1:
            await interaction.response.send_message("❌ Il doit y avoir au moins 1 gagnant.", ephemeral=True)
            return

        if gagnants > 20:
            await interaction.response.send_message("❌ Maximum 20 gagnants.", ephemeral=True)
            return

        # Calculer la fin du giveaway
        if 'minute' in unite:
            delta = timedelta(minutes=duree)
        elif 'heure' in unite:
            delta = timedelta(hours=duree)
        else:  # jours
            delta = timedelta(days=duree)

        end_time = datetime.now() + delta
        prix = input_validator.sanitize_text(prix, 500)

        # Créer l'embed
        embed = discord.Embed(
            title="🎉 GIVEAWAY !",
            description=f"**Prix:** {prix}\n\n"
                       f"Réagis avec {self.giveaway_emoji} pour participer !\n"
                       f"**Gagnants:** {gagnants}\n"
                       f"**Fin:** {discord.utils.format_dt(end_time, 'R')}",
            color=discord.Color.gold(),
            timestamp=end_time
        )
        embed.set_footer(text=f"Organisé par {interaction.user.name} | Se termine", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.response.send_message("✅ Giveaway créé !")
        message = await interaction.channel.send(embed=embed)
        await message.add_reaction(self.giveaway_emoji)

        # Sauvegarder dans la base de données
        async with aiosqlite.connect(db_manager.db_path) as db:
            await db.execute("""
                INSERT INTO giveaways (guild_id, channel_id, message_id, prize, winners_count, end_time, host_id, ended)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """, (interaction.guild.id, message.channel.id, message.id, prix, gagnants,
                  end_time.isoformat(), interaction.user.id))
            await db.commit()

        bot_logger.logger.info(f"Giveaway créé par {interaction.user.id}: {prix}")

    @app_commands.command(name="giveaway_end", description="Termine un giveaway immédiatement")
    @require_permissions("admin")
    async def giveaway_end_cmd(self, interaction: discord.Interaction, message_id: str):
        """Termine un giveaway immédiatement"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        try:
            msg_id = int(message_id)
        except ValueError:
            await interaction.response.send_message("❌ ID de message invalide.", ephemeral=True)
            return

        # Récupérer le giveaway
        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM giveaways
                WHERE guild_id = ? AND message_id = ? AND ended = 0
            """, (interaction.guild.id, msg_id)) as cursor:
                giveaway = await cursor.fetchone()

        if not giveaway:
            await interaction.response.send_message("❌ Giveaway introuvable ou déjà terminé.", ephemeral=True)
            return

        await interaction.response.send_message("✅ Terminaison du giveaway en cours...", ephemeral=True)
        await self.end_giveaway(giveaway)

    @app_commands.command(name="giveaway_reroll", description="Retire de nouveaux gagnants")
    @require_permissions("admin")
    async def giveaway_reroll(self, interaction: discord.Interaction, message_id: str):
        """Retire de nouveaux gagnants pour un giveaway terminé"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        try:
            msg_id = int(message_id)
        except ValueError:
            await interaction.response.send_message("❌ ID de message invalide.", ephemeral=True)
            return

        # Récupérer le giveaway
        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM giveaways
                WHERE guild_id = ? AND message_id = ? AND ended = 1
            """, (interaction.guild.id, msg_id)) as cursor:
                giveaway = await cursor.fetchone()

        if not giveaway:
            await interaction.response.send_message("❌ Giveaway introuvable ou non terminé.", ephemeral=True)
            return

        try:
            channel = interaction.guild.get_channel(giveaway['channel_id'])
            message = await channel.fetch_message(giveaway['message_id'])

            # Récupérer les participants
            participants = []
            for reaction in message.reactions:
                if str(reaction.emoji) == self.giveaway_emoji:
                    async for user in reaction.users():
                        if not user.bot:
                            participants.append(user)

            # Exclure les anciens gagnants
            old_winner_ids = [int(wid) for wid in giveaway['winner_ids'].split('|') if wid]
            participants = [p for p in participants if p.id not in old_winner_ids]

            # Choisir de nouveaux gagnants
            if len(participants) == 0:
                await interaction.response.send_message("❌ Aucun nouveau participant disponible.", ephemeral=True)
                return

            winners_count = min(giveaway['winners_count'], len(participants))
            winners = random.sample(participants, winners_count)
            winners_text = ", ".join([w.mention for w in winners])

            embed = discord.Embed(
                title="🎉 Nouveaux Gagnants !",
                description=f"**Prix:** {giveaway['prize']}",
                color=discord.Color.gold()
            )
            embed.add_field(name="🏆 Nouveaux Gagnant(s)", value=winners_text, inline=False)

            await interaction.response.send_message(embed=embed)
            bot_logger.logger.info(f"Giveaway reroll: {len(winners)} nouveau(x) gagnant(s)")

        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
            bot_logger.logger.error(f"Erreur reroll giveaway: {e}")

async def setup(bot):
    await bot.add_cog(GiveawaysCog(bot))
