#!/usr/bin/env python3
import os
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms


class SiameseDataset(Dataset):
    """
    Dataset pour charger les paires d'images pour l'entraînement du réseau siamois.
    Lit les paires depuis un fichier CSV et applique les transformations nécessaires.
    """
    def __init__(self, csv_file, root_dir, transform=None):
        """
        Args:
            csv_file (str): Chemin vers le fichier CSV contenant les paires d'images.
            root_dir (str): Dossier racine contenant les images.
            transform (callable, optional): Transformations à appliquer aux images.
        """
        self.pairs_frame = pd.read_csv(csv_file)
        self.root_dir = Path(root_dir)
        self.transform = transform or transforms.Compose([
            transforms.Resize((64, 64)),  # Redimensionner à 64x64 pour le modèle
            transforms.ToTensor()
        ])
    def __len__(self):
        return len(self.pairs_frame)
    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        # Récupérer les chemins des images
        img1_path = str(self.root_dir / self.pairs_frame.iloc[idx, 0].replace('\\', '/'))
        img2_path = str(self.root_dir / self.pairs_frame.iloc[idx, 1].replace('\\', '/'))
        
        try:
            # Charger et transformer les images
            image1 = Image.open(img1_path).convert('L')  # Convertir en niveaux de gris
            image2 = Image.open(img2_path).convert('L')  # Convertir en niveaux de gris
            
            if self.transform:
                image1 = self.transform(image1)
                image2 = self.transform(image2)
            # Récupérer le label (1 si même symbole, 0 sinon)
            label = self.pairs_frame.iloc[idx, 2]
            
            return image1, image2, torch.tensor(label, dtype=torch.float32)
            
        except Exception as e:
            print(f"Erreur lors du chargement des images:")
            print(f"Image 1: {img1_path}")
            print(f"Image 2: {img2_path}")
            raise e 