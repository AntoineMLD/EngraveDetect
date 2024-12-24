import json
import os
from collections import Counter

def analyze_materials(input_file):
    """
    Analyse les matériaux présents dans un fichier JSON et retourne les matériaux uniques avec leurs occurrences.
    :param input_file: Chemin du fichier JSON à analyser.
    """
    try:
        # Charger les données depuis le fichier JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extraire les matériaux
        materials = [item.get('material', '').strip().lower() for item in data if 'material' in item]

        # Compter les occurrences
        material_counts = Counter(materials)

        # Afficher les matériaux et leurs occurrences
        print("Liste des matériaux uniques trouvés :")
        for material, count in material_counts.items():
            print(f"{material}: {count} occurrences")

        # Retourner les matériaux uniques sous forme de liste
        return list(material_counts.keys())

    except Exception as e:
        print(f"Erreur lors de l'analyse des matériaux : {e}")
        return []

if __name__ == "__main__":
    # Emplacement du fichier à analyser
    input_file = "scrapper/data/cleaned_output.json"

    # Vérifier que le fichier d'entrée existe
    if not os.path.exists(input_file):
        print(f"Erreur : Le fichier d'entrée {input_file} n'existe pas.")
    else:
        analyze_materials(input_file)
