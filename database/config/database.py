import os
from typing import Generator
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from database.utils.logger import db_logger

# Chargement des variables d'environnement
load_dotenv()

def get_database_url() -> str:
    """
    Retourne l'URL de connexion à la base de données SQLite
    
    Returns:
        str: URL de connexion à la base de données
    """
    # Obtenir le chemin absolu du répertoire racine du projet
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Créer le dossier data s'il n'existe pas
    db_dir = os.path.join(project_root, 'data')
    os.makedirs(db_dir, exist_ok=True)
    
    # Construire le chemin complet de la base de données
    db_path = os.path.join(db_dir, 'verres.db')
    
    # Convertir les backslashes en forward slashes pour SQLite
    db_path = db_path.replace('\\', '/')
    
    db_logger.info(f"Chemin de la base de données : {db_path}")
    return f"sqlite:///{db_path}"

# Configuration du moteur SQLAlchemy
def create_db_engine():
    """
    Crée et configure le moteur SQLAlchemy pour SQLite
    
    Returns:
        Engine: Instance du moteur SQLAlchemy
    """
    try:
        engine = create_engine(
            get_database_url(),
            echo=False  # Mettre à True pour voir les requêtes SQL
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

def get_db() -> Generator[Session, None, None]:
    """
    Générateur pour obtenir une session de base de données
    
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
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            db_logger.info("Connexion à la base de données vérifiée avec succès")
            return True
        except Exception as e:
            db_logger.error(f"Erreur de connexion à la base de données: {str(e)}")
            return False
        finally:
            db.close()
    except Exception as e:
        db_logger.error(f"Erreur lors de la création de la session: {str(e)}")
        return False