import sys
import os
from pathlib import Path

# Ajoute le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from database.config.database import get_db
from sqlalchemy import text
from typing import List, Dict
from tabulate import tabulate

def check_null_counts() -> List[Dict]:
    """
    Vérifie le nombre de valeurs NULL pour chaque colonne de la table verres
    et calcule les pourcentages.
    """
    results = []
    
    columns = [
        'categorie', 'nom_verre', 'gravure_url', 'indice',
        'materiau', 'has_image', 'fournisseur_nom'
    ]
    
    query_template = """
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE {col} IS NULL) as nulls,
            CAST(
                (COUNT(*) FILTER (WHERE {col} IS NULL))::float * 100 / NULLIF(COUNT(*), 0) 
                AS DECIMAL(10,2)
            ) as percentage
        FROM verres
    """
    
    with get_db() as db:
        for column in columns:
            query = text(query_template.format(col=column))
            result = db.execute(query).fetchone()
            
            results.append({
                'colonne': column,
                'total': result[0],
                'null': result[1],
                'pourcentage': result[2] if result[2] is not None else 0.0
            })
    
    return results

def main():
    """
    Fonction principale qui affiche les résultats dans un tableau formaté
    """
    try:
        print("\nAnalyse des valeurs NULL dans la table 'verres':\n")
        
        results = check_null_counts()
        
        # Préparation des données pour le tableau
        headers = ['Colonne', 'Total', 'NULL', '% NULL']
        table_data = [
            [r['colonne'], r['total'], r['null'], f"{r['pourcentage']}%"]
            for r in results
        ]
        
        # Affichage du tableau
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        print()
        
    except Exception as e:
        print(f"Erreur lors de l'analyse : {str(e)}")

if __name__ == "__main__":
    main()