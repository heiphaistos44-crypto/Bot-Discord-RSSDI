"""
Système de modération avancé avec automod pour le bot Discord
"""
import re
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Union
import discord
from discord.ext import commands, tasks
from discord import app_commands

from config import Config
from database import db_manager
from utils.logger import bot_logger
from utils.security import (
    require_permissions, rate_limit, input_validator, 
    permission_manager, content_filter
)

class ModerationCog(commands.Cog):
    """Commandes et système de modération avancé"""
    
    def __init__(self, bot):
        self.bot = bot
        self.automod_enabled = {}  # guild_id: bool
        self.spam_tracker = {}     # user_id: [timestamps]
        self.muted_users = {}      # guild_id: {user_id: unmute_time}
        self.automod_cleanup.start()
        
    async def cog_load(self):
        """Chargement du cog"""
        bot_logger.logger.info("Module modération chargé")
        
    def cog_unload(self):
        """Déchargement du cog"""
        self.automod_cleanup.cancel()
    
    @tasks.loop(minutes=1)
    async def automod_cleanup(self):
        """Nettoie les données d'automod expirées"""
        now = datetime.now()
        
        # Nettoyer le tracker de spam
        for user_id in list(self.spam_tracker.keys()):
            cutoff = now - timedelta(minutes=1)
            self.spam_tracker[user_id] = [
                ts for ts in self.spam_tracker[user_id] if ts > cutoff
            ]
            if not self.spam_tracker[user_id]:
                del self.spam_tracker[user_id]
        
        # Démueter les utilisateurs automatiquement
        for guild_id in list(self.muted_users.keys()):
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue
                
            for user_id in list(self.muted_users[guild_id].keys()):
                unmute_time = self.muted_users[guild_id][user_id]
                if now >= unmute_time:
                    member = guild.get_member(user_id)
                    if member:
                        await self.unmute_member(member, reason="Timeout automatique")
                    del self.muted_users[guild_id][user_id]
    
    @automod_cleanup.before_loop
    async def before_automod_cleanup(self):
        await self.bot.wait_until_ready()
    
    # === COMMANDES DE MODÉRATION BASIQUES ===
    
    @app_commands.command(name="kick", description="Expulse un membre du serveur")
    @require_permissions("moderator")
    async def kick(self, interaction: discord.Interaction, membre: discord.Member, 
                   raison: str = "Aucune raison spécifiée"):
        """Expulse un membre"""
        if not permission_manager.can_moderate_user(interaction.user, membre):
            await interaction.response.send_message(
                "❌ Tu ne peux pas modérer ce membre (hiérarchie).", ephemeral=True
            )
            return
        
        try:
            raison = input_validator.sanitize_text(raison, 500)
            await membre.kick(reason=f"{raison} | Par {interaction.user}")
            
            embed = discord.Embed(
                title="👢 Membre expulsé",
                description=f"{membre.mention} a été expulsé",
                color=discord.Color.orange()
            )
            embed.add_field(name="Raison", value=raison, inline=False)
            embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            bot_logger.moderation_action(
                (interaction.guild.id if interaction.guild else 0),
                (interaction.user.id if interaction.user else 0),
                (membre.id if membre else 0), "KICK", raison
            )
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Je n'ai pas les permissions pour expulser ce membre.", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @app_commands.command(name="ban", description="Bannit un membre du serveur")
    @require_permissions("moderator")
    async def ban(self, interaction: discord.Interaction, membre: discord.Member, 
                  raison: str = "Aucune raison spécifiée", delete_days: int = 1):
        """Bannit un membre"""
        if not permission_manager.can_moderate_user(interaction.user, membre):
            await interaction.response.send_message(
                "❌ Tu ne peux pas modérer ce membre (hiérarchie).", ephemeral=True
            )
            return
        
        try:
            raison = input_validator.sanitize_text(raison, 500)
            delete_days = input_validator.validate_integer(delete_days, 0, 7)
            
            await membre.ban(
                reason=f"{raison} | Par {interaction.user}",
                delete_message_days=delete_days
            )
            
            embed = discord.Embed(
                title="🔨 Membre banni",
                description=f"{membre.mention} a été banni",
                color=discord.Color.red()
            )
            embed.add_field(name="Raison", value=raison, inline=False)
            embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
            embed.add_field(name="Messages supprimés", value=f"{delete_days} jour(s)", inline=True)
            
            await interaction.response.send_message(embed=embed)
            bot_logger.moderation_action(
                (interaction.guild.id if interaction.guild else 0),
                (interaction.user.id if interaction.user else 0),
                (membre.id if membre else 0), "BAN", raison
            )
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Je n'ai pas les permissions pour bannir ce membre.", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @app_commands.command(name="unban", description="Débannit un utilisateur par ID")
    @require_permissions("moderator")
    async def unban(self, interaction: discord.Interaction, user_id: str, 
                    raison: str = "Aucune raison spécifiée"):
        """Débannit un utilisateur"""
        try:
            user_id_str = input_validator.validate_discord_id(str(user_id))
            user_id = str(user_id_str)  # garder str pour la signature
            user_id_int = int(user_id_str)  # conversion pour les opérations
            raison = input_validator.sanitize_text(raison, 500)
            
            user = await self.bot.fetch_user(user_id)
            if interaction.guild:
                await interaction.guild.unban(user, reason=f"{raison} | Par {interaction.user}")
            
            embed = discord.Embed(
                title="✅ Utilisateur débanni",
                description=f"{user.mention} ({user}) a été débanni",
                color=discord.Color.green()
            )
            embed.add_field(name="Raison", value=raison, inline=False)
            embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            bot_logger.moderation_action(
                (interaction.guild.id if interaction.guild else 0),
                (interaction.user.id if interaction.user else 0),
                user_id_int, "UNBAN", raison
            )
            
        except discord.NotFound:
            await interaction.response.send_message("❌ Utilisateur introuvable ou pas banni.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @app_commands.command(name="timeout", description="Met un membre en timeout")
    @require_permissions("moderator")
    async def timeout(self, interaction: discord.Interaction, membre: discord.Member, 
                      duree: int, unite: str = "minutes", raison: str = "Aucune raison spécifiée"):
        """Met un membre en timeout"""
        if not permission_manager.can_moderate_user(interaction.user, membre):
            await interaction.response.send_message(
                "❌ Tu ne peux pas modérer ce membre (hiérarchie).", ephemeral=True
            )
            return
        
        try:
            duree = input_validator.validate_integer(duree, 1, 40320)  # Max 28 jours en minutes
            raison = input_validator.sanitize_text(raison, 500)
            
            # Convertir en timedelta
            if unite.lower() in ["s", "sec", "seconde", "secondes"]:
                delta = timedelta(seconds=duree)
            elif unite.lower() in ["m", "min", "minute", "minutes"]:
                delta = timedelta(minutes=duree)
            elif unite.lower() in ["h", "heure", "heures"]:
                delta = timedelta(hours=duree)
            elif unite.lower() in ["j", "jour", "jours"]:
                delta = timedelta(days=duree)
            else:
                await interaction.response.send_message(
                    "❌ Unité invalide. Utilise: s, m, h, j", ephemeral=True
                )
                return
            
            # Discord limite à 28 jours
            if delta > timedelta(days=28):
                await interaction.response.send_message(
                    "❌ La durée maximale est de 28 jours.", ephemeral=True
                )
                return
            
            until = datetime.utcnow() + delta
            await membre.timeout(until, reason=f"{raison} | Par {interaction.user}")
            
            embed = discord.Embed(
                title="⏰ Membre en timeout",
                description=f"{membre.mention} a été mis en timeout",
                color=discord.Color.orange()
            )
            embed.add_field(name="Durée", value=f"{duree} {unite}", inline=True)
            embed.add_field(name="Fin", value=f"<t:{int(until.timestamp())}:R>", inline=True)
            embed.add_field(name="Raison", value=raison, inline=False)
            embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            bot_logger.moderation_action(
                (interaction.guild.id if interaction.guild else 0),
                (interaction.user.id if interaction.user else 0),
                (membre.id if membre else 0), "TIMEOUT",
                f"{duree} {unite} - {raison}"
            )
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Je n'ai pas les permissions pour timeout ce membre.", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @app_commands.command(name="untimeout", description="Retire le timeout d'un membre")
    @require_permissions("moderator")
    async def untimeout(self, interaction: discord.Interaction, membre: discord.Member):
        """Retire le timeout d'un membre"""
        try:
            await membre.timeout(None, reason=f"Timeout retiré par {interaction.user}")
            
            embed = discord.Embed(
                title="✅ Timeout retiré",
                description=f"Le timeout de {membre.mention} a été retiré",
                color=discord.Color.green()
            )
            embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            bot_logger.moderation_action(
                (interaction.guild.id if interaction.guild else 0),
                (interaction.user.id if interaction.user else 0),
                (membre.id if membre else 0), "UNTIMEOUT", "Manuel"
            )
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    # === SYSTÈME D'AVERTISSEMENTS ===
    
    @app_commands.command(name="warn", description="Avertit un membre")
    @require_permissions("moderator")
    async def warn(self, interaction: discord.Interaction, membre: discord.Member, 
                   raison: str = "Aucune raison spécifiée"):
        """Avertit un membre"""
        if not permission_manager.can_moderate_user(interaction.user, membre):
            await interaction.response.send_message(
                "❌ Tu ne peux pas modérer ce membre (hiérarchie).", ephemeral=True
            )
            return
        
        try:
            raison = input_validator.sanitize_text(raison, 500)
            
            # Ajouter l'avertissement en base
            import aiosqlite
            async with aiosqlite.connect(db_manager.db_path) as db:
                await db.execute("""
                    INSERT INTO warnings (guild_id, user_id, moderator_id, reason, active)
                    VALUES (?, ?, ?, ?, TRUE)
                """, ((interaction.guild.id if interaction.guild else 0),
                      (membre.id if membre else 0),
                      (interaction.user.id if interaction.user else 0),
                      raison))
                await db.commit()
            
            # Compter les avertissements
            import aiosqlite
            async with aiosqlite.connect(db_manager.db_path) as db:
                async with db.execute("""
                    SELECT COUNT(*) FROM warnings
                    WHERE guild_id = ? AND user_id = ? AND active = TRUE
                """, ((interaction.guild.id if interaction.guild else 0),
                      (membre.id if membre else 0))) as cursor:
                    result = await cursor.fetchone()
                    warn_count = result[0] if result else 0
            
            embed = discord.Embed(
                title="⚠️ Avertissement",
                description=f"{membre.mention} a reçu un avertissement",
                color=discord.Color.yellow()
            )
            embed.add_field(name="Raison", value=raison, inline=False)
            embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
            embed.add_field(name="Total", value=f"{warn_count} avertissement(s)", inline=True)
            
            # Actions automatiques selon le nombre d'avertissements
            if warn_count >= Config.MAX_WARNINGS:
                try:
                    await membre.ban(reason="Trop d'avertissements")
                    embed.add_field(
                        name="⚡ Action automatique", 
                        value="Membre banni (trop d'avertissements)", 
                        inline=False
                    )
                except discord.Forbidden:
                    pass
            elif warn_count >= Config.MAX_WARNINGS - 1:
                try:
                    until = datetime.utcnow() + timedelta(hours=24)
                    await membre.timeout(until, reason="Avertissement final")
                    embed.add_field(
                        name="⚡ Action automatique", 
                        value="Timeout 24h (avertissement final)", 
                        inline=False
                    )
                except discord.Forbidden:
                    pass
            
            await interaction.response.send_message(embed=embed)
            bot_logger.moderation_action(
                (interaction.guild.id if interaction.guild else 0),
                (interaction.user.id if interaction.user else 0),
                (membre.id if membre else 0), "WARN", raison
            )
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @app_commands.command(name="warnings", description="Affiche les avertissements d'un membre")
    async def warnings(self, interaction: discord.Interaction, membre: discord.Member):
        """Affiche les avertissements d'un membre"""
        try:
            import aiosqlite
            async with aiosqlite.connect(db_manager.db_path) as db:
                async with db.execute("""
                    SELECT reason, moderator_id, created_at FROM warnings
                    WHERE guild_id = ? AND user_id = ? AND active = TRUE
                    ORDER BY created_at DESC
                """, ((interaction.guild.id if interaction.guild else 0),
                      (membre.id if membre else 0))) as cursor:
                    warnings = list(await cursor.fetchall())
            
            if not warnings:
                embed = discord.Embed(
                    title="✅ Aucun avertissement",
                    description=f"{membre.mention} n'a aucun avertissement actif",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title=f"⚠️ Avertissements de {membre.display_name}",
                    description=f"Total: {len(warnings)} avertissement(s)",
                    color=discord.Color.yellow()
                )
                
                for i, (reason, mod_id, created_at) in enumerate(warnings[:10], 1):
                    moderator = self.bot.get_user(mod_id)
                    mod_name = moderator.display_name if moderator else f"ID:{mod_id}"
                    
                    try:
                        timestamp = int(datetime.fromisoformat(created_at).timestamp())
                    except (ValueError, TypeError):
                        # Fallback si le format de date est invalide
                        timestamp = int(datetime.now().timestamp())
                    
                    embed.add_field(
                        name=f"#{i}",
                        value=f"**Raison:** {reason}\n**Par:** {mod_name}\n**Date:** <t:{timestamp}:d>",
                        inline=False
                    )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @app_commands.command(name="clearwarnings", description="Efface les avertissements d'un membre")
    @require_permissions("moderator")
    async def clearwarnings(self, interaction: discord.Interaction, membre: discord.Member):
        """Efface les avertissements d'un membre"""
        try:
            import aiosqlite
            async with aiosqlite.connect(db_manager.db_path) as db:
                await db.execute("""
                    UPDATE warnings SET active = FALSE
                    WHERE guild_id = ? AND user_id = ?
                """, ((interaction.guild.id if interaction.guild else 0),
                      (membre.id if membre else 0)))
                await db.commit()
            
            embed = discord.Embed(
                title="🗑️ Avertissements effacés",
                description=f"Tous les avertissements de {membre.mention} ont été effacés",
                color=discord.Color.green()
            )
            embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            bot_logger.moderation_action(
                (interaction.guild.id if interaction.guild else 0),
                (interaction.user.id if interaction.user else 0),
                (membre.id if membre else 0), "CLEAR_WARNINGS", "Manuel"
            )
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    # === AUTOMOD ===
    
    @app_commands.command(name="automod", description="Active/désactive l'automod")
    @require_permissions("admin")
    async def automod(self, interaction: discord.Interaction, activer: bool):
        """Active ou désactive l'automod"""
        if interaction.guild:
            self.automod_enabled[interaction.guild.id] = activer
        
        status = "activé" if activer else "désactivé"
        embed = discord.Embed(
            title="🤖 Automod",
            description=f"L'automod a été {status}",
            color=discord.Color.green() if activer else discord.Color.red()
        )
        embed.add_field(name="Configuré par", value=interaction.user.mention, inline=True)
        
        await interaction.response.send_message(embed=embed)
        bot_logger.moderation_action(
            (interaction.guild.id if interaction.guild else 0),
            (interaction.user.id if interaction.user else 0),
            0, "AUTOMOD", status
        )
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Surveillance automatique des messages"""
        if message.author.bot or not message.guild:
            return
        
        guild_id = message.guild.id
        if not self.automod_enabled.get(guild_id, False):
            return
        
        # Vérifier les permissions (ne pas modérer les modérateurs)
        if permission_manager.has_moderator_permissions(message.author):
            return
        
        # Détecter le spam
        await self._check_spam(message)
        
        # Filtrer le contenu
        await self._check_content(message)
        
        # Détecter les mentions en masse
        await self._check_mass_mentions(message)
        
        # Détecter les liens suspects
        await self._check_suspicious_links(message)
    
    async def _check_spam(self, message):
        """Détecte le spam de messages"""
        user_id = message.author.id
        now = datetime.now()
        
        if user_id not in self.spam_tracker:
            self.spam_tracker[user_id] = []
        
        self.spam_tracker[user_id].append(now)
        
        # Vérifier les 10 dernières secondes
        recent = [ts for ts in self.spam_tracker[user_id] if now - ts <= timedelta(seconds=10)]
        self.spam_tracker[user_id] = recent  # Mettre à jour la liste
        
        if len(recent) >= 5:  # 5 messages en 10 secondes = spam
            try:
                await message.delete()
                until = datetime.utcnow() + timedelta(minutes=5)
                await message.author.timeout(until, reason="Automod: Spam détecté")
                
                embed = discord.Embed(
                    title="🤖 Automod - Spam détecté",
                    description=f"{message.author.mention} a été timeout pour spam",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed, delete_after=10)
                
                bot_logger.moderation_action(
                    message.guild.id, 0, message.author.id, "AUTOMOD_SPAM", "5 msg/10s"
                )
                
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass  # Message déjà supprimé ou autre erreur
    
    async def _check_content(self, message):
        """Vérifie le contenu du message"""
        try:
            if content_filter.is_spam(message.content):
                await message.delete()
                
                embed = discord.Embed(
                    title="🤖 Automod - Contenu filtré",
                    description=f"Message de {message.author.mention} supprimé",
                    color=discord.Color.orange()
                )
                await message.channel.send(embed=embed, delete_after=5)
                
                bot_logger.moderation_action(
                    message.guild.id, 0, message.author.id, "AUTOMOD_FILTER", "Contenu suspect"
                )
                
        except discord.Forbidden:
            pass  # Pas de permissions pour supprimer
        except discord.HTTPException:
            pass  # Message déjà supprimé
        except Exception:
            pass  # Autres erreurs
    
    async def _check_mass_mentions(self, message):
        """Détecte les mentions en masse"""
        if len(message.mentions) >= 5 or message.mention_everyone:
            try:
                await message.delete()
                until = datetime.utcnow() + timedelta(minutes=10)
                await message.author.timeout(until, reason="Automod: Mentions en masse")
                
                embed = discord.Embed(
                    title="🤖 Automod - Mentions en masse",
                    description=f"{message.author.mention} timeout pour mentions abusives",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed, delete_after=10)
                
                bot_logger.moderation_action(
                    message.guild.id, 0, message.author.id, "AUTOMOD_MENTIONS", 
                    f"{len(message.mentions)} mentions"
                )
                
            except discord.Forbidden:
                pass
    
    async def _check_suspicious_links(self, message):
        """Détecte les liens suspects"""
        suspicious_domains = [
            'bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly', 't.co',
            'grabify.link', 'iplogger.org', 'discord-nitro'
        ]
        
        for domain in suspicious_domains:
            if domain in message.content.lower():
                try:
                    await message.delete()
                    
                    embed = discord.Embed(
                        title="🤖 Automod - Lien suspect",
                        description=f"Lien suspect supprimé de {message.author.mention}",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed, delete_after=10)
                    
                    bot_logger.moderation_action(
                        message.guild.id, 0, message.author.id, "AUTOMOD_LINK", 
                        f"Domaine: {domain}"
                    )
                    break
                    
                except discord.Forbidden:
                    pass
    
    # === UTILITAIRES ===
    
    async def unmute_member(self, member: discord.Member, reason: str = "Automatique"):
        """Démute un membre"""
        try:
            await member.timeout(None, reason=reason)
            bot_logger.moderation_action(
                member.guild.id, 0, member.id, "UNMUTE", reason
            )
        except Exception:
            pass

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))