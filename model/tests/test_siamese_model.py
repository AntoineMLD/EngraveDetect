import pytest
import torch
import torch.nn as nn
from model.siamese_model import SiameseNetwork, ContrastiveLoss

class TestSiameseNetwork:
    def test_model_creation(self, device):
        """Test la création du modèle"""
        model = SiameseNetwork().to(device)
        assert isinstance(model, nn.Module)
        assert isinstance(model, SiameseNetwork)
        
    def test_forward_once(self, device):
        """Test le forward_once du modèle"""
        model = SiameseNetwork().to(device)
        # Créer un batch d'images factice
        x = torch.randn(1, 1, 64, 64).to(device)
        output = model.forward_once(x)
        
        # Vérifier la forme de la sortie
        assert output.shape == (1, 128)  # Taille du vecteur d'embedding
        assert output.requires_grad  # Vérifier que les gradients sont activés
        
    def test_forward(self, device):
        """Test le forward complet du modèle"""
        model = SiameseNetwork().to(device)
        # Créer deux images factices
        x1 = torch.randn(1, 1, 64, 64).to(device)
        x2 = torch.randn(1, 1, 64, 64).to(device)
        
        output1, output2 = model(x1, x2)
        
        # Vérifier les formes des sorties
        assert output1.shape == (1, 128)
        assert output2.shape == (1, 128)
        assert output1.requires_grad
        assert output2.requires_grad
        
    def test_model_parameters(self, device):
        """Test les paramètres du modèle"""
        model = SiameseNetwork().to(device)
        # Vérifier que le modèle a des paramètres entraînables
        assert sum(p.numel() for p in model.parameters() if p.requires_grad) > 0
        
class TestContrastiveLoss:
    def test_loss_creation(self):
        """Test la création de la fonction de perte"""
        criterion = ContrastiveLoss(margin=2.0)
        assert isinstance(criterion, nn.Module)
        assert criterion.margin == 2.0
        
    def test_loss_similar_pairs(self, device):
        """Test la perte pour des paires similaires"""
        criterion = ContrastiveLoss(margin=2.0)
        
        # Créer des embeddings similaires
        output1 = torch.tensor([[1.0, 0.0]], device=device)
        output2 = torch.tensor([[1.0, 0.0]], device=device)
        label = torch.tensor([1], device=device)  # Paire similaire
        
        loss = criterion(output1, output2, label)
        
        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0  # La perte doit être positive
        assert loss.item() < 1e-6  # La perte doit être proche de 0 pour des embeddings identiques
        
    def test_loss_dissimilar_pairs(self, device):
        """Test la perte pour des paires dissimilaires"""
        criterion = ContrastiveLoss(margin=2.0)
        
        # Créer des embeddings différents
        output1 = torch.tensor([[1.0, 0.0]], device=device)
        output2 = torch.tensor([[-1.0, 0.0]], device=device)
        label = torch.tensor([0], device=device)  # Paire dissimilaire
        
        loss = criterion(output1, output2, label)
        
        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0  # La perte doit être positive
        assert loss.item() < criterion.margin  # La perte doit être inférieure à la marge
        
    def test_loss_gradient(self, device):
        """Test que la perte permet la rétropropagation"""
        criterion = ContrastiveLoss(margin=2.0)
        
        # Créer des tenseurs qui nécessitent des gradients
        output1 = torch.tensor([[1.0, 0.0]], device=device, requires_grad=True)
        output2 = torch.tensor([[0.5, 0.0]], device=device, requires_grad=True)
        label = torch.tensor([1], device=device)
        
        loss = criterion(output1, output2, label)
        loss.backward()
        
        # Vérifier que les gradients ont été calculés
        assert output1.grad is not None
        assert output2.grad is not None
        
    def test_loss_batch(self, device):
        """Test la perte sur un batch"""
        criterion = ContrastiveLoss(margin=2.0)
        
        # Créer un batch de paires
        output1 = torch.randn(32, 128, device=device)
        output2 = torch.randn(32, 128, device=device)
        labels = torch.randint(0, 2, (32,), device=device)
        
        loss = criterion(output1, output2, labels)
        
        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0
        assert not torch.isnan(loss) 