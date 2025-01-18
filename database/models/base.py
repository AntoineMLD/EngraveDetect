from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index
from database.config.database import Base
from database.utils.logger import db_logger

class Verres(Base):
    __tablename__ = "verres"
    
    __table_args__ = (
        Index('idx_verres_categorie', 'categorie'),
        Index('idx_verres_nom_verre', 'nom_verre'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    categorie = Column(String(500), nullable=False)      
    nom_verre = Column(String(500), nullable=False)     
    gravure_url = Column(String(1000), nullable=True)    
    indice = Column(Float, nullable=True)
    materiau = Column(String(500), nullable=True)        
    has_image = Column(Boolean, default=False)
    
    # Relations
    fournisseur_nom = Column(
        String(500),
        ForeignKey('fournisseurs.nom', ondelete='CASCADE'),
        nullable=False
    )
    fournisseur = relationship(
        "Fournisseurs",
        back_populates="verres",
        lazy='joined'
    )
    tags = relationship(
        "Tags",
        secondary='verres_tags',
        back_populates="verres",
        lazy='select'
    )

class Tags(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(500), unique=True, nullable=False)  # Augmenté à 500
    
    # Relation
    verres = relationship(
        "Verres",
        secondary='verres_tags',
        back_populates="tags",
        lazy='select'
    )

class Fournisseurs(Base):
    __tablename__ = "fournisseurs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(500), unique=True, nullable=False)  # Augmenté à 500
    
    # Relation
    verres = relationship(
        "Verres",
        back_populates="fournisseur",
        lazy='select'
    )

class VerresTags(Base):
    __tablename__ = 'verres_tags'

    verre_id = Column(
        Integer, 
        ForeignKey('verres.id', ondelete='CASCADE'), 
        primary_key=True
    )
    tag_id = Column(
        Integer, 
        ForeignKey('tags.id', ondelete='CASCADE'), 
        primary_key=True
    )

    __table_args__ = (
        Index('idx_verres_tags_verre_id', 'verre_id'),
        Index('idx_verres_tags_tag_id', 'tag_id')
    )

def init_models():
    """
    Initialise les modèles dans la base de données
    """
    from database.config.database import init_database
    try:
        db_logger.info("Début de l'initialisation des modèles")
        init_database()
        db_logger.info("Modèles initialisés avec succès")
    except Exception as e:
        db_logger.critical(f"Erreur lors de l'initialisation des modèles: {str(e)}")
        raise

if __name__ == "__main__":
    init_models()