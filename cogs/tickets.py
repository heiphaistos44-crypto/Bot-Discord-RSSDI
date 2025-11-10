"""
Système de tickets de support pour le bot Discord
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

class TicketsCog(commands.Cog):
    """Système de gestion des tickets de support"""

    def __init__(self, bot):
        self.bot = bot
        self.ticket_category_name = "🎫 Tickets"

    async def cog_load(self):
        """Chargement du cog"""
        bot_logger.logger.info("Module tickets chargé")

    @app_commands.command(name="ticket_setup", description="Configure le système de tickets")
    @require_permissions("admin")
    async def ticket_setup(self, interaction: discord.Interaction,
                          category: Optional[discord.CategoryChannel] = None):
        """Configure le système de tickets pour le serveur"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        # Créer ou utiliser la catégorie spécifiée
        if category is None:
            category = await interaction.guild.create_category(self.ticket_category_name)

        # Sauvegarder la configuration dans la base de données
        async with aiosqlite.connect(db_manager.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO ticket_config (guild_id, category_id)
                VALUES (?, ?)
            """, (interaction.guild.id, category.id))
            await db.commit()

        embed = discord.Embed(
            title="✅ Système de tickets configuré",
            description=f"Catégorie: {category.mention}\n\nUtilisez `/ticket_create` pour créer un ticket.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ticket_create", description="Crée un nouveau ticket de support")
    async def ticket_create(self, interaction: discord.Interaction, sujet: str):
        """Crée un nouveau ticket"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        sujet = input_validator.sanitize_text(sujet, 100)

        # Récupérer la configuration
        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT category_id FROM ticket_config WHERE guild_id = ?
            """, (interaction.guild.id,)) as cursor:
                config = await cursor.fetchone()

        if not config:
            await interaction.response.send_message("❌ Le système de tickets n'est pas configuré. Demandez à un administrateur d'utiliser `/ticket_setup`.", ephemeral=True)
            return

        category = interaction.guild.get_channel(config['category_id'])
        if not category:
            await interaction.response.send_message("❌ La catégorie de tickets n'existe plus. Demandez à un administrateur de refaire `/ticket_setup`.", ephemeral=True)
            return

        # Vérifier si l'utilisateur n'a pas déjà un ticket ouvert
        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT channel_id FROM tickets
                WHERE guild_id = ? AND user_id = ? AND status = 'open'
            """, (interaction.guild.id, interaction.user.id)) as cursor:
                existing = await cursor.fetchone()

        if existing:
            channel = interaction.guild.get_channel(existing['channel_id'])
            if channel:
                await interaction.response.send_message(f"❌ Tu as déjà un ticket ouvert: {channel.mention}", ephemeral=True)
                return

        # Créer le canal du ticket
        ticket_number = int(datetime.now().timestamp())
        channel_name = f"ticket-{interaction.user.name}-{ticket_number}"

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await interaction.guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"Ticket de {interaction.user.name} | Sujet: {sujet}"
        )

        # Enregistrer le ticket dans la base de données
        async with aiosqlite.connect(db_manager.db_path) as db:
            await db.execute("""
                INSERT INTO tickets (guild_id, channel_id, user_id, subject, status, created_at)
                VALUES (?, ?, ?, ?, 'open', ?)
            """, (interaction.guild.id, ticket_channel.id, interaction.user.id, sujet, datetime.now().isoformat()))
            await db.commit()

        # Message initial dans le ticket
        embed = discord.Embed(
            title="🎫 Nouveau Ticket",
            description=f"**Créé par:** {interaction.user.mention}\n**Sujet:** {sujet}",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📝 Instructions",
            value="• Décris ton problème en détail\n• Un modérateur te répondra bientôt\n• Utilise `/ticket_close` pour fermer ce ticket",
            inline=False
        )
        embed.set_footer(text=f"Ticket #{ticket_number}")

        await ticket_channel.send(f"{interaction.user.mention}", embed=embed)

        # Réponse à l'utilisateur
        await interaction.response.send_message(f"✅ Ticket créé: {ticket_channel.mention}", ephemeral=True)

        bot_logger.logger.info(f"Ticket créé: {ticket_channel.name} par {interaction.user.id}")

    @app_commands.command(name="ticket_close", description="Ferme un ticket")
    async def ticket_close(self, interaction: discord.Interaction, raison: Optional[str] = "Aucune raison"):
        """Ferme le ticket actuel"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        # Vérifier si c'est un canal de ticket
        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT user_id, subject FROM tickets
                WHERE guild_id = ? AND channel_id = ? AND status = 'open'
            """, (interaction.guild.id, interaction.channel.id)) as cursor:
                ticket = await cursor.fetchone()

        if not ticket:
            await interaction.response.send_message("❌ Ce n'est pas un canal de ticket ou le ticket est déjà fermé.", ephemeral=True)
            return

        # Vérifier les permissions
        ticket_owner = interaction.guild.get_member(ticket['user_id'])
        from utils.security import permission_manager
        is_staff = permission_manager.has_moderator_permissions(interaction.user)
        is_owner = interaction.user.id == ticket['user_id']

        if not (is_staff or is_owner):
            await interaction.response.send_message("❌ Tu ne peux fermer que tes propres tickets, ou être modérateur.", ephemeral=True)
            return

        # Archiver le ticket
        raison = input_validator.sanitize_text(raison, 200)

        embed = discord.Embed(
            title="🔒 Ticket Fermé",
            description=f"**Fermé par:** {interaction.user.mention}\n**Raison:** {raison}",
            color=discord.Color.red()
        )
        embed.add_field(
            name="📊 Informations",
            value=f"**Sujet original:** {ticket['subject']}\n**Propriétaire:** <@{ticket['user_id']}>",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

        # Mettre à jour la base de données
        async with aiosqlite.connect(db_manager.db_path) as db:
            await db.execute("""
                UPDATE tickets
                SET status = 'closed', closed_at = ?, closed_by = ?, close_reason = ?
                WHERE guild_id = ? AND channel_id = ?
            """, (datetime.now().isoformat(), interaction.user.id, raison, interaction.guild.id, interaction.channel.id))
            await db.commit()

        # Supprimer le canal après 5 secondes
        await interaction.channel.send("⚠️ Ce canal sera supprimé dans 5 secondes...")
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=5))
        await interaction.channel.delete(reason=f"Ticket fermé par {interaction.user}")

        bot_logger.logger.info(f"Ticket fermé: {interaction.channel.name} par {interaction.user.id}")

    @app_commands.command(name="ticket_add", description="Ajoute un membre à un ticket")
    @require_permissions("moderator")
    async def ticket_add(self, interaction: discord.Interaction, membre: discord.Member):
        """Ajoute un membre au ticket actuel"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        # Vérifier si c'est un canal de ticket
        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT user_id FROM tickets
                WHERE guild_id = ? AND channel_id = ? AND status = 'open'
            """, (interaction.guild.id, interaction.channel.id)) as cursor:
                ticket = await cursor.fetchone()

        if not ticket:
            await interaction.response.send_message("❌ Ce n'est pas un canal de ticket ouvert.", ephemeral=True)
            return

        # Ajouter les permissions
        await interaction.channel.set_permissions(membre, read_messages=True, send_messages=True)

        await interaction.response.send_message(f"✅ {membre.mention} a été ajouté au ticket.")

    @app_commands.command(name="ticket_list", description="Liste tous les tickets ouverts")
    @require_permissions("moderator")
    async def ticket_list(self, interaction: discord.Interaction):
        """Liste tous les tickets ouverts"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return

        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT channel_id, user_id, subject, created_at
                FROM tickets
                WHERE guild_id = ? AND status = 'open'
                ORDER BY created_at DESC
            """, (interaction.guild.id,)) as cursor:
                tickets = await cursor.fetchall()

        if not tickets:
            await interaction.response.send_message("📭 Aucun ticket ouvert pour le moment.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎫 Tickets Ouverts",
            description=f"Il y a **{len(tickets)}** ticket(s) ouvert(s)",
            color=discord.Color.blue()
        )

        for ticket in tickets[:10]:  # Limiter à 10 pour éviter les embeds trop longs
            channel = interaction.guild.get_channel(ticket['channel_id'])
            if channel:
                embed.add_field(
                    name=f"🎫 {channel.name}",
                    value=f"**Créé par:** <@{ticket['user_id']}>\n**Sujet:** {ticket['subject']}\n**Canal:** {channel.mention}",
                    inline=False
                )

        if len(tickets) > 10:
            embed.set_footer(text=f"... et {len(tickets) - 10} autre(s) ticket(s)")

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketsCog(bot))
