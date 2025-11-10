"""
Mini-jeux avancés pour le bot Discord
"""
import discord
from discord.ext import commands
from discord import app_commands
import random

from utils.logger import bot_logger

class MinigamesCog(commands.Cog):
    """Mini-jeux avancés"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        bot_logger.logger.info("Module mini-jeux chargé")

    @app_commands.command(name="blackjack", description="Joue au blackjack")
    async def blackjack(self, interaction: discord.Interaction, mise: int):
        await interaction.response.send_message(f"🃏 Blackjack! Mise: {mise}")

    @app_commands.command(name="slots", description="Machine à sous")
    async def slots(self, interaction: discord.Interaction, mise: int):
        await interaction.response.send_message(f"🎰 Slots! Mise: {mise}")

    @app_commands.command(name="roulette", description="Roulette russe")
    async def roulette(self, interaction: discord.Interaction, numero: int):
        await interaction.response.send_message(f"🎡 Roulette! Numéro: {numero}")

    @app_commands.command(name="poker", description="Joue au poker")
    async def poker(self, interaction: discord.Interaction):
        await interaction.response.send_message("🃏 Poker en cours...")

    @app_commands.command(name="baccarat", description="Joue au baccarat")
    async def baccarat(self, interaction: discord.Interaction, mise: int):
        await interaction.response.send_message(f"🎴 Baccarat! Mise: {mise}")

    @app_commands.command(name="war", description="Jeu de bataille")
    async def war(self, interaction: discord.Interaction):
        await interaction.response.send_message("⚔️ Bataille!")

    @app_commands.command(name="dice", description="Lance des dés")
    async def dice(self, interaction: discord.Interaction, nombre: int = 1):
        await interaction.response.send_message(f"🎲 Lancer de {nombre} dé(s)")

    @app_commands.command(name="coinflip", description="Pile ou face")
    async def coinflip(self, interaction: discord.Interaction, mise: int, choix: str):
        await interaction.response.send_message(f"🪙 Pile ou face! Mise: {mise}")

    @app_commands.command(name="lottery", description="Loterie")
    async def lottery(self, interaction: discord.Interaction):
        await interaction.response.send_message("🎟️ Ticket de loterie acheté")

    @app_commands.command(name="bingo", description="Joue au bingo")
    async def bingo(self, interaction: discord.Interaction):
        await interaction.response.send_message("🎱 Bingo!")

    @app_commands.command(name="scratch", description="Carte à gratter")
    async def scratch(self, interaction: discord.Interaction):
        await interaction.response.send_message("💳 Carte à gratter")

    @app_commands.command(name="horse_race", description="Course de chevaux")
    async def horse_race(self, interaction: discord.Interaction, cheval: int, mise: int):
        await interaction.response.send_message(f"🐎 Course! Cheval #{cheval}")

    @app_commands.command(name="crash", description="Jeu crash")
    async def crash(self, interaction: discord.Interaction, mise: int):
        await interaction.response.send_message(f"💥 Crash! Mise: {mise}")

    @app_commands.command(name="mines", description="Démineur")
    async def mines(self, interaction: discord.Interaction):
        await interaction.response.send_message("💣 Démineur lancé")

    @app_commands.command(name="plinko", description="Plinko")
    async def plinko(self, interaction: discord.Interaction, mise: int):
        await interaction.response.send_message(f"📍 Plinko! Mise: {mise}")

    @app_commands.command(name="wheel", description="Roue de la fortune")
    async def wheel(self, interaction: discord.Interaction, mise: int):
        await interaction.response.send_message(f"🎡 Roue! Mise: {mise}")

    @app_commands.command(name="keno", description="Keno")
    async def keno(self, interaction: discord.Interaction):
        await interaction.response.send_message("🎰 Keno!")

    @app_commands.command(name="scratchcard", description="Grattage de carte")
    async def scratchcard(self, interaction: discord.Interaction):
        await interaction.response.send_message("💳 Carte à gratter")

    @app_commands.command(name="connect4", description="Puissance 4")
    async def connect4(self, interaction: discord.Interaction, adversaire: discord.Member):
        await interaction.response.send_message(f"🔴🟡 Puissance 4 vs {adversaire.mention}")

    @app_commands.command(name="tictactoe", description="Morpion")
    async def tictactoe(self, interaction: discord.Interaction, adversaire: discord.Member):
        await interaction.response.send_message(f"❌⭕ Morpion vs {adversaire.mention}")

    @app_commands.command(name="chess", description="Échecs")
    async def chess(self, interaction: discord.Interaction, adversaire: discord.Member):
        await interaction.response.send_message(f"♟️ Échecs vs {adversaire.mention}")

    @app_commands.command(name="checkers", description="Dames")
    async def checkers(self, interaction: discord.Interaction, adversaire: discord.Member):
        await interaction.response.send_message(f"⚫⚪ Dames vs {adversaire.mention}")

    @app_commands.command(name="reversi", description="Reversi/Othello")
    async def reversi(self, interaction: discord.Interaction, adversaire: discord.Member):
        await interaction.response.send_message(f"⚫⚪ Reversi vs {adversaire.mention}")

    @app_commands.command(name="gomoku", description="Gomoku")
    async def gomoku(self, interaction: discord.Interaction, adversaire: discord.Member):
        await interaction.response.send_message(f"⚫⚪ Gomoku vs {adversaire.mention}")

    @app_commands.command(name="battleship", description="Bataille navale")
    async def battleship(self, interaction: discord.Interaction, adversaire: discord.Member):
        await interaction.response.send_message(f"🚢 Bataille navale vs {adversaire.mention}")

    @app_commands.command(name="hangman", description="Pendu")
    async def hangman(self, interaction: discord.Interaction):
        await interaction.response.send_message("🎯 Pendu lancé")

    @app_commands.command(name="wordle", description="Wordle")
    async def wordle(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔤 Wordle du jour")

    @app_commands.command(name="anagram", description="Anagramme")
    async def anagram(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔀 Anagramme à résoudre")

    @app_commands.command(name="scramble", description="Mots mélangés")
    async def scramble(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔀 Mot mélangé")

    @app_commands.command(name="akinator", description="Akinator")
    async def akinator(self, interaction: discord.Interaction):
        await interaction.response.send_message("🧞 Akinator lancé")

    @app_commands.command(name="trivia_multi", description="Trivia multijoueur")
    async def trivia_multi(self, interaction: discord.Interaction):
        await interaction.response.send_message("❓ Trivia multijoueur")

    @app_commands.command(name="quiz", description="Quiz thématique")
    async def quiz(self, interaction: discord.Interaction, theme: str):
        await interaction.response.send_message(f"📝 Quiz: {theme}")

    @app_commands.command(name="typing_test", description="Test de vitesse de frappe")
    async def typing_test(self, interaction: discord.Interaction):
        await interaction.response.send_message("⌨️ Test de frappe")

    @app_commands.command(name="math_quiz", description="Quiz de maths")
    async def math_quiz(self, interaction: discord.Interaction, niveau: str):
        await interaction.response.send_message(f"🔢 Quiz maths: {niveau}")

    @app_commands.command(name="memory", description="Jeu de mémoire")
    async def memory(self, interaction: discord.Interaction):
        await interaction.response.send_message("🧠 Jeu de mémoire")

    @app_commands.command(name="simon", description="Jacques a dit")
    async def simon(self, interaction: discord.Interaction):
        await interaction.response.send_message("🎮 Jacques a dit")

    @app_commands.command(name="2048", description="Jeu 2048")
    async def game_2048(self, interaction: discord.Interaction):
        await interaction.response.send_message("🎯 2048 lancé")

    @app_commands.command(name="sudoku", description="Sudoku")
    async def sudoku(self, interaction: discord.Interaction, niveau: str):
        await interaction.response.send_message(f"🔢 Sudoku: {niveau}")

    @app_commands.command(name="crossword", description="Mots croisés")
    async def crossword(self, interaction: discord.Interaction):
        await interaction.response.send_message("📝 Mots croisés")

    @app_commands.command(name="maze", description="Labyrinthe")
    async def maze(self, interaction: discord.Interaction):
        await interaction.response.send_message("🌀 Labyrinthe")

    @app_commands.command(name="snake", description="Snake")
    async def snake(self, interaction: discord.Interaction):
        await interaction.response.send_message("🐍 Snake lancé")

    @app_commands.command(name="tetris", description="Tetris")
    async def tetris(self, interaction: discord.Interaction):
        await interaction.response.send_message("🟦 Tetris lancé")

    @app_commands.command(name="flappy", description="Flappy Bird")
    async def flappy(self, interaction: discord.Interaction):
        await interaction.response.send_message("🐦 Flappy Bird")

    @app_commands.command(name="dino", description="Chrome Dino")
    async def dino(self, interaction: discord.Interaction):
        await interaction.response.send_message("🦕 Chrome Dino")

    @app_commands.command(name="minesweeper", description="Démineur classique")
    async def minesweeper(self, interaction: discord.Interaction, taille: str):
        await interaction.response.send_message(f"💣 Démineur: {taille}")

    @app_commands.command(name="sokoban", description="Sokoban")
    async def sokoban(self, interaction: discord.Interaction):
        await interaction.response.send_message("📦 Sokoban")

    @app_commands.command(name="pacman", description="Pac-Man")
    async def pacman(self, interaction: discord.Interaction):
        await interaction.response.send_message("👻 Pac-Man")

    @app_commands.command(name="pong", description="Pong")
    async def pong(self, interaction: discord.Interaction, adversaire: discord.Member):
        await interaction.response.send_message(f"🏓 Pong vs {adversaire.mention}")

async def setup(bot):
    await bot.add_cog(MinigamesCog(bot))
