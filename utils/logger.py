"""
Système de logging centralisé pour le bot Discord
"""
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional
import json
import asyncio
from discord.ext import commands

from config import Config

class ColoredFormatter(logging.Formatter):
    """Formateur avec couleurs pour le terminal"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Vert
        'WARNING': '\033[33m',    # Jaune
        'ERROR': '\033[31m',      # Rouge
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)

class JSONFormatter(logging.Formatter):
    """Formateur JSON pour les logs structurés"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Ajouter des informations Discord si disponibles
        if record.__dict__.get('guild_id') is not None:
            log_data['guild_id'] = record.__dict__.get('guild_id')
        if record.__dict__.get('user_id') is not None:
            log_data['user_id'] = record.__dict__.get('user_id')
        if record.__dict__.get('channel_id') is not None:
            log_data['channel_id'] = record.__dict__.get('channel_id')
            
        # Ajouter l'exception si présente
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_data, ensure_ascii=False)

class DiscordLogHandler(logging.Handler):
    """Handler pour envoyer les logs critiques vers Discord"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        super().__init__()
        self.webhook_url = webhook_url or Config.DISCORD_WEBHOOK_URL
        self.setLevel(logging.ERROR)
        
    def emit(self, record):
        if not self.webhook_url:
            return
            
        try:
            import requests
            
            message = self.format(record)
            payload = {
                "embeds": [{
                    "title": f"🚨 Erreur Bot - {record.levelname}",
                    "description": f"```\n{message}\n```",
                    "color": 0xff0000,  # Rouge
                    "timestamp": datetime.now().isoformat(),
                    "fields": [
                        {"name": "Module", "value": record.module, "inline": True},
                        {"name": "Fonction", "value": record.funcName, "inline": True},
                        {"name": "Ligne", "value": str(record.lineno), "inline": True}
                    ]
                }]
            }
            
            requests.post(self.webhook_url, json=payload, timeout=5)
        except Exception:
            pass  # Ne pas faire planter le bot pour les logs

def setup_logging():
    """Configure le système de logging"""
    
    # Créer le dossier logs
    Config.LOGS_DIR.mkdir(exist_ok=True)
    
    # Logger principal
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Console handler avec couleurs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)8s | %(name)s:%(lineno)d | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Fichier de logs rotatif
    file_handler = logging.handlers.RotatingFileHandler(
        Config.LOGS_DIR / 'bot.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)8s | %(name)s:%(lineno)d | %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Logs JSON structurés pour analyse
    json_handler = logging.handlers.RotatingFileHandler(
        Config.LOGS_DIR / 'bot.json',
        maxBytes=10*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    json_handler.setLevel(logging.INFO)
    json_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(json_handler)
    
    # Discord webhook pour erreurs critiques
    discord_handler = DiscordLogHandler()
    root_logger.addHandler(discord_handler)
    
    # Réduire le niveau de logging pour les librairies externes
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return root_logger

class BotLogger:
    """Logger spécialisé pour les événements du bot"""
    
    def __init__(self):
        self.logger = logging.getLogger('bot')
        
    def command_used(self, ctx: commands.Context, command_name: str):
        """Log d'utilisation d'une commande (résistant aux mocks imparfaits)"""
        guild = getattr(ctx, 'guild', None)
        author = getattr(ctx, 'author', None)
        channel = getattr(ctx, 'channel', None)
        extra = {
            'guild_id': getattr(guild, 'id', None) if guild is not None else None,
            'user_id': getattr(author, 'id', None),
            'channel_id': getattr(channel, 'id', None)
        }
        self.logger.info(
            f"Commande '{command_name}' utilisée par {author} "
            f"dans #{channel}" + (f" ({guild})" if guild else ""),
            extra=extra
        )
    
    def error_occurred(self, ctx: commands.Context, error: Exception):
        """Log d'erreur de commande"""
        extra = {
            'guild_id': ctx.guild.id if ctx.guild else None,
            'user_id': ctx.author.id,
            'channel_id': ctx.channel.id
        }
        self.logger.error(
            f"Erreur dans commande par {ctx.author}: {error}",
            exc_info=True,
            extra=extra
        )
    
    def moderation_action(self, guild_id: int, moderator_id: int, target_id: int, 
                         action: str, reason: str = "Non spécifié"):
        """Log d'action de modération"""
        extra = {'guild_id': guild_id}
        self.logger.warning(
            f"Action modération: {action} sur {target_id} par {moderator_id} - {reason}",
            extra=extra
        )
    
    def economy_transaction(self, guild_id: int, user_id: int, amount: int, 
                          transaction_type: str, description: str):
        """Log de transaction économique"""
        extra = {'guild_id': guild_id, 'user_id': user_id}
        self.logger.info(
            f"Transaction économie: {transaction_type} {amount} pièces pour {user_id} - {description}",
            extra=extra
        )
    
    def level_up(self, guild_id: int, user_id: int, new_level: int):
        """Log de montée de niveau"""
        extra = {'guild_id': guild_id, 'user_id': user_id}
        self.logger.info(
            f"Montée de niveau: {user_id} niveau {new_level}",
            extra=extra
        )
    
    def security_event(self, guild_id: int, user_id: int, event_type: str, details: str):
        """Log d'événement de sécurité"""
        extra = {'guild_id': guild_id, 'user_id': user_id}
        self.logger.warning(
            f"Événement sécurité: {event_type} - {details}",
            extra=extra
        )

# Instance globale
bot_logger = BotLogger()

# Fonction d'aide pour les décorateurs
def log_command_usage(func):
    """Décorateur pour logger automatiquement l'usage des commandes"""
    from functools import wraps
    
    @wraps(func)
    async def wrapper(self, ctx, *args, **kwargs):
        bot_logger.command_used(ctx, func.__name__)
        try:
            return await func(self, ctx, *args, **kwargs)
        except Exception as e:
            bot_logger.error_occurred(ctx, e)
            raise
    return wrapper

class PerformanceLogger:
    """Logger pour mesurer les performances"""
    
    def __init__(self):
        self.logger = logging.getLogger('performance')
        
    async def time_async_function(self, func_name: str, coro):
        """Mesure le temps d'exécution d'une coroutine"""
        start_time = datetime.now()
        try:
            result = await coro
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.debug(f"{func_name} exécuté en {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.warning(f"{func_name} échoué après {execution_time:.3f}s: {e}")
            raise

# Instance globale
perf_logger = PerformanceLogger()

# Configuration automatique au chargement du module
setup_logging()