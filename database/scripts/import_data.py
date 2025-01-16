import pandas as pd
from database.config.database import get_db
from database.utils.logger import db_logger
from database.scripts.data_processing import process_glass_data, create_suppliers, insert_glasses

def import_data(csv_path: str) -> None:
    """
    Importe les données depuis le fichier CSV dans la base de données
    
    Args:
        csv_path: Chemin vers le fichier CSV
    """
    try:
        # Lecture du fichier CSV
        db_logger.info(f"Début de la lecture du fichier {csv_path}")
        df = pd.read_csv(csv_path)
        db_logger.info(f"Fichier lu avec succès : {len(df)} lignes trouvées")
        
        # Traitement des données
        db_logger.info("Début du traitement des données")
        glasses_data, suppliers, categories = process_glass_data(df)
        db_logger.info(f"Données traitées : {len(glasses_data)} verres, "
                      f"{len(suppliers)} fournisseurs, {len(categories)} catégories")
        
        # Insertion dans la base de données
        with get_db() as db:
            db_logger.info("Création des fournisseurs")
            create_suppliers(db, suppliers)
            
            db_logger.info("Insertion des verres")
            insert_glasses(db, glasses_data)
            
        db_logger.info("Import terminé avec succès")
        
    except Exception as e:
        db_logger.error(f"Erreur lors de l'import des données: {str(e)}")
        raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python import_data.py <chemin_vers_csv>")
        sys.exit(1)
        
    csv_path = sys.argv[1]
    import_data(csv_path)