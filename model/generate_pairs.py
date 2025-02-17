#!/usr/bin/env python3
"""
Script de génération de paires d'images pour l'entraînement d'un réseau siamois.
Ce script parcourt les dossiers train/val/test et génère des paires d'images :
- Paires positives : deux images de la même catégorie (label=1)
- Paires négatives : deux images de catégories différentes (label=0)
Les paires sont équilibrées (autant de positives que de négatives) et
sauvegardées dans des fichiers CSV pour chaque ensemble de données.
"""
import os
import csv
import random
from pathlib import Path
from typing import List, Tuple, Dict
from itertools import combinations
import logging
# Configuration du logging
logging.basicConfig(level=logging.INFO)
class PairGenerator:
    """
    Classe gérant la génération de paires d'images pour l'entraînement du réseau siamois.
    """
    
    def __init__(self, dataset_dir: Path, output_dir: Path, splits: List[str]):
        """
        Initialise le générateur de paires.
        
        Args:
            dataset_dir (Path): Chemin vers le dossier contenant les sous-dossiers train/val/test
            output_dir (Path): Chemin vers le dossier où sauvegarder les fichiers CSV
            splits (List[str]): Liste des splits à générer ('train', 'val', 'test')
        """
        self.dataset_dir = dataset_dir
        self.output_dir = output_dir
        
        # Création du dossier de sortie
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.splits = splits
    
    def get_category_images(self, split_dir: Path) -> Dict[str, List[Path]]:
        """
        Récupère toutes les images par catégorie pour un split donné.
        
        Args:
            split_dir (Path): Chemin vers le dossier du split (train/val/test)
            
        Returns:
            Dict[str, List[Path]]: Dictionnaire {catégorie: liste des chemins d'images}
        """
        categories = {}
        for category_dir in split_dir.iterdir():
            if category_dir.is_dir():
                images = list(category_dir.glob('*.png'))
                if images:  # Ne garde que les catégories non vides
                    categories[category_dir.name] = images
        return categories
    
    def generate_positive_pairs(self, images: List[Path], num_pairs: int) -> List[Tuple[Path, Path]]:
        """
        Génère des paires positives à partir d'une liste d'images de la même catégorie.
        
        Args:
            images (List[Path]): Liste des chemins d'images
            num_pairs (int): Nombre de paires à générer
            
        Returns:
            List[Tuple[Path, Path]]: Liste de paires d'images
        """
        # Génère toutes les combinaisons possibles
        all_pairs = list(combinations(images, 2))
        
        # Si on demande plus de paires que possible, on duplique certaines paires
        if num_pairs > len(all_pairs):
            return random.choices(all_pairs, k=num_pairs)
        
        # Sinon, on sélectionne aléatoirement le nombre demandé
        return random.sample(all_pairs, num_pairs)
    
    def generate_negative_pairs(self, categories: Dict[str, List[Path]], 
                              num_pairs: int) -> List[Tuple[Path, Path]]:
        """
        Génère des paires négatives en prenant des images de catégories différentes.
        
        Args:
            categories (Dict[str, List[Path]]): Dictionnaire des images par catégorie
            num_pairs (int): Nombre de paires à générer
            
        Returns:
            List[Tuple[Path, Path]]: Liste de paires d'images
        """
        negative_pairs = []
        category_names = list(categories.keys())
        
        while len(negative_pairs) < num_pairs:
            # Sélectionne deux catégories différentes au hasard
            cat1, cat2 = random.sample(category_names, 2)
            
            # Sélectionne une image aléatoire de chaque catégorie
            img1 = random.choice(categories[cat1])
            img2 = random.choice(categories[cat2])
            
            negative_pairs.append((img1, img2))
        
        return negative_pairs
    
    def generate_pairs_for_split(self, split: str, pairs_per_category: int = 100):
        """
        Génère des paires positives et négatives pour un split donné.
        
        Args:
            split (str): Nom du split ('train', 'val' ou 'test')
            pairs_per_category (int): Nombre de paires positives à générer par catégorie
        """
        split_dir = self.dataset_dir / split
        categories = self.get_category_images(split_dir)
        
        all_pairs = []  # Liste pour stocker toutes les paires avec leurs labels
        total_positive_pairs = 0
        
        # Génère les paires positives pour chaque catégorie
        for category, images in categories.items():
            positive_pairs = self.generate_positive_pairs(images, pairs_per_category)
            all_pairs.extend((img1, img2, 1) for img1, img2 in positive_pairs)
            total_positive_pairs += len(positive_pairs)
        
        # Génère autant de paires négatives que de paires positives
        negative_pairs = self.generate_negative_pairs(categories, total_positive_pairs)
        all_pairs.extend((img1, img2, 0) for img1, img2 in negative_pairs)
        
        # Mélange aléatoirement toutes les paires
        random.shuffle(all_pairs)
        
        # Sauvegarde dans un fichier CSV
        csv_path = self.output_dir / f'{split}_pairs.csv'
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['image1_path', 'image2_path', 'same_symbol'])
            for img1, img2, label in all_pairs:
                writer.writerow([
                    str(img1.relative_to(self.dataset_dir)),
                    str(img2.relative_to(self.dataset_dir)),
                    label
                ])
        
        logging.info(f"Généré {len(all_pairs)} paires pour {split} "
                    f"({total_positive_pairs} positives, {len(negative_pairs)} négatives)")
    
    def generate_all_pairs(self, pairs_per_category: int = 100):
        """
        Génère les paires pour tous les splits (train/val/test).
        
        Args:
            pairs_per_category (int): Nombre de paires positives à générer par catégorie
        """
        for split in self.splits:
            logging.info(f"Génération des paires pour {split}")
            self.generate_pairs_for_split(split, pairs_per_category)
def main():
    """
    Point d'entrée principal
    """
    generator = PairGenerator(
        dataset_dir=Path("model/dataset"),
        output_dir=Path("model/pairs"),
        splits=["train", "test"]  # Changé 'val' en 'test'
    )
    generator.generate_all_pairs()
if __name__ == "__main__":
    main() 