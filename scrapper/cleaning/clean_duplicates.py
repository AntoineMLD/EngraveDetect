import json
import os


def remove_duplicates(input_file, output_file):
    """
    Supprime les doublons dans un fichier JSON en se basant sur des clés uniques.
    :param input_file: Chemin du fichier JSON à nettoyer.
    :param output_file: Chemin où sauvegarder le fichier nettoyé.
    """
    try:
        # Charger les données depuis le fichier JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Utiliser une clé unique pour identifier chaque item
        unique_items = {
            json.dumps({
                "category": item.get("category", "").strip().lower(),
                "glass_name": item.get("glass_name", "").strip().lower(),
                "glass_index": item.get("glass_index", ""),
                "material": item.get("material", "").strip().lower(),
                "glass_supplier_id": item.get("glass_supplier_id", "")
            }, sort_keys=True): item for item in data
        }

        # Obtenir les données nettoyées
        cleaned_data = list(unique_items.values())

        # Sauvegarder les données nettoyées dans un nouveau fichier
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

        print(f"Suppression des doublons terminée. Fichier nettoyé sauvegardé à : {output_file}")
        print(f"Nombre d'éléments avant nettoyage : {len(data)}")
        print(f"Nombre d'éléments après nettoyage : {len(cleaned_data)}")

    except Exception as e:
        print(f"Erreur lors du nettoyage des doublons : {e}")


if __name__ == "__main__":
    # Emplacements des fichiers
    input_file = "scrapper/data/output.json"  # Fichier JSON original
    output_file = "scrapper/data/cleaned_output.json"  # Fichier nettoyé

    # Vérifier que le fichier d'entrée existe
    if not os.path.exists(input_file):
        print(f"Erreur : Le fichier d'entrée {input_file} n'existe pas.")
    else:
        remove_duplicates(input_file, output_file)
