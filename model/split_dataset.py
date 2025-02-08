#!/usr/bin/env python3
"""
Script de séparation du dataset en ensembles d'entraînement, validation et test.

Ce script prend en entrée un dossier contenant des sous-dossiers de catégories d'images
et les répartit en trois ensembles :
- Entraînement (70%)
- Validation (15%)
- Test (15%)

Les images sont soit déplacées physiquement dans des dossiers correspondants,
soit référencées dans un fichier JSON avec leurs labels et leur attribution.
"""

import json
import logging
import os
import random
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np

# Configuration du logging
logging.basicConfig(level=logging.INFO)


class DatasetSplitter:
    """
    Classe gérant la séparation du dataset en ensembles d'entraînement, validation et test.
    """

    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        use_json: bool = True,
    ):
        """
        Initialise le splitter avec les paramètres de séparation.

        Args:
            input_dir (Path): Chemin vers le dossier contenant les images normalisées
            output_dir (Path): Chemin vers le dossier de sortie
            train_ratio (float): Proportion d'images pour l'entraînement (défaut: 0.7)
            val_ratio (float): Proportion d'images pour la validation (défaut: 0.15)
            use_json (bool): Si True, crée un fichier JSON au lieu de déplacer les fichiers
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = 1.0 - train_ratio - val_ratio
        self.use_json = use_json

        # Vérification des ratios
        if not 0.99 < (train_ratio + val_ratio + self.test_ratio) < 1.01:
            raise ValueError("La somme des ratios doit être égale à 1")

        # Création du dossier de sortie
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Création des sous-dossiers si nécessaire
        if not use_json:
            for split in ["train", "val", "test"]:
                (output_dir / split).mkdir(parents=True, exist_ok=True)

    def get_image_files(self, category_dir: Path) -> List[Path]:
        """
        Récupère la liste des fichiers images dans un dossier de catégorie.

        Args:
            category_dir (Path): Chemin vers le dossier de la catégorie

        Returns:
            List[Path]: Liste des chemins vers les images
        """
        # Récupère tous les fichiers PNG dans le dossier et ses sous-dossiers
        return list(category_dir.glob("**/*.png"))

    def split_files(
        self, files: List[Path]
    ) -> Tuple[List[Path], List[Path], List[Path]]:
        """
        Sépare une liste de fichiers en trois ensembles selon les ratios définis.

        Args:
            files (List[Path]): Liste des fichiers à séparer

        Returns:
            Tuple[List[Path], List[Path], List[Path]]: Listes des fichiers pour train, val et test
        """
        # Mélange aléatoire des fichiers
        random.shuffle(files)

        # Calcul des indices de séparation
        n_files = len(files)
        train_idx = int(n_files * self.train_ratio)
        val_idx = train_idx + int(n_files * self.val_ratio)

        # Séparation des fichiers
        train_files = files[:train_idx]
        val_files = files[train_idx:val_idx]
        test_files = files[val_idx:]

        return train_files, val_files, test_files

    def process_category(self, category_dir: Path) -> Dict:
        """
        Traite une catégorie en séparant ses images en trois ensembles.

        Args:
            category_dir (Path): Chemin vers le dossier de la catégorie

        Returns:
            Dict: Dictionnaire contenant les informations de séparation si use_json=True
        """
        category_name = category_dir.name
        files = self.get_image_files(category_dir)
        train_files, val_files, test_files = self.split_files(files)

        if self.use_json:
            # Création du dictionnaire pour le JSON
            return {
                "category": category_name,
                "train": [str(f.relative_to(self.input_dir)) for f in train_files],
                "val": [str(f.relative_to(self.input_dir)) for f in val_files],
                "test": [str(f.relative_to(self.input_dir)) for f in test_files],
            }
        else:
            # Déplacement physique des fichiers
            for split_name, split_files in [
                ("train", train_files),
                ("val", val_files),
                ("test", test_files),
            ]:
                split_dir = self.output_dir / split_name / category_name
                split_dir.mkdir(parents=True, exist_ok=True)

                for file in split_files:
                    dest = split_dir / file.name
                    shutil.copy2(file, dest)
                    logging.info(f"Copié {file.name} vers {split_name}/{category_name}")

            return None

    def process_dataset(self):
        """
        Traite l'ensemble du dataset en parcourant toutes les catégories.
        """
        dataset_info = []

        # Parcours de chaque catégorie dans le dossier d'entrée
        for category_dir in self.input_dir.iterdir():
            if category_dir.is_dir():
                logging.info(f"Traitement de la catégorie : {category_dir.name}")
                info = self.process_category(category_dir)

                if info:
                    dataset_info.append(info)

        # Si on utilise JSON, sauvegarde des informations
        if self.use_json:
            json_path = self.output_dir / "dataset_split.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(dataset_info, f, ensure_ascii=False, indent=2)
            logging.info(f"Informations de séparation sauvegardées dans {json_path}")


def extract_symbol(image: np.ndarray) -> np.ndarray:
    """
    Extrait et centre le symbole dans l'image en préservant son intégrité.

    Args:
        image: Image en niveaux de gris

    Returns:
        Image recadrée et centrée contenant le symbole
    """
    # Seuillage pour isoler le symbole (fond blanc = 255)
    _, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)

    # Trouve les contours du symbole
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return image

    # Trouve le plus grand contour (le symbole)
    main_contour = max(contours, key=cv2.contourArea)

    # Obtient le rectangle englobant avec une marge
    x, y, w, h = cv2.boundingRect(main_contour)
    margin = 10  # pixels de marge

    # Calcule les nouvelles dimensions en préservant le ratio
    max_dim = max(w, h) + 2 * margin
    square_size = max_dim

    # Crée une image carrée blanche
    square_img = np.full((square_size, square_size), 255, dtype=np.uint8)

    # Calcule les positions pour centrer le symbole
    start_x = (square_size - w) // 2
    start_y = (square_size - h) // 2

    # Copie le symbole dans l'image carrée
    roi = image[y : y + h, x : x + w]
    square_img[start_y : start_y + h, start_x : start_x + w] = roi

    return square_img


def process_image(image_path: Path, output_path: Path):
    """
    Traite une image pour l'ajouter au dataset.

    Args:
        image_path: Chemin de l'image source
        output_path: Chemin où sauvegarder l'image traitée
    """
    # Lecture de l'image en niveaux de gris
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    if image is None:
        logging.error(f"Impossible de lire l'image : {image_path}")
        return

    # Extraction et centrage du symbole
    processed = extract_symbol(image)

    # Redimensionnement avec préservation du ratio
    target_size = 64
    h, w = processed.shape
    ratio = min(target_size / w, target_size / h)
    new_w = int(w * ratio)
    new_h = int(h * ratio)

    resized = cv2.resize(processed, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

    # Création d'une image carrée avec padding
    final = np.full((target_size, target_size), 255, dtype=np.uint8)
    x_offset = (target_size - new_w) // 2
    y_offset = (target_size - new_h) // 2
    final[y_offset : y_offset + new_h, x_offset : x_offset + new_w] = resized

    # Sauvegarde de l'image
    cv2.imwrite(str(output_path), final)


def main():
    """
    Point d'entrée principal du script.
    """
    # Définition des chemins
    input_dir = Path("model/gravures_normalisees")
    output_dir = Path("model/dataset")

    # Création du splitter et traitement du dataset
    # use_json=False pour créer une copie physique des fichiers
    splitter = DatasetSplitter(input_dir, output_dir, use_json=False)
    splitter.process_dataset()


if __name__ == "__main__":
    main()
