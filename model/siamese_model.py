#!/usr/bin/env python3

"""
Implémentation d'un réseau siamois pour la reconnaissance de symboles gravés.

Ce module définit :
- L'architecture du réseau siamois basée sur un CNN
- La fonction de perte contrastive pour l'entraînement
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class SiameseNetwork(nn.Module):
    """
    Implémente un réseau siamois pour la reconnaissance de symboles.
    
    Le réseau utilise une architecture CNN pour extraire des caractéristiques
    discriminantes des images. La même architecture est utilisée pour les
    deux branches du réseau (poids partagés).
    """
    
    def __init__(self, input_channels: int = 1):
        """
        Initialise l'architecture du réseau.
        
        Args:
            input_channels (int): Nombre de canaux des images d'entrée (1 pour niveaux de gris)
        """
        super(SiameseNetwork, self).__init__()
        
        # Couches de convolution
        self.conv1 = nn.Conv2d(input_channels, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        
        # Couches fully connected
        self.fc1 = nn.Linear(128 * 8 * 8, 512)
        self.fc2 = nn.Linear(512, 128)
        
        # Dropout pour la régularisation
        self.dropout = nn.Dropout(0.3)
    
    def forward_once(self, x: torch.Tensor) -> torch.Tensor:
        """
        Passe une image à travers une branche du réseau siamois.
        
        Args:
            x (torch.Tensor): Tensor d'entrée de forme (batch_size, channels, height, width)
            
        Returns:
            torch.Tensor: Embedding de l'image de forme (batch_size, embedding_size)
        """
        # Premier bloc convolutif
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)  # 64x64 -> 32x32
        
        # Deuxième bloc convolutif
        x = self.conv2(x)
        x = self.bn2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)  # 32x32 -> 16x16
        
        # Troisième bloc convolutif
        x = self.conv3(x)
        x = self.bn3(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)  # 16x16 -> 8x8
        
        # Aplatissement et couches fully connected
        x = x.view(x.size(0), -1)  # (batch_size, 128*8*8)
        x = self.dropout(x)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        
        # Normalisation L2 de l'embedding
        x = F.normalize(x, p=2, dim=1)
        return x
    
    def forward(self, input_a: torch.Tensor, input_b: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Passe une paire d'images à travers le réseau siamois.
        
        Args:
            input_a (torch.Tensor): Première image du couple
            input_b (torch.Tensor): Deuxième image du couple
            
        Returns:
            tuple[torch.Tensor, torch.Tensor]: Embeddings des deux images
        """
        output_a = self.forward_once(input_a)
        output_b = self.forward_once(input_b)
        return output_a, output_b


class ContrastiveLoss(nn.Module):
    """
    Implémente la fonction de perte contrastive pour l'entraînement du réseau siamois.
    
    Cette perte rapproche les embeddings des images similaires (label=1) et
    éloigne ceux des images différentes (label=0) jusqu'à une certaine marge.
    """
    
    def __init__(self, margin: float = 2.0):
        """
        Initialise la fonction de perte.
        
        Args:
            margin (float): Marge minimale souhaitée entre les embeddings d'images différentes
        """
        super(ContrastiveLoss, self).__init__()
        self.margin = margin
    
    def forward(self, output_a: torch.Tensor, output_b: torch.Tensor, 
                label: torch.Tensor) -> torch.Tensor:
        """
        Calcule la perte contrastive pour un batch de paires.
        
        Args:
            output_a (torch.Tensor): Embeddings des premières images
            output_b (torch.Tensor): Embeddings des deuxièmes images
            label (torch.Tensor): Labels (1 pour même symbole, 0 pour différent)
            
        Returns:
            torch.Tensor: Valeur de la perte moyennée sur le batch
        """
        # Calcul des distances euclidiennes entre les paires d'embeddings
        distances = F.pairwise_distance(output_a, output_b)
        
        # Perte pour les paires positives : minimiser la distance
        loss_pos = label * distances.pow(2)
        
        # Perte pour les paires négatives : maximiser la distance jusqu'à la marge
        loss_neg = (1 - label) * F.relu(self.margin - distances).pow(2)
        
        # Moyenne des deux composantes
        loss = 0.5 * (loss_pos + loss_neg)
        return loss.mean()


def compute_accuracy(output1: torch.Tensor, output2: torch.Tensor, 
                    label: torch.Tensor, threshold: float = 1.0) -> float:
    """
    Calcule la précision de classification pour un seuil donné.
    
    Args:
        output1: Premier tensor d'embedding
        output2: Second tensor d'embedding
        label: Tensor de labels (1 pour même symbole, 0 pour différent)
        threshold: Seuil de distance pour la classification
        
    Returns:
        Précision de classification (entre 0 et 1)
    """
    distances = F.pairwise_distance(output1, output2)
    predictions = (distances < threshold).float()
    correct = (predictions == label).float()
    accuracy = correct.mean().item()
    return accuracy 