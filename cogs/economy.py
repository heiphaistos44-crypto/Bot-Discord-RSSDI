"""
Système d'économie avancé pour le bot Discord
"""
import random
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
import inspect
import discord
from discord.ext import commands, tasks
from discord import app_commands

from config import Config
from database import user_manager, economy_manager
from utils.logger import bot_logger
from utils.security import require_permissions, rate_limit, input_validator

class EconomyCog(commands.Cog):
    """Commandes d'économie et système de pièces"""
    
    def __init__(self, bot):
        self.bot = bot
        self.work_cooldowns = {}  # user_id: datetime
        self.crime_cooldowns = {}
        self.rob_cooldowns = {}
        
    async def cog_load(self):
        """Chargement du cog"""
        bot_logger.logger.info("Module économie chargé")
        
    async def _balance_impl(self, interaction: discord.Interaction, utilisateur: Optional[discord.Member] = None):
        """Affiche le solde d'un utilisateur"""
        target = utilisateur or interaction.user
        try:
            await user_manager.get_or_create_user(
                getattr(target, "id", 0),
                getattr(target, "display_name", None) or getattr(target, "name", None)
            )
        except Exception:
            # Ne pas bloquer l'affichage du solde si la création échoue
            pass

        guild_id = getattr(getattr(interaction, "guild", None), "id", 0)
        _res = economy_manager.get_balance(getattr(target, "id", 0), guild_id)
        balance = await _res if inspect.isawaitable(_res) else _res
        
        embed = discord.Embed(
            title="💰 Portefeuille",
            description=f"{getattr(target, 'mention', getattr(target, 'display_name', 'Utilisateur'))} possède **{balance:,}** pièces",
            color=discord.Color.gold()
        )
        avatar = getattr(target, "avatar", None)
        default_avatar = getattr(target, "default_avatar", None)
        thumb_url = getattr(avatar, "url", None) if avatar else None
        if not thumb_url and default_avatar:
            thumb_url = getattr(default_avatar, "url", None)
        if thumb_url:
            embed.set_thumbnail(url=thumb_url)
        
        await interaction.response.send_message(embed=embed)

    # Méthode appelable directement (tests)
    async def balance(self, interaction: discord.Interaction, utilisateur: Optional[discord.Member] = None):
        return await self._balance_impl(interaction, utilisateur)

    # Slash command officielle
    @app_commands.command(name="balance", description="Affiche ton solde ou celui d'un autre utilisateur")
    async def balance_cmd(self, interaction: discord.Interaction, utilisateur: Optional[discord.Member] = None):
        await self._balance_impl(interaction, utilisateur)
    
    @app_commands.command(name="daily", description="Récupère tes pièces quotidiennes")
    @rate_limit(max_requests=1, window_seconds=86400)  # Une fois par jour
    async def daily(self, interaction: discord.Interaction):
        """Récompense quotidienne"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return
            
        can_claim = await economy_manager.can_daily(interaction.user.id, interaction.guild.id)
        
        if not can_claim:
            embed = discord.Embed(
                title="⏰ Déjà récupéré",
                description="Tu as déjà récupéré tes pièces quotidiennes aujourd'hui !",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        amount = await economy_manager.claim_daily(interaction.user.id, interaction.guild.id)
        
        embed = discord.Embed(
            title="🎁 Récompense quotidienne",
            description=f"Tu as reçu **{amount}** pièces !",
            color=discord.Color.green()
        )
        embed.add_field(
            name="💡 Astuce",
            value="Reviens demain pour une nouvelle récompense !",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        bot_logger.economy_transaction(
            interaction.guild.id, interaction.user.id, amount, "daily", "Récompense quotidienne"
        )
    
    @app_commands.command(name="work", description="Travaille pour gagner des pièces")
    @rate_limit(max_requests=1, window_seconds=3600)  # Une fois par heure
    async def work(self, interaction: discord.Interaction):
        """Système de travail"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return
            
        user_id = interaction.user.id
        
        # Vérifier le cooldown
        if user_id in self.work_cooldowns:
            time_left = (self.work_cooldowns[user_id] - datetime.now()).total_seconds()
            if time_left > 0:
                minutes = int(time_left // 60)
                seconds = int(time_left % 60)
                embed = discord.Embed(
                    title="⏱️ Cooldown",
                    description=f"Tu peux retravailler dans {minutes}m {seconds}s",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Pas besoin de créer l'utilisateur ici, fait automatiquement
        
        # Métiers et leurs récompenses
        jobs = [
            ("développeur", Config.WORK_COINS_MIN + 20, Config.WORK_COINS_MAX + 30),
            ("serveur", Config.WORK_COINS_MIN, Config.WORK_COINS_MAX),
            ("livreur", Config.WORK_COINS_MIN + 5, Config.WORK_COINS_MAX + 10),
            ("vendeur", Config.WORK_COINS_MIN + 10, Config.WORK_COINS_MAX + 15),
            ("nettoyeur", Config.WORK_COINS_MIN - 5, Config.WORK_COINS_MAX),
        ]
        
        job_name, min_earn, max_earn = random.choice(jobs)
        earned = random.randint(max(1, min_earn), max_earn)
        
        # Messages de travail
        work_messages = [
            f"Tu as travaillé comme {job_name} et gagné {earned} pièces !",
            f"Une journée productive en tant que {job_name} t'a rapporté {earned} pièces !",
            f"Ton travail de {job_name} a été récompensé par {earned} pièces !",
        ]
        
        await economy_manager.add_coins(user_id, interaction.guild.id, earned, f"Travail: {job_name}")
        
        # Définir le cooldown (1 heure)
        self.work_cooldowns[user_id] = datetime.now() + timedelta(hours=1)
        
        embed = discord.Embed(
            title="💼 Travail terminé",
            description=random.choice(work_messages),
            color=discord.Color.green()
        )
        embed.add_field(
            name="💰 Pièces gagnées",
            value=f"{earned}",
            inline=True
        )
        embed.add_field(
            name="👷 Métier",
            value=job_name.title(),
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
        bot_logger.economy_transaction(
            interaction.guild.id, user_id, earned, "work", f"Travail: {job_name}"
        )
    
    @app_commands.command(name="crime", description="Commet un crime pour gagner beaucoup... ou perdre !")
    @rate_limit(max_requests=1, window_seconds=7200)  # Une fois toutes les 2h
    async def crime(self, interaction: discord.Interaction):
        """Système de crime (risqué)"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return
            
        user_id = interaction.user.id
        
        # Vérifier le cooldown
        if user_id in self.crime_cooldowns:
            time_left = (self.crime_cooldowns[user_id] - datetime.now()).total_seconds()
            if time_left > 0:
                hours = int(time_left // 3600)
                minutes = int((time_left % 3600) // 60)
                embed = discord.Embed(
                    title="🚨 Cooldown",
                    description=f"Tu peux commettre un nouveau crime dans {hours}h {minutes}m",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        current_balance = await economy_manager.get_balance(user_id, interaction.guild.id)
        
        # 60% de réussite, 40% d'échec
        success = random.random() < 0.6
        
        crimes = [
            ("vol de banque", 200, 500, 100, 200),
            ("cambriolage", 100, 300, 50, 150),
            ("pickpocket", 50, 150, 25, 75),
            ("fraude informatique", 150, 400, 75, 180),
        ]
        
        crime_name, min_gain, max_gain, min_loss, max_loss = random.choice(crimes)
        
        # Définir le cooldown
        self.crime_cooldowns[user_id] = datetime.now() + timedelta(hours=2)
        
        if success:
            earned = random.randint(min_gain, max_gain)
            await economy_manager.add_coins(user_id, interaction.guild.id, earned, f"Crime réussi: {crime_name}")
            
            embed = discord.Embed(
                title="🎭 Crime réussi !",
                description=f"Ton {crime_name} a été un succès ! Tu as gagné **{earned}** pièces !",
                color=discord.Color.green()
            )
            embed.add_field(name="💰 Gain", value=f"{earned} pièces", inline=True)
            
            bot_logger.economy_transaction(
                interaction.guild.id, user_id, earned, "crime_success", f"Crime: {crime_name}"
            )
        else:
            lost = random.randint(min_loss, min(max_loss, current_balance))
            if lost > 0:
                await economy_manager.add_coins(user_id, interaction.guild.id, -lost, f"Crime échoué: {crime_name}")
            
            embed = discord.Embed(
                title="🚨 Crime échoué !",
                description=f"Ton {crime_name} a échoué ! Tu as perdu **{lost}** pièces en amendes.",
                color=discord.Color.red()
            )
            embed.add_field(name="💸 Perte", value=f"{lost} pièces", inline=True)
            
            bot_logger.economy_transaction(
                interaction.guild.id, user_id, -lost, "crime_fail", f"Crime échoué: {crime_name}"
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="rob", description="Vole un autre utilisateur")
    @rate_limit(max_requests=3, window_seconds=3600)  # 3 fois par heure
    async def rob(self, interaction: discord.Interaction, cible: discord.Member):
        """Vol entre utilisateurs"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return
            
        user_id = interaction.user.id
        target_id = cible.id
        
        if user_id == target_id:
            await interaction.response.send_message("❌ Tu ne peux pas te voler toi-même !", ephemeral=True)
            return
        
        if cible.bot:
            await interaction.response.send_message("❌ Tu ne peux pas voler un bot !", ephemeral=True)
            return
        
        # Vérifier le cooldown
        if user_id in self.rob_cooldowns:
            time_left = (self.rob_cooldowns[user_id] - datetime.now()).total_seconds()
            if time_left > 0:
                minutes = int(time_left // 60)
                embed = discord.Embed(
                    title="⏱️ Cooldown",
                    description=f"Tu peux voler quelqu'un dans {minutes} minutes",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        robber_balance = await economy_manager.get_balance(user_id, interaction.guild.id)
        target_balance = await economy_manager.get_balance(target_id, interaction.guild.id)
        
        if robber_balance < 100:
            await interaction.response.send_message(
                "❌ Tu as besoin d'au moins 100 pièces pour voler quelqu'un !",
                ephemeral=True
            )
            return
        
        if target_balance < 50:
            await interaction.response.send_message(
                f"❌ {cible.mention} n'a pas assez de pièces à voler !",
                ephemeral=True
            )
            return
        
        # 45% de réussite
        success = random.random() < 0.45
        
        # Définir le cooldown (20 minutes)
        self.rob_cooldowns[user_id] = datetime.now() + timedelta(minutes=20)
        
        if success:
            stolen = min(random.randint(10, 100), target_balance // 2)
            await economy_manager.add_coins(target_id, interaction.guild.id, -stolen, f"Volé par {interaction.user}")
            await economy_manager.add_coins(user_id, interaction.guild.id, stolen, f"Vol de {cible}")
            
            embed = discord.Embed(
                title="💰 Vol réussi !",
                description=f"Tu as volé **{stolen}** pièces à {cible.mention} !",
                color=discord.Color.green()
            )
            
            bot_logger.economy_transaction(
                interaction.guild.id, user_id, stolen, "rob_success", f"Vol de {cible}"
            )
        else:
            fine = min(random.randint(50, 150), robber_balance // 3)
            await economy_manager.add_coins(user_id, interaction.guild.id, -fine, f"Échec vol de {cible}")
            
            embed = discord.Embed(
                title="🚨 Vol échoué !",
                description=f"Tu t'es fait attraper ! Amende de **{fine}** pièces.",
                color=discord.Color.red()
            )
            
            bot_logger.economy_transaction(
                interaction.guild.id, user_id, -fine, "rob_fail", f"Échec vol de {cible}"
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="give", description="Donne des pièces à un autre utilisateur")
    async def give(self, interaction: discord.Interaction, destinataire: discord.Member, montant: int):
        """Don de pièces entre utilisateurs"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return
            
        if interaction.user.id == destinataire.id:
            await interaction.response.send_message("❌ Tu ne peux pas te donner des pièces à toi-même !", ephemeral=True)
            return
        
        if destinataire.bot:
            await interaction.response.send_message("❌ Tu ne peux pas donner des pièces à un bot !", ephemeral=True)
            return
        
        try:
            montant = input_validator.validate_integer(montant, min_val=1, max_val=100000)
        except Exception as e:
            await interaction.response.send_message(f"❌ {e}", ephemeral=True)
            return
        
        sender_balance = await economy_manager.get_balance(interaction.user.id, interaction.guild.id)
        
        if sender_balance < montant:
            await interaction.response.send_message(
                f"❌ Tu n'as que {sender_balance} pièces ! Tu ne peux pas donner {montant} pièces.",
                ephemeral=True
            )
            return
        
        await economy_manager.add_coins(interaction.user.id, interaction.guild.id, -montant, f"Don à {destinataire}")
        await economy_manager.add_coins(destinataire.id, interaction.guild.id, montant, f"Don de {interaction.user}")
        
        embed = discord.Embed(
            title="💝 Don effectué",
            description=f"{interaction.user.mention} a donné **{montant}** pièces à {destinataire.mention} !",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed)
        bot_logger.economy_transaction(
            interaction.guild.id, interaction.user.id, -montant, "give", f"Don à {destinataire}"
        )
        bot_logger.economy_transaction(
            interaction.guild.id, destinataire.id, montant, "receive", f"Don de {interaction.user}"
        )
    
    @app_commands.command(name="leaderboard", description="Affiche le classement des plus riches")
    async def leaderboard(self, interaction: discord.Interaction):
        """Classement économique du serveur"""
        # Cette fonction nécessiterait une requête à la base de données
        # pour récupérer le top des utilisateurs par pièces
        await interaction.response.send_message("🚧 Fonctionnalité en développement...")
    
    @app_commands.command(name="shop", description="Affiche la boutique du serveur")
    async def shop(self, interaction: discord.Interaction):
        """Boutique d'objets virtuels"""
        await interaction.response.send_message("🚧 Boutique en développement...")
    
    @app_commands.command(name="gamble", description="Joue tes pièces à pile ou face")
    @rate_limit(max_requests=5, window_seconds=300)  # 5 fois toutes les 5 minutes
    async def gamble(self, interaction: discord.Interaction, mise: int):
        """Jeu de hasard"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return
            
        try:
            mise = input_validator.validate_integer(mise, min_val=10, max_val=1000)
        except Exception as e:
            await interaction.response.send_message(f"❌ {e}", ephemeral=True)
            return
        
        balance = await economy_manager.get_balance(interaction.user.id, interaction.guild.id)
        
        if balance < mise:
            await interaction.response.send_message(
                f"❌ Tu n'as que {balance} pièces ! Tu ne peux pas miser {mise} pièces.",
                ephemeral=True
            )
            return
        
        # 48% de chance de gagner (légèrement en faveur de la maison)
        won = random.random() < 0.48
        
        if won:
            winnings = int(mise * 1.8)  # Gain de 80% en plus
            await economy_manager.add_coins(
                interaction.user.id, interaction.guild.id, winnings, "Gambling win"
            )
            
            embed = discord.Embed(
                title="🎰 Félicitations !",
                description=f"Tu as gagné **{winnings}** pièces !",
                color=discord.Color.green()
            )
            embed.add_field(name="💰 Mise", value=f"{mise}", inline=True)
            embed.add_field(name="🏆 Gain", value=f"{winnings}", inline=True)
            
            bot_logger.economy_transaction(
                interaction.guild.id, interaction.user.id, winnings, "gamble_win", f"Mise: {mise}"
            )
        else:
            await economy_manager.add_coins(
                interaction.user.id, interaction.guild.id, -mise, "Gambling loss"
            )
            
            embed = discord.Embed(
                title="💸 Dommage !",
                description=f"Tu as perdu **{mise}** pièces...",
                color=discord.Color.red()
            )
            embed.add_field(name="💸 Perte", value=f"{mise}", inline=True)
            
            bot_logger.economy_transaction(
                interaction.guild.id, interaction.user.id, -mise, "gamble_loss", f"Mise: {mise}"
            )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(EconomyCog(bot))