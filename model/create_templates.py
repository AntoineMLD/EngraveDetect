#!/usr/bin/env python3
"""
Script utilitaire pour créer le dossier de templates.
Copie une image de référence pour chaque symbole depuis le jeu d'entraînement.
"""
import logging
import os
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

# Configuration du logging
logging.basicConfig(level=logging.INFO)


def normalize_image(image_path, target_size=64):
    """
    Normalise une image selon les mêmes critères que l'interface de dessin.
    """
    try:
        # Ouvrir et convertir en noir et blanc
        image = Image.open(image_path).convert("L")

        # Convertir en numpy array pour un meilleur contrôle
        img_array = np.array(image)

        # Binariser avec un seuil adaptatif basé sur la moyenne
        threshold = np.mean(img_array)
        binary = (img_array > threshold).astype(np.uint8) * 255
        binary_image = Image.fromarray(binary)

        # Inverser l'image (dessin en noir sur fond blanc)
        inverted = ImageOps.invert(binary_image)

        # Trouver la boîte englobante
        bbox = inverted.getbbox()
        if not bbox:
            return None

        # Recadrer
        cropped = inverted.crop(bbox)

        # S'assurer que l'image n'est pas trop petite
        min_size = 10
        if cropped.size[0] < min_size or cropped.size[1] < min_size:
            return None

        # Ajouter une marge fixe de 4 pixels
        margin = 4
        padded_size = (cropped.size[0] + 2 * margin, cropped.size[1] + 2 * margin)
        padded = Image.new("L", padded_size, 255)
        padded.paste(cropped, (margin, margin))

        # Redimensionner en préservant le ratio
        w, h = padded.size
        if w > h:
            new_w = target_size
            new_h = int((h * target_size) / w)
        else:
            new_h = target_size
            new_w = int((w * target_size) / h)

        # S'assurer que les dimensions ne sont pas nulles
        new_w = max(new_w, 1)
        new_h = max(new_h, 1)

        resized = padded.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Centrer dans une image carrée
        final = Image.new("L", (target_size, target_size), 255)
        paste_x = (target_size - new_w) // 2
        paste_y = (target_size - new_h) // 2
        final.paste(resized, (paste_x, paste_y))

        return final

    except Exception as e:
        print(f"Erreur lors de la normalisation: {str(e)}")
        return None


def create_normalized_templates():
    """
    Crée des templates normalisés pour tous les symboles.
    """
    # Chemins des dossiers
    dataset_dir = Path("model/dataset/train")
    templates_dir = Path("model/templates")

    # Créer le dossier des templates s'il n'existe pas
    templates_dir.mkdir(parents=True, exist_ok=True)

    # Pour chaque symbole dans le dataset
    for symbol_dir in dataset_dir.iterdir():
        if not symbol_dir.is_dir():
            continue

        symbol_name = symbol_dir.name
        print(f"Traitement du symbole: {symbol_name}")

        # Créer le dossier du template
        template_dir = templates_dir / symbol_name
        template_dir.mkdir(exist_ok=True)

        # Essayer toutes les images jusqu'à en trouver une qui fonctionne
        success = False
        for image_path in symbol_dir.glob("*.png"):
            template = normalize_image(image_path)
            if template is not None:
                # Sauvegarder le template
                template_path = template_dir / "template.png"
                template.save(template_path)
                print(f"Template créé: {template_path}")
                success = True
                break

        if not success:
            print(f"Impossible de créer un template pour {symbol_name}")


def verify_templates():
    """
    Vérifie que tous les templates sont présents et conformes.
    """
    templates_dir = Path("model/templates")
    dataset_dir = Path("model/dataset/train")

    # Vérifier que chaque symbole a un template
    missing_templates = []
    invalid_templates = []

    for symbol_dir in dataset_dir.iterdir():
        if not symbol_dir.is_dir():
            continue

        symbol_name = symbol_dir.name
        template_path = templates_dir / symbol_name / "template.png"

        if not template_path.exists():
            missing_templates.append(symbol_name)
            continue

        # Vérifier que le template est une image valide de 64x64
        try:
            template = Image.open(template_path)
            if template.size != (64, 64):
                invalid_templates.append(symbol_name)
        except:
            invalid_templates.append(symbol_name)

    return missing_templates, invalid_templates


def main():
    print("Création des templates normalisés...")
    create_normalized_templates()

    print("\nVérification des templates...")
    missing, invalid = verify_templates()

    if missing:
        print("\nTemplates manquants:")
        for symbol in missing:
            print(f"- {symbol}")

    if invalid:
        print("\nTemplates invalides:")
        for symbol in invalid:
            print(f"- {symbol}")

    if not missing and not invalid:
        print("\nTous les templates sont conformes!")


if __name__ == "__main__":
    main()
