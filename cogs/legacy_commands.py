"""
Cog contenant toutes les commandes de l'ancien système pour préserver les 51 commandes slash
"""
import os
import json
import random
import asyncio
import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import discord
from discord import app_commands
from discord.ext import commands

from config import Config
from database import db_manager
from utils.logger import bot_logger
from utils.security import require_permissions, rate_limit, input_validator

try:
    import feedparser
except ImportError:
    feedparser = None

class LegacyCommandsCog(commands.Cog):
    """Toutes les commandes de l'ancien système"""
    
    def __init__(self, bot):
        self.bot = bot
        self.quotes_store = {}
        self.suggestions_store = {}
        self.tags_store = {}
        self.auto_react_store = {}
        self.afk_store = {}
        
    async def cog_load(self):
        """Chargement du cog"""
        bot_logger.logger.info("Module commandes legacy chargé")
        await self._load_legacy_data()
        
    async def _load_legacy_data(self):
        """Charge les données legacy depuis data.json si présent"""
        try:
            data_path = Path("data.json")
            if data_path.exists():
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.quotes_store = data.get("quotes_store", {})
                self.suggestions_store = data.get("suggestions_store", {})
                self.tags_store = data.get("tags_store", {})
                self.auto_react_store = data.get("auto_react_store", {})
                self.afk_store = data.get("afk_store", {})
        except Exception as e:
            bot_logger.logger.warning(f"Erreur chargement données legacy: {e}")
    
    async def _save_legacy_data(self):
        """Sauvegarde les données legacy"""
        try:
            data = {
                "quotes_store": self.quotes_store,
                "suggestions_store": self.suggestions_store,
                "tags_store": self.tags_store,
                "auto_react_store": self.auto_react_store,
                "afk_store": self.afk_store,
            }
            with open("data.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            bot_logger.logger.error(f"Erreur sauvegarde données legacy: {e}")

    # === COMMANDES D'INFORMATION ===
    
    @app_commands.command(name="ping", description="Affiche la latence du bot")
    async def ping(self, interaction: discord.Interaction):
        """Ping du bot"""
        await interaction.response.send_message(f"🏓 Pong ! Latence: {round(self.bot.latency * 1000)}ms")

    @app_commands.command(name="botinfo", description="Informations sur le bot")
    async def botinfo(self, interaction: discord.Interaction):
        """Informations du bot"""
        embed = discord.Embed(title="🤖 Informations Bot", color=discord.Color.blurple())
        embed.add_field(name="Nom", value=str(self.bot.user), inline=True)
        embed.add_field(name="Serveurs", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Utilisateurs", value=len(self.bot.users), inline=True)
        embed.add_field(name="Latence", value=f"{round(self.bot.latency*1000)}ms", inline=True)
        embed.add_field(name="Version Discord.py", value=discord.__version__, inline=True)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serveur", description="Informations sur le serveur")
    async def serveur(self, interaction: discord.Interaction):
        """Informations du serveur"""
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ Impossible de récupérer les informations du serveur.")
            return
        embed = discord.Embed(title=f"📊 {guild.name}", color=discord.Color.blue())
        embed.add_field(name="👥 Membres", value=guild.member_count, inline=True)
        embed.add_field(name="👑 Propriétaire", value=str(guild.owner), inline=True)
        embed.add_field(name="📅 Créé le", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="🌍 Région", value=str(guild.preferred_locale), inline=True)
        embed.add_field(name="📝 Salons", value=len(guild.channels), inline=True)
        embed.add_field(name="🎭 Rôles", value=len(guild.roles), inline=True)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
            
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Informations sur un utilisateur")
    async def userinfo(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        """Informations d'un utilisateur"""
        user = membre or interaction.user
        
        embed = discord.Embed(title=f"👤 {user.display_name}", color=user.color)
        embed.add_field(name="🏷️ Nom", value=str(user), inline=True)
        embed.add_field(name="🆔 ID", value=user.id, inline=True)
        embed.add_field(name="📅 Créé le", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
        if isinstance(user, discord.Member) and user.joined_at:
            embed.add_field(name="📥 Rejoint le", value=user.joined_at.strftime("%d/%m/%Y"), inline=True)
        else:
            embed.add_field(name="📥 Rejoint le", value="N/A", inline=True)
        if isinstance(user, discord.Member):
            embed.add_field(name="🎭 Rôles", value=len(user.roles) - 1, inline=True)
        else:
            embed.add_field(name="🎭 Rôles", value="N/A", inline=True)
        embed.add_field(name="🤖 Bot", value="Oui" if user.bot else "Non", inline=True)
        
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
            
        await interaction.response.send_message(embed=embed)

    # === COMMANDES FUN ===
    
    @app_commands.command(name="de", description="Lance un dé")
    async def de(self, interaction: discord.Interaction, faces: int = 6):
        """Lance un dé"""
        if faces < 2:
            await interaction.response.send_message("❌ Le nombre de faces doit être >= 2.")
            return
        result = random.randint(1, faces)
        await interaction.response.send_message(f"🎲 Résultat du dé ({faces} faces): **{result}**")

    @app_commands.command(name="huitboule", description="Répond à une question comme une boule magique")
    async def huitboule(self, interaction: discord.Interaction, question: str):
        """Boule magique 8-ball"""
        responses = [
            "Oui, absolument ! 🌟", "Non, certainement pas ❌", "Peut-être... 🤔",
            "C'est certain ! ✅", "Jamais de la vie ! 🚫", "Demande plus tard ⏰",
            "Sans aucun doute ! 💯", "Très douteux 😬", "Concentre-toi et redemande 🧘",
            "Les perspectives sont bonnes ! 🌅", "Ne compte pas dessus 😕", "Oui ! 👍"
        ]
        response = random.choice(responses)
        
        embed = discord.Embed(title="🎱 Boule Magique", color=discord.Color.purple())
        embed.add_field(name="❓ Question", value=question, inline=False)
        embed.add_field(name="🔮 Réponse", value=response, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="choisir", description="Choisit un élément parmi une liste")
    async def choisir(self, interaction: discord.Interaction, options: str):
        """Choisit aléatoirement dans une liste"""
        items = [x.strip() for x in options.split(",") if x.strip()]
        if not items:
            await interaction.response.send_message("❌ Donne des options séparées par des virgules.")
            return
        choice = random.choice(items)
        await interaction.response.send_message(f"🎯 Mon choix: **{choice}**")

    @app_commands.command(name="blague", description="Raconte une blague geek")
    async def blague(self, interaction: discord.Interaction):
        """Blagues de développeur"""
        blagues = [
            "Pourquoi les programmeurs confondent Halloween et Noël ? Parce que OCT 31 == DEC 25.",
            "Un SQL entre dans un bar, il voit deux tables et dit : 'Puis-je vous joindre ?'",
            "Combien de programmeurs faut-il pour changer une ampoule ? Aucun, c'est un problème hardware.",
            "Comment appelle-t-on un développeur qui ne boit pas de café ? Endormi.",
            "Pourquoi les développeurs détestent la nature ? Trop de bugs.",
            "Que dit un développeur quand il se marie ? 'Oui, j'accepte les conditions d'utilisation.'",
            "Un bit rencontre un byte dans un bar. Le byte dit : 'Tu as l'air down.' Le bit répond : 'Non, juste un peu off.'"
        ]
        
        embed = discord.Embed(
            title="😄 Blague de Dev",
            description=random.choice(blagues),
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="taquiner", description="Envoie une petite vanne amicale")
    async def taquiner(self, interaction: discord.Interaction, membre: discord.Member):
        """Taquinerie amicale"""
        taquineries = [
            "Tu es comme un bug en prod : personne ne t'attendait, mais tout le monde doit faire avec 😆",
            "Si la paresse était un sport, tu serais champion olympique 🏆",
            "On devrait t'appeler Ctrl+Z, parce qu'on regrette toujours un peu quand tu arrives 😂",
            "Tu es la preuve vivante que même les processeurs ont besoin de temps morts 🖥️",
            "Ton humour est comme un code spaghetti : difficile à suivre mais toujours divertissant 🍝"
        ]
        phrase = random.choice(taquineries)
        await interaction.response.send_message(f"{membre.mention} {phrase}")

    # === SYSTÈME DE QUOTES ===
    
    @app_commands.command(name="quote_add", description="Ajoute une citation")
    async def quote_add(self, interaction: discord.Interaction, citation: str):
        """Ajoute une citation"""
        if not interaction.guild:
            await interaction.response.send_message(" Cette commande ne peut être utilisée que dans un serveur.")
            return
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.")
            return
        guild_id = str(interaction.guild.id)
        quotes = self.quotes_store.setdefault(guild_id, [])
        quotes.append(citation)
        await self._save_legacy_data()
        
        embed = discord.Embed(
            title=" Citation ajoutée",
            description=f"Citation #{len(quotes)} ajoutée avec succès !",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="quote", description="Affiche une citation aléatoire")
    async def quote(self, interaction: discord.Interaction):
        """Affiche une citation aléatoire"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.")
            return
            
        guild_id = str(interaction.guild.id)
        quotes = self.quotes_store.get(guild_id, [])
        
        if not quotes:
            await interaction.response.send_message("❌ Aucune citation enregistrée. Utilisez `/quote_add` pour en ajouter !")
            return
            
        quote_text = random.choice(quotes)
        
        embed = discord.Embed(
            title="📜 Citation Aléatoire",
            description=f"*\"{quote_text}\"*",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Citation {quotes.index(quote_text) + 1} sur {len(quotes)}")
        
        await interaction.response.send_message(embed=embed)

    # === SYSTÈME DE SUGGESTIONS ===
    
    @app_commands.command(name="suggest", description="Soumet une suggestion")
    async def suggest(self, interaction: discord.Interaction, contenu: str):
        """Soumet une suggestion"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.")
            return
            
        guild_id = str(interaction.guild.id)
        suggestions = self.suggestions_store.setdefault(guild_id, [])
        
        suggestion = {
            "author_id": interaction.user.id,
            "content": contenu,
            "status": "open",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        suggestions.append(suggestion)
        await self._save_legacy_data()
        
        embed = discord.Embed(
            title="💡 Suggestion soumise",
            description=f"Suggestion #{len(suggestions)} ajoutée avec succès !",
            color=discord.Color.green()
        )
        embed.add_field(name="Contenu", value=contenu, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="suggest_list", description="Liste les suggestions")
    async def suggest_list(self, interaction: discord.Interaction):
        """Liste toutes les suggestions"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.")
            return
            
        guild_id = str(interaction.guild.id)
        suggestions = self.suggestions_store.get(guild_id, [])
        
        if not suggestions:
            await interaction.response.send_message("❌ Aucune suggestion enregistrée.")
            return
            
        embed = discord.Embed(title="📋 Liste des suggestions", color=discord.Color.blue())
        
        for i, s in enumerate(suggestions[:10], 1):  # Limiter à 10 pour éviter les messages trop longs
            status_emoji = "🟢" if s["status"] == "open" else "🔴"
            embed.add_field(
                name=f"{status_emoji} Suggestion #{i}",
                value=f"{s['content'][:100]}{'...' if len(s['content']) > 100 else ''}\n*Par <@{s['author_id']}>*",
                inline=False
            )
            
        if len(suggestions) > 10:
            embed.set_footer(text=f"Affichage de 10 sur {len(suggestions)} suggestions")
            
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="suggest_close", description="Ferme une suggestion")
    @require_permissions("admin")
    async def suggest_close(self, interaction: discord.Interaction, index: int):
        """Ferme une suggestion"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.")
            return
            
        guild_id = str(interaction.guild.id)
        suggestions = self.suggestions_store.get(guild_id, [])
        
        if not (1 <= index <= len(suggestions)):
            await interaction.response.send_message("❌ Index de suggestion invalide.")
            return
            
        suggestions[index - 1]["status"] = "closed"
        await self._save_legacy_data()
        
        embed = discord.Embed(
            title="🔒 Suggestion fermée",
            description=f"Suggestion #{index} marquée comme fermée.",
            color=discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed)

    # === SYSTÈME DE TAGS ===
    
    @app_commands.command(name="tag_add", description="Ajoute un tag")
    async def tag_add(self, interaction: discord.Interaction, nom: str, contenu: str):
        """Ajoute un tag"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.")
            return
            
        guild_id = str(interaction.guild.id)
        tags = self.tags_store.setdefault(guild_id, {})
        tags[nom.lower()] = contenu
        await self._save_legacy_data()
        
        embed = discord.Embed(
            title="🏷️ Tag ajouté",
            description=f"Tag **{nom}** créé avec succès !",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tag", description="Affiche un tag")
    async def tag(self, interaction: discord.Interaction, nom: str):
        """Affiche un tag"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.")
            return
            
        guild_id = str(interaction.guild.id)
        tags = self.tags_store.get(guild_id, {})
        content = tags.get(nom.lower())
        
        if not content:
            await interaction.response.send_message(f"❌ Tag **{nom}** introuvable.")
            return
            
        embed = discord.Embed(
            title=f"🏷️ Tag: {nom}",
            description=content,
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tag_remove", description="Supprime un tag")
    @require_permissions("admin")
    async def tag_remove(self, interaction: discord.Interaction, nom: str):
        """Supprime un tag"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.")
            return
            
        guild_id = str(interaction.guild.id)
        tags = self.tags_store.get(guild_id, {})
        
        if nom.lower() not in tags:
            await interaction.response.send_message(f"❌ Tag **{nom}** introuvable.")
            return
            
        del tags[nom.lower()]
        await self._save_legacy_data()
        
        embed = discord.Embed(
            title="🗑️ Tag supprimé",
            description=f"Tag **{nom}** supprimé avec succès.",
            color=discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tags_list", description="Liste tous les tags")
    async def tags_list(self, interaction: discord.Interaction):
        """Liste tous les tags"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.")
            return
            
        guild_id = str(interaction.guild.id)
        tags = self.tags_store.get(guild_id, {})
        
        if not tags:
            await interaction.response.send_message("❌ Aucun tag enregistré.")
            return
            
        embed = discord.Embed(title="🏷️ Liste des tags", color=discord.Color.blue())
        
        tag_list = list(tags.keys())[:20]  # Limiter à 20 tags
        embed.description = ", ".join(f"`{tag}`" for tag in tag_list)
        
        if len(tags) > 20:
            embed.set_footer(text=f"Affichage de 20 sur {len(tags)} tags")
            
        await interaction.response.send_message(embed=embed)

    # === SYSTÈME AFK ===
    
    @app_commands.command(name="afk", description="Définit un statut AFK")
    async def afk(self, interaction: discord.Interaction, raison: str = "AFK"):
        """Définit le statut AFK"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.")
            return
            
        guild_id = str(interaction.guild.id)
        afk_users = self.afk_store.setdefault(guild_id, {})
        afk_users[str(interaction.user.id)] = raison
        await self._save_legacy_data()
        
        embed = discord.Embed(
            title="😴 Statut AFK activé",
            description=f"Tu es maintenant AFK: {raison}",
            color=discord.Color.orange()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="afk_remove", description="Retire le statut AFK")
    async def afk_remove(self, interaction: discord.Interaction):
        """Retire le statut AFK"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.")
            return
            
        guild_id = str(interaction.guild.id)
        afk_users = self.afk_store.get(guild_id, {})
        user_id = str(interaction.user.id)
        
        if user_id in afk_users:
            del afk_users[user_id]
            await self._save_legacy_data()
            
            embed = discord.Embed(
                title="✅ Statut AFK retiré",
                description="Tu n'es plus AFK.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Pas AFK",
                description="Tu n'étais pas AFK.",
                color=discord.Color.red()
            )
            
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # === UTILITAIRES ===
    
    @app_commands.command(name="sondage", description="Crée un sondage simple")
    async def sondage(self, interaction: discord.Interaction, question: str):
        """Crée un sondage simple"""
        embed = discord.Embed(
            title="📊 Sondage",
            description=question,
            color=discord.Color.orange()
        )
        embed.set_footer(text="Réagis avec 👍 ou 👎")
        
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction("👍")
        await message.add_reaction("👎")

    @app_commands.command(name="rappel", description="Crée un rappel")
    async def rappel(self, interaction: discord.Interaction, secondes: int, message: str):
        """Crée un rappel"""
        if secondes <= 0 or secondes > 86400:  # Max 24h
            await interaction.response.send_message("❌ Durée invalide (1s - 24h max).")
            return
            
        await interaction.response.send_message(f"⏳ Rappel programmé dans {secondes} secondes...")
        
        await asyncio.sleep(secondes)
        
        embed = discord.Embed(
            title="🔔 Rappel",
            description=message,
            color=discord.Color.blue()
        )
        
        try:
            await interaction.followup.send(f"{interaction.user.mention}", embed=embed)
        except:
            pass

    @app_commands.command(name="calcul", description="Calcule une expression mathématique")
    async def calcul(self, interaction: discord.Interaction, expression: str):
        """Calculateur simple et sécurisé"""
        try:
            # Sécuriser l'expression (enlever les caractères dangereux)
            allowed_chars = "0123456789+-*/()., "
            if not all(c in allowed_chars for c in expression):
                await interaction.response.send_message("❌ Expression invalide. Utilisez seulement des nombres et +, -, *, /, ().")
                return
                
            # Évaluer de manière sécurisée
            result = eval(expression, {"__builtins__": {}}, {})
            
            embed = discord.Embed(
                title="🔢 Calculateur",
                color=discord.Color.green()
            )
            embed.add_field(name="Expression", value=f"`{expression}`", inline=False)
            embed.add_field(name="Résultat", value=f"**{result}**", inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur de calcul: Expression invalide.")

    # === RSS (si feedparser disponible) ===
    
    @app_commands.command(name="rss_test", description="Teste un flux RSS")
    async def rss_test(self, interaction: discord.Interaction, url: str):
        """Teste un flux RSS"""
        if not feedparser:
            await interaction.response.send_message("❌ Module RSS non disponible.")
            return
            
        await interaction.response.defer()
        
        try:
            feed = feedparser.parse(url)
            
            if not feed.entries:
                await interaction.followup.send("❌ Aucun article trouvé ou URL invalide.")
                return
                
            embed = discord.Embed(
                title="📰 Test RSS",
                description=f"Flux RSS: {getattr(feed.feed, 'title', 'Sans titre')}",
                color=discord.Color.blue()
            )
            
            for i, entry in enumerate(feed.entries[:5], 1):
                title = (entry.get('title') or 'Sans titre')[:100]
                embed.add_field(
                    name=f"Article {i}",
                    value=f"[{title}]({entry.get('link', '#')})",
                    inline=False
                )
                
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors du test RSS: {e}")

    # === MODÉRATION SUPPLÉMENTAIRE ===
    
    @app_commands.command(name="slowmode", description="Définit le slowmode")
    @require_permissions("moderator")
    async def slowmode(self, interaction: discord.Interaction, secondes: int):
        """Définit le slowmode du salon"""
        if secondes < 0 or secondes > 21600:  # Max 6h
            await interaction.response.send_message("❌ Durée invalide (0-21600 secondes).")
            return
            
        if isinstance(interaction.channel, discord.TextChannel):
            await interaction.channel.edit(slowmode_delay=secondes)
        else:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un salon textuel.", ephemeral=True)
        
        embed = discord.Embed(
            title="⏱️ Slowmode modifié",
            description=f"Slowmode défini à {secondes} secondes.",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addrole", description="Ajoute un rôle à un membre")
    @require_permissions("moderator")
    async def addrole(self, interaction: discord.Interaction, membre: discord.Member, role: discord.Role):
        """Ajoute un rôle à un membre"""
        try:
            await membre.add_roles(role, reason=f"Ajout par {interaction.user}")
            
            embed = discord.Embed(
                title="✅ Rôle ajouté",
                description=f"Rôle {role.mention} ajouté à {membre.mention}",
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ Permissions insuffisantes.")
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}")

    @app_commands.command(name="removerole", description="Retire un rôle à un membre")
    @require_permissions("moderator")
    async def removerole(self, interaction: discord.Interaction, membre: discord.Member, role: discord.Role):
        """Retire un rôle à un membre"""
        try:
            await membre.remove_roles(role, reason=f"Retrait par {interaction.user}")
            
            embed = discord.Embed(
                title="✅ Rôle retiré",
                description=f"Rôle {role.mention} retiré de {membre.mention}",
                color=discord.Color.orange()
            )
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ Permissions insuffisantes.")
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}")

    @app_commands.command(name="invite", description="Crée une invitation")
    @require_permissions("moderator")
    async def invite(self, interaction: discord.Interaction, duree_heures: int = 1, max_utilisations: int = 1):
        """Crée une invitation"""
        try:
            if isinstance(interaction.channel, (discord.TextChannel, discord.VoiceChannel)):
                invite = await interaction.channel.create_invite(
                    max_age=duree_heures * 3600,
                    max_uses=max_utilisations,
                    unique=True
                )
            else:
                await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un salon textuel ou vocal.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🔗 Invitation créée",
                description=f"[Cliquez ici pour rejoindre]({invite.url})",
                color=discord.Color.green()
            )
            embed.add_field(name="Durée", value=f"{duree_heures}h", inline=True)
            embed.add_field(name="Utilisations max", value=max_utilisations, inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ Permissions insuffisantes.")
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}")

    # === ÉVÉNEMENTS ===
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Gestion des messages pour AFK et auto-react"""
        if message.author.bot or not message.guild:
            return
            
        guild_id = str(message.guild.id)
        
        # Vérifier AFK des mentions
        afk_users = self.afk_store.get(guild_id, {})
        for user in message.mentions:
            user_id = str(user.id)
            if user_id in afk_users:
                try:
                    embed = discord.Embed(
                        title="😴 Utilisateur AFK",
                        description=f"{user.mention} est AFK: {afk_users[user_id]}",
                        color=discord.Color.orange()
                    )
                    await message.channel.send(embed=embed, delete_after=10)
                except:
                    pass
        
        # Auto-réactions
        auto_reacts = self.auto_react_store.get(guild_id, {})
        if message.content:
            content_lower = message.content.lower()
            for trigger, emoji in auto_reacts.items():
                if trigger.lower() in content_lower:
                    try:
                        await message.add_reaction(emoji)
                    except:
                        pass

async def setup(bot):
    await bot.add_cog(LegacyCommandsCog(bot))