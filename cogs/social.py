"""
Module social et profils utilisateur
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from utils.logger import bot_logger

class SocialCog(commands.Cog):
    """Commandes sociales"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        bot_logger.logger.info("Module social chargé")

    @app_commands.command(name="profile", description="Ton profil")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.send_message("👤 Ton profil")

    @app_commands.command(name="rep", description="Donne une réputation")
    async def rep(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"⭐ +1 rep pour {membre.mention}")

    @app_commands.command(name="bio", description="Modifie ta bio")
    async def bio(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message(f"📝 Bio mise à jour")

    @app_commands.command(name="birthday", description="Définis ta date de naissance")
    async def birthday(self, interaction: discord.Interaction, jour: int, mois: int, annee: int):
        await interaction.response.send_message(f"🎂 Date enregistrée: {jour}/{mois}/{annee}")

    @app_commands.command(name="birthdays", description="Liste des anniversaires")
    async def birthdays(self, interaction: discord.Interaction):
        await interaction.response.send_message("🎂 Anniversaires à venir")

    @app_commands.command(name="marry", description="Demande en mariage")
    async def marry(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"💍 Demande en mariage à {membre.mention}")

    @app_commands.command(name="divorce", description="Divorce")
    async def divorce(self, interaction: discord.Interaction):
        await interaction.response.send_message("💔 Divorce effectué")

    @app_commands.command(name="couples", description="Liste des couples")
    async def couples(self, interaction: discord.Interaction):
        await interaction.response.send_message("💑 Liste des couples")

    @app_commands.command(name="hug", description="Fait un câlin")
    async def hug(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"🤗 {interaction.user.mention} fait un câlin à {membre.mention}")

    @app_commands.command(name="kiss", description="Embrasse quelqu'un")
    async def kiss(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"😘 {interaction.user.mention} embrasse {membre.mention}")

    @app_commands.command(name="slap", description="Gifle quelqu'un")
    async def slap(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"👋 {interaction.user.mention} gifle {membre.mention}")

    @app_commands.command(name="pat", description="Tapote la tête")
    async def pat(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"🤲 {interaction.user.mention} tapote {membre.mention}")

    @app_commands.command(name="poke", description="Poke quelqu'un")
    async def poke(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"👉 {interaction.user.mention} poke {membre.mention}")

    @app_commands.command(name="highfive", description="Tape-m'en cinq")
    async def highfive(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"🙌 {interaction.user.mention} et {membre.mention} se tapent dans la main")

    @app_commands.command(name="cuddle", description="Câlin doux")
    async def cuddle(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"🥰 {interaction.user.mention} fait un câlin doux à {membre.mention}")

    @app_commands.command(name="bonk", description="Bonk!")
    async def bonk(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"🔨 Bonk! {membre.mention}")

    @app_commands.command(name="bite", description="Mord quelqu'un")
    async def bite(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"😬 {interaction.user.mention} mord {membre.mention}")

    @app_commands.command(name="punch", description="Donne un coup de poing")
    async def punch(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"👊 {interaction.user.mention} frappe {membre.mention}")

    @app_commands.command(name="kick_rp", description="Donne un coup de pied (RP)")
    async def kick_rp(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"🦵 {interaction.user.mention} donne un coup de pied à {membre.mention}")

    @app_commands.command(name="wave", description="Fait un signe")
    async def wave(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"👋 {interaction.user.mention} fait signe à {membre.mention}")

    @app_commands.command(name="handshake", description="Serre la main")
    async def handshake(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"🤝 {interaction.user.mention} serre la main de {membre.mention}")

    @app_commands.command(name="fistbump", description="Check des poings")
    async def fistbump(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"🤜🤛 {interaction.user.mention} et {membre.mention} se checkent les poings")

    @app_commands.command(name="wink", description="Fait un clin d'œil")
    async def wink(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"😉 {interaction.user.mention} fait un clin d'œil à {membre.mention}")

    @app_commands.command(name="stare", description="Fixe du regard")
    async def stare(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"👀 {interaction.user.mention} fixe {membre.mention}")

    @app_commands.command(name="laugh", description="Rit")
    async def laugh(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"😂 {interaction.user.mention} rit")

    @app_commands.command(name="cry", description="Pleure")
    async def cry(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"😭 {interaction.user.mention} pleure")

    @app_commands.command(name="dance", description="Danse")
    async def dance(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"💃 {interaction.user.mention} danse")

    @app_commands.command(name="sleep", description="Dort")
    async def sleep(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"😴 {interaction.user.mention} dort")

    @app_commands.command(name="eat", description="Mange")
    async def eat(self, interaction: discord.Interaction, nourriture: str):
        await interaction.response.send_message(f"🍽️ {interaction.user.mention} mange {nourriture}")

async def setup(bot):
    await bot.add_cog(SocialCog(bot))
