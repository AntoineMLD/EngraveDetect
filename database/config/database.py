import os
from typing import Generator
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from database.utils.logger import db_logger

# Chargement des variables d'environnement
load_dotenv()

def get_database_url() -> str:
    """
    Construit et retourne l'URL de connexion à la base de données
    
    Returns:
        str: URL de connexion à la base de données
    """
    required_env_vars = ['DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        error_msg = f"Variables d'environnement manquantes : {', '.join(missing_vars)}"
        db_logger.critical(error_msg)
        raise ValueError(error_msg)

    return "postgresql://{user}:{password}@{host}:{port}/{name}".format(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        name=os.getenv("DB_NAME")
    )

# Configuration du moteur SQLAlchemy
def create_db_engine():
    """
    Crée et configure le moteur SQLAlchemy
    
    Returns:
        Engine: Instance du moteur SQLAlchemy
    """
    try:
        engine = create_engine(
            get_database_url(),
            pool_size=20,  # Nombre de connexions dans le pool
            max_overflow=10,  # Connexions supplémentaires maximales
            pool_timeout=30,  # Timeout pour obtenir une connexion
            pool_recycle=3600,  # Recycle des connexions après 1 heure
            pool_pre_ping=True,  # Vérifie la validité des connexions
            echo=os.getenv("SQL_ECHO", "false").lower() == "true"  # Logs SQL
        )
        db_logger.info("Moteur de base de données créé avec succès")
        return engine
    except Exception as e:
        db_logger.critical(f"Erreur lors de la création du moteur de base de données: {str(e)}")
        raise

# Création du moteur
engine = create_db_engine()

# Configuration de la session
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# Création de la base déclarative
Base = declarative_base()

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Gestionnaire de contexte pour obtenir une session de base de données
    
    Yields:
        Session: Session de base de données
    """
    db = SessionLocal()
    try:
        db_logger.debug("Nouvelle session de base de données créée")
        yield db
        db.commit()
        db_logger.debug("Session de base de données validée")
    except SQLAlchemyError as e:
        db.rollback()
        db_logger.error(f"Erreur SQL lors de l'utilisation de la session: {str(e)}")
        raise
    except Exception as e:
        db.rollback()
        db_logger.error(f"Erreur inattendue lors de l'utilisation de la session: {str(e)}")
        raise
    finally:
        db.close()
        db_logger.debug("Session de base de données fermée")

def init_database() -> None:
    """
    Initialise la base de données en créant toutes les tables
    """
    try:
        Base.metadata.create_all(bind=engine)
        db_logger.info("Base de données initialisée avec succès")
    except Exception as e:
        db_logger.critical(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        raise

def check_database_connection() -> bool:
    """
    Vérifie la connexion à la base de données
    
    Returns:
        bool: True si la connexion est établie, False sinon
    """
    try:
        with get_db() as db:
            db.execute("SELECT 1")
            db_logger.info("Connexion à la base de données vérifiée avec succès")
            return True
    except Exception as e:
        db_logger.error(f"Erreur de connexion à la base de données: {str(e)}")
        return False