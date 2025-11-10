"""
Module de divertissement avec de nombreuses commandes fun
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from utils.logger import bot_logger

class EntertainmentCog(commands.Cog):
    """Commandes de divertissement"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        bot_logger.logger.info("Module divertissement chargé")

    @app_commands.command(name="meme_random", description="Meme aléatoire")
    async def meme_random(self, interaction: discord.Interaction):
        await interaction.response.send_message("😂 Meme aléatoire")

    @app_commands.command(name="cat", description="Image de chat")
    async def cat(self, interaction: discord.Interaction):
        await interaction.response.send_message("🐱 Chat mignon")

    @app_commands.command(name="dog", description="Image de chien")
    async def dog(self, interaction: discord.Interaction):
        await interaction.response.send_message("🐕 Chien mignon")

    @app_commands.command(name="fox", description="Image de renard")
    async def fox(self, interaction: discord.Interaction):
        await interaction.response.send_message("🦊 Renard mignon")

    @app_commands.command(name="bird", description="Image d'oiseau")
    async def bird(self, interaction: discord.Interaction):
        await interaction.response.send_message("🐦 Oiseau")

    @app_commands.command(name="panda", description="Image de panda")
    async def panda(self, interaction: discord.Interaction):
        await interaction.response.send_message("🐼 Panda")

    @app_commands.command(name="koala", description="Image de koala")
    async def koala(self, interaction: discord.Interaction):
        await interaction.response.send_message("🐨 Koala")

    @app_commands.command(name="duck", description="Image de canard")
    async def duck(self, interaction: discord.Interaction):
        await interaction.response.send_message("🦆 Canard")

    @app_commands.command(name="bunny", description="Image de lapin")
    async def bunny(self, interaction: discord.Interaction):
        await interaction.response.send_message("🐰 Lapin")

    @app_commands.command(name="otter", description="Image de loutre")
    async def otter(self, interaction: discord.Interaction):
        await interaction.response.send_message("🦦 Loutre")

    @app_commands.command(name="shiba", description="Image de Shiba Inu")
    async def shiba(self, interaction: discord.Interaction):
        await interaction.response.send_message("🐕 Shiba Inu")

    @app_commands.command(name="seal", description="Image de phoque")
    async def seal(self, interaction: discord.Interaction):
        await interaction.response.send_message("🦭 Phoque")

    @app_commands.command(name="capybara", description="Image de capybara")
    async def capybara(self, interaction: discord.Interaction):
        await interaction.response.send_message("🦫 Capybara")

    @app_commands.command(name="axolotl", description="Image d'axolotl")
    async def axolotl(self, interaction: discord.Interaction):
        await interaction.response.send_message("🦎 Axolotl")

    @app_commands.command(name="raccoon", description="Image de raton-laveur")
    async def raccoon(self, interaction: discord.Interaction):
        await interaction.response.send_message("🦝 Raton-laveur")

    @app_commands.command(name="wholesome", description="Image wholesome")
    async def wholesome(self, interaction: discord.Interaction):
        await interaction.response.send_message("🥰 Image wholesome")

    @app_commands.command(name="cursed", description="Image cursed")
    async def cursed(self, interaction: discord.Interaction):
        await interaction.response.send_message("😱 Image cursed")

    @app_commands.command(name="blursed", description="Image blursed")
    async def blursed(self, interaction: discord.Interaction):
        await interaction.response.send_message("🤨 Image blursed")

    @app_commands.command(name="aesthetic", description="Image aesthetic")
    async def aesthetic(self, interaction: discord.Interaction):
        await interaction.response.send_message("✨ Image aesthetic")

    @app_commands.command(name="vibe", description="Vibe check")
    async def vibe(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("✨ Vibe check")

    @app_commands.command(name="simp", description="Calcul de simpitude")
    async def simp(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("💝 Niveau de simp")

    @app_commands.command(name="chad", description="Calcul de chad")
    async def chad(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("💪 Niveau de chad")

    @app_commands.command(name="cringe", description="Niveau de cringe")
    async def cringe(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("😬 Niveau de cringe")

    @app_commands.command(name="based", description="Niveau de based")
    async def based(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("😎 Niveau de based")

    @app_commands.command(name="sus", description="Niveau de sus")
    async def sus(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("🤨 Niveau de sus")

    @app_commands.command(name="ratio", description="Ratio quelqu'un")
    async def ratio(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"📊 Ratio {membre.mention}")

    @app_commands.command(name="pp", description="Mesure de pp")
    async def pp(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("📏 Taille de pp")

    @app_commands.command(name="iq", description="Test de QI")
    async def iq(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("🧠 Niveau de QI")

    @app_commands.command(name="gay", description="Niveau de gay")
    async def gay(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("🏳️‍🌈 Niveau de gay")

    @app_commands.command(name="furry", description="Niveau de furry")
    async def furry(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("🦊 Niveau de furry")

    @app_commands.command(name="weeb", description="Niveau de weeb")
    async def weeb(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("🇯🇵 Niveau de weeb")

    @app_commands.command(name="uwu", description="UwU-fie un texte")
    async def uwu(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message(f"UwU {texte}")

    @app_commands.command(name="owo", description="OwO-fie un texte")
    async def owo(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message(f"OwO {texte}")

    @app_commands.command(name="mock", description="mOcK uN tExTe")
    async def mock(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message("🙃 Texte mocké")

    @app_commands.command(name="clap", description="👏 Texte 👏 avec 👏 clap")
    async def clap(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message("👏 Texte 👏 avec 👏 clap")

    @app_commands.command(name="emojify", description="Emojifie un texte")
    async def emojify(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message("😀 Texte emojifié")

    @app_commands.command(name="fancy", description="Texte fancy")
    async def fancy(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message("✨ 𝓣𝓮𝔁𝓽𝓮 𝓯𝓪𝓷𝓬𝔂")

    @app_commands.command(name="vapor", description="Texte vaporwave")
    async def vapor(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message("🌊 ｔｅｘｔｅ　ｖａｐｏｒｗａｖｅ")

    @app_commands.command(name="regional", description="Texte en emojis régionaux")
    async def regional(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message("🔤 Emojis régionaux")

    @app_commands.command(name="spoiler", description="Spoilerise un texte")
    async def spoiler(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message(f"||{texte}||")

    @app_commands.command(name="quote_format", description="Formate en citation")
    async def quote_format(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message(f"> {texte}")

    @app_commands.command(name="typewriter", description="Effet machine à écrire")
    async def typewriter(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message("⌨️ Effet machine à écrire")

    @app_commands.command(name="zalgo", description="T̴e̸x̷t̶e̵ ̶z̸a̴l̷g̶o̵")
    async def zalgo(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message("👹 Texte zalgo")

    @app_commands.command(name="aesthetic_text", description="Texte aesthetic")
    async def aesthetic_text(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message("✨ ａｅｓｔｈｅｔｉｃ")

    @app_commands.command(name="smallcaps", description="ᴛᴇxᴛᴇ ᴇɴ ᴘᴇᴛɪᴛᴇs ᴍᴀᴊᴜsᴄᴜʟᴇs")
    async def smallcaps(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message("ᴛᴇxᴛᴇ")

    @app_commands.command(name="superscript", description="ᵗᵉˣᵗᵉ ᵉⁿ ᵉˣᵖᵒˢᵃⁿᵗ")
    async def superscript(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message("ᵗᵉˣᵗᵉ")

    @app_commands.command(name="subscript", description="ₜₑₓₜₑ ₑₙ ᵢₙdᵢcₑ")
    async def subscript(self, interaction: discord.Interaction, texte: str):
        await interaction.response.send_message("ₜₑₓₜₑ")

async def setup(bot):
    await bot.add_cog(EntertainmentCog(bot))
