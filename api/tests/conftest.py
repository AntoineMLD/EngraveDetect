import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from database.config.database import get_db
from api.dependencies.auth import verify_auth
from api.routes import verres, traitements, materiaux, gammes, series, fournisseurs

# Configuration de l'application de test
@pytest.fixture
def app():
    """Fixture pour l'application FastAPI."""
    app = FastAPI()
    app.include_router(verres.router, prefix="/api")
    app.include_router(traitements.router, prefix="/api")
    app.include_router(materiaux.router, prefix="/api")
    app.include_router(gammes.router, prefix="/api")
    app.include_router(series.router, prefix="/api")
    app.include_router(fournisseurs.router, prefix="/api")
    return app

@pytest.fixture
def db_session():
    """Fixture pour la session de base de données mockée."""
    return MagicMock(spec=Session)

@pytest.fixture
def auth_headers():
    """Fournit les en-têtes d'authentification pour les tests."""
    return {"Authorization": "Bearer test_token"}

@pytest.fixture
def client(app, db_session, mocker):
    """Configure le client de test avec les dépendances mockées."""
    def override_get_db():
        return db_session
    
    # Mock de l'authentification
    mocker.patch("api.auth.auth.verify_token", return_value="test_user")
    
    # Override des dépendances
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[verify_auth] = lambda: "test_user"
    
    client = TestClient(app)
    yield client
    app.dependency_overrides = {} 