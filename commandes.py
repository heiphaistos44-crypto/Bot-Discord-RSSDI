import os
import json
import random
import asyncio
import datetime
from pathlib import Path
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

# Initialisation du bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Chargement du token
try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError("Installe python-dotenv: pip install python-dotenv")

env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("Token Discord manquant.")

# Persistance des données
DATA_PATH = Path(__file__).resolve().parent / "data.json"
_data_lock = asyncio.Lock()

def _empty_data():
    return {
        "quotes": {},
        "warnings": {},
        "tags": {},
        "xp": {},
    }

def load_data():
    if not DATA_PATH.exists():
        return _empty_data()
    try:
        with DATA_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            base = _empty_data()
            base.update({k: data.get(k, base[k]) for k in base.keys()})
            return base
    except Exception:
        return _empty_data()

async def save_data(data):
    async with _data_lock:
        try:
            with DATA_PATH.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur sauvegarde data.json: {e}")

# Stores en mémoire
data_store = load_data()

# ============================
# Commandes d'information
# ============================
@bot.tree.command(name="help", description="Affiche la liste des commandes")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="Commandes disponibles", color=discord.Color.green())
    embed.add_field(name="/quote", value="Affiche une citation aléatoire", inline=False)
    embed.add_field(name="/warn", value="Avertit un membre", inline=False)
    embed.add_field(name="/clear", value="Supprime des messages", inline=False)
    embed.add_field(name="/tag", value="Affiche un tag", inline=False)
    embed.add_field(name="/xp", value="Affiche l'XP d'un membre", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="ping", description="Affiche la latence du bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong ! {round(bot.latency * 1000)} ms")

# ============================
# Commandes fun
# ============================
@bot.tree.command(name="quote", description="Affiche une citation aléatoire")
async def quote(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("Cette commande doit être utilisée dans un serveur.", ephemeral=True)
        return
    quotes = data_store["quotes"].get(str(interaction.guild.id), [])
    if not quotes:
        await interaction.response.send_message("Aucune citation enregistrée.")
    else:
        await interaction.response.send_message(random.choice(quotes))

@bot.tree.command(name="quote_add", description="Ajoute une citation")
async def quote_add(interaction: discord.Interaction, citation: str):
    if interaction.guild is None:
        await interaction.response.send_message("Cette commande doit être utilisée dans un serveur.", ephemeral=True)
        return
    gid = str(interaction.guild.id)
    quotes = data_store["quotes"].setdefault(gid, [])
    quotes.append(citation)
    await save_data(data_store)
    await interaction.response.send_message("Citation ajoutée.")

@bot.tree.command(name="de", description="Lance un dé")
async def de(interaction: discord.Interaction, faces: int = 6):
    if faces < 2:
        await interaction.response.send_message("Le nombre de faces doit être >= 2.")
        return
    await interaction.response.send_message(f"Résultat du dé ({faces}): {random.randint(1, faces)}")

# ============================
# Modération
# ============================
@bot.tree.command(name="warn", description="Avertit un membre")
@app_commands.checks.has_permissions(moderate_members=True)
async def warn(interaction: discord.Interaction, membre: discord.Member, raison: str = "Aucune raison"):
    if interaction.guild is None:
        await interaction.response.send_message("Cette commande doit être utilisée dans un serveur.", ephemeral=True)
        return
    gid = str(interaction.guild.id)
    warns = data_store["warnings"].setdefault(gid, {})
    warns.setdefault(str(membre.id), []).append(raison)
    await save_data(data_store)
    await interaction.response.send_message(f"{membre} averti. Raison: {raison}")

@bot.tree.command(name="warnings", description="Affiche les avertissements d'un membre")
async def warnings(interaction: discord.Interaction, membre: discord.Member):
    if interaction.guild is None:
        await interaction.response.send_message("Cette commande doit être utilisée dans un serveur.", ephemeral=True)
        return
    gid = str(interaction.guild.id)
    warns = data_store["warnings"].get(gid, {})
    lst = warns.get(str(membre.id), [])
    if not lst:
        await interaction.response.send_message(f"Aucun avertissement pour {membre}.")
    else:
        await interaction.response.send_message(f"Avertissements de {membre}:\n" + "\n".join(f"- {r}" for r in lst))

@bot.tree.command(name="clear", description="Supprime des messages dans ce salon")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, nombre: int = 5):
    if isinstance(interaction.channel, discord.TextChannel):
        deleted = await interaction.channel.purge(limit=nombre)
        await interaction.response.send_message(f"{len(deleted)} messages supprimés", ephemeral=True)
    else:
        await interaction.response.send_message("Cette commande ne peut être utilisée que dans un salon texte.", ephemeral=True)

# ============================
# Tags
# ============================
@bot.tree.command(name="tag_add", description="Ajoute un tag")
async def tag_add(interaction: discord.Interaction, nom: str, contenu: str):
    if interaction.guild is None:
        await interaction.response.send_message("Cette commande doit être utilisée dans un serveur.", ephemeral=True)
        return
    gid = str(interaction.guild.id)
    tags = data_store["tags"].setdefault(gid, {})
    tags[nom.lower()] = contenu
    await save_data(data_store)
    await interaction.response.send_message(f"Tag '{nom}' ajouté.")

@bot.tree.command(name="tag", description="Affiche un tag")
async def tag(interaction: discord.Interaction, nom: str):
    if interaction.guild is None:
        await interaction.response.send_message("Cette commande doit être utilisée dans un serveur.", ephemeral=True)
        return
    gid = str(interaction.guild.id)
    tags = data_store["tags"].get(gid, {})
    val = tags.get(nom.lower())
    await interaction.response.send_message(val if val else "Tag introuvable.")

@bot.tree.command(name="tags_list", description="Liste tous les tags")
async def tags_list(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("Cette commande doit être utilisée dans un serveur.", ephemeral=True)
        return
    gid = str(interaction.guild.id)
    tags = data_store["tags"].get(gid, {})
    if not tags:
        await interaction.response.send_message("Aucun tag.", ephemeral=True)
    else:
        lines = [f"- {k}: {v}" for k, v in tags.items()]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

# ============================
# XP
# ============================
@bot.tree.command(name="xp", description="Affiche l'XP d'un membre")
async def xp(interaction: discord.Interaction, membre: Optional[discord.Member] = None):
    if interaction.guild is None:
        await interaction.response.send_message("Cette commande doit être utilisée dans un serveur.", ephemeral=True)
        return
    gid = str(interaction.guild.id)
    cible = membre if membre is not None else interaction.user
    if cible is None:
        await interaction.response.send_message("Impossible de déterminer l'utilisateur.", ephemeral=True)
        return
    xp_map = data_store["xp"].setdefault(gid, {})
    await interaction.response.send_message(f"XP de {cible}: {xp_map.get(str(cible.id), 0)}")

@bot.event
async def on_message(message: discord.Message):
    if getattr(message.author, "bot", False) or not message.guild:
        return
    gid = str(message.guild.id)
    xp_map = data_store["xp"].setdefault(gid, {})
    xp_map[str(message.author.id)] = xp_map.get(str(message.author.id), 0) + 1
    await save_data(data_store)
    await bot.process_commands(message)

# ============================
# Lancement
# ============================
if __name__ == "__main__":
    if not DATA_PATH.exists():
        try:
            with DATA_PATH.open("w", encoding="utf-8") as f:
                json.dump(_empty_data(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur init data.json: {e}")
    bot.run(TOKEN)
