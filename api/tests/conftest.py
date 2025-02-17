from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.dependencies.auth import verify_auth
from api.routes import (
    detection,
    fournisseurs,
    gammes,
    materiaux,
    series,
    symboles,
    traitements,
    verres,
    verres_symboles,
)
from database.config.database import get_db


class MockSession(MagicMock):
    """Mock personnalisé pour la session de base de données."""

    _id_counter = 1
    _objects = {}  # Stockage des objets par type et ID

    def add(self, obj):
        """Simule l'ajout d'un objet en lui assignant un ID."""
        if not hasattr(obj, "id") or obj.id is None:
            obj.id = self._id_counter
            self._id_counter += 1

        # Stocker l'objet
        obj_type = type(obj).__name__
        if obj_type not in self._objects:
            self._objects[obj_type] = {}
        self._objects[obj_type][obj.id] = obj

    def add_all(self, objects):
        """Simule l'ajout de plusieurs objets en leur assignant des IDs."""
        for obj in objects:
            self.add(obj)

    def commit(self):
        """Simule le commit."""
        pass

    def refresh(self, obj):
        """Simule le refresh."""
        pass

    def delete(self, obj):
        """Simule la suppression d'un objet."""
        obj_type = type(obj).__name__
        if obj_type in self._objects and obj.id in self._objects[obj_type]:
            del self._objects[obj_type][obj.id]

    def query(self, model):
        """Simule une requête."""
        model_name = model.__name__

        class MockQuery:
            def __init__(self, session, model_name):
                self.session = session
                self.model_name = model_name
                self._filter_conditions = []

            def filter(self, *conditions):
                self._filter_conditions.extend(conditions)
                return self

            def first(self):
                if self.model_name not in self.session._objects:
                    return None

                # Pour simplifier, on retourne le premier objet qui correspond
                # Dans un cas réel, il faudrait évaluer les conditions
                objects = list(self.session._objects[self.model_name].values())
                return objects[0] if objects else None

            def all(self):
                if self.model_name not in self.session._objects:
                    return []
                return list(self.session._objects[self.model_name].values())

            def offset(self, n):
                return self

            def limit(self, n):
                return self

        return MockQuery(self, model_name)


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
    app.include_router(detection.router, prefix="/api")
    app.include_router(symboles.router, prefix="/api")
    app.include_router(verres_symboles.router, prefix="/api")
    return app


@pytest.fixture
def db_session():
    """Fixture pour la session de base de données mockée."""
    session = MockSession(spec=Session)
    session._id_counter = 1  # Réinitialise le compteur pour chaque test
    session._objects = {}  # Réinitialise le stockage des objets
    return session


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
