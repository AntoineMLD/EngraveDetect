#!/usr/bin/env python3
import os
import random
import shutil
from pathlib import Path



def create_dataset(source_dir="model/drawing_normalized", 
                  output_dir="model/dataset",
                  train_ratio=0.8):

    """
    Crée les datasets d'entraînement et de test à partir des images normalisées.

    Args:
        source_dir: Dossier contenant les images normalisées par catégorie
        output_dir: Dossier de sortie pour les datasets train/test
        train_ratio: Ratio d'images pour l'entraînement (0.8 = 80% train, 20% test)
    """
    source_path = Path(source_dir)
    output_path = Path(output_dir)

    # Créer les dossiers train et test
    train_dir = output_path / "train"
    test_dir = output_path / "test"

    train_dir.mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(parents=True, exist_ok=True)

    # Pour chaque catégorie
    for category_dir in source_path.iterdir():
        if not category_dir.is_dir():
            continue

        category_name = category_dir.name
        print(f"Traitement de la catégorie : {category_name}")

        # Créer les sous-dossiers pour cette catégorie
        (train_dir / category_name).mkdir(exist_ok=True)
        (test_dir / category_name).mkdir(exist_ok=True)

        # Lister toutes les images de la catégorie
        images = list(category_dir.glob("*.png"))

        # Séparer les images originales et augmentées
        original_images = [img for img in images if "_aug" not in img.name]
        augmented_images = [img for img in images if "_aug" in img.name]

        # Mélanger les images originales
        random.shuffle(original_images)

        # Calculer le nombre d'images pour l'entraînement
        n_train = int(len(original_images) * train_ratio)

        # Séparer en train et test
        train_originals = original_images[:n_train]
        test_originals = original_images[n_train:]

        # Copier les images originales
        for img in train_originals:
            shutil.copy2(img, train_dir / category_name)
            # Copier aussi les versions augmentées correspondantes
            img_base = img.stem.split("_aug")[0]
            for aug_img in augmented_images:
                if aug_img.stem.startswith(img_base):
                    shutil.copy2(aug_img, train_dir / category_name)

        for img in test_originals:
            shutil.copy2(img, test_dir / category_name)

        print(f"  Train: {len(list((train_dir / category_name).glob('*.png')))} images")
        print(f"  Test: {len(list((test_dir / category_name).glob('*.png')))} images")


if __name__ == "__main__":
    create_dataset()
