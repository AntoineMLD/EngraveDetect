import pandas as pd
import os
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from database.config.database import get_db
from database.models.base import Verre, Fournisseur, Materiau, Gamme, Serie, Traitement
from database.utils.logger import db_logger
from typing import Any, List, Optional
from pydantic import BaseModel

def get_or_create(db, model, **kwargs):
    """
    Récupère une instance existante ou en crée une nouvelle
    avec gestion des transactions
    """
    try:
        instance = db.query(model).filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = model(**kwargs)
            db.add(instance)
            db.flush()  # Flush pour obtenir l'ID sans commit
            return instance
    except Exception as e:
        db.rollback()
        # Nouvelle tentative de récupération après rollback
        instance = db.query(model).filter_by(**kwargs).first()
        if instance:
            return instance
        raise e

def check_duplicate_verre(db, verre_data, fournisseur, materiau, gamme, serie):
    """
    Vérifie si un verre identique existe déjà dans la base
    
    Returns:
        Verre or None: L'instance du verre si trouvée, None sinon
    """
    query = db.query(Verre).filter(
        and_(
            Verre.nom == verre_data['nom_du_verre'],
            Verre.variante == (verre_data['variante'] if pd.notna(verre_data['variante']) else None),
            Verre.hauteur_min == (verre_data['hauteur_min'] if pd.notna(verre_data['hauteur_min']) else None),
            Verre.hauteur_max == (verre_data['hauteur_max'] if pd.notna(verre_data['hauteur_max']) else None),
            Verre.indice == (verre_data['indice'] if pd.notna(verre_data['indice']) else None),
            Verre.url_gravure == (verre_data['url_gravure'] if pd.notna(verre_data['url_gravure']) else None),
            Verre.url_source == (verre_data['url_source'] if pd.notna(verre_data['url_source']) else None),
            Verre.fournisseur_id == fournisseur.id,
            Verre.gamme_id == gamme.id
        )
    )
    
    if materiau:
        query = query.filter(Verre.materiau_id == materiau.id)
    else:
        query = query.filter(Verre.materiau_id.is_(None))
        
    if serie:
        query = query.filter(Verre.serie_id == serie.id)
    else:
        query = query.filter(Verre.serie_id.is_(None))
        
    return query.first()

def process_csv_file(db, csv_file: Path, global_stats: dict) -> None:
    """
    Traite un fichier CSV spécifique
    """
    try:
        df = pd.read_csv(csv_file)
        df = df.drop_duplicates()
        
        file_stats = {
            'total': len(df),
            'importes': 0,
            'doublons': 0
        }
        
        # Création des traitements standards
        traitement_protection = get_or_create(db, Traitement, 
                                            nom="Protection UV", 
                                            type="protection")
        traitement_photochromique = get_or_create(db, Traitement, 
                                                 nom="Photochromique", 
                                                 type="photochromique")
        
        # Import des données
        for _, row in df.iterrows():
            # Création ou récupération des entités liées
            fournisseur = get_or_create(db, Fournisseur, nom=row['fournisseur'])
            materiau = get_or_create(db, Materiau, nom=row['materiau']) if pd.notna(row['materiau']) else None
            gamme = get_or_create(db, Gamme, nom=row['gamme'])
            serie = get_or_create(db, Serie, nom=row['serie']) if pd.notna(row['serie']) else None

            # Vérification des doublons
            existing_verre = check_duplicate_verre(db, row, fournisseur, materiau, gamme, serie)
            
            if existing_verre:
                file_stats['doublons'] += 1
                global_stats['doublons'] += 1
                continue

            # Création du verre
            verre = Verre(
                nom=row['nom_du_verre'],
                variante=row['variante'] if pd.notna(row['variante']) else None,
                hauteur_min=row['hauteur_min'] if pd.notna(row['hauteur_min']) else None,
                hauteur_max=row['hauteur_max'] if pd.notna(row['hauteur_max']) else None,
                indice=row['indice'] if pd.notna(row['indice']) else None,
                url_gravure=row['url_gravure'] if pd.notna(row['url_gravure']) else None,
                url_source=row['url_source'] if pd.notna(row['url_source']) else None,
                fournisseur=fournisseur,
                materiau=materiau,
                gamme=gamme,
                serie=serie
            )

            # Ajout des traitements
            if row.get('traitement_protection') == 'OUI':
                verre.traitements.append(traitement_protection)
            if row.get('traitement_photochromique') == 'OUI':
                verre.traitements.append(traitement_photochromique)

            db.add(verre)
            file_stats['importes'] += 1
            global_stats['importes'] += 1
            global_stats['total'] += 1

        db_logger.info(f"Traitement de {csv_file.name} terminé :")
        db_logger.info(f"- Lignes traitées : {file_stats['total']}")
        db_logger.info(f"- Verres importés : {file_stats['importes']}")
        db_logger.info(f"- Doublons ignorés : {file_stats['doublons']}")
        
    except Exception as e:
        db_logger.error(f"Erreur lors du traitement de {csv_file.name}: {str(e)}")
        raise

