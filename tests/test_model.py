import io
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import torch
from PIL import Image

from model.infer_siamese import load_templates, predict_symbol


@pytest.fixture
def test_image():
    """Fixture pour créer une image de test"""
    # Créer une image test
    img = Image.fromarray(np.zeros((100, 100), dtype=np.uint8))

    # Sauvegarder l'image dans un fichier temporaire
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        img.save(tmp.name)
        yield tmp.name

    # Nettoyer après le test
    os.unlink(tmp.name)


@pytest.fixture
def mock_templates(test_image):
    """Mock le chargement des templates"""
    with patch("model.infer_siamese.SiamesePredictor") as mock_predictor:
        # Créer une instance mockée du prédicteur
        predictor_instance = MagicMock()
        predictor_instance.templates = {"test_symbol": test_image}
        predictor_instance.similarity_threshold = 0.5
        predictor_instance.find_closest_symbol.return_value = ("test_symbol", 0.8)
        predictor_instance.predict.return_value = {
            "predicted_symbol": "test_symbol",
            "similarity_score": 0.8,
            "is_confident": True,
            "message": "Test prediction",
        }
        mock_predictor.return_value = predictor_instance
        yield predictor_instance


def test_load_templates(mock_templates):
    """Test du chargement des templates"""
    templates = load_templates()
    assert templates is not None
    assert len(templates.templates) > 0
    assert "test_symbol" in templates.templates


def test_predict_symbol(test_image, mock_templates):
    """Test de la prédiction de symbole"""
    templates = load_templates()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    predicted_symbol, similarity_score = predict_symbol(
        test_image, None, templates, device
    )

    assert isinstance(predicted_symbol, str)
    assert isinstance(similarity_score, float)
    assert 0 <= similarity_score <= 1
    assert predicted_symbol == "test_symbol"
    assert similarity_score == 0.8
