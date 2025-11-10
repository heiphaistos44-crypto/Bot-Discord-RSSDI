"""
Système de niveaux avancé
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from utils.logger import bot_logger

class LevelingCog(commands.Cog):
    """Système de niveaux"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        bot_logger.logger.info("Module leveling chargé")

    @app_commands.command(name="level", description="Ton niveau")
    async def level(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("⭐ Niveau actuel")

    @app_commands.command(name="rank", description="Ton rang")
    async def rank(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("📊 Carte de rang")

    @app_commands.command(name="xp", description="Ton XP")
    async def xp(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("✨ Expérience")

    @app_commands.command(name="leaderboard_xp", description="Classement XP")
    async def leaderboard_xp(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏆 Top XP")

    @app_commands.command(name="leaderboard_level", description="Classement niveaux")
    async def leaderboard_level(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏆 Top niveaux")

    @app_commands.command(name="setlevel", description="Définit un niveau")
    @app_commands.checks.has_permissions(administrator=True)
    async def setlevel(self, interaction: discord.Interaction, membre: discord.Member, niveau: int):
        await interaction.response.send_message(f"⭐ Niveau de {membre.mention}: {niveau}")

    @app_commands.command(name="addxp", description="Ajoute de l'XP")
    @app_commands.checks.has_permissions(administrator=True)
    async def addxp(self, interaction: discord.Interaction, membre: discord.Member, xp: int):
        await interaction.response.send_message(f"✨ +{xp} XP pour {membre.mention}")

    @app_commands.command(name="removexp", description="Retire de l'XP")
    @app_commands.checks.has_permissions(administrator=True)
    async def removexp(self, interaction: discord.Interaction, membre: discord.Member, xp: int):
        await interaction.response.send_message(f"✨ -{xp} XP pour {membre.mention}")

    @app_commands.command(name="resetxp", description="Remet l'XP à zéro")
    @app_commands.checks.has_permissions(administrator=True)
    async def resetxp(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"🔄 XP de {membre.mention} réinitialisé")

    @app_commands.command(name="levelroles", description="Rôles de niveau")
    async def levelroles(self, interaction: discord.Interaction):
        await interaction.response.send_message("🎭 Rôles de niveau")

    @app_commands.command(name="levelrole_add", description="Ajoute un rôle de niveau")
    @app_commands.checks.has_permissions(administrator=True)
    async def levelrole_add(self, interaction: discord.Interaction, niveau: int, role: discord.Role):
        await interaction.response.send_message(f"🎁 Niveau {niveau} → {role.mention}")

    @app_commands.command(name="levelrole_remove", description="Retire un rôle de niveau")
    @app_commands.checks.has_permissions(administrator=True)
    async def levelrole_remove(self, interaction: discord.Interaction, niveau: int):
        await interaction.response.send_message(f"❌ Rôle niveau {niveau} retiré")

    @app_commands.command(name="xpmultiplier", description="Multiplie l'XP d'un rôle")
    @app_commands.checks.has_permissions(administrator=True)
    async def xpmultiplier(self, interaction: discord.Interaction, role: discord.Role, multiplicateur: float):
        await interaction.response.send_message(f"⚡ {role.mention}: x{multiplicateur} XP")

    @app_commands.command(name="levelup_message", description="Message de montée de niveau")
    @app_commands.checks.has_permissions(administrator=True)
    async def levelup_message(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message(f"📝 Message configuré")

    @app_commands.command(name="levelup_channel", description="Salon de montées de niveau")
    @app_commands.checks.has_permissions(administrator=True)
    async def levelup_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.send_message(f"📢 Salon: {channel.mention}")

    @app_commands.command(name="ignorexp_channel", description="Salon sans XP")
    @app_commands.checks.has_permissions(administrator=True)
    async def ignorexp_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.send_message(f"🚫 Pas d'XP dans {channel.mention}")

    @app_commands.command(name="ignorexp_role", description="Rôle sans XP")
    @app_commands.checks.has_permissions(administrator=True)
    async def ignorexp_role(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f"🚫 Pas d'XP pour {role.mention}")

    @app_commands.command(name="xp_cooldown", description="Cooldown de gain d'XP")
    @app_commands.checks.has_permissions(administrator=True)
    async def xp_cooldown(self, interaction: discord.Interaction, secondes: int):
        await interaction.response.send_message(f"⏱️ Cooldown: {secondes}s")

    @app_commands.command(name="prestige", description="Prestige (reset pour bonus)")
    async def prestige(self, interaction: discord.Interaction):
        await interaction.response.send_message("✨ Prestige!")

    @app_commands.command(name="prestige_rewards", description="Récompenses de prestige")
    async def prestige_rewards(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏆 Récompenses de prestige")

async def setup(bot):
    await bot.add_cog(LevelingCog(bot))