def import_data() -> None:
    """
    Importe les données de tous les fichiers CSV du dossier enhanced/data
    """
    try:
        enhanced_data_path = Path("scrapers/scrapers/datalake/enhanced/data")
        
        if not enhanced_data_path.exists():
            raise FileNotFoundError(f"Le dossier {enhanced_data_path} n'existe pas")
        
        global_stats = {
            'total': 0,
            'importes': 0,
            'doublons': 0
        }
        
        with get_db() as db:
            # Création des traitements standards une seule fois
            traitement_protection = get_or_create(db, Traitement, 
                                                nom="Protection UV", 
                                                type="protection")
            traitement_photochromique = get_or_create(db, Traitement, 
                                                     nom="Photochromique", 
                                                     type="photochromique")
            
            # Dictionnaire pour stocker les fournisseurs déjà créés
            fournisseurs_cache = {}
            materiaux_cache = {}
            gammes_cache = {}
            series_cache = {}
            
            # Traitement de chaque fichier CSV
            for csv_file in enhanced_data_path.glob("*.csv"):
                db_logger.info(f"Traitement du fichier : {csv_file.name}")
                
                try:
                    df = pd.read_csv(csv_file)
                    df = df.drop_duplicates()
                    
                    file_stats = {
                        'total': len(df),
                        'importes': 0,
                        'doublons': 0
                    }
                    
                    for _, row in df.iterrows():
                        try:
                            # Utilisation du cache pour les entités liées
                            fournisseur_nom = row['fournisseur']
                            if fournisseur_nom not in fournisseurs_cache:
                                fournisseurs_cache[fournisseur_nom] = get_or_create(db, Fournisseur, nom=fournisseur_nom)
                            fournisseur = fournisseurs_cache[fournisseur_nom]
                            
                            materiau = None
                            if pd.notna(row['materiau']):
                                if row['materiau'] not in materiaux_cache:
                                    materiaux_cache[row['materiau']] = get_or_create(db, Materiau, nom=row['materiau'])
                                materiau = materiaux_cache[row['materiau']]
                            
                            if row['gamme'] not in gammes_cache:
                                gammes_cache[row['gamme']] = get_or_create(db, Gamme, nom=row['gamme'])
                            gamme = gammes_cache[row['gamme']]
                            
                            serie = None
                            if pd.notna(row['serie']):
                                if row['serie'] not in series_cache:
                                    series_cache[row['serie']] = get_or_create(db, Serie, nom=row['serie'])
                                serie = series_cache[row['serie']]
                            
                            # Vérification des doublons
                            existing_verre = check_duplicate_verre(db, row, fournisseur, materiau, gamme, serie)
                            
                            if existing_verre:
                                file_stats['doublons'] += 1
                                continue
                            
                            # Création du verre
                            verre = Verre(
                                nom=row['nom_du_verre'],
                                variante=row['variante'] if pd.notna(row['variante']) else None,
                                hauteur_min=row['hauteur_min'] if pd.notna(row['hauteur_min']) else None,
                                hauteur_max=row['hauteur_max'] if pd.notna(row['hauteur_max']) else None,
                                indice=row['indice'] if pd.notna(row['indice']) else None,
                                url_gravure=row['url_gravure'] if pd.notna(row['url_gravure']) else None,
                                url_source=row['url_source'] if pd.notna(row['url_source']) else None,
                                fournisseur=fournisseur,
                                materiau=materiau,
                                gamme=gamme,
                                serie=serie
                            )
                            
                            if row.get('traitement_protection') == 'OUI':
                                verre.traitements.append(traitement_protection)
                            if row.get('traitement_photochromique') == 'OUI':
                                verre.traitements.append(traitement_photochromique)
                            
                            db.add(verre)
                            file_stats['importes'] += 1
                            
                        except Exception as e:
                            db_logger.error(f"Erreur lors du traitement d'une ligne : {str(e)}")
                            db.rollback()
                            continue
                    
                    db.commit()
                    
                    # Mise à jour des statistiques globales
                    global_stats['total'] += file_stats['total']
                    global_stats['importes'] += file_stats['importes']
                    global_stats['doublons'] += file_stats['doublons']
                    
                    db_logger.info(f"Traitement de {csv_file.name} terminé :")
                    db_logger.info(f"- Lignes traitées : {file_stats['total']}")
                    db_logger.info(f"- Verres importés : {file_stats['importes']}")
                    db_logger.info(f"- Doublons ignorés : {file_stats['doublons']}")
                    
                except Exception as e:
                    db_logger.error(f"Erreur lors du traitement du fichier {csv_file.name}: {str(e)}")
                    db.rollback()
                    continue
            
            # Log des statistiques globales
            db_logger.info("\nStatistiques globales de l'import :")
            db_logger.info(f"- Total lignes traitées : {global_stats['total']}")
            db_logger.info(f"- Total verres importés : {global_stats['importes']}")
            db_logger.info(f"- Total doublons ignorés : {global_stats['doublons']}")
            
    except Exception as e:
        db_logger.error(f"Erreur lors de l'import : {str(e)}")
        raise

if __name__ == "__main__":
    import_data()

class VerreBase(BaseModel):
    id: int
    name: str

class VerreResponse(VerreBase):
    additional_info: Optional[Any] = None