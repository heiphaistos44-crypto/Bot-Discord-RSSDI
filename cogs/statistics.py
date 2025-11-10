"""
Module de statistiques avancées
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from utils.logger import bot_logger

class StatisticsCog(commands.Cog):
    """Statistiques avancées"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        bot_logger.logger.info("Module statistiques chargé")

    @app_commands.command(name="stats", description="Statistiques générales")
    async def stats(self, interaction: discord.Interaction):
        await interaction.response.send_message("📊 Statistiques générales")

    @app_commands.command(name="messages_stats", description="Stats de messages")
    async def messages_stats(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("📝 Statistiques de messages")

    @app_commands.command(name="activity_stats", description="Stats d'activité")
    async def activity_stats(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("📈 Statistiques d'activité")

    @app_commands.command(name="voice_stats", description="Stats vocales")
    async def voice_stats(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("🎙️ Statistiques vocales")

    @app_commands.command(name="top_messages", description="Top messages")
    async def top_messages(self, interaction: discord.Interaction):
        await interaction.response.send_message("📊 Top messages")

    @app_commands.command(name="top_voice", description="Top vocal")
    async def top_voice(self, interaction: discord.Interaction):
        await interaction.response.send_message("🎙️ Top vocal")

    @app_commands.command(name="top_active", description="Top actifs")
    async def top_active(self, interaction: discord.Interaction):
        await interaction.response.send_message("👥 Top actifs")

    @app_commands.command(name="top_level", description="Top niveaux")
    async def top_level(self, interaction: discord.Interaction):
        await interaction.response.send_message("⭐ Top niveaux")

    @app_commands.command(name="top_coins", description="Top richesse")
    async def top_coins(self, interaction: discord.Interaction):
        await interaction.response.send_message("💰 Top richesse")

    @app_commands.command(name="server_growth", description="Croissance du serveur")
    async def server_growth(self, interaction: discord.Interaction):
        await interaction.response.send_message("📈 Croissance du serveur")

    @app_commands.command(name="join_stats", description="Stats d'arrivées")
    async def join_stats(self, interaction: discord.Interaction):
        await interaction.response.send_message("➕ Statistiques d'arrivées")

    @app_commands.command(name="leave_stats", description="Stats de départs")
    async def leave_stats(self, interaction: discord.Interaction):
        await interaction.response.send_message("➖ Statistiques de départs")

    @app_commands.command(name="ban_stats", description="Stats de bans")
    async def ban_stats(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔨 Statistiques de bans")

    @app_commands.command(name="role_stats", description="Stats des rôles")
    async def role_stats(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f"📊 Stats du rôle {role.mention}")

    @app_commands.command(name="channel_stats", description="Stats d'un salon")
    async def channel_stats(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        await interaction.response.send_message("📊 Statistiques du salon")

    @app_commands.command(name="emoji_stats", description="Stats des emojis")
    async def emoji_stats(self, interaction: discord.Interaction):
        await interaction.response.send_message("😀 Statistiques des emojis")

    @app_commands.command(name="word_count", description="Compte de mots")
    async def word_count(self, interaction: discord.Interaction, mot: str):
        await interaction.response.send_message(f"🔍 Occurrences de '{mot}'")

    @app_commands.command(name="user_activity", description="Activité d'un utilisateur")
    async def user_activity(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"📊 Activité de {membre.mention}")

    @app_commands.command(name="daily_activity", description="Activité quotidienne")
    async def daily_activity(self, interaction: discord.Interaction):
        await interaction.response.send_message("📅 Activité quotidienne")

    @app_commands.command(name="weekly_activity", description="Activité hebdomadaire")
    async def weekly_activity(self, interaction: discord.Interaction):
        await interaction.response.send_message("📅 Activité hebdomadaire")

    @app_commands.command(name="monthly_activity", description="Activité mensuelle")
    async def monthly_activity(self, interaction: discord.Interaction):
        await interaction.response.send_message("📅 Activité mensuelle")

    @app_commands.command(name="peak_hours", description="Heures de pointe")
    async def peak_hours(self, interaction: discord.Interaction):
        await interaction.response.send_message("⏰ Heures de pointe")

    @app_commands.command(name="bot_usage", description="Utilisation du bot")
    async def bot_usage(self, interaction: discord.Interaction):
        await interaction.response.send_message("🤖 Utilisation du bot")

    @app_commands.command(name="command_stats", description="Stats des commandes")
    async def command_stats(self, interaction: discord.Interaction):
        await interaction.response.send_message("⚙️ Statistiques des commandes")

    @app_commands.command(name="user_commands", description="Commandes d'un utilisateur")
    async def user_commands(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"⚙️ Commandes de {membre.mention}")

    @app_commands.command(name="invite_stats", description="Stats d'invitations")
    async def invite_stats(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("🔗 Statistiques d'invitations")

    @app_commands.command(name="reaction_stats", description="Stats de réactions")
    async def reaction_stats(self, interaction: discord.Interaction):
        await interaction.response.send_message("❤️ Statistiques de réactions")

    @app_commands.command(name="mention_stats", description="Stats de mentions")
    async def mention_stats(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("@️ Statistiques de mentions")

    @app_commands.command(name="attachment_stats", description="Stats de fichiers")
    async def attachment_stats(self, interaction: discord.Interaction):
        await interaction.response.send_message("📎 Statistiques de fichiers")

async def setup(bot):
    await bot.add_cog(StatisticsCog(bot))
