from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from database.config.database import Base
from database.utils.logger import db_logger

# Table d'association pour les traitements
verres_traitements = Table(
    "verres_traitements",
    Base.metadata,
    Column("verre_id", Integer, ForeignKey("verres.id"), primary_key=True),
    Column("traitement_id", Integer, ForeignKey("traitements.id"), primary_key=True),
)


class Fournisseur(Base):
    __tablename__ = "fournisseurs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(500), nullable=False, unique=True)
    verres = relationship("Verre", back_populates="fournisseur")

    __table_args__ = (Index("idx_fournisseurs_nom", "nom"),)


class Materiau(Base):
    __tablename__ = "materiaux"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(500), nullable=False, unique=True)
    verres = relationship("Verre", back_populates="materiau")

    __table_args__ = (Index("idx_materiaux_nom", "nom"),)


class Gamme(Base):
    __tablename__ = "gammes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(500), nullable=False, unique=True)
    verres = relationship("Verre", back_populates="gamme")

    __table_args__ = (Index("idx_gammes_nom", "nom"),)


class Serie(Base):
    __tablename__ = "series"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(500), nullable=False, unique=True)
    verres = relationship("Verre", back_populates="serie")

    __table_args__ = (Index("idx_series_nom", "nom"),)


class Traitement(Base):
    __tablename__ = "traitements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(500), nullable=False, unique=True)
    type = Column(String(50), nullable=False)  # 'protection' ou 'photochromique'
    verres = relationship(
        "Verre", secondary=verres_traitements, back_populates="traitements"
    )

    __table_args__ = (
        Index("idx_traitements_nom", "nom"),
        Index("idx_traitements_type", "type"),
    )


class Verre(Base):
    __tablename__ = "verres"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(500), nullable=False)
    variante = Column(String(500), nullable=True)
    hauteur_min = Column(Integer, nullable=True)
    hauteur_max = Column(Integer, nullable=True)
    indice = Column(Float, nullable=True)
    url_gravure = Column(String(1000), nullable=True)
    url_source = Column(String(1000), nullable=True)

    # Clés étrangères
    fournisseur_id = Column(Integer, ForeignKey("fournisseurs.id"), nullable=False)
    materiau_id = Column(Integer, ForeignKey("materiaux.id"), nullable=True)
    gamme_id = Column(Integer, ForeignKey("gammes.id"), nullable=False)
    serie_id = Column(Integer, ForeignKey("series.id"), nullable=True)

    # Relations
    fournisseur = relationship("Fournisseur", back_populates="verres")
    materiau = relationship("Materiau", back_populates="verres")
    gamme = relationship("Gamme", back_populates="verres")
    serie = relationship("Serie", back_populates="verres")
    traitements = relationship(
        "Traitement",
        secondary=verres_traitements,
        back_populates="verres",
        lazy="joined",  # Chargement eager pour éviter les problèmes N+1
    )

    def __repr__(self):
        return f"<Verre(id={self.id}, nom={self.nom})>"

    __table_args__ = (
        Index("idx_verres_nom", "nom"),
        Index("idx_verres_indice", "indice"),
        Index("idx_verres_fournisseur_id", "fournisseur_id"),
        Index("idx_verres_materiau_id", "materiau_id"),
        Index("idx_verres_gamme_id", "gamme_id"),
    )


class ExampleModel(BaseModel):
    # Définissez vos champs ici

    class Config:
        orm_mode = True  # Ajout de orm_mode = True


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
