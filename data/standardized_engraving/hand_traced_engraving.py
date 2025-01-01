import cv2
import numpy as np
import os

def prepare_traced_images(input_dir, output_dir):
    """
    Prépare les images pour qu'elles ressemblent à des tracés faits à la main.
    
    Args:
        input_dir (str): Dossier contenant les images originales.
        output_dir (str): Dossier pour sauvegarder les résultats.
    """
    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        # Vérifier les extensions de fichiers
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename.replace('.jpg', '.png'))

            # Charger l'image
            image = cv2.imread(file_path)

            # Vérifier si l'image a été chargée correctement
            if image is None:
                print(f"Erreur : Impossible de charger le fichier {file_path}. Vérifiez le chemin ou l'intégrité du fichier.")
                continue

            try:
                # Conversion en niveaux de gris
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                # Réduction de bruit
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)

                # Détection des contours
                edges = cv2.Canny(blurred, 50, 150)

                # Trouver les contours
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Créer une image blanche pour les tracés
                traced_image = np.ones_like(gray) * 255

                for contour in contours:
                    # Simplification des contours
                    epsilon = 0.01 * cv2.arcLength(contour, True)
                    simplified_contour = cv2.approxPolyDP(contour, epsilon, True)

                    # Tracer les contours simplifiés
                    cv2.drawContours(traced_image, [simplified_contour], -1, (0, 0, 0), 1)

                # Sauvegarder l'image résultante
                cv2.imwrite(output_path, traced_image)
                print(f"{filename}: Traitement terminé.")

            except Exception as e:
                print(f"Erreur lors du traitement de {filename}: {e}")

if __name__ == "__main__":
    input_directory = "data/original_engraving/"
    output_directory = "data/hand_traced_engraving/"

    prepare_traced_images(input_directory, output_directory)
    print("Préparation des images avec tracés manuels terminée.")
