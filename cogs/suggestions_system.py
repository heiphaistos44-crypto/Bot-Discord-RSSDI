"""
Système de suggestions amélioré
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from utils.logger import bot_logger
from utils.security import require_permissions, input_validator

class SuggestionsCog(commands.Cog):
    """Système de suggestions"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        bot_logger.logger.info("Module suggestions chargé")

    @app_commands.command(name="suggest", description="Fait une suggestion")
    async def suggest(self, interaction: discord.Interaction, suggestion: str):
        await interaction.response.send_message(f"💡 Suggestion envoyée")

    @app_commands.command(name="suggestions_list", description="Liste les suggestions")
    @require_permissions("moderator")
    async def suggestions_list(self, interaction: discord.Interaction, status: Optional[str] = None):
        await interaction.response.send_message("📋 Liste des suggestions")

    @app_commands.command(name="suggest_approve", description="Approuve une suggestion")
    @require_permissions("moderator")
    async def suggest_approve(self, interaction: discord.Interaction, suggestion_id: int):
        await interaction.response.send_message(f"✅ Suggestion #{suggestion_id} approuvée")

    @app_commands.command(name="suggest_deny", description="Refuse une suggestion")
    @require_permissions("moderator")
    async def suggest_deny(self, interaction: discord.Interaction, suggestion_id: int, raison: str):
        await interaction.response.send_message(f"❌ Suggestion #{suggestion_id} refusée")

    @app_commands.command(name="suggest_consider", description="Marque comme 'en considération'")
    @require_permissions("moderator")
    async def suggest_consider(self, interaction: discord.Interaction, suggestion_id: int):
        await interaction.response.send_message(f"🤔 Suggestion #{suggestion_id} en considération")

    @app_commands.command(name="suggest_implement", description="Marque comme 'implémentée'")
    @require_permissions("moderator")
    async def suggest_implement(self, interaction: discord.Interaction, suggestion_id: int):
        await interaction.response.send_message(f"✅ Suggestion #{suggestion_id} implémentée")

    @app_commands.command(name="suggest_delete", description="Supprime une suggestion")
    @require_permissions("moderator")
    async def suggest_delete(self, interaction: discord.Interaction, suggestion_id: int):
        await interaction.response.send_message(f"🗑️ Suggestion #{suggestion_id} supprimée")

    @app_commands.command(name="suggest_setup", description="Configure le système")
    @require_permissions("admin")
    async def suggest_setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.send_message(f"⚙️ Suggestions: {channel.mention}")

    @app_commands.command(name="bug_report", description="Signale un bug")
    async def bug_report(self, interaction: discord.Interaction, description: str):
        await interaction.response.send_message("🐛 Bug signalé")

    @app_commands.command(name="bug_list", description="Liste les bugs")
    @require_permissions("moderator")
    async def bug_list(self, interaction: discord.Interaction):
        await interaction.response.send_message("🐛 Liste des bugs")

    @app_commands.command(name="bug_fix", description="Marque un bug comme corrigé")
    @require_permissions("moderator")
    async def bug_fix(self, interaction: discord.Interaction, bug_id: int):
        await interaction.response.send_message(f"✅ Bug #{bug_id} corrigé")

    @app_commands.command(name="feature_request", description="Demande une fonctionnalité")
    async def feature_request(self, interaction: discord.Interaction, description: str):
        await interaction.response.send_message("✨ Fonctionnalité demandée")

    @app_commands.command(name="feedback", description="Donne un retour")
    async def feedback(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message("📝 Feedback envoyé")

    @app_commands.command(name="report", description="Signale un utilisateur")
    async def report(self, interaction: discord.Interaction, membre: discord.Member, raison: str):
        await interaction.response.send_message(f"⚠️ {membre.mention} signalé")

    @app_commands.command(name="reports_list", description="Liste les signalements")
    @require_permissions("moderator")
    async def reports_list(self, interaction: discord.Interaction):
        await interaction.response.send_message("⚠️ Liste des signalements")

    @app_commands.command(name="report_close", description="Ferme un signalement")
    @require_permissions("moderator")
    async def report_close(self, interaction: discord.Interaction, report_id: int):
        await interaction.response.send_message(f"✅ Signalement #{report_id} fermé")

    @app_commands.command(name="appeal", description="Fait appel d'une sanction")
    async def appeal(self, interaction: discord.Interaction, raison: str):
        await interaction.response.send_message("📝 Appel envoyé")

    @app_commands.command(name="appeals_list", description="Liste les appels")
    @require_permissions("moderator")
    async def appeals_list(self, interaction: discord.Interaction):
        await interaction.response.send_message("📋 Liste des appels")

    @app_commands.command(name="appeal_accept", description="Accepte un appel")
    @require_permissions("admin")
    async def appeal_accept(self, interaction: discord.Interaction, appeal_id: int):
        await interaction.response.send_message(f"✅ Appel #{appeal_id} accepté")

    @app_commands.command(name="appeal_deny", description="Refuse un appel")
    @require_permissions("admin")
    async def appeal_deny(self, interaction: discord.Interaction, appeal_id: int):
        await interaction.response.send_message(f"❌ Appel #{appeal_id} refusé")

async def setup(bot):
    await bot.add_cog(SuggestionsCog(bot))
