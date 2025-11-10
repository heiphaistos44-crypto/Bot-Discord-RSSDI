"""
Cog avec des commandes fun supplémentaires et des fonctionnalités amusantes
"""
import random
import asyncio
import datetime
import json
from typing import Optional, List, Dict

import discord
from discord import app_commands
from discord.ext import commands

from config import Config
from database import db_manager
from utils.logger import bot_logger
from utils.security import rate_limit, input_validator

class FunExtrasCog(commands.Cog):
    """Commandes fun et divertissantes supplémentaires"""
    
    def __init__(self, bot):
        self.bot = bot
        self.trivia_questions = self._load_extended_trivia()
        self.truth_questions = self._load_truth_questions()
        self.dare_challenges = self._load_dare_challenges()
        
    async def cog_load(self):
        """Chargement du cog"""
        bot_logger.logger.info("Module fun extras chargé")

    def _load_extended_trivia(self):
        """Questions de trivia étendues"""
        return [
            {
                "question": "Quel est le plus petit pays du monde ?",
                "options": ["Monaco", "Vatican", "Liechtenstein", "Saint-Marin"],
                "correct": 1,
                "category": "Géographie"
            },
            {
                "question": "Qui a peint 'La Joconde' ?",
                "options": ["Picasso", "Van Gogh", "Léonard de Vinci", "Michel-Ange"],
                "correct": 2,
                "category": "Art"
            },
            {
                "question": "Combien d'os a un adulte humain ?",
                "options": ["186", "206", "226", "246"],
                "correct": 1,
                "category": "Sciences"
            },
            {
                "question": "Quelle est la vitesse de la lumière ?",
                "options": ["299 792 458 m/s", "300 000 000 m/s", "299 000 000 m/s", "301 000 000 m/s"],
                "correct": 0,
                "category": "Physique"
            },
            {
                "question": "Quel langage utilise des indentations pour définir les blocs ?",
                "options": ["Java", "C++", "Python", "JavaScript"],
                "correct": 2,
                "category": "Programmation"
            }
        ]

    def _load_truth_questions(self):
        """Questions pour le jeu Truth or Dare"""
        return [
            "Quel est ton plus grand secret ?",
            "Quelle est la chose la plus embarrassante qui te soit arrivée ?",
            "Qui est ton crush secret ?",
            "Quelle est ta plus grande peur ?",
            "Quel est le mensonge le plus gros que tu aies dit ?",
            "Si tu pouvais changer quelque chose dans ta vie, ce serait quoi ?",
            "Quel est ton rêve le plus fou ?",
            "Quelle est la chose la plus bizarre que tu aies mangée ?",
            "Si tu étais invisible pendant 24h, que ferais-tu ?",
            "Quel est ton film/livre guilty pleasure ?"
        ]

    def _load_dare_challenges(self):
        """Défis pour le jeu Truth or Dare"""
        return [
            "Envoie un message vocal en chantant",
            "Change ta photo de profil pour quelque chose d'embarrassant pendant 1h",
            "Écris un compliment à la dernière personne qui t'a envoyé un message",
            "Raconte une blague (même nulle)",
            "Poste un selfie sans filtre",
            "Imite un animal pendant 30 secondes en vocal",
            "Envoie un message à quelqu'un que tu n'as pas contacté depuis longtemps",
            "Fais 10 pompes (et poste une photo/vidéo)",
            "Écris et poste un petit poème",
            "Mange quelque chose d'épicé et filme ta réaction"
        ]

    # === JEUX INTERACTIFS ===
    
    @app_commands.command(name="truth_or_dare", description="Jeu Truth or Dare")
    @rate_limit(max_requests=5, window_seconds=300)
    async def truth_or_dare(self, interaction: discord.Interaction, choix: str):
        """Jeu Truth or Dare"""
        if choix.lower() not in ["truth", "dare", "vérité", "défi"]:
            await interaction.response.send_message("❌ Choisis 'truth/vérité' ou 'dare/défi'.")
            return
            
        if choix.lower() in ["truth", "vérité"]:
            question = random.choice(self.truth_questions)
            
            embed = discord.Embed(
                title="🤔 Truth (Vérité)",
                description=question,
                color=discord.Color.blue()
            )
            embed.set_footer(text="Réponds honnêtement ! 😊")
            
        else:  # dare/défi
            challenge = random.choice(self.dare_challenges)
            
            embed = discord.Embed(
                title="😈 Dare (Défi)",
                description=challenge,
                color=discord.Color.red()
            )
            embed.set_footer(text="Relève le défi ! 💪")
            
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="would_you_rather", description="Jeu Would You Rather")
    async def would_you_rather(self, interaction: discord.Interaction):
        """Jeu Would You Rather"""
        scenarios = [
            ("Pouvoir voler", "Pouvoir devenir invisible"),
            ("Lire dans les pensées", "Voir le futur"),
            ("Vivre 1000 ans", "Revivre ta vie en changeant une chose"),
            ("Être toujours en retard de 20 min", "Être toujours en avance de 20 min"),
            ("Ne plus jamais utiliser internet", "Ne plus jamais regarder la TV"),
            ("Avoir des super pouvoirs mais être détesté", "Être normal mais aimé de tous"),
            ("Pouvoir parler aux animaux", "Pouvoir parler toutes les langues"),
            ("Vivre dans le passé", "Vivre dans le futur"),
            ("Avoir beaucoup d'argent mais être seul", "Être pauvre mais entouré d'amis"),
            ("Ne plus jamais mentir", "Ne plus jamais dire la vérité")
        ]
        
        option1, option2 = random.choice(scenarios)
        
        embed = discord.Embed(
            title="🤷 Would You Rather?",
            description="Que préférerais-tu ?",
            color=discord.Color.purple()
        )
        embed.add_field(name="Option A", value=option1, inline=True)
        embed.add_field(name="Option B", value=option2, inline=True)
        embed.set_footer(text="Réagis avec 🅰️ ou 🅱️ pour voter !")
        
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction("🅰️")
        await message.add_reaction("🅱️")

    @app_commands.command(name="ship", description="Calcule la compatibilité entre deux personnes")
    async def ship_calculator(self, interaction: discord.Interaction, personne1: discord.Member, personne2: discord.Member):
        """Calculateur de ship"""
        if personne1.id == personne2.id:
            await interaction.response.send_message("❌ On ne peut pas se ship avec soi-même !")
            return
            
        # Utiliser les IDs pour avoir un résultat consistant
        combined_id = str(min(personne1.id, personne2.id)) + str(max(personne1.id, personne2.id))
        compatibility = hash(combined_id) % 101
        
        # Nom du ship
        name1 = personne1.display_name
        name2 = personne2.display_name
        ship_name = name1[:len(name1)//2] + name2[len(name2)//2:]
        
        # Déterminer la description
        if compatibility >= 90:
            emoji = "💕"
            status = "Couple parfait !"
            description = "C'est écrit dans les étoiles ! ⭐"
        elif compatibility >= 70:
            emoji = "💖"
            status = "Très compatible"
            description = "Il y a de la magie dans l'air ! ✨"
        elif compatibility >= 50:
            emoji = "💛"
            status = "Bonne entente"
            description = "Ça peut marcher avec des efforts ! 😊"
        elif compatibility >= 30:
            emoji = "🧡"
            status = "Amitié possible"
            description = "Peut-être juste amis ? 🤝"
        else:
            emoji = "💙"
            status = "Peu compatible"
            description = "Opposés s'attirent... parfois ? 🤷"
            
        embed = discord.Embed(
            title="💘 Ship Calculator",
            color=discord.Color.pink()
        )
        embed.add_field(name="Couple", value=f"{personne1.mention} + {personne2.mention}", inline=False)
        embed.add_field(name="Nom du Ship", value=f"**{ship_name}**", inline=True)
        embed.add_field(name="Compatibilité", value=f"**{compatibility}%** {emoji}", inline=True)
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Verdict", value=description, inline=False)
        
        # Barre de progression
        filled = "█" * (compatibility // 10)
        empty = "░" * (10 - (compatibility // 10))
        progress_bar = f"[{filled}{empty}]"
        embed.add_field(name="Barre d'amour", value=f"`{progress_bar}`", inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="compliment", description="Donne un compliment à quelqu'un")
    async def compliment_generator(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        """Générateur de compliments"""
        target = membre or interaction.user
        
        compliments = [
            "Tu es une personne extraordinaire ! ⭐",
            "Ton sourire illumine la journée de tout le monde ! 😊",
            "Tu as un cœur en or ! 💛",
            "Ta créativité est inspirante ! 🎨",
            "Tu rends le monde meilleur rien qu'en y étant ! 🌟",
            "Ton intelligence brille de mille feux ! 🧠✨",
            "Tu es unique et c'est magnifique ! 🦄",
            "Ta gentillesse touche les cœurs ! 💝",
            "Tu as une énergie positive contagieuse ! ⚡",
            "Tu es quelqu'un sur qui on peut compter ! 🤝",
            "Ton humour égaye les journées ! 😄",
            "Tu as un style incroyable ! 👗✨",
            "Ta détermination est admirable ! 💪",
            "Tu es un vrai rayon de soleil ! ☀️",
            "Ton talent est impressionnant ! 🏆"
        ]
        
        compliment = random.choice(compliments)
        
        embed = discord.Embed(
            title="💝 Compliment",
            description=f"{target.mention}\n\n{compliment}",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Envoyé avec amour par {interaction.user.display_name} 💕")
        
        if target.avatar:
            embed.set_thumbnail(url=target.avatar.url)
            
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roast", description="Roast quelqu'un (gentiment)")
    async def roast_generator(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        """Générateur de roasts amicaux"""
        target = membre or interaction.user
        
        roasts = [
            "Tu es comme une mise à jour Windows : personne ne t'attend, mais on doit faire avec ! 😏",
            "Si l'ignorance était un sport olympique, tu serais disqualifié pour dopage ! 🏃‍♂️",
            "Tu es la preuve vivante que l'évolution peut parfois reculer ! 🐒",
            "Ton QI est tellement bas qu'il fait de la spéléologie ! 🕳️",
            "Tu es comme un nuage : quand tu disparais, la journée devient plus belle ! ☁️",
            "Si les neurones étaient des soldats, tu aurais une armée de pacifistes ! 🕊️",
            "Tu es unique... exactement comme tout le monde ! ❄️",
            "Ton cerveau doit se sentir seul dans ta tête ! 🧠",
            "Tu es comme un dictionnaire sans définitions : on ne comprend rien ! 📚",
            "Si la beauté était un crime, tu serais un citoyen exemplaire ! 👮‍♂️"
        ]
        
        roast = random.choice(roasts)
        
        embed = discord.Embed(
            title="🔥 Roast Amical",
            description=f"{target.mention}\n\n{roast}",
            color=discord.Color.orange()
        )
        embed.set_footer(text="C'est de l'humour, ne le prends pas mal ! 😘")
        
        await interaction.response.send_message(embed=embed)

    # === MINI-JEUX ===
    
    @app_commands.command(name="higher_lower", description="Jeu Plus ou Moins")
    @rate_limit(max_requests=3, window_seconds=300)
    async def higher_lower(self, interaction: discord.Interaction):
        """Jeu Plus ou Moins"""
        target = random.randint(1, 100)
        attempts = 0
        max_attempts = 7
        
        embed = discord.Embed(
            title="🎯 Plus ou Moins",
            description=f"J'ai choisi un nombre entre 1 et 100.\nTu as {max_attempts} tentatives pour le trouver !",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed)
        
        def check(message):
            return (
                message.channel and interaction.channel and
                message.channel.id == interaction.channel.id and
                message.author.id == interaction.user.id and
                message.content.isdigit()
            )
        
        while attempts < max_attempts:
            try:
                message = await self.bot.wait_for('message', check=check, timeout=60.0)
                attempts += 1
                guess = int(message.content)
                
                if guess == target:
                    # Victoire !
                    embed = discord.Embed(
                        title="🎉 Bravo !",
                        description=f"Tu as trouvé le nombre **{target}** en {attempts} tentative(s) !",
                        color=discord.Color.green()
                    )
                    
                    # Récompense selon le nombre de tentatives
                    if attempts <= 3:
                        embed.add_field(name="Performance", value="🏆 Excellent !", inline=True)
                    elif attempts <= 5:
                        embed.add_field(name="Performance", value="🥈 Bien joué !", inline=True)
                    else:
                        embed.add_field(name="Performance", value="🥉 Pas mal !", inline=True)
                        
                    await message.reply(embed=embed)
                    return
                    
                elif guess < target:
                    hint = f"📈 Plus grand ! ({attempts}/{max_attempts})"
                else:
                    hint = f"📉 Plus petit ! ({attempts}/{max_attempts})"
                    
                await message.reply(hint)
                
            except asyncio.TimeoutError:
                await interaction.followup.send("⏰ Temps écoulé ! Tu peux relancer le jeu.")
                return
        
        # Défaite
        embed = discord.Embed(
            title="💀 Dommage !",
            description=f"Tu n'as pas trouvé en {max_attempts} tentatives.\nLe nombre était **{target}**.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="word_chain", description="Jeu de chaîne de mots")
    async def word_chain(self, interaction: discord.Interaction):
        """Jeu de chaîne de mots"""
        words = ["python", "discord", "ordinateur", "programmation", "jeu"]
        current_word = random.choice(words)
        used_words = [current_word]
        
        embed = discord.Embed(
            title="🔗 Chaîne de Mots",
            description=f"Trouve un mot qui commence par la dernière lettre de : **{current_word}**\n\nDernière lettre : **{current_word[-1].upper()}**",
            color=discord.Color.green()
        )
        embed.set_footer(text="Tu as 30 secondes par mot !")
        
        await interaction.response.send_message(embed=embed)
        
        def check(message):
            return (
                message.channel and interaction.channel and
                message.channel.id == interaction.channel.id and
                message.author.id == interaction.user.id and
                len(message.content.split()) == 1 and
                message.content.isalpha()
            )
        
        score = 0
        
        while True:
            try:
                message = await self.bot.wait_for('message', check=check, timeout=30.0)
                new_word = message.content.lower().strip()
                
                if new_word in used_words:
                    await message.reply("❌ Mot déjà utilisé ! Fin du jeu.")
                    break
                    
                if not new_word.startswith(current_word[-1].lower()):
                    await message.reply(f"❌ Le mot doit commencer par '{current_word[-1].upper()}' ! Fin du jeu.")
                    break
                
                # Mot valide
                used_words.append(new_word)
                current_word = new_word
                score += 1
                
                await message.reply(f"✅ Bien ! Maintenant un mot qui commence par **{current_word[-1].upper()}**")
                
            except asyncio.TimeoutError:
                await interaction.followup.send("⏰ Temps écoulé !")
                break
        
        # Score final
        embed = discord.Embed(
            title="🏁 Fin du jeu",
            description=f"Score final : **{score}** mots",
            color=discord.Color.blue()
        )
        
        if score >= 10:
            embed.add_field(name="Performance", value="🏆 Excellent vocabulaire !", inline=True)
        elif score >= 5:
            embed.add_field(name="Performance", value="🥈 Pas mal du tout !", inline=True)
        else:
            embed.add_field(name="Performance", value="🥉 Continue à t'entraîner !", inline=True)
            
        embed.add_field(name="Mots utilisés", value=', '.join(used_words), inline=False)
        
        await interaction.followup.send(embed=embed)

    # === OUTILS DE SERVEUR ===
    
    @app_commands.command(name="avatar", description="Affiche l'avatar d'un utilisateur")
    async def avatar(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        """Affiche l'avatar d'un membre"""
        user = membre or interaction.user
        
        embed = discord.Embed(
            title=f"🖼️ Avatar de {user.display_name}",
            color=user.color if user.color.value else discord.Color.blue()
        )
        
        if user.avatar:
            embed.set_image(url=user.avatar.url)
            embed.add_field(name="Lien direct", value=f"[Cliquez ici]({user.avatar.url})", inline=True)
        else:
            embed.set_image(url=user.default_avatar.url)
            embed.add_field(name="Avatar", value="Avatar par défaut Discord", inline=True)
            
        embed.add_field(name="Format", value="PNG/GIF", inline=True)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="membercount", description="Affiche le nombre de membres")
    async def member_count(self, interaction: discord.Interaction):
        """Statistiques des membres"""
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée qu'en serveur.")
            return
        
        total = guild.member_count or 0
        bots = sum(1 for member in guild.members if member.bot)
        humans = total - bots
        
        # Statuts
        online = sum(1 for member in guild.members if member.status == discord.Status.online)
        idle = sum(1 for member in guild.members if member.status == discord.Status.idle)
        dnd = sum(1 for member in guild.members if member.status == discord.Status.dnd)
        offline = total - online - idle - dnd
        
        embed = discord.Embed(
            title=f"👥 Membres de {guild.name}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Total", value=f"**{total}**", inline=True)
        embed.add_field(name="👤 Humains", value=f"**{humans}**", inline=True)
        embed.add_field(name="🤖 Bots", value=f"**{bots}**", inline=True)
        
        embed.add_field(name="🟢 En ligne", value=f"**{online}**", inline=True)
        embed.add_field(name="🟡 Absent", value=f"**{idle}**", inline=True)
        embed.add_field(name="🔴 Occupé", value=f"**{dnd}**", inline=True)
        
        # Graphique simple
        percentage_online = (online / total * 100) if total > 0 else 0
        bar_length = 20
        filled = int(percentage_online / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        embed.add_field(
            name="Activité",
            value=f"`{bar}` {percentage_online:.1f}% actifs",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="random_member", description="Sélectionne un membre aléatoire")
    async def random_member(self, interaction: discord.Interaction, exclure_bots: bool = True):
        """Sélectionne un membre aléatoire"""
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée qu'en serveur.")
            return
            
        members = [m for m in interaction.guild.members if not (exclure_bots and m.bot)]
        
        if not members:
            await interaction.response.send_message("❌ Aucun membre trouvé.")
            return
            
        selected = random.choice(members)
        
        embed = discord.Embed(
            title="🎲 Membre Aléatoire",
            description=f"Le membre sélectionné est : {selected.mention}",
            color=selected.color if selected.color.value else discord.Color.blue()
        )
        
        embed.add_field(name="Nom", value=selected.display_name, inline=True)
        embed.add_field(name="Statut", value=str(selected.status).title(), inline=True)
        embed.add_field(name="Rejoint le", value=selected.joined_at.strftime("%d/%m/%Y") if selected.joined_at else "Inconnu", inline=True)
        
        if selected.avatar:
            embed.set_thumbnail(url=selected.avatar.url)
            
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(FunExtrasCog(bot))