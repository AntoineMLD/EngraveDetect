import cv2
import numpy as np
import os

def refine_traced_images(input_dir, output_dir):
    """
    Affine les tracés pour qu'ils soient plus précis et uniformes, adaptés à la reconnaissance utilisateur.
    
    Args:
        input_dir (str): Dossier contenant les images originales.
        output_dir (str): Dossier pour sauvegarder les résultats.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename.replace('.jpg', '.png'))

            # Charger l'image
            image = cv2.imread(file_path)
            
            # Vérification si l'image est bien chargée
            if image is None:
                print(f"Erreur : Impossible de charger l'image {file_path}. Vérifiez le chemin ou l'intégrité du fichier.")
                continue

            try:
                # Conversion en niveaux de gris
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                # Réduction de bruit
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)

                # Seuil adaptatif pour détecter les zones claires et sombres
                adaptive_thresh = cv2.adaptiveThreshold(
                    blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
                )

                # Trouver les contours
                contours, _ = cv2.findContours(adaptive_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Créer une image blanche pour les tracés
                traced_image = np.ones_like(gray) * 255

                for contour in contours:
                    # Ajustement des contours pour conserver plus de détails
                    epsilon = 0.005 * cv2.arcLength(contour, True)
                    refined_contour = cv2.approxPolyDP(contour, epsilon, True)

                    # Tracer les contours raffinés
                    cv2.drawContours(traced_image, [refined_contour], -1, (0, 0, 0), 1)

                # Sauvegarder l'image résultante
                cv2.imwrite(output_path, traced_image)
                print(f"{filename}: Traitement raffiné terminé.")

            except Exception as e:
                print(f"Erreur lors du traitement de {filename}: {e}")

if __name__ == "__main__":
    input_directory = "data/original_engraving/"
    output_directory = "data/refined_traced_engraving/"

    refine_traced_images(input_directory, output_directory)
    print("Affinage des tracés terminé.")
