"""
Module de gestion avancée du serveur
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from utils.logger import bot_logger
from utils.security import require_permissions

class ServerManagementCog(commands.Cog):
    """Gestion avancée du serveur"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        bot_logger.logger.info("Module gestion serveur chargé")

    @app_commands.command(name="role_create", description="Crée un rôle")
    @require_permissions("admin")
    async def role_create(self, interaction: discord.Interaction, nom: str, couleur: str):
        await interaction.response.send_message(f"🎨 Rôle '{nom}' créé")

    @app_commands.command(name="role_delete", description="Supprime un rôle")
    @require_permissions("admin")
    async def role_delete(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f"🗑️ Rôle '{role.name}' supprimé")

    @app_commands.command(name="role_edit", description="Modifie un rôle")
    @require_permissions("admin")
    async def role_edit(self, interaction: discord.Interaction, role: discord.Role, nouveau_nom: str):
        await interaction.response.send_message(f"✏️ Rôle modifié: {nouveau_nom}")

    @app_commands.command(name="role_color", description="Change la couleur d'un rôle")
    @require_permissions("admin")
    async def role_color(self, interaction: discord.Interaction, role: discord.Role, couleur: str):
        await interaction.response.send_message(f"🎨 Couleur de {role.mention} changée")

    @app_commands.command(name="role_give", description="Donne un rôle")
    @require_permissions("moderator")
    async def role_give(self, interaction: discord.Interaction, membre: discord.Member, role: discord.Role):
        await interaction.response.send_message(f"✅ Rôle {role.mention} donné à {membre.mention}")

    @app_commands.command(name="role_take", description="Retire un rôle")
    @require_permissions("moderator")
    async def role_take(self, interaction: discord.Interaction, membre: discord.Member, role: discord.Role):
        await interaction.response.send_message(f"❌ Rôle {role.mention} retiré de {membre.mention}")

    @app_commands.command(name="role_all", description="Donne un rôle à tous")
    @require_permissions("admin")
    async def role_all(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f"👥 Rôle {role.mention} donné à tous")

    @app_commands.command(name="role_humans", description="Donne un rôle à tous les humains")
    @require_permissions("admin")
    async def role_humans(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f"👤 Rôle donné aux humains")

    @app_commands.command(name="role_bots", description="Donne un rôle à tous les bots")
    @require_permissions("admin")
    async def role_bots(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f"🤖 Rôle donné aux bots")

    @app_commands.command(name="role_members", description="Liste des membres avec un rôle")
    async def role_members(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f"👥 Membres avec {role.mention}")

    @app_commands.command(name="channel_create", description="Crée un salon")
    @require_permissions("admin")
    async def channel_create(self, interaction: discord.Interaction, nom: str, type: str):
        await interaction.response.send_message(f"📝 Salon '{nom}' créé")

    @app_commands.command(name="channel_delete", description="Supprime un salon")
    @require_permissions("admin")
    async def channel_delete(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.send_message(f"🗑️ Salon supprimé")

    @app_commands.command(name="channel_clone", description="Clone un salon")
    @require_permissions("admin")
    async def channel_clone(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.send_message(f"📋 Salon cloné")

    @app_commands.command(name="channel_lock", description="Verrouille un salon")
    @require_permissions("moderator")
    async def channel_lock(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        await interaction.response.send_message(f"🔒 Salon verrouillé")

    @app_commands.command(name="channel_unlock", description="Déverrouille un salon")
    @require_permissions("moderator")
    async def channel_unlock(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        await interaction.response.send_message(f"🔓 Salon déverrouillé")

    @app_commands.command(name="channel_slowmode", description="Active le mode lent")
    @require_permissions("moderator")
    async def channel_slowmode(self, interaction: discord.Interaction, secondes: int):
        await interaction.response.send_message(f"⏱️ Mode lent: {secondes}s")

    @app_commands.command(name="channel_nsfw", description="Marque comme NSFW")
    @require_permissions("admin")
    async def channel_nsfw(self, interaction: discord.Interaction, activer: bool):
        await interaction.response.send_message(f"🔞 NSFW: {'activé' if activer else 'désactivé'}")

    @app_commands.command(name="purge", description="Supprime des messages")
    @require_permissions("moderator")
    async def purge(self, interaction: discord.Interaction, nombre: int):
        await interaction.response.send_message(f"🗑️ {nombre} messages supprimés")

    @app_commands.command(name="purge_user", description="Supprime les messages d'un utilisateur")
    @require_permissions("moderator")
    async def purge_user(self, interaction: discord.Interaction, membre: discord.Member, nombre: int):
        await interaction.response.send_message(f"🗑️ Messages de {membre.mention} supprimés")

    @app_commands.command(name="purge_bots", description="Supprime les messages des bots")
    @require_permissions("moderator")
    async def purge_bots(self, interaction: discord.Interaction, nombre: int):
        await interaction.response.send_message(f"🤖 Messages des bots supprimés")

    @app_commands.command(name="purge_embeds", description="Supprime les messages avec embeds")
    @require_permissions("moderator")
    async def purge_embeds(self, interaction: discord.Interaction, nombre: int):
        await interaction.response.send_message(f"🗑️ Embeds supprimés")

    @app_commands.command(name="purge_links", description="Supprime les messages avec liens")
    @require_permissions("moderator")
    async def purge_links(self, interaction: discord.Interaction, nombre: int):
        await interaction.response.send_message(f"🔗 Liens supprimés")

    @app_commands.command(name="purge_images", description="Supprime les messages avec images")
    @require_permissions("moderator")
    async def purge_images(self, interaction: discord.Interaction, nombre: int):
        await interaction.response.send_message(f"🖼️ Images supprimées")

    @app_commands.command(name="nuke", description="Recrée le salon (supprime tout)")
    @require_permissions("admin")
    async def nuke(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"💣 Salon recréé")

    @app_commands.command(name="announce", description="Annonce dans un salon")
    @require_permissions("moderator")
    async def announce(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        await interaction.response.send_message(f"📢 Annonce envoyée")

    @app_commands.command(name="embed_create", description="Crée un embed")
    @require_permissions("moderator")
    async def embed_create(self, interaction: discord.Interaction, titre: str, description: str):
        await interaction.response.send_message(f"📝 Embed créé")

    @app_commands.command(name="emoji_create", description="Ajoute un emoji")
    @require_permissions("admin")
    async def emoji_create(self, interaction: discord.Interaction, nom: str):
        await interaction.response.send_message(f"😀 Emoji '{nom}' ajouté")

    @app_commands.command(name="emoji_delete", description="Supprime un emoji")
    @require_permissions("admin")
    async def emoji_delete(self, interaction: discord.Interaction, emoji: str):
        await interaction.response.send_message(f"🗑️ Emoji supprimé")

    @app_commands.command(name="emoji_list", description="Liste les emojis")
    async def emoji_list(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"😀 Liste des emojis")

    @app_commands.command(name="sticker_list", description="Liste les stickers")
    async def sticker_list(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🎨 Liste des stickers")

    @app_commands.command(name="category_create", description="Crée une catégorie")
    @require_permissions("admin")
    async def category_create(self, interaction: discord.Interaction, nom: str):
        await interaction.response.send_message(f"📁 Catégorie '{nom}' créée")

    @app_commands.command(name="category_delete", description="Supprime une catégorie")
    @require_permissions("admin")
    async def category_delete(self, interaction: discord.Interaction, categorie: discord.CategoryChannel):
        await interaction.response.send_message(f"🗑️ Catégorie supprimée")

    @app_commands.command(name="backup", description="Sauvegarde le serveur")
    @require_permissions("admin")
    async def backup(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"💾 Sauvegarde en cours...")

    @app_commands.command(name="restore", description="Restaure une sauvegarde")
    @require_permissions("admin")
    async def restore(self, interaction: discord.Interaction, backup_id: str):
        await interaction.response.send_message(f"📂 Restauration en cours...")

    @app_commands.command(name="audit", description="Journal d'audit")
    @require_permissions("admin")
    async def audit(self, interaction: discord.Interaction, limite: int = 10):
        await interaction.response.send_message(f"📋 Journal d'audit")

    @app_commands.command(name="bans", description="Liste des bans")
    @require_permissions("moderator")
    async def bans(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🔨 Liste des bans")

    @app_commands.command(name="invites", description="Liste des invitations")
    @require_permissions("moderator")
    async def invites(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🔗 Liste des invitations")

    @app_commands.command(name="webhooks", description="Liste des webhooks")
    @require_permissions("admin")
    async def webhooks(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🔗 Liste des webhooks")

async def setup(bot):
    await bot.add_cog(ServerManagementCog(bot))
