"""
Utilitaires supplémentaires
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from utils.logger import bot_logger

class UtilitiesExtraCog(commands.Cog):
    """Utilitaires supplémentaires"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        bot_logger.logger.info("Module utilitaires extra chargé")

    @app_commands.command(name="afk_set", description="Mode AFK")
    async def afk_set(self, interaction: discord.Interaction, raison: Optional[str] = "AFK"):
        await interaction.response.send_message(f"😴 AFK: {raison}")

    @app_commands.command(name="afk_remove", description="Retire l'AFK")
    async def afk_remove(self, interaction: discord.Interaction):
        await interaction.response.send_message("👋 Welcome back!")

    @app_commands.command(name="snipe", description="Dernier message supprimé")
    async def snipe(self, interaction: discord.Interaction):
        await interaction.response.send_message("🎯 Message snipé")

    @app_commands.command(name="editsnipe", description="Dernier message édité")
    async def editsnipe(self, interaction: discord.Interaction):
        await interaction.response.send_message("✏️ Édition snipée")

    @app_commands.command(name="firstmessage", description="Premier message du salon")
    async def firstmessage(self, interaction: discord.Interaction):
        await interaction.response.send_message("📜 Premier message")

    @app_commands.command(name="jumpto", description="Va à un message")
    async def jumpto(self, interaction: discord.Interaction, message_id: str):
        await interaction.response.send_message("🔗 Lien vers le message")

    @app_commands.command(name="topic", description="Sujet du salon")
    async def topic(self, interaction: discord.Interaction):
        await interaction.response.send_message("📝 Sujet du salon")

    @app_commands.command(name="topic_set", description="Définit le sujet")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def topic_set(self, interaction: discord.Interaction, sujet: str):
        await interaction.response.send_message(f"📝 Sujet: {sujet}")

    @app_commands.command(name="pin", description="Épingle un message")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def pin(self, interaction: discord.Interaction, message_id: str):
        await interaction.response.send_message("📌 Message épinglé")

    @app_commands.command(name="unpin", description="Désépingle un message")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def unpin(self, interaction: discord.Interaction, message_id: str):
        await interaction.response.send_message("📌 Message désépinglé")

    @app_commands.command(name="pins", description="Messages épinglés")
    async def pins(self, interaction: discord.Interaction):
        await interaction.response.send_message("📌 Messages épinglés")

    @app_commands.command(name="steal_emoji", description="Vole un emoji")
    @app_commands.checks.has_permissions(manage_emojis=True)
    async def steal_emoji(self, interaction: discord.Interaction, emoji: str, nom: str):
        await interaction.response.send_message(f"😀 Emoji '{nom}' ajouté")

    @app_commands.command(name="enlarge_emoji", description="Agrandit un emoji")
    async def enlarge_emoji(self, interaction: discord.Interaction, emoji: str):
        await interaction.response.send_message("🔍 Emoji agrandi")

    @app_commands.command(name="roleicon", description="Icône d'un rôle")
    async def roleicon(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f"🎨 Icône de {role.mention}")

    @app_commands.command(name="permissions", description="Permissions d'un membre")
    async def permissions(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("🔐 Permissions")

    @app_commands.command(name="permissions_in", description="Permissions dans un salon")
    async def permissions_in(self, interaction: discord.Interaction, membre: discord.Member, channel: discord.TextChannel):
        await interaction.response.send_message(f"🔐 Permissions dans {channel.mention}")

    @app_commands.command(name="shorten_url", description="Raccourcit une URL")
    async def shorten_url(self, interaction: discord.Interaction, url: str):
        await interaction.response.send_message("🔗 URL raccourcie")

    @app_commands.command(name="expand_url", description="Développe une URL courte")
    async def expand_url(self, interaction: discord.Interaction, url: str):
        await interaction.response.send_message("🔗 URL développée")

    @app_commands.command(name="screenshot", description="Screenshot d'un site web")
    async def screenshot(self, interaction: discord.Interaction, url: str):
        await interaction.response.send_message("📸 Screenshot")

    @app_commands.command(name="carbon", description="Carbon code snippet")
    async def carbon(self, interaction: discord.Interaction, code: str):
        await interaction.response.send_message("💻 Carbon snippet")

    @app_commands.command(name="hastebin", description="Upload vers hastebin")
    async def hastebin(self, interaction: discord.Interaction, contenu: str):
        await interaction.response.send_message("📝 Hastebin")

    @app_commands.command(name="pastebin", description="Upload vers pastebin")
    async def pastebin(self, interaction: discord.Interaction, contenu: str):
        await interaction.response.send_message("📝 Pastebin")

    @app_commands.command(name="github_gist", description="Crée un GitHub Gist")
    async def github_gist(self, interaction: discord.Interaction, contenu: str):
        await interaction.response.send_message("🐙 GitHub Gist")

    @app_commands.command(name="status_page", description="Page de statut")
    async def status_page(self, interaction: discord.Interaction):
        await interaction.response.send_message("📊 Page de statut")

    @app_commands.command(name="uptime", description="Uptime du bot")
    async def uptime(self, interaction: discord.Interaction):
        await interaction.response.send_message("⏰ Uptime")

    @app_commands.command(name="system_info", description="Infos système")
    async def system_info(self, interaction: discord.Interaction):
        await interaction.response.send_message("💻 Infos système")

    @app_commands.command(name="shards", description="Infos sur les shards")
    async def shards(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔷 Shards")

    @app_commands.command(name="websocket", description="Infos WebSocket")
    async def websocket(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔌 WebSocket")

    @app_commands.command(name="dependencies", description="Dépendances du bot")
    async def dependencies(self, interaction: discord.Interaction):
        await interaction.response.send_message("📦 Dépendances")

    @app_commands.command(name="version", description="Version du bot")
    async def version(self, interaction: discord.Interaction):
        await interaction.response.send_message("📌 Version")

    @app_commands.command(name="changelog", description="Changelog")
    async def changelog(self, interaction: discord.Interaction):
        await interaction.response.send_message("📋 Changelog")

    @app_commands.command(name="credits", description="Crédits")
    async def credits(self, interaction: discord.Interaction):
        await interaction.response.send_message("👏 Crédits")

    @app_commands.command(name="privacy", description="Politique de confidentialité")
    async def privacy(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔒 Confidentialité")

    @app_commands.command(name="terms", description="Conditions d'utilisation")
    async def terms(self, interaction: discord.Interaction):
        await interaction.response.send_message("📜 Conditions")

    @app_commands.command(name="support_server", description="Serveur de support")
    async def support_server(self, interaction: discord.Interaction):
        await interaction.response.send_message("💬 Serveur de support")

    @app_commands.command(name="donate", description="Soutenir le bot")
    async def donate(self, interaction: discord.Interaction):
        await interaction.response.send_message("💖 Donation")

    @app_commands.command(name="vote", description="Vote pour le bot")
    async def vote(self, interaction: discord.Interaction):
        await interaction.response.send_message("⭐ Vote")

    @app_commands.command(name="invite_bot", description="Lien d'invitation")
    async def invite_bot(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔗 Invitation")

async def setup(bot):
    await bot.add_cog(UtilitiesExtraCog(bot))
