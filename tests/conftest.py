import pytest
from fastapi.testclient import TestClient
from api.main import app
from database.database import Base, engine

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