import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import torch
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from api.main import app
from database.config.database import Base, engine


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Configure les variables d'environnement pour les tests"""
    # Sauvegarde les variables d'environnement actuelles
    original_environ = dict(os.environ)

    # Charge les variables de test depuis .env.test s'il existe
    env_test_path = Path(__file__).parent / ".env.test"
    if env_test_path.exists():
        load_dotenv(env_test_path, override=True)
    else:
        # Utilise des valeurs par défaut sécurisées pour les tests
        os.environ.update(
            {
                "ADMIN_USERNAME": "test_user",  # Uniquement pour les tests
                "ADMIN_PASSWORD": "test_pass",  # Uniquement pour les tests
                "JWT_ALGORITHM": "HS256",
                "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "30",
            }
        )

    yield

    # Restaure les variables d'environnement originales
    os.environ.clear()
    os.environ.update(original_environ)


@pytest.fixture(autouse=True)
def mock_siamese_network():
    """Mock le modèle SiameseNetwork et son chargement"""
    with patch("model.infer_siamese.SiameseNetwork") as mock_network:
        # Créer un mock du modèle
        model_mock = MagicMock()
        model_mock.eval.return_value = model_mock
        model_mock.to.return_value = model_mock

        # Configurer forward_once pour retourner un tensor valide
        def mock_forward_once(x):
            return torch.ones(1, 128)  # Retourne un tensor de taille (1, 128)

        model_mock.forward_once.side_effect = mock_forward_once
        mock_network.return_value = model_mock

        # Mock le chargement du modèle
        with patch("torch.load") as mock_load, patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True  # Simule que le fichier existe
            mock_load.return_value = {
                "model_state_dict": {},
                "epoch": 100,
                "optimizer_state_dict": {},
                "loss": 0.1,
            }
            yield mock_network


@pytest.fixture(autouse=True)
def mock_load_templates():
    """Mock le chargement des templates pour tous les tests"""
    with patch("model.infer_siamese.load_templates", autospec=True) as mock:
        # Créer un mock du prédicteur
        predictor_mock = MagicMock()
        predictor_mock.predict.return_value = {
            "predicted_symbol": "test_symbol",
            "similarity_score": 0.8,
            "is_confident": True,
            "message": "Test prediction",
        }
        predictor_mock.similarity_threshold = 0.5
        predictor_mock.templates = {"test_symbol": "test_template"}
        mock.return_value = predictor_mock
        yield mock


@pytest.fixture
def client():
    """Fixture pour le client de test FastAPI"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_db():
    """Fixture pour la base de données de test"""
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    yield
    # Nettoyer après les tests
    Base.metadata.drop_all(bind=engine)
