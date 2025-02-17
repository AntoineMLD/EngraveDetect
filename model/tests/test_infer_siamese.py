from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image

from model.infer_siamese import SiamesePredictor, load_templates, predict_symbol
from model.siamese_model import SiameseNetwork


class TestSiamesePredictor:
    def test_predictor_creation(self, device, model_dir):
        """Test la création du prédicteur"""
        # Créer un modèle factice et le sauvegarder
        model = SiameseNetwork()
        model_path = model_dir / "best_model.pth"
        torch.save(
            {
                "epoch": 1,
                "model_state_dict": model.state_dict(),
            },
            model_path,
        )

        predictor = SiamesePredictor(model, device)
        assert predictor.model is not None
        assert predictor.device == device
        assert predictor.image_size == 64
        assert predictor.similarity_threshold == 0.4488

    def test_preprocess_image(self, device, sample_image):
        """Test le prétraitement d'une image"""
        model = SiameseNetwork()
        predictor = SiamesePredictor(model, device)

        # Charger et prétraiter l'image
        image = Image.open(sample_image)
        tensor = predictor.preprocess_image(image)

        assert tensor is not None
        assert isinstance(tensor, torch.Tensor)
        assert tensor.shape == (1, 1, 64, 64)  # [batch, channel, height, width]
        assert tensor.device == device

    def test_compare_images(self, device, sample_image):
        """Test la comparaison d'images"""
        model = SiameseNetwork()
        predictor = SiamesePredictor(model, device)

        # Charger et prétraiter l'image
        image = Image.open(sample_image)
        tensor1 = predictor.preprocess_image(image)
        tensor2 = predictor.preprocess_image(image)

        similarity = predictor.compare_images(tensor1, tensor2)
        assert isinstance(similarity, float)
        assert 0 <= similarity <= 1  # La similarité doit être entre 0 et 1
        assert similarity > 0.9  # Images identiques doivent avoir une forte similarité

    def test_find_closest_symbol(self, device, sample_image, templates_dir):
        """Test la recherche du symbole le plus proche"""
        model = SiameseNetwork()
        predictor = SiamesePredictor(model, device)

        # Créer un template
        template_dir = templates_dir / "test_symbol"
        template_dir.mkdir(exist_ok=True)
        image = Image.open(sample_image)
        image.save(template_dir / "template.png")

        # Charger les templates
        predictor.load_templates(templates_dir)

        # Trouver le symbole le plus proche
        symbol, similarity = predictor.find_closest_symbol(sample_image)

        assert symbol == "test_symbol"
        assert isinstance(similarity, float)
        assert 0 <= similarity <= 1

    def test_predict(self, device, sample_image, templates_dir):
        """Test la prédiction complète"""
        model = SiameseNetwork()
        predictor = SiamesePredictor(model, device)

        # Créer un template
        template_dir = templates_dir / "test_symbol"
        template_dir.mkdir(exist_ok=True)
        image = Image.open(sample_image)
        image.save(template_dir / "template.png")

        # Charger les templates
        predictor.load_templates(templates_dir)

        # Faire une prédiction
        prediction = predictor.predict(sample_image)

        assert isinstance(prediction, dict)
        assert "image_path" in prediction
        assert "predicted_symbol" in prediction
        assert "similarity_score" in prediction
        assert "is_confident" in prediction
        assert isinstance(prediction["is_confident"], bool)


def test_load_templates(device, templates_dir):
    """Test le chargement des templates"""
    templates = load_templates()
    assert templates is not None
    assert isinstance(templates, SiamesePredictor)
    assert templates.device == device


def test_predict_symbol(device, sample_image, templates_dir):
    """Test la fonction de prédiction de symbole"""
    # Créer un template
    template_dir = templates_dir / "test_symbol"
    template_dir.mkdir(exist_ok=True)
    image = Image.open(sample_image)
    image.save(template_dir / "template.png")

    # Charger les templates
    templates = load_templates()

    # Faire une prédiction
    symbol, similarity = predict_symbol(str(sample_image), None, templates, device)

    assert isinstance(symbol, str)
    assert isinstance(similarity, float)
    assert 0 <= similarity <= 1
