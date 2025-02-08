import shutil
from pathlib import Path

import pytest
import torch


@pytest.fixture
def device():
    """Fixture pour le device PyTorch"""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@pytest.fixture
def test_data_dir(tmp_path):
    """Fixture pour le répertoire de données de test"""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    # Nettoyage après les tests
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture
def model_dir(test_data_dir):
    """Fixture pour le répertoire des modèles"""
    model_dir = test_data_dir / "models"
    model_dir.mkdir(exist_ok=True)
    return model_dir


@pytest.fixture
def templates_dir(test_data_dir):
    """Fixture pour le répertoire des templates"""
    templates_dir = test_data_dir / "templates"
    templates_dir.mkdir(exist_ok=True)
    return templates_dir


@pytest.fixture
def debug_dir(test_data_dir):
    """Fixture pour le répertoire de debug"""
    debug_dir = test_data_dir / "debug"
    debug_dir.mkdir(exist_ok=True)
    return debug_dir


@pytest.fixture
def sample_image(test_data_dir):
    """Fixture pour créer une image de test"""
    from PIL import Image, ImageDraw

    # Créer une image test simple
    img = Image.new("L", (100, 100), color=255)
    draw = ImageDraw.Draw(img)
    draw.rectangle([30, 30, 70, 70], fill=0)  # Dessiner un carré noir

    # Sauvegarder l'image
    img_path = test_data_dir / "test_image.png"
    img.save(img_path)

    return img_path
