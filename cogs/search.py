"""
Module de recherche et APIs externes
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from utils.logger import bot_logger

class SearchCog(commands.Cog):
    """Commandes de recherche et API"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        bot_logger.logger.info("Module recherche chargé")

    @app_commands.command(name="wikipedia", description="Recherche sur Wikipedia")
    async def wikipedia(self, interaction: discord.Interaction, recherche: str, langue: str = "fr"):
        await interaction.response.send_message(f"📚 Recherche Wikipedia: {recherche}")

    @app_commands.command(name="google", description="Recherche Google")
    async def google(self, interaction: discord.Interaction, recherche: str):
        await interaction.response.send_message(f"🔍 Recherche Google: {recherche}")

    @app_commands.command(name="youtube", description="Recherche sur YouTube")
    async def youtube(self, interaction: discord.Interaction, recherche: str):
        await interaction.response.send_message(f"📺 Recherche YouTube: {recherche}")

    @app_commands.command(name="image_search", description="Recherche d'images")
    async def image_search(self, interaction: discord.Interaction, recherche: str):
        await interaction.response.send_message(f"🖼️ Recherche d'images: {recherche}")

    @app_commands.command(name="gif", description="Recherche de GIF")
    async def gif(self, interaction: discord.Interaction, recherche: str):
        await interaction.response.send_message(f"🎬 Recherche GIF: {recherche}")

    @app_commands.command(name="weather", description="Météo d'une ville")
    async def weather(self, interaction: discord.Interaction, ville: str):
        await interaction.response.send_message(f"🌤️ Météo de {ville}")

    @app_commands.command(name="forecast", description="Prévisions météo 5 jours")
    async def forecast(self, interaction: discord.Interaction, ville: str):
        await interaction.response.send_message(f"📅 Prévisions pour {ville}")

    @app_commands.command(name="crypto", description="Prix d'une crypto-monnaie")
    async def crypto(self, interaction: discord.Interaction, symbole: str):
        await interaction.response.send_message(f"₿ Prix de {symbole}")

    @app_commands.command(name="stock", description="Cours d'une action")
    async def stock(self, interaction: discord.Interaction, symbole: str):
        await interaction.response.send_message(f"📈 Cours de {symbole}")

    @app_commands.command(name="forex", description="Taux de change")
    async def forex(self, interaction: discord.Interaction, de: str, vers: str):
        await interaction.response.send_message(f"💱 Taux {de} → {vers}")

    @app_commands.command(name="news", description="Dernières actualités")
    async def news(self, interaction: discord.Interaction, sujet: Optional[str] = None):
        await interaction.response.send_message(f"📰 Actualités: {sujet or 'générales'}")

    @app_commands.command(name="reddit", description="Top posts Reddit")
    async def reddit(self, interaction: discord.Interaction, subreddit: str):
        await interaction.response.send_message(f"🤖 r/{subreddit}")

    @app_commands.command(name="github", description="Recherche sur GitHub")
    async def github(self, interaction: discord.Interaction, repository: str):
        await interaction.response.send_message(f"🐙 GitHub: {repository}")

    @app_commands.command(name="stackoverflow", description="Recherche StackOverflow")
    async def stackoverflow(self, interaction: discord.Interaction, recherche: str):
        await interaction.response.send_message(f"📚 StackOverflow: {recherche}")

    @app_commands.command(name="translate", description="Traduit un texte")
    async def translate(self, interaction: discord.Interaction, texte: str, vers: str = "en"):
        await interaction.response.send_message(f"🌐 Traduction vers {vers}")

    @app_commands.command(name="define", description="Définition d'un mot")
    async def define(self, interaction: discord.Interaction, mot: str):
        await interaction.response.send_message(f"📖 Définition de: {mot}")

    @app_commands.command(name="synonym", description="Synonymes d'un mot")
    async def synonym(self, interaction: discord.Interaction, mot: str):
        await interaction.response.send_message(f"📝 Synonymes de: {mot}")

    @app_commands.command(name="antonym", description="Antonymes d'un mot")
    async def antonym(self, interaction: discord.Interaction, mot: str):
        await interaction.response.send_message(f"📝 Antonymes de: {mot}")

    @app_commands.command(name="rhyme", description="Trouve des rimes")
    async def rhyme(self, interaction: discord.Interaction, mot: str):
        await interaction.response.send_message(f"🎵 Rimes avec: {mot}")

    @app_commands.command(name="imdb", description="Recherche sur IMDB")
    async def imdb(self, interaction: discord.Interaction, titre: str):
        await interaction.response.send_message(f"🎬 IMDB: {titre}")

    @app_commands.command(name="anime", description="Recherche d'anime")
    async def anime(self, interaction: discord.Interaction, titre: str):
        await interaction.response.send_message(f"📺 Anime: {titre}")

    @app_commands.command(name="manga", description="Recherche de manga")
    async def manga(self, interaction: discord.Interaction, titre: str):
        await interaction.response.send_message(f"📚 Manga: {titre}")

    @app_commands.command(name="pokemon", description="Info sur un Pokémon")
    async def pokemon(self, interaction: discord.Interaction, nom: str):
        await interaction.response.send_message(f"⚡ Pokémon: {nom}")

    @app_commands.command(name="cat_fact", description="Fait aléatoire sur les chats")
    async def cat_fact(self, interaction: discord.Interaction):
        await interaction.response.send_message("🐱 Fait sur les chats")

    @app_commands.command(name="dog_fact", description="Fait aléatoire sur les chiens")
    async def dog_fact(self, interaction: discord.Interaction):
        await interaction.response.send_message("🐕 Fait sur les chiens")

    @app_commands.command(name="joke", description="Blague aléatoire")
    async def joke(self, interaction: discord.Interaction):
        await interaction.response.send_message("😂 Blague du jour")

    @app_commands.command(name="dadjoke", description="Dad joke")
    async def dadjoke(self, interaction: discord.Interaction):
        await interaction.response.send_message("👨 Dad joke")

    @app_commands.command(name="quote_random", description="Citation aléatoire")
    async def quote_random(self, interaction: discord.Interaction):
        await interaction.response.send_message("💭 Citation inspirante")

    @app_commands.command(name="advice", description="Conseil aléatoire")
    async def advice(self, interaction: discord.Interaction):
        await interaction.response.send_message("💡 Conseil du jour")

    @app_commands.command(name="inspire", description="Citation inspirante")
    async def inspire(self, interaction: discord.Interaction):
        await interaction.response.send_message("✨ Citation inspirante")

    @app_commands.command(name="horoscope", description="Horoscope du jour")
    async def horoscope(self, interaction: discord.Interaction, signe: str):
        await interaction.response.send_message(f"🔮 Horoscope: {signe}")

    @app_commands.command(name="recipe", description="Recherche de recette")
    async def recipe(self, interaction: discord.Interaction, plat: str):
        await interaction.response.send_message(f"🍳 Recette de: {plat}")

    @app_commands.command(name="cocktail", description="Recette de cocktail")
    async def cocktail(self, interaction: discord.Interaction, nom: str):
        await interaction.response.send_message(f"🍹 Cocktail: {nom}")

    @app_commands.command(name="country", description="Info sur un pays")
    async def country(self, interaction: discord.Interaction, pays: str):
        await interaction.response.send_message(f"🌍 Info sur: {pays}")

    @app_commands.command(name="flag", description="Drapeau d'un pays")
    async def flag(self, interaction: discord.Interaction, pays: str):
        await interaction.response.send_message(f"🚩 Drapeau de: {pays}")

    @app_commands.command(name="capital", description="Capitale d'un pays")
    async def capital(self, interaction: discord.Interaction, pays: str):
        await interaction.response.send_message(f"🏛️ Capitale de: {pays}")

    @app_commands.command(name="population", description="Population d'un pays")
    async def population(self, interaction: discord.Interaction, pays: str):
        await interaction.response.send_message(f"👥 Population de: {pays}")

    @app_commands.command(name="timezone", description="Fuseau horaire")
    async def timezone(self, interaction: discord.Interaction, ville: str):
        await interaction.response.send_message(f"🕐 Fuseau de: {ville}")

    @app_commands.command(name="distance", description="Distance entre deux villes")
    async def distance(self, interaction: discord.Interaction, ville1: str, ville2: str):
        await interaction.response.send_message(f"📏 Distance {ville1} ↔ {ville2}")

async def setup(bot):
    await bot.add_cog(SearchCog(bot))
