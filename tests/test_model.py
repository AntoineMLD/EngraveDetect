import os
import tempfile

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


def test_load_templates():
    """Test du chargement des templates"""
    templates = load_templates()
    assert templates is not None
    assert len(templates.templates) > 0
    assert templates.similarity_threshold > 0


def test_predict_symbol(test_image):
    """Test de la prédiction de symbole"""
    templates = load_templates()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    predicted_symbol, similarity_score = predict_symbol(
        test_image, None, templates, device
    )

    assert isinstance(predicted_symbol, str)
    assert isinstance(similarity_score, float)
    assert 0 <= similarity_score <= 1
