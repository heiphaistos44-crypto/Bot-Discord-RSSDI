"""
Système de jeux interactifs pour le bot Discord
"""
import random
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
import discord
from discord.ext import commands, tasks
from discord import app_commands

from config import Config
from database import db_manager, economy_manager
from utils.logger import bot_logger
from utils.security import rate_limit, input_validator

class GamesCog(commands.Cog):
    """Jeux interactifs et mini-jeux"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # channel_id: game_instance
        self.trivia_questions = self._load_trivia_questions()
        
    async def cog_load(self):
        """Chargement du cog"""
        bot_logger.logger.info("Module jeux chargé")
    
    def _load_trivia_questions(self) -> List[Dict]:
        """Charge les questions de trivia"""
        return [
            {
                "question": "Quel est le langage de programmation le plus utilisé pour le web côté client ?",
                "options": ["Python", "JavaScript", "Java", "C++"],
                "correct": 1,
                "category": "Programmation"
            },
            {
                "question": "Qui a créé Discord ?",
                "options": ["Elon Musk", "Jason Citron", "Mark Zuckerberg", "Bill Gates"],
                "correct": 1,
                "category": "Technologie"
            },
            {
                "question": "Combien de côtés a un hexagone ?",
                "options": ["5", "6", "7", "8"],
                "correct": 1,
                "category": "Mathématiques"
            },
            {
                "question": "Quelle est la capitale du Japon ?",
                "options": ["Osaka", "Kyoto", "Tokyo", "Nagoya"],
                "correct": 2,
                "category": "Géographie"
            },
            {
                "question": "En quelle année a été créé Python ?",
                "options": ["1989", "1991", "1995", "2000"],
                "correct": 1,
                "category": "Programmation"
            },
            {
                "question": "Quel est l'élément chimique avec le symbole 'Au' ?",
                "options": ["Argent", "Aluminium", "Or", "Arsenic"],
                "correct": 2,
                "category": "Sciences"
            },
            {
                "question": "Combien de joueurs maximum dans une équipe de football ?",
                "options": ["10", "11", "12", "13"],
                "correct": 1,
                "category": "Sport"
            },
            {
                "question": "Quel est le plus grand océan du monde ?",
                "options": ["Atlantique", "Indien", "Arctique", "Pacifique"],
                "correct": 3,
                "category": "Géographie"
            }
        ]
    
    # === PIERRE PAPIER CISEAUX ===
    
    async def rock_paper_scissors(self, interaction: discord.Interaction, choix: str):
        """Pierre-Papier-Ciseaux contre le bot"""
        choices = {
            "pierre": "🪨", "rock": "🪨", "p": "🪨",
            "papier": "📄", "paper": "📄", "pa": "📄",
            "ciseaux": "✂️", "scissors": "✂️", "c": "✂️"
        }
        
        user_choice = choix.lower()
        if user_choice not in choices:
            await interaction.response.send_message(
                "❌ Choix invalide ! Utilise: pierre, papier, ou ciseaux", ephemeral=True
            )
            return
        
        bot_choice = random.choice(list(choices.keys())[:3])  # Prendre seulement pierre, papier, ciseaux
        
        user_emoji = choices[user_choice]
        bot_emoji = choices[bot_choice]
        
        # Déterminer le gagnant
        win_conditions = {
            "pierre": "ciseaux",
            "papier": "pierre",
            "ciseaux": "papier"
        }
        
        user_normalized = list(choices.keys())[list(choices.values()).index(user_emoji)]
        bot_normalized = list(choices.keys())[list(choices.values()).index(bot_emoji)]
        
        if user_normalized == bot_normalized:
            result = "Égalité !"
            color = discord.Color.yellow()
            reward = 0
        elif win_conditions[user_normalized] == bot_normalized:
            result = "Tu as gagné ! 🎉"
            color = discord.Color.green()
            reward = 5
        else:
            result = "J'ai gagné ! 😄"
            color = discord.Color.red()
            reward = 0
        
        embed = discord.Embed(
            title="🎮 Pierre-Papier-Ciseaux",
            description=f"{interaction.user.mention} VS Bot",
            color=color
        )
        embed.add_field(name="Ton choix", value=user_emoji, inline=True)
        embed.add_field(name="Mon choix", value=bot_emoji, inline=True)
        embed.add_field(name="Résultat", value=result, inline=False)
        
        if reward > 0 and Config.ENABLE_ECONOMY and interaction.guild and interaction.user:
            await economy_manager.add_coins(
                interaction.user.id, interaction.guild.id, reward, "Gain RPS"
            )
            embed.add_field(name="💰 Récompense", value=f"+{reward} pièces", inline=True)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rps", description="Joue à Pierre-Papier-Ciseaux contre le bot")
    @rate_limit(max_requests=10, window_seconds=60)
    async def rps_cmd(self, interaction: discord.Interaction, choix: str):
        await self.rock_paper_scissors(interaction, choix)
    
    # === DEVINER LE NOMBRE ===
    
    @app_commands.command(name="guess", description="Devine un nombre entre 1 et 100")
    @rate_limit(max_requests=5, window_seconds=300)
    async def guess_number(self, interaction: discord.Interaction):
        """Jeu de devinette de nombre"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return
            
        if interaction.channel and interaction.channel.id in self.active_games:
            await interaction.response.send_message(
                "❌ Un jeu est déjà en cours dans ce salon !", ephemeral=True
            )
            return
        
        target_number = random.randint(1, 100)
        attempts = 0
        max_attempts = 7
        
        embed = discord.Embed(
            title="🎯 Devine le nombre !",
            description=f"J'ai choisi un nombre entre **1** et **100**.\nTu as **{max_attempts}** tentatives !",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Comment jouer",
            value="Écris simplement un nombre dans le chat !",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Marquer le jeu comme actif
        if interaction.channel:
            self.active_games[interaction.channel.id] = {
            'type': 'guess',
            'target': target_number,
            'attempts': attempts,
            'max_attempts': max_attempts,
            'player': interaction.user.id,
            'start_time': datetime.now()
        }
        
        def check(message):
            return (
                interaction.channel and message.channel.id == interaction.channel.id and
                message.author.id == interaction.user.id and
                message.content.isdigit()
            )
        
        try:
            while attempts < max_attempts:
                try:
                    message = await self.bot.wait_for('message', check=check, timeout=60.0)
                    attempts += 1
                    guess = int(message.content)
                    
                    if guess == target_number:
                        # Victoire !
                        if interaction.channel:
                            time_taken = (datetime.now() - self.active_games[interaction.channel.id]['start_time']).seconds
                        reward = max(10, 50 - attempts * 5)  # Plus de récompense avec moins de tentatives
                        
                        embed = discord.Embed(
                            title="🎉 Bravo !",
                            description=f"Tu as trouvé le nombre **{target_number}** en **{attempts}** tentative(s) !",
                            color=discord.Color.green()
                        )
                        embed.add_field(name="⏱️ Temps", value=f"{time_taken}s", inline=True)
                        
                        if Config.ENABLE_ECONOMY:
                            await economy_manager.add_coins(
                                interaction.user.id, interaction.guild.id, reward, "Gain devine nombre"
                            )
                            embed.add_field(name="💰 Récompense", value=f"+{reward} pièces", inline=True)
                        
                        await message.reply(embed=embed)
                        break
                        
                    elif guess < target_number:
                        await message.reply(f"📈 Plus grand ! ({attempts}/{max_attempts})")
                    else:
                        await message.reply(f"📉 Plus petit ! ({attempts}/{max_attempts})")
                        
                except asyncio.TimeoutError:
                    embed = discord.Embed(
                        title="⏰ Temps écoulé !",
                        description=f"Le nombre était **{target_number}**.",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed)
                    break
            else:
                # Défaite
                embed = discord.Embed(
                    title="💀 Défaite !",
                    description=f"Tu n'as pas trouvé en {max_attempts} tentatives.\nLe nombre était **{target_number}**.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                
        finally:
            # Nettoyer le jeu
            if interaction.channel and interaction.channel.id in self.active_games:
                del self.active_games[interaction.channel.id]
    
    # === TRIVIA ===
    
    @app_commands.command(name="trivia", description="Réponds à une question de culture générale")
    @rate_limit(max_requests=5, window_seconds=300)
    async def trivia(self, interaction: discord.Interaction, 
                     categorie: Optional[str] = None):
        """Quiz de culture générale"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return
            
        if interaction.channel and interaction.channel.id in self.active_games:
            await interaction.response.send_message(
                "❌ Un jeu est déjà en cours dans ce salon !", ephemeral=True
            )
            return
        
        # Filtrer par catégorie si spécifiée
        questions = self.trivia_questions
        if categorie:
            questions = [q for q in questions if q['category'].lower() == categorie.lower()]
            if not questions:
                await interaction.response.send_message(
                    f"❌ Aucune question trouvée pour la catégorie '{categorie}'", ephemeral=True
                )
                return
        
        question_data = random.choice(questions)
        
        embed = discord.Embed(
            title="🧠 Question Trivia",
            description=question_data['question'],
            color=discord.Color.purple()
        )
        embed.add_field(name="Catégorie", value=question_data['category'], inline=True)
        embed.add_field(name="⏱️ Temps", value="30 secondes", inline=True)
        
        options_text = ""
        for i, option in enumerate(question_data['options']):
            options_text += f"{chr(65 + i)}. {option}\n"
        
        embed.add_field(name="Options", value=options_text, inline=False)
        embed.set_footer(text="Réponds avec A, B, C ou D")
        
        await interaction.response.send_message(embed=embed)
        
        # Marquer le jeu comme actif
        if interaction.guild:
            if interaction.channel:
                self.active_games[interaction.channel.id] = {
            'type': 'trivia',
            'question': question_data,
            'player': interaction.user.id,
            'start_time': datetime.now()
        }
        
        def check(message):
            return (
                interaction.channel and message.channel.id == interaction.channel.id and
                message.author.id == interaction.user.id and
                message.content.upper() in ['A', 'B', 'C', 'D']
            )
        
        try:
            try:
                message = await self.bot.wait_for('message', check=check, timeout=30.0)
                answer_index = ord(message.content.upper()) - ord('A')
                correct_index = question_data['correct']
                
                if answer_index == correct_index:
                    # Bonne réponse
                    if interaction.channel:
                        time_taken = (datetime.now() - self.active_games[interaction.channel.id]['start_time']).seconds
                    reward = max(10, 30 - time_taken)  # Plus de récompense si réponse rapide
                    
                    embed = discord.Embed(
                        title="✅ Bonne réponse !",
                        description=f"La réponse était bien **{question_data['options'][correct_index]}** !",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="⏱️ Temps", value=f"{time_taken}s", inline=True)
                    
                    if Config.ENABLE_ECONOMY:
                        await economy_manager.add_coins(
                            interaction.user.id, interaction.guild.id, reward, "Gain trivia"
                        )
                        embed.add_field(name="💰 Récompense", value=f"+{reward} pièces", inline=True)
                    
                    await message.reply(embed=embed)
                else:
                    # Mauvaise réponse
                    embed = discord.Embed(
                        title="❌ Mauvaise réponse !",
                        description=f"La bonne réponse était **{question_data['options'][correct_index]}**.",
                        color=discord.Color.red()
                    )
                    await message.reply(embed=embed)
                    
            except asyncio.TimeoutError:
                embed = discord.Embed(
                    title="⏰ Temps écoulé !",
                    description=f"La réponse était **{question_data['options'][question_data['correct']]}**.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                
        finally:
            # Nettoyer le jeu
            if interaction.channel and interaction.channel.id in self.active_games:
                del self.active_games[interaction.channel.id]
    
    # === 8-BALL ===
    
    @app_commands.command(name="8ball", description="Pose une question à la boule magique")
    @rate_limit(max_requests=10, window_seconds=60)
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        """Boule magique 8-ball"""
        try:
            question = input_validator.sanitize_text(question, 200)
        except Exception as e:
            await interaction.response.send_message(f"❌ {e}", ephemeral=True)
            return
        
        responses = [
            # Réponses positives
            "Oui, absolument ! 🌟",
            "C'est certain ! ✅",
            "Sans aucun doute ! 💯",
            "Oui, définitivement ! 🎯",
            "Tu peux compter dessus ! 🤝",
            "Comme je le vois, oui ! 👁️",
            "Très probablement ! 📈",
            "Les perspectives sont bonnes ! 🌅",
            "Oui ! 👍",
            "Les signes pointent vers oui ! 🧭",
            
            # Réponses neutres
            "Pose la question plus tard... ⏰",
            "Mieux vaut ne pas te le dire maintenant 🤐",
            "Impossible de prédire maintenant 🔮",
            "Concentre-toi et redemande 🧘",
            "Ne compte pas dessus 😕",
            
            # Réponses négatives
            "Ma réponse est non ❌",
            "Mes sources disent non 📚",
            "Les perspectives ne sont pas bonnes 📉",
            "Très douteux 😬",
            "Non 👎"
        ]
        
        response = random.choice(responses)
        
        embed = discord.Embed(
            title="🎱 Boule Magique 8-Ball",
            color=discord.Color.dark_purple()
        )
        embed.add_field(name="❓ Ta question", value=question, inline=False)
        embed.add_field(name="🔮 Réponse", value=response, inline=False)
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/8-Ball_Pool.svg/1200px-8-Ball_Pool.svg.png")
        
        await interaction.response.send_message(embed=embed)
    
    # === DUEL DE RÉACTION ===
    
    @app_commands.command(name="reaction_duel", description="Défie quelqu'un dans un duel de réaction")
    @rate_limit(max_requests=3, window_seconds=300)
    async def reaction_duel(self, interaction: discord.Interaction, adversaire: discord.Member):
        """Duel de vitesse de réaction"""
        if adversaire.bot:
            await interaction.response.send_message("❌ Tu ne peux pas défier un bot !", ephemeral=True)
            return
        
        if adversaire.id == interaction.user.id:
            await interaction.response.send_message("❌ Tu ne peux pas te défier toi-même !", ephemeral=True)
            return
        
        if interaction.channel and interaction.channel.id in self.active_games:
            await interaction.response.send_message(
                "❌ Un jeu est déjà en cours dans ce salon !", ephemeral=True
            )
            return
        
        # Demander l'acceptation
        embed = discord.Embed(
            title="⚔️ Duel de Réaction !",
            description=f"{interaction.user.mention} défie {adversaire.mention} !\n\n"
                       f"{adversaire.mention}, réagis avec ⚔️ pour accepter !",
            color=discord.Color.orange()
        )
        embed.set_footer(text="Le défi expire dans 30 secondes")
        
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction("⚔️")
        
        def check_accept(reaction, user):
            return (
                user.id == adversaire.id and
                str(reaction.emoji) == "⚔️" and
                reaction.message.id == message.id
            )
        
        try:
            await self.bot.wait_for('reaction_add', check=check_accept, timeout=30.0)
        except asyncio.TimeoutError:
            embed.description = f"⏰ {adversaire.mention} n'a pas accepté le défi à temps."
            embed.color = discord.Color.red()
            await message.edit(embed=embed)
            return
        
        # Démarrer le duel
        await self._start_reaction_duel(interaction, message, adversaire)
    
    async def _start_reaction_duel(self, interaction, message, adversaire):
        """Lance le duel de réaction"""
        self.active_games[interaction.channel.id] = {
            'type': 'reaction_duel',
            'players': [interaction.user.id, adversaire.id],
            'start_time': datetime.now()
        }
        
        embed = discord.Embed(
            title="⚔️ Duel de Réaction",
            description="Préparez-vous...\n\nQuand vous verrez 🔥, soyez le premier à réagir !",
            color=discord.Color.yellow()
        )
        await message.edit(embed=embed)
        await message.clear_reactions()
        
        # Attendre un délai aléatoire (3-8 secondes)
        delay = random.uniform(3, 8)
        await asyncio.sleep(delay)
        
        start_time = datetime.now()
        
        embed = discord.Embed(
            title="🔥 MAINTENANT !",
            description="Premier à réagir avec 🔥 gagne !",
            color=discord.Color.red()
        )
        await message.edit(embed=embed)
        await message.add_reaction("🔥")
        
        def check_reaction(reaction, user):
            return (
                user.id in [interaction.user.id, adversaire.id] and
                str(reaction.emoji) == "🔥" and
                reaction.message.id == message.id
            )
        
        try:
            reaction, winner = await self.bot.wait_for('reaction_add', check=check_reaction, timeout=10.0)
            reaction_time = (datetime.now() - start_time).total_seconds()
            
            loser = adversaire if winner.id == interaction.user.id else interaction.user
            
            embed = discord.Embed(
                title="🏆 Résultat du Duel",
                description=f"**Gagnant:** {winner.mention}\n**Temps de réaction:** {reaction_time:.3f}s",
                color=discord.Color.green()
            )
            embed.add_field(name="🥇 Vainqueur", value=winner.display_name, inline=True)
            embed.add_field(name="🥈 Finaliste", value=loser.display_name, inline=True)
            
            if Config.ENABLE_ECONOMY:
                reward = 15
                await economy_manager.add_coins(
                    winner.id, interaction.guild.id, reward, "Gain duel réaction"
                )
                embed.add_field(name="💰 Récompense", value=f"+{reward} pièces", inline=True)
            
            await message.edit(embed=embed)
            
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="⏰ Temps écoulé !",
                description="Personne n'a réagi à temps...",
                color=discord.Color.orange()
            )
            await message.edit(embed=embed)
        
        finally:
            # Nettoyer le jeu
            if interaction.channel.id in self.active_games:
                del self.active_games[interaction.channel.id]
    
    # === COMMANDES D'INFORMATION ===
    
    @app_commands.command(name="games_help", description="Affiche l'aide des jeux")
    async def games_help(self, interaction: discord.Interaction):
        """Aide pour les jeux"""
        embed = discord.Embed(
            title="🎮 Jeux Disponibles",
            description="Liste de tous les jeux que tu peux jouer !",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🪨📄✂️ Pierre-Papier-Ciseaux",
            value="`/rps <choix>` - Joue contre le bot",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Devine le Nombre",
            value="`/guess` - Devine un nombre entre 1 et 100",
            inline=False
        )
        
        embed.add_field(
            name="🧠 Trivia",
            value="`/trivia [catégorie]` - Questions de culture générale",
            inline=False
        )
        
        embed.add_field(
            name="🎱 8-Ball",
            value="`/8ball <question>` - Pose une question à la boule magique",
            inline=False
        )
        
        embed.add_field(
            name="⚔️ Duel de Réaction",
            value="`/reaction_duel <@utilisateur>` - Défie quelqu'un en vitesse",
            inline=False
        )
        
        if Config.ENABLE_ECONOMY:
            embed.add_field(
                name="💰 Récompenses",
                value="Gagne des pièces en jouant et en gagnant !",
                inline=False
            )
        
        categories = list(set(q['category'] for q in self.trivia_questions))
        embed.add_field(
            name="📚 Catégories Trivia",
            value=", ".join(categories),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="game_stats", description="Affiche tes statistiques de jeu")
    async def game_stats(self, interaction: discord.Interaction, utilisateur: Optional[discord.Member] = None):
        """Statistiques de jeu d'un utilisateur"""
        target = utilisateur or interaction.user
        
        # Pour l'instant, on peut juste afficher un placeholder
        # Dans une vraie implémentation, on stockerait les stats en base
        embed = discord.Embed(
            title=f"📊 Statistiques de {target.display_name}",
            description="🚧 Fonctionnalité en développement...",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="💡 Bientôt disponible",
            value="Victoires, défaites, temps moyens, etc.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(GamesCog(bot))