import pytest
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError
from api.routes.materiaux import MateriauBase
from database.models.base import Materiau
from pydantic import BaseModel
from unittest.mock import MagicMock

# Mock data
class MockMateriau(BaseModel):
    id: int
    nom: str
    description: str = None

@pytest.fixture
def mock_materiau():
    return MockMateriau(
        id=1,
        nom="Materiau Test",
        description="Description Test"
    )

class TestGetMateriaux:
    def test_get_materiaux_returns_list(self, client, db_session, mock_materiau):
        # Arrange
        db_session.query.return_value.all.return_value = [mock_materiau]

        # Act
        response = client.get("/api/materiaux")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["nom"] == mock_materiau.nom

    def test_get_materiaux_returns_empty_list(self, client, db_session):
        # Arrange
        db_session.query.return_value.all.return_value = []

        # Act
        response = client.get("/api/materiaux")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0

class TestGetMateriau:
    def test_get_materiau_success(self, client, db_session, mock_materiau):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = mock_materiau

        # Act
        response = client.get("/api/materiaux/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["nom"] == mock_materiau.nom

    def test_get_materiau_not_found(self, client, db_session):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        response = client.get("/api/materiaux/999")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Materiau non trouvé"

    def test_get_materiau_invalid_id(self, client):
        # Act
        response = client.get("/api/materiaux/invalid")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestCreateMateriau:
    def test_create_materiau_success(self, client, db_session, auth_headers):
        # Arrange
        materiau_data = {
            "nom": "Nouveau Materiau"
        }
        mock_materiau = Materiau(id=1, **materiau_data)
        db_session.add = MagicMock()
        db_session.commit = MagicMock()
        db_session.refresh = MagicMock(side_effect=lambda x: setattr(x, 'id', 1))

        # Act
        response = client.post("/api/materiaux", json=materiau_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["nom"] == materiau_data["nom"]
        assert response.json()["id"] == 1
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()

    def test_create_materiau_db_error(self, client, db_session, auth_headers):
        # Arrange
        materiau_data = {"nom": "Test Materiau"}
        db_session.commit.side_effect = SQLAlchemyError("DB Error")

        # Act
        response = client.post("/api/materiaux", json=materiau_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Erreur lors de la création du materiau" in response.json()["detail"]
        db_session.rollback.assert_called_once()

class TestUpdateMateriau:
    def test_update_materiau_success(self, client, db_session, mock_materiau, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = mock_materiau
        update_data = {"nom": "Materiau Modifié"}

        # Act
        response = client.put(f"/api/materiaux/{mock_materiau.id}", json=update_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["nom"] == update_data["nom"]
        db_session.commit.assert_called_once()

    def test_update_materiau_not_found(self, client, db_session, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None
        update_data = {"nom": "Materiau Modifié"}

        # Act
        response = client.put("/api/materiaux/999", json=update_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Materiau non trouvé"

class TestDeleteMateriau:
    def test_delete_materiau_success(self, client, db_session, mock_materiau, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = mock_materiau

        # Act
        response = client.delete(f"/api/materiaux/{mock_materiau.id}", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        db_session.delete.assert_called_once()
        db_session.commit.assert_called_once()

    def test_delete_materiau_not_found(self, client, db_session, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        response = client.delete("/api/materiaux/999", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Materiau non trouvé"

    def test_delete_materiau_invalid_id(self, client, auth_headers):
        # Act
        response = client.delete("/api/materiaux/invalid", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY 