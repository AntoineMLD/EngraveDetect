import pytest
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError
from api.routes.fournisseurs import FournisseurBase
from database.models.base import Fournisseur
from pydantic import BaseModel
from unittest.mock import MagicMock

# Mock data
class MockFournisseur(BaseModel):
    id: int
    nom: str
    adresse: str = None
    telephone: str = None
    email: str = None

@pytest.fixture
def mock_fournisseur():
    return MockFournisseur(
        id=1,
        nom="Fournisseur Test",
        adresse="1 rue Test",
        telephone="0123456789",
        email="test@fournisseur.com"
    )

class TestGetFournisseurs:
    def test_get_fournisseurs_returns_list(self, client, db_session, mock_fournisseur):
        # Arrange
        db_session.query.return_value.all.return_value = [mock_fournisseur]

        # Act
        response = client.get("/api/fournisseurs")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["nom"] == mock_fournisseur.nom

    def test_get_fournisseurs_returns_empty_list(self, client, db_session):
        # Arrange
        db_session.query.return_value.all.return_value = []

        # Act
        response = client.get("/api/fournisseurs")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0

class TestGetFournisseur:
    def test_get_fournisseur_success(self, client, db_session, mock_fournisseur):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = mock_fournisseur

        # Act
        response = client.get("/api/fournisseurs/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["nom"] == mock_fournisseur.nom

    def test_get_fournisseur_not_found(self, client, db_session):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        response = client.get("/api/fournisseurs/999")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Fournisseur non trouvé"

    def test_get_fournisseur_invalid_id(self, client):
        # Act
        response = client.get("/api/fournisseurs/invalid")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestCreateFournisseur:
    def test_create_fournisseur_success(self, client, db_session, auth_headers):
        # Arrange
        fournisseur_data = {
            "nom": "Nouveau Fournisseur"
        }
        mock_fournisseur = Fournisseur(id=1, **fournisseur_data)
        db_session.add = MagicMock()
        db_session.commit = MagicMock()
        db_session.refresh = MagicMock(side_effect=lambda x: setattr(x, 'id', 1))

        # Act
        response = client.post("/api/fournisseurs", json=fournisseur_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["nom"] == fournisseur_data["nom"]
        assert response.json()["id"] == 1
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()

    def test_create_fournisseur_db_error(self, client, db_session, auth_headers):
        # Arrange
        fournisseur_data = {"nom": "Test Fournisseur"}
        db_session.commit.side_effect = SQLAlchemyError("DB Error")

        # Act
        response = client.post("/api/fournisseurs", json=fournisseur_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Erreur lors de la création du fournisseur" in response.json()["detail"]
        db_session.rollback.assert_called_once()

class TestUpdateFournisseur:
    def test_update_fournisseur_success(self, client, db_session, mock_fournisseur, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = mock_fournisseur
        update_data = {"nom": "Fournisseur Modifié"}

        # Act
        response = client.put(f"/api/fournisseurs/{mock_fournisseur.id}", json=update_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["nom"] == update_data["nom"]
        db_session.commit.assert_called_once()

    def test_update_fournisseur_not_found(self, client, db_session, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None
        update_data = {"nom": "Fournisseur Modifié"}

        # Act
        response = client.put("/api/fournisseurs/999", json=update_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Fournisseur non trouvé"

class TestDeleteFournisseur:
    def test_delete_fournisseur_success(self, client, db_session, mock_fournisseur, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = mock_fournisseur

        # Act
        response = client.delete(f"/api/fournisseurs/{mock_fournisseur.id}", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        db_session.delete.assert_called_once()
        db_session.commit.assert_called_once()

    def test_delete_fournisseur_not_found(self, client, db_session, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        response = client.delete("/api/fournisseurs/999", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Fournisseur non trouvé"

    def test_delete_fournisseur_invalid_id(self, client, auth_headers):
        # Act
        response = client.delete("/api/fournisseurs/invalid", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY