"""
Module de sécurité et validation pour le bot Discord
"""
import re
import ast
import operator
import asyncio
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
import hashlib
import secrets
import logging
import discord
from functools import wraps

from config import Config
# Assurez-vous que utils/logger.py contient la définition de bot_logger, par exemple :
# bot_logger = logging.getLogger("bot_logger")
# Sinon, utilisez le logger local défini dans ce fichier :
logger = logging.getLogger(__name__)
bot_logger = logger

class SecurityError(Exception):
    """Exception pour les erreurs de sécurité"""
    pass

class InputValidator:
    """Validateur d'entrées utilisateur"""
    
    # Patterns de validation
    PATTERNS = {
        'discord_id': re.compile(r'^\d{17,19}$'),
        'discord_token': re.compile(r'^[A-Za-z0-9_-]{24}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27}$'),
        'webhook_url': re.compile(r'^https://discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_-]+$'),
        'url': re.compile(r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'),
        'username': re.compile(r'^[a-zA-Z0-9_-]{1,32}$'),
        'tag_name': re.compile(r'^[a-zA-Z0-9_-]{1,50}$'),
        'emoji': re.compile(r'^(?:[\u2600-\u27BF]|[\U0001F000-\U0001F6FF]|<a?:\w+:\d+>)$'),
    }
    
    @classmethod
    def validate_discord_id(cls, value: Union[str, int]) -> int:
        """Valide un ID Discord"""
        str_value = str(value)
        if not cls.PATTERNS['discord_id'].match(str_value):
            raise SecurityError(f"ID Discord invalide: {value}")
        return int(str_value)
    
    @classmethod
    def validate_url(cls, url: str, allow_discord_only: bool = False) -> str:
        """Valide une URL"""
        if not url:
            return url
            
        if allow_discord_only:
            if not cls.PATTERNS['webhook_url'].match(url):
                raise SecurityError("URL Discord webhook invalide")
        else:
            if not cls.PATTERNS['url'].match(url):
                raise SecurityError("URL invalide")
                
        return url
    
    @classmethod
    def validate_username(cls, username: str) -> str:
        """Valide un nom d'utilisateur"""
        if not cls.PATTERNS['username'].match(username):
            raise SecurityError("Nom d'utilisateur invalide (a-z, A-Z, 0-9, _, -, 1-32 caractères)")
        return username
    
    @classmethod
    def validate_tag_name(cls, name: str) -> str:
        """Valide un nom de tag"""
        if not cls.PATTERNS['tag_name'].match(name):
            raise SecurityError("Nom de tag invalide (a-z, A-Z, 0-9, _, -, 1-50 caractères)")
        return name.lower()
    
    @classmethod
    def validate_emoji(cls, emoji: str) -> str:
        """Valide un emoji"""
        if not cls.PATTERNS['emoji'].match(emoji):
            raise SecurityError("Emoji invalide")
        return emoji
    
    @classmethod
    def sanitize_text(cls, text: str, max_length: int = 2000) -> str:
        """Nettoie et limite un texte"""
        if not isinstance(text, str):
            raise SecurityError("Le texte doit être une chaîne de caractères")
            
        # Supprimer les caractères de contrôle
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Limiter la longueur
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
            
        return text
    
    @classmethod
    def validate_integer(cls, value: Union[str, int], min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
        """Valide et convertit un entier"""
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise SecurityError(f"Valeur entière invalide: {value}")

        if min_val is not None and int_value < min_val:
            raise SecurityError(f"Valeur trop petite (minimum: {min_val})")

        if max_val is not None and int_value > max_val:
            raise SecurityError(f"Valeur trop grande (maximum: {max_val})")

        return int_value

class SafeCalculator:
    """Calculateur sécurisé pour remplacer eval()"""
    
    # Opérateurs autorisés
    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    
    # Fonctions autorisées
    SAFE_FUNCTIONS = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
    }
    
    @classmethod
    def safe_eval(cls, expression: str, max_depth: int = 10) -> Union[int, float]:
        """Évalue une expression mathématique de manière sécurisée"""
        if len(expression) > 200:
            raise SecurityError("Expression trop longue")
            
        try:
            tree = ast.parse(expression, mode='eval')
            return cls._eval_node(tree.body, max_depth)
        except (SyntaxError, ValueError) as e:
            raise SecurityError(f"Expression mathématique invalide: {e}")
    
    @classmethod
    def _eval_node(cls, node: ast.AST, depth: int) -> Union[int, float]:
        """Évalue récursivement un nœud AST"""
        if depth <= 0:
            raise SecurityError("Expression trop complexe")
            
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise SecurityError("Seuls les nombres sont autorisés")
            
        elif isinstance(node, ast.Num):  # Python < 3.8
            if isinstance(node.n, (int, float)):
                return node.n
            raise SecurityError("Seuls les nombres sont autorisés")
            
        elif isinstance(node, ast.BinOp):
            left = cls._eval_node(node.left, depth - 1)
            right = cls._eval_node(node.right, depth - 1)
            op = cls.SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise SecurityError(f"Opérateur non autorisé: {type(node.op).__name__}")
            return op(left, right)
            
        elif isinstance(node, ast.UnaryOp):
            operand = cls._eval_node(node.operand, depth - 1)
            op = cls.SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise SecurityError(f"Opérateur unaire non autorisé: {type(node.op).__name__}")
            return op(operand)
            
        elif isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else None
            if func_name not in cls.SAFE_FUNCTIONS:
                raise SecurityError(f"Fonction non autorisée: {func_name}")
            
            args = [cls._eval_node(arg, depth - 1) for arg in node.args]
            return cls.SAFE_FUNCTIONS[func_name](*args)
            
        else:
            raise SecurityError(f"Élément non autorisé dans l'expression: {type(node).__name__}")

class RateLimiter:
    """Système de limitation de taux pour éviter le spam"""
    
    def __init__(self):
        self.user_buckets: Dict[int, List[datetime]] = {}
        self.guild_buckets: Dict[int, List[datetime]] = {}
        
    def is_rate_limited(self, user_id: int, guild_id: Optional[int] = None, 
                       max_requests: int = 5, window_seconds: int = 60) -> bool:
        """Vérifie si un utilisateur est limité par le taux"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)
        
        # Nettoyer les anciennes entrées
        if user_id in self.user_buckets:
            self.user_buckets[user_id] = [
                req_time for req_time in self.user_buckets[user_id] 
                if req_time > cutoff
            ]
        else:
            self.user_buckets[user_id] = []
            
        # Vérifier la limite
        if len(self.user_buckets[user_id]) >= max_requests:
            bot_logger.warning(
                f"RATE_LIMIT: Dépassement du taux de {max_requests}/{window_seconds}s "
                f"pour l'utilisateur {user_id} dans le serveur {guild_id or 0}"
            )
            return True
            
        # Ajouter la requête actuelle
        self.user_buckets[user_id].append(now)
        return False
    
    def get_remaining_cooldown(self, user_id: int, window_seconds: int = 60) -> int:
        """Retourne le temps restant avant de pouvoir refaire une requête"""
        if user_id not in self.user_buckets:
            return 0
            
        oldest_request = min(self.user_buckets[user_id])
        elapsed = (datetime.now() - oldest_request).total_seconds()
        return max(0, int(window_seconds - elapsed))

class ContentFilter:
    """Filtre de contenu pour détecter le spam et contenu inapproprié"""
    
    # Mots interdits (liste basique, à étendre)
    BANNED_WORDS = {
        'spam', 'hack', 'cheat', 'bot', 'raid', 'discord.gg', 
        'bit.ly', 'tinyurl', 'free', 'nitro', 'gift'
    }
    
    # Patterns suspects
    SUSPICIOUS_PATTERNS = [
        re.compile(r'(.)\1{10,}'),  # Répétition excessive de caractères
        re.compile(r'https?://(?!discord\.com|github\.com)', re.IGNORECASE),  # URLs suspectes
        re.compile(r'@everyone|@here', re.IGNORECASE),  # Mentions de masse
        re.compile(r'[A-Z]{10,}'),  # Texte en CAPS excessif
    ]
    
    @classmethod
    def is_spam(cls, content: str) -> bool:
        """Détecte si le contenu est du spam"""
        content_lower = content.lower()
        
        # Vérifier les mots interdits
        for word in cls.BANNED_WORDS:
            if word in content_lower:
                return True
                
        # Vérifier les patterns suspects
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if pattern.search(content):
                return True
                
        return False
    
    @classmethod
    def filter_content(cls, content: str, user_id: int, guild_id: int) -> str:
        """Filtre le contenu et log les événements suspects"""
        if cls.is_spam(content):
            bot_logger.warning(
                f"SECURITY EVENT: Guild {guild_id}, User {user_id}, Type SPAM_DETECTED, "
                f"Contenu suspect: {content[:100]}..."
            )
            raise SecurityError("Contenu détecté comme spam")

        return InputValidator.sanitize_text(content)

class PermissionManager:
    """Gestionnaire de permissions avancé"""
    
    ADMIN_PERMISSIONS = [
        'administrator', 'manage_guild', 'manage_channels', 
        'manage_roles', 'ban_members', 'kick_members'
    ]
    
    MODERATOR_PERMISSIONS = [
        'manage_messages', 'moderate_members', 'move_members', 
        'mute_members', 'deafen_members'
    ]
    
    @classmethod
    def has_admin_permissions(cls, member) -> bool:
        """Vérifie si un membre a des permissions d'administrateur"""
        if not member or not member.guild_permissions:
            return False
            
        return any(
            getattr(member.guild_permissions, perm, False) 
            for perm in cls.ADMIN_PERMISSIONS
        )
    
    @classmethod
    def has_moderator_permissions(cls, member) -> bool:
        """Vérifie si un membre a des permissions de modérateur"""
        if cls.has_admin_permissions(member):
            return True
            
        if not member or not member.guild_permissions:
            return False
            
        return any(
            getattr(member.guild_permissions, perm, False) 
            for perm in cls.MODERATOR_PERMISSIONS
        )
    
    @classmethod
    def can_moderate_user(cls, moderator, target) -> bool:
        """Vérifie si un modérateur peut agir sur un utilisateur"""
        if not moderator or not target:
            return False
            
        # Le propriétaire peut tout faire
        if moderator.guild.owner_id == moderator.id:
            return True
            
        # On ne peut pas modérer le propriétaire
        if target.guild.owner_id == target.id:
            return False
            
        # Vérifier la hiérarchie des rôles
        if moderator.top_role <= target.top_role:
            return False
            
        return cls.has_moderator_permissions(moderator)

class SessionManager:
    """Gestionnaire de sessions pour l'interface web"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        
    def create_session(self, user_id: str) -> str:
        """Crée une nouvelle session"""
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'ip_address': None  # À définir selon le contexte
        }
        return session_id
    
    def validate_session(self, session_id: str) -> bool:
        """Valide une session existante"""
        if session_id not in self.sessions:
            return False
            
        session = self.sessions[session_id]
        
        # Vérifier l'expiration (24h)
        if datetime.now() - session['created_at'] > timedelta(hours=24):
            del self.sessions[session_id]
            return False
            
        # Mettre à jour l'activité
        session['last_activity'] = datetime.now()
        return True
    
    def cleanup_expired_sessions(self):
        """Nettoie les sessions expirées"""
        now = datetime.now()
        expired = [
            sid for sid, session in self.sessions.items()
            if now - session['created_at'] > timedelta(hours=24)
        ]
        
        for sid in expired:
            del self.sessions[sid]

# Instances globales
input_validator = InputValidator()
safe_calculator = SafeCalculator()
rate_limiter = RateLimiter()
content_filter = ContentFilter()
permission_manager = PermissionManager()
session_manager = SessionManager()

# Décorateurs de sécurité
def require_permissions(permission_level: str = "member"):
    """Décorateur pour vérifier les permissions (compatible slash commands)"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            # Gérer les deux types d'interactions - pour slash commands, utiliser .user
            user = interaction.user if hasattr(interaction, 'user') else getattr(interaction, 'author', None)
            
            # Vérifier que l'utilisateur est membre du serveur pour les permissions
            if interaction.guild and user:
                member = interaction.guild.get_member(user.id)
                if not member:
                    if hasattr(interaction, 'response') and not interaction.response.is_done():
                        await interaction.response.send_message("❌ Erreur: membre introuvable.", ephemeral=True)
                    else:
                        await interaction.followup.send("❌ Erreur: membre introuvable.", ephemeral=True)
                    return
            else:
                member = user
            
            if permission_level == "admin":
                if not permission_manager.has_admin_permissions(member):
                    if hasattr(interaction, 'response') and not interaction.response.is_done():
                        await interaction.response.send_message("❌ Permissions administrateur requises.", ephemeral=True)
                    else:
                        await interaction.followup.send("❌ Permissions administrateur requises.", ephemeral=True)
                    return
            elif permission_level == "moderator":
                if not permission_manager.has_moderator_permissions(member):
                    if hasattr(interaction, 'response') and not interaction.response.is_done():
                        await interaction.response.send_message("❌ Permissions de modération requises.", ephemeral=True)
                    else:
                        await interaction.followup.send("❌ Permissions de modération requises.", ephemeral=True)
                    return
                    
            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator

def rate_limit(max_requests: int = 5, window_seconds: int = 60):
    """Décorateur pour limiter le taux d'utilisation (compatible slash commands)"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            # Pour slash commands, utiliser .user
            user = interaction.user if hasattr(interaction, 'user') else getattr(interaction, 'author', None)
            guild = getattr(interaction, 'guild', None)
            
            if user is None:
                if hasattr(interaction, 'response') and not interaction.response.is_done():
                    await interaction.response.send_message("❌ Erreur: utilisateur introuvable.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Erreur: utilisateur introuvable.", ephemeral=True)
                return

            if rate_limiter.is_rate_limited(
                user.id,
                guild.id if guild else None,
                max_requests,
                window_seconds
            ):
                cooldown = rate_limiter.get_remaining_cooldown(user.id, window_seconds)
                if hasattr(interaction, 'response') and not interaction.response.is_done():
                    await interaction.response.send_message(f"⏱️ Trop de requêtes. Réessayez dans {cooldown}s.", ephemeral=True)
                else:
                    await interaction.followup.send(f"⏱️ Trop de requêtes. Réessayez dans {cooldown}s.", ephemeral=True)
                return
                
            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator

def filter_input(content_param: str = "content"):
    """Décorateur pour filtrer le contenu d'entrée"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            # Récupérer le paramètre de contenu
            if content_param in kwargs:
                try:
                    user = interaction.user if hasattr(interaction, 'user') else getattr(interaction, 'author', None)
                    kwargs[content_param] = content_filter.filter_content(
                        kwargs[content_param],
                        user.id if user is not None else 0,
                        interaction.guild.id if interaction.guild else 0
                    )
                except SecurityError as e:
                    if hasattr(interaction, 'response') and not interaction.response.is_done():
                        await interaction.response.send_message(f"❌ {e}", ephemeral=True)
                    else:
                        await interaction.followup.send(f"❌ {e}", ephemeral=True)
                    return
                    
            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator