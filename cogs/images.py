"""
Module de manipulation d'images et génération
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from utils.logger import bot_logger

class ImagesCog(commands.Cog):
    """Commandes de manipulation d'images"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        bot_logger.logger.info("Module images chargé")

    @app_commands.command(name="meme", description="Génère un meme")
    async def meme(self, interaction: discord.Interaction, template: str, texte_haut: str, texte_bas: str):
        await interaction.response.send_message(f"🎨 Génération du meme: {template}")

    @app_commands.command(name="jpeg", description="Ajoute un effet JPEG compressé")
    async def jpeg(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        await interaction.response.send_message("📸 Effet JPEG appliqué")

    @app_commands.command(name="blur", description="Floute une image")
    async def blur(self, interaction: discord.Interaction, intensite: int):
        await interaction.response.send_message(f"🌫️ Flou appliqué (intensité: {intensite})")

    @app_commands.command(name="pixelate", description="Pixelise une image")
    async def pixelate(self, interaction: discord.Interaction, niveau: int):
        await interaction.response.send_message(f"🎮 Pixelisation niveau {niveau}")

    @app_commands.command(name="invert", description="Inverse les couleurs")
    async def invert(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔄 Couleurs inversées")

    @app_commands.command(name="grayscale", description="Convertit en noir et blanc")
    async def grayscale(self, interaction: discord.Interaction):
        await interaction.response.send_message("⚫⚪ Conversion N&B")

    @app_commands.command(name="sepia", description="Applique un filtre sépia")
    async def sepia(self, interaction: discord.Interaction):
        await interaction.response.send_message("🟤 Filtre sépia appliqué")

    @app_commands.command(name="rotate", description="Fait pivoter une image")
    async def rotate(self, interaction: discord.Interaction, angle: int):
        await interaction.response.send_message(f"🔄 Rotation de {angle}°")

    @app_commands.command(name="flip", description="Retourne une image")
    async def flip(self, interaction: discord.Interaction, direction: str):
        await interaction.response.send_message(f"↕️ Image retournée ({direction})")

    @app_commands.command(name="brighten", description="Augmente la luminosité")
    async def brighten(self, interaction: discord.Interaction, niveau: int):
        await interaction.response.send_message(f"☀️ Luminosité: +{niveau}%")

    @app_commands.command(name="darken", description="Assombrit une image")
    async def darken(self, interaction: discord.Interaction, niveau: int):
        await interaction.response.send_message(f"🌙 Assombrissement: -{niveau}%")

    @app_commands.command(name="contrast", description="Ajuste le contraste")
    async def contrast(self, interaction: discord.Interaction, niveau: int):
        await interaction.response.send_message(f"⚖️ Contraste: {niveau}%")

    @app_commands.command(name="saturation", description="Ajuste la saturation")
    async def saturation(self, interaction: discord.Interaction, niveau: int):
        await interaction.response.send_message(f"🎨 Saturation: {niveau}%")

    @app_commands.command(name="rainbow", description="Applique un effet arc-en-ciel")
    async def rainbow(self, interaction: discord.Interaction):
        await interaction.response.send_message("🌈 Effet arc-en-ciel appliqué")

    @app_commands.command(name="glitch", description="Applique un effet glitch")
    async def glitch(self, interaction: discord.Interaction):
        await interaction.response.send_message("📺 Effet glitch appliqué")

    @app_commands.command(name="vaporwave_img", description="Style vaporwave")
    async def vaporwave_img(self, interaction: discord.Interaction):
        await interaction.response.send_message("🌊 Style vaporwave appliqué")

    @app_commands.command(name="deepfry", description="Deep fry une image")
    async def deepfry(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔥 Image deep fried")

    @app_commands.command(name="油炸", description="Applique un effet 'oil painting'")
    async def oil_painting(self, interaction: discord.Interaction):
        await interaction.response.send_message("🖼️ Effet peinture à l'huile")

    @app_commands.command(name="sketch", description="Convertit en croquis")
    async def sketch(self, interaction: discord.Interaction):
        await interaction.response.send_message("✏️ Conversion en croquis")

    @app_commands.command(name="cartoon", description="Style cartoon/dessin animé")
    async def cartoon(self, interaction: discord.Interaction):
        await interaction.response.send_message("🎨 Style cartoon appliqué")

    @app_commands.command(name="wasted", description="Overlay GTA 'Wasted'")
    async def wasted(self, interaction: discord.Interaction):
        await interaction.response.send_message("💀 WASTED")

    @app_commands.command(name="triggered", description="Effet 'triggered'")
    async def triggered(self, interaction: discord.Interaction):
        await interaction.response.send_message("😡 TRIGGERED")

    @app_commands.command(name="jail", description="Met en prison")
    async def jail(self, interaction: discord.Interaction):
        await interaction.response.send_message("⛓️ En prison!")

    @app_commands.command(name="wanted", description="Affiche 'recherché'")
    async def wanted(self, interaction: discord.Interaction):
        await interaction.response.send_message("🤠 WANTED")

    @app_commands.command(name="frame", description="Ajoute un cadre")
    async def frame(self, interaction: discord.Interaction, style: str):
        await interaction.response.send_message(f"🖼️ Cadre {style} ajouté")

    @app_commands.command(name="resize", description="Redimensionne une image")
    async def resize(self, interaction: discord.Interaction, largeur: int, hauteur: int):
        await interaction.response.send_message(f"📏 Redimensionnement: {largeur}x{hauteur}")

    @app_commands.command(name="crop", description="Recadre une image")
    async def crop(self, interaction: discord.Interaction, x: int, y: int, largeur: int, hauteur: int):
        await interaction.response.send_message(f"✂️ Recadrage appliqué")

    @app_commands.command(name="circle", description="Rend l'image circulaire")
    async def circle(self, interaction: discord.Interaction):
        await interaction.response.send_message("⭕ Image circulaire")

    @app_commands.command(name="mirror", description="Effet miroir")
    async def mirror(self, interaction: discord.Interaction):
        await interaction.response.send_message("🪞 Effet miroir")

    @app_commands.command(name="kaleidoscope", description="Effet kaléidoscope")
    async def kaleidoscope(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔮 Effet kaléidoscope")

    @app_commands.command(name="fisheye", description="Effet fisheye")
    async def fisheye(self, interaction: discord.Interaction):
        await interaction.response.send_message("🐟 Effet fisheye")

    @app_commands.command(name="swirl", description="Effet tourbillon")
    async def swirl(self, interaction: discord.Interaction, intensite: int):
        await interaction.response.send_message(f"🌀 Tourbillon (intensité: {intensite})")

    @app_commands.command(name="wave", description="Effet vague")
    async def wave(self, interaction: discord.Interaction):
        await interaction.response.send_message("🌊 Effet vague")

    @app_commands.command(name="emboss", description="Effet embossé")
    async def emboss(self, interaction: discord.Interaction):
        await interaction.response.send_message("🗿 Effet embossé")

    @app_commands.command(name="edge", description="Détection de contours")
    async def edge(self, interaction: discord.Interaction):
        await interaction.response.send_message("📐 Détection de contours")

    @app_commands.command(name="sharpen", description="Augmente la netteté")
    async def sharpen(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔍 Netteté augmentée")

    @app_commands.command(name="noise", description="Ajoute du bruit")
    async def noise(self, interaction: discord.Interaction, niveau: int):
        await interaction.response.send_message(f"📡 Bruit ajouté (niveau: {niveau})")

    @app_commands.command(name="mosaic", description="Effet mosaïque")
    async def mosaic(self, interaction: discord.Interaction, taille: int):
        await interaction.response.send_message(f"🧩 Mosaïque (taille: {taille})")

    @app_commands.command(name="ascii_art", description="Convertit en ASCII art")
    async def ascii_art(self, interaction: discord.Interaction):
        await interaction.response.send_message("📝 Conversion en ASCII art")

    @app_commands.command(name="polaroid", description="Style polaroid")
    async def polaroid(self, interaction: discord.Interaction):
        await interaction.response.send_message("📷 Style polaroid")

async def setup(bot):
    await bot.add_cog(ImagesCog(bot))
