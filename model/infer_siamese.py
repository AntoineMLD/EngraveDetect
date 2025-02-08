#!/usr/bin/env python3

"""
Script d'inférence pour le réseau siamois.
Permet de :
- Charger le modèle entraîné
- Calculer l'embedding d'une nouvelle image
- Comparer avec une base de templates
- Identifier le symbole le plus proche
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image, ImageOps
from torchvision import transforms

from .siamese_model import SiameseNetwork

# Configuration du logging
logging.basicConfig(level=logging.INFO)


class SiamesePredictor:
    """
    Classe pour l'inférence avec le réseau siamois.
    """

    def __init__(
        self,
        model: torch.nn.Module,
        device: torch.device,
        image_size: int = 64,
        similarity_threshold: float = 0.4488,
    ):
        """
        Initialise le prédicteur.

        Args:
            model: Le réseau siamois
            device: Device sur lequel effectuer les calculs
            image_size: Taille des images après redimensionnement
            similarity_threshold: Seuil de similarité (déterminé lors de l'évaluation)
        """
        self.model = model.to(device)
        self.device = device
        self.similarity_threshold = similarity_threshold
        self.image_size = image_size
        self.model.eval()

        # Transformations de base (comme pendant l'entraînement)
        self.transform = transforms.Compose(
            [
                transforms.Grayscale(),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5], std=[0.5]),  # Normalisation standard
            ]
        )

    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Prétraite une image pour le réseau siamois."""
        try:
            # Convertit en niveaux de gris
            gray_image = image.convert("L")

            # Binarise l'image avec un seuil adaptatif
            img_array = np.array(gray_image)
            threshold = np.mean(
                img_array
            )  # Utilise la moyenne comme dans create_templates.py
            binary = (img_array > threshold).astype(np.uint8) * 255
            binary_image = Image.fromarray(binary)

            # Inverse l'image (dessin en noir sur fond blanc)
            inverted = ImageOps.invert(binary_image)

            # Trouve la boîte englobante
            bbox = inverted.getbbox()
            if not bbox:
                return None

            # Recadre l'image
            cropped = inverted.crop(bbox)

            # Vérifie la taille minimale
            min_size = 10
            if cropped.size[0] < min_size or cropped.size[1] < min_size:
                return None

            # Ajoute une marge fixe comme dans create_templates.py
            margin = 4
            padded_size = (cropped.size[0] + 2 * margin, cropped.size[1] + 2 * margin)
            padded = Image.new("L", padded_size, 255)
            padded.paste(cropped, (margin, margin))

            # Redimensionne en préservant le ratio
            w, h = padded.size
            if w > h:
                new_w = self.image_size
                new_h = int((h * self.image_size) / w)
            else:
                new_h = self.image_size
                new_w = int((w * self.image_size) / h)

            new_w = max(new_w, 1)
            new_h = max(new_h, 1)
            resized = padded.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # Centre dans une image carrée
            final = Image.new("L", (self.image_size, self.image_size), 255)
            paste_x = (self.image_size - new_w) // 2
            paste_y = (self.image_size - new_h) // 2
            final.paste(resized, (paste_x, paste_y))

            # Applique les transformations finales
            tensor = self.transform(final)
            return tensor.unsqueeze(0).to(self.device)

        except Exception as e:
            print(f"Erreur lors du prétraitement: {str(e)}")
            return None

    def load_image(self, image_path: Path) -> torch.Tensor:
        """Charge et prétraite une image."""
        image = Image.open(image_path)
        return self.preprocess_image(image)

    def compare_images(
        self, img1_tensor: torch.Tensor, img2_tensor: torch.Tensor
    ) -> float:
        """Compare deux images en utilisant le modèle siamois."""
        with torch.no_grad():
            # Passe les deux images dans le modèle siamois
            output1 = self.model.forward_once(img1_tensor)
            output2 = self.model.forward_once(img2_tensor)

            # Calcule la distance euclidienne (comme pendant l'entraînement)
            distance = F.pairwise_distance(output1, output2).item()

            # Convertit la distance en similarité (0 à 1)
            max_dist = 2.0  # Distance maximale possible avec des vecteurs normalisés
            similarity = 1 - (distance / max_dist)

            return similarity

    def find_closest_symbol(self, image_path: Path) -> Tuple[str, float]:
        """Trouve le symbole le plus proche pour une nouvelle image."""
        # Charge et prétraite l'image d'entrée
        image = Image.open(image_path)
        input_tensor = self.preprocess_image(image)
        if input_tensor is None:
            return None, 0.0

        # Compare avec tous les templates
        best_symbol = None
        best_similarity = -1
        similarities = {}

        for symbol_name, template_path in self.templates.items():
            # Charge et prétraite le template
            template = Image.open(template_path)
            template_tensor = self.preprocess_image(template)
            if template_tensor is None:
                continue

            # Compare les images
            similarity = self.compare_images(input_tensor, template_tensor)
            similarities[symbol_name] = similarity

            if similarity > best_similarity:
                best_similarity = similarity
                best_symbol = symbol_name

        # Affiche les similarités pour le débogage
        print("\nSimilarités avec les templates:")
        for symbol, similarity in sorted(
            similarities.items(), key=lambda x: x[1], reverse=True
        )[
            :5
        ]:  # Top 5 seulement
            print(f"- {symbol}: {similarity:.2%}")

        return best_symbol, best_similarity

    def load_templates(self, templates_dir: Path):
        """Charge tous les templates depuis un dossier."""
        self.templates = {}
        for symbol_dir in templates_dir.iterdir():
            if symbol_dir.is_dir():
                template_files = list(symbol_dir.glob("template.png"))
                if template_files:
                    self.templates[symbol_dir.name] = template_files[0]
                    logging.info(f"Template ajouté pour le symbole '{symbol_dir.name}'")

    def predict(self, image_path: Path) -> Dict:
        """Prédit le symbole pour une nouvelle image."""
        symbol, similarity = self.find_closest_symbol(image_path)

        return {
            "image_path": str(image_path),
            "predicted_symbol": symbol,
            "similarity_score": similarity,
            "is_confident": similarity >= self.similarity_threshold,
        }


def main():
    """
    Point d'entrée principal du script.
    """
    # Paramètres
    IMAGE_SIZE = 64

    # Chemins
    model_dir = Path("model/models")
    templates_dir = Path("model/templates")
    templates_dir.mkdir(parents=True, exist_ok=True)

    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info(f"Utilisation du device: {device}")

    # Chargement du modèle
    model = SiameseNetwork()
    checkpoint = torch.load(model_dir / "best_model.pth")
    model.load_state_dict(checkpoint["model_state_dict"])
    logging.info(f"Modèle chargé depuis l'époque {checkpoint['epoch']}")

    # Création du prédicteur
    predictor = SiamesePredictor(model, device, IMAGE_SIZE)

    # Chargement des templates
    logging.info("Chargement des templates...")
    predictor.load_templates(templates_dir)

    # Test sur une image si fournie en argument
    import sys

    if len(sys.argv) > 1:
        image_path = Path(sys.argv[1])
        if image_path.exists():
            prediction = predictor.predict(image_path)
            print("\nRésultat de la prédiction :")
            print(json.dumps(prediction, indent=2, ensure_ascii=False))
        else:
            logging.error(f"Image non trouvée : {image_path}")
    else:
        logging.info(
            "Aucune image fournie. Usage : python infer_siamese.py <chemin_image>"
        )


def load_templates():
    """
    Charge les templates et retourne un prédicteur initialisé.

    Returns:
        SiamesePredictor: Instance du prédicteur initialisé avec les templates
    """
    # Paramètres
    IMAGE_SIZE = 64

    # Chemins
    model_dir = Path("model/models")
    templates_dir = Path("model/templates")
    templates_dir.mkdir(parents=True, exist_ok=True)

    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info(f"Utilisation du device: {device}")

    # Chargement du modèle
    model = SiameseNetwork()
    model_path = model_dir / "best_model.pth"

    if not model_path.exists():
        raise FileNotFoundError(f"Modèle non trouvé : {model_path}")

    checkpoint = torch.load(model_path, map_location=device)
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
        logging.info(f"Modèle chargé depuis l'époque {checkpoint['epoch']}")
    else:
        model.load_state_dict(checkpoint)
        logging.info("Modèle chargé")

    model.eval()  # Mettre le modèle en mode évaluation

    # Création du prédicteur
    predictor = SiamesePredictor(model, device, IMAGE_SIZE)

    # Chargement des templates
    logging.info("Chargement des templates...")
    predictor.load_templates(templates_dir)

    return predictor


def predict_symbol(
    image_path: str,
    model: torch.nn.Module,
    templates: SiamesePredictor,
    device: torch.device,
) -> Tuple[str, float]:
    """
    Prédit le symbole pour une image donnée.

    Args:
        image_path: Chemin vers l'image à classifier
        model: Le modèle Siamese (non utilisé car déjà dans le prédicteur)
        templates: Le prédicteur avec les templates chargés
        device: Device pour les calculs (non utilisé car déjà dans le prédicteur)

    Returns:
        Tuple[str, float]: Symbole prédit et score de similarité
    """
    prediction = templates.predict(Path(image_path))
    return prediction["predicted_symbol"], prediction["similarity_score"]


if __name__ == "__main__":
    main()
