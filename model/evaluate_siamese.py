#!/usr/bin/env python3

"""
Script d'évaluation du réseau siamois sur l'ensemble de test.
Permet de :
- Charger le modèle entraîné
- Évaluer les performances sur le jeu de test
- Déterminer le seuil optimal de décision
- Calculer les métriques (précision, rappel, F1-score)
"""

import logging
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F
from siamese_model import SiameseNetwork
from sklearn.metrics import f1_score, precision_recall_curve
from torch.utils.data import DataLoader
from train_siamese import PairDataset

# Configuration du logging
logging.basicConfig(level=logging.INFO)


class SiameseEvaluator:
    """
    Classe pour l'évaluation du réseau siamois.
    """

    def __init__(self, model: torch.nn.Module, device: torch.device):
        """
        Initialise l'évaluateur.

        Args:
            model: Le réseau siamois
            device: Device sur lequel effectuer les calculs
        """
        self.model = model.to(device)
        self.device = device
        self.model.eval()

    def compute_distances_and_labels(
        self, test_loader: DataLoader
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcule les distances entre les paires d'images et récupère leurs labels.

        Args:
            test_loader: DataLoader pour les données de test

        Returns:
            Tuple contenant les distances et les labels
        """
        distances = []
        labels = []

        with torch.no_grad():
            for img1, img2, label in test_loader:
                img1, img2 = img1.to(self.device), img2.to(self.device)

                # Forward pass
                output1, output2 = self.model(img1, img2)
                distance = F.pairwise_distance(output1, output2).cpu().numpy()

                distances.extend(distance)
                labels.extend(label.numpy())

        return np.array(distances), np.array(labels)

    def find_optimal_threshold(
        self, distances: np.ndarray, labels: np.ndarray
    ) -> Tuple[float, float]:
        """
        Trouve le seuil optimal en utilisant la courbe précision-rappel.

        Args:
            distances: Array des distances entre paires
            labels: Array des vrais labels

        Returns:
            Tuple contenant le seuil optimal et le F1-score correspondant
        """
        # Conversion des distances en scores de similarité (1 - distance normalisée)
        max_dist = np.max(distances)
        scores = 1 - distances / max_dist

        # Calcul de la courbe précision-rappel
        precisions, recalls, thresholds = precision_recall_curve(labels, scores)

        # Calcul du F1-score pour chaque seuil
        f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-8)

        # Trouve le meilleur seuil
        best_idx = np.argmax(f1_scores)
        best_threshold = (
            thresholds[best_idx] if best_idx < len(thresholds) else thresholds[-1]
        )
        best_f1 = f1_scores[best_idx]

        return best_threshold, best_f1

    def plot_precision_recall_curve(
        self,
        distances: np.ndarray,
        labels: np.ndarray,
        best_threshold: float,
        output_path: Path,
    ):
        """
        Trace la courbe précision-rappel et sauvegarde le graphique.

        Args:
            distances: Array des distances entre paires
            labels: Array des vrais labels
            best_threshold: Seuil optimal trouvé
            output_path: Chemin où sauvegarder le graphique
        """
        max_dist = np.max(distances)
        scores = 1 - distances / max_dist

        precisions, recalls, thresholds = precision_recall_curve(labels, scores)

        plt.figure(figsize=(10, 6))
        plt.plot(recalls, precisions, "b-", label="Courbe PR")

        # Marque le point optimal
        idx = np.argmin(np.abs(thresholds - best_threshold))
        plt.plot(recalls[idx], precisions[idx], "ro", label="Seuil optimal")

        plt.xlabel("Rappel")
        plt.ylabel("Précision")
        plt.title("Courbe Précision-Rappel")
        plt.legend()
        plt.grid(True)

        plt.savefig(output_path / "precision_recall_curve.png")
        plt.close()

    def evaluate_with_threshold(
        self, distances: np.ndarray, labels: np.ndarray, threshold: float
    ) -> dict:
        """
        Évalue les performances avec un seuil donné.

        Args:
            distances: Array des distances entre paires
            labels: Array des vrais labels
            threshold: Seuil de décision

        Returns:
            Dict contenant les différentes métriques
        """
        max_dist = np.max(distances)
        scores = 1 - distances / max_dist
        predictions = (scores >= threshold).astype(int)

        accuracy = np.mean(predictions == labels)
        f1 = f1_score(labels, predictions)

        # Calcul des métriques par classe
        true_positives = np.sum((predictions == 1) & (labels == 1))
        false_positives = np.sum((predictions == 1) & (labels == 0))
        false_negatives = np.sum((predictions == 0) & (labels == 1))

        precision = true_positives / (true_positives + false_positives + 1e-8)
        recall = true_positives / (true_positives + false_negatives + 1e-8)

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
        }


def main():
    """
    Point d'entrée principal du script.
    """
    # Paramètres
    BATCH_SIZE = 32
    IMAGE_SIZE = 64

    # Chemins
    dataset_dir = Path("model/dataset")
    pairs_dir = Path("model/pairs")
    model_dir = Path("model/models")
    output_dir = Path("model/evaluation")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info(f"Utilisation du device: {device}")

    # Chargement du modèle
    model = SiameseNetwork()
    checkpoint = torch.load(model_dir / "best_model.pth")
    model.load_state_dict(checkpoint["model_state_dict"])
    logging.info(f"Modèle chargé depuis l'époque {checkpoint['epoch']}")

    # Chargement des données de test
    test_dataset = PairDataset(
        pairs_dir / "test_pairs.csv", dataset_dir, image_size=IMAGE_SIZE
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=4,
        pin_memory=True,
    )

    # Évaluation
    evaluator = SiameseEvaluator(model, device)

    # Calcul des distances et récupération des labels
    logging.info("Calcul des distances entre paires...")
    distances, labels = evaluator.compute_distances_and_labels(test_loader)

    # Recherche du seuil optimal
    logging.info("Recherche du seuil optimal...")
    best_threshold, best_f1 = evaluator.find_optimal_threshold(distances, labels)
    logging.info(
        f"Seuil optimal trouvé : {best_threshold:.4f} (F1-score : {best_f1:.4f})"
    )

    # Évaluation avec le seuil optimal
    metrics = evaluator.evaluate_with_threshold(distances, labels, best_threshold)
    logging.info("\nMétriques avec le seuil optimal :")
    logging.info(f"Accuracy : {metrics['accuracy']:.4%}")
    logging.info(f"Precision : {metrics['precision']:.4%}")
    logging.info(f"Recall : {metrics['recall']:.4%}")
    logging.info(f"F1-score : {metrics['f1_score']:.4%}")

    # Génération de la courbe précision-rappel
    evaluator.plot_precision_recall_curve(distances, labels, best_threshold, output_dir)
    logging.info(
        "\nCourbe précision-rappel sauvegardée dans evaluation/precision_recall_curve.png"
    )


if __name__ == "__main__":
    main()
