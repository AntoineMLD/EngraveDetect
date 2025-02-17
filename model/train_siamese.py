#!/usr/bin/env python3
"""
Script d'entraînement du réseau siamois pour la reconnaissance de symboles gravés.
Ce script :
- Charge les paires d'images depuis les fichiers CSV
- Entraîne le réseau siamois avec la perte contrastive
- Évalue les performances sur l'ensemble de validation
- Sauvegarde le meilleur modèle
"""
import csv
import logging
import os
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from PIL import Image
from siamese_model import ContrastiveLoss, SiameseNetwork
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

# Configuration du logging
logging.basicConfig(level=logging.INFO)


class PairDataset(Dataset):
    """Dataset de paires d'images pour l'entraînement du réseau siamois"""

    def __init__(self, csv_file, dataset_dir, transform=None):
        """
        Args:
            csv_file (str): Chemin vers le fichier CSV contenant les paires
            dataset_dir (str): Chemin vers le dossier contenant les images
            transform (callable, optional): Transformation à appliquer aux images
        """
        self.pairs_df = pd.read_csv(csv_file)
        self.dataset_dir = Path(
            dataset_dir
        ).parent  # On remonte d'un niveau car les chemins dans le CSV incluent train/test
        self.transform = transform

    def __len__(self):
        return len(self.pairs_df)

    def __getitem__(self, idx):
        # Récupérer les chemins des images et le label
        img1_path = self.dataset_dir / self.pairs_df.iloc[idx, 0]
        img2_path = self.dataset_dir / self.pairs_df.iloc[idx, 1]
        label = self.pairs_df.iloc[idx, 2]

        # Charger les images
        img1 = Image.open(img1_path).convert("L")  # Conversion en niveaux de gris
        img2 = Image.open(img2_path).convert("L")

        # Appliquer les transformations si nécessaire
        if self.transform:
            img1 = self.transform(img1)
            img2 = self.transform(img2)

        return img1, img2, torch.tensor(label, dtype=torch.float32)


class SiameseTrainer:
    """
    Classe gérant l'entraînement et l'évaluation du réseau siamois.
    """

    def __init__(
        self,
        model: nn.Module,
        criterion: nn.Module,
        optimizer: optim.Optimizer,
        device: torch.device,
        model_dir: Path,
    ):
        """
        Initialise le trainer.

        Args:
            model (nn.Module): Le réseau siamois
            criterion (nn.Module): La fonction de perte
            optimizer (optim.Optimizer): L'optimiseur
            device (torch.device): Le device sur lequel effectuer les calculs
            model_dir (Path): Dossier où sauvegarder les modèles
        """
        self.model = model.to(device)
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device
        self.model_dir = model_dir
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.best_val_loss = float("inf")

    def train_epoch(self, train_loader: DataLoader) -> float:
        """
        Entraîne le modèle pendant une époque.

        Args:
            train_loader (DataLoader): DataLoader pour les données d'entraînement

        Returns:
            float: Perte moyenne sur l'époque
        """
        self.model.train()
        total_loss = 0

        for batch_idx, (img1, img2, label) in enumerate(train_loader):
            # Transfert des données sur le device
            img1, img2 = img1.to(self.device), img2.to(self.device)
            label = label.to(self.device)

            # Forward pass
            self.optimizer.zero_grad()
            output1, output2 = self.model(img1, img2)
            loss = self.criterion(output1, output2, label)

            # Backward pass
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()

            if batch_idx % 100 == 0:
                logging.info(
                    f"Batch [{batch_idx}/{len(train_loader)}] - Loss: {loss.item():.6f}"
                )

        return total_loss / len(train_loader)

    def validate(
        self, val_loader: DataLoader, threshold: float = 1.0
    ) -> Tuple[float, float]:
        """
        Évalue le modèle sur l'ensemble de validation.

        Args:
            val_loader (DataLoader): DataLoader pour les données de validation
            threshold (float): Seuil de distance pour la classification

        Returns:
            Tuple[float, float]: Perte moyenne et accuracy
        """
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0

        with torch.no_grad():
            for img1, img2, label in val_loader:
                img1, img2 = img1.to(self.device), img2.to(self.device)
                label = label.to(self.device)

                # Forward pass
                output1, output2 = self.model(img1, img2)
                loss = self.criterion(output1, output2, label)

                # Calcul de l'accuracy
                distances = F.pairwise_distance(output1, output2)
                predictions = (distances < threshold).float()
                correct += (predictions == label).sum().item()
                total += label.size(0)

                total_loss += loss.item()

        val_loss = total_loss / len(val_loader)
        accuracy = correct / total
        return val_loss, accuracy

    def save_checkpoint(self, epoch: int, val_loss: float):
        """
        Sauvegarde un checkpoint du modèle.

        Args:
            epoch (int): Numéro de l'époque
            val_loss (float): Perte sur la validation
        """
        if val_loss < self.best_val_loss:
            self.best_val_loss = val_loss
            checkpoint = {
                "epoch": epoch,
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "val_loss": val_loss,
            }
            torch.save(checkpoint, self.model_dir / "best_model.pth")
            logging.info(f"Meilleur modèle sauvegardé (val_loss: {val_loss:.6f})")

    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        num_epochs: int,
        save_frequency: int = 5,
    ):
        """
        Entraîne le modèle pendant plusieurs époques.

        Args:
            train_loader (DataLoader): DataLoader pour l'entraînement
            val_loader (DataLoader): DataLoader pour la validation
            num_epochs (int): Nombre d'époques
            save_frequency (int): Fréquence de sauvegarde du modèle
        """
        for epoch in range(num_epochs):
            logging.info(f"\nÉpoque {epoch+1}/{num_epochs}")

            # Entraînement
            train_loss = self.train_epoch(train_loader)
            logging.info(f"Perte moyenne en entraînement: {train_loss:.6f}")

            # Validation
            val_loss, val_accuracy = self.validate(val_loader)
            logging.info(f"Perte en validation: {val_loss:.6f}")
            logging.info(f"Accuracy en validation: {val_accuracy:.2%}")

            # Sauvegarde du modèle
            if (epoch + 1) % save_frequency == 0:
                self.save_checkpoint(epoch, val_loss)


def get_transform(image_size):
    """
    Retourne les transformations à appliquer aux images
    """
    return transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize(mean=[0.5], std=[0.5])]
    )


def main():
    """
    Fonction principale d'entraînement
    """
    # Configuration
    batch_size = 32
    num_epochs = 30
    learning_rate = 0.001
    margin = 1.0
    image_size = 64

    # Création des datasets
    train_dataset = PairDataset(
        csv_file="model/pairs/train_pairs.csv",
        dataset_dir="model/dataset/train",
        transform=get_transform(image_size),
    )

    test_dataset = PairDataset(
        csv_file="model/pairs/test_pairs.csv",
        dataset_dir="model/dataset/test",
        transform=get_transform(image_size),
    )

    # Device (GPU si disponible)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info(f"Utilisation du device: {device}")

    # Chargement des données
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=4,
        pin_memory=True,
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True,
    )

    # Création du modèle et des outils d'entraînement
    model = SiameseNetwork()
    criterion = ContrastiveLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Création du trainer et lancement de l'entraînement
    trainer = SiameseTrainer(model, criterion, optimizer, device, Path("model/models"))
    trainer.train(train_loader, test_loader, num_epochs)


if __name__ == "__main__":
    main()
