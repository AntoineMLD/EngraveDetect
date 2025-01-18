import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

class CustomFormatter(logging.Formatter):
    """Formateur personnalisé pour les logs avec des couleurs en console"""
    
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: blue + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    Configure et retourne un logger personnalisé
    
    Args:
        name (str): Nom du logger
        log_file (str, optional): Chemin du fichier de log. Par défaut None.
    
    Returns:
        logging.Logger: Logger configuré
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Création du dossier logs s'il n'existe pas
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Handler pour la console avec couleurs
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)

    # Handler pour le fichier avec rotation
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

# Création du logger principal de la base de données
db_logger = setup_logger(
    'database',
    os.path.join('database', 'logs', f'db_{datetime.now().strftime("%Y%m%d")}.log')
)