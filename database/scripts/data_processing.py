from typing import Dict, List, Optional, Tuple, Set
from database.models.base import Verres, Tags, Fournisseurs
from database.utils.logger import db_logger
from sqlalchemy.orm import Session
import pandas as pd
from dataclasses import dataclass

def clean_string(value: str) -> Optional[str]:
    """
    Nettoie une chaîne de caractères
    
    Args:
        value: Valeur à nettoyer
        
    Returns:
        str: Chaîne nettoyée ou None si vide
    """
    if pd.isna(value) or value == "":
        return None
    return str(value).strip()

def clean_float(value: str) -> Optional[float]:
    """
    Convertit une chaîne en float
    
    Args:
        value: Valeur à convertir
        
    Returns:
        float: Valeur convertie ou None si invalide
    """
    if pd.isna(value) or value == "":
        return None
    try:
        return float(str(value).replace(',', '.'))
    except ValueError:
        return None

def process_glass_data(df: pd.DataFrame) -> Tuple[List[Dict], List[str], List[str]]:
    """
    Traite les données des verres depuis le DataFrame
    
    Args:
        df: DataFrame contenant les données
        
    Returns:
        Tuple contenant:
        - Liste des données de verres nettoyées
        - Liste des fournisseurs uniques
        - Liste des catégories uniques
    """
    processed_data = []
    suppliers = set()
    categories = set()
    seen_rows = set()  # Pour détecter les doublons exacts
    
    for _, row in df.iterrows():
        # Nettoyage des données
        category = clean_string(row['category'])
        glass_name = clean_string(row['glass_name'])
        supplier = clean_string(row['glass_supplier_name'])
        index = clean_float(row['glass_index'])
        engraving = clean_string(row['nasal_engraving'])
        material = clean_string(row['material'])
        
        if not all([category, glass_name, supplier]):
            db_logger.warning(f"Données invalides ignorées: {row.to_dict()}")
            continue
            
        # Créer un tuple avec toutes les données nettoyées pour détecter les doublons exacts
        row_key = (
            category,
            glass_name,
            engraving,
            index,
            material,
            bool(row['image_engraving']),
            supplier
        )
            
        # Vérifier si cette ligne existe déjà (doublon exact)
        if row_key in seen_rows:
            db_logger.warning(f"Ligne dupliquée ignorée: {row.to_dict()}")
            continue
            
        seen_rows.add(row_key)
        suppliers.add(supplier)
        categories.add(category)
        
        # Création du dictionnaire de données
        glass_data = {
            'categorie': category,
            'nom_verre': glass_name,
            'gravure_url': engraving,
            'indice': index,
            'materiau': material,
            'has_image': bool(row['image_engraving']),
            'fournisseur_nom': supplier
        }
        
        processed_data.append(glass_data)
    
    db_logger.info(f"Données traitées : {len(processed_data)} verres uniques sur {len(df)} lignes")
    if len(df) - len(processed_data) > 0:
        db_logger.warning(f"{len(df) - len(processed_data)} lignes dupliquées ignorées")
    
    return processed_data, list(suppliers), list(categories)

def create_suppliers(db: Session, suppliers: List[str]) -> None:
    """
    Crée les fournisseurs dans la base de données
    
    Args:
        db: Session de base de données
        suppliers: Liste des noms de fournisseurs
    """
    for supplier in suppliers:
        if not db.query(Fournisseurs).filter(Fournisseurs.nom == supplier).first():
            db.add(Fournisseurs(nom=supplier))
    db.commit()

def insert_glasses(db: Session, glasses_data: List[Dict]) -> None:
    """
    Insère les verres dans la base de données
    
    Args:
        db: Session de base de données
        glasses_data: Liste des données de verres à insérer
    """
    try:
        # Insertion en masse de tous les verres
        for glass_data in glasses_data:
            db.add(Verres(**glass_data))
        db.commit()
        db_logger.info(f"Import terminé avec succès pour {len(glasses_data)} verres")
    except Exception as e:
        db.rollback()
        db_logger.error(f"Erreur lors de l'insertion des verres : {str(e)}")
        raise