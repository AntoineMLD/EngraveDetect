from unittest.mock import MagicMock

import pytest
from fastapi import status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from api.routes.traitements import TraitementBase
from database.models.base import Traitement


# Mock data
class MockTraitement(BaseModel):
    id: int
    nom: str
    type: str


@pytest.fixture
def mock_traitement():
    return MockTraitement(id=1, nom="Traitement Test", type="Type Test")


class TestGetTraitements:
    def test_get_traitements_returns_list(self, client, db_session, mock_traitement):
        # Arrange
        db_session.query.return_value.all.return_value = [mock_traitement]

        # Act
        response = client.get("/api/traitements")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["nom"] == mock_traitement.nom

    def test_get_traitements_returns_empty_list(self, client, db_session):
        # Arrange
        db_session.query.return_value.all.return_value = []

        # Act
        response = client.get("/api/traitements")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0


class TestGetTraitement:
    def test_get_traitement_success(self, client, db_session, mock_traitement):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = (
            mock_traitement
        )

        # Act
        response = client.get("/api/traitements/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["nom"] == mock_traitement.nom

    def test_get_traitement_not_found(self, client, db_session):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        response = client.get("/api/traitements/999")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Traitement non trouvé"

    def test_get_traitement_invalid_id(self, client):
        # Act
        response = client.get("/api/traitements/invalid")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCreateTraitement:
    def test_create_traitement_success(self, client, db_session, auth_headers):
        # Arrange
        traitement_data = {"nom": "Nouveau Traitement", "type": "Nouveau Type"}
        mock_traitement = Traitement(id=1, **traitement_data)
        db_session.add = MagicMock()
        db_session.commit = MagicMock()
        db_session.refresh = MagicMock(side_effect=lambda x: setattr(x, "id", 1))

        # Act
        response = client.post(
            "/api/traitements", json=traitement_data, headers=auth_headers
        )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["nom"] == traitement_data["nom"]
        assert response.json()["id"] == 1
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()

    def test_create_traitement_db_error(self, client, db_session, auth_headers):
        # Arrange
        traitement_data = {"nom": "Test", "type": "Test"}
        db_session.commit.side_effect = SQLAlchemyError("DB Error")

        # Act
        response = client.post(
            "/api/traitements", json=traitement_data, headers=auth_headers
        )

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Erreur lors de la création du traitement" in response.json()["detail"]
        db_session.rollback.assert_called_once()


class TestUpdateTraitement:
    def test_update_traitement_success(
        self, client, db_session, mock_traitement, auth_headers
    ):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = (
            mock_traitement
        )
        update_data = {"nom": "Traitement Modifié", "type": "Type Test"}

        # Act
        response = client.put(
            f"/api/traitements/{mock_traitement.id}",
            json=update_data,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["nom"] == update_data["nom"]
        db_session.commit.assert_called_once()

    def test_update_traitement_not_found(self, client, db_session, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None
        update_data = {"nom": "Traitement Modifié", "type": "Type Test"}

        # Act
        response = client.put(
            "/api/traitements/999", json=update_data, headers=auth_headers
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Traitement non trouvé"


class TestDeleteTraitement:
    def test_delete_traitement_success(
        self, client, db_session, mock_traitement, auth_headers
    ):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = (
            mock_traitement
        )

        # Act
        response = client.delete(
            f"/api/traitements/{mock_traitement.id}", headers=auth_headers
        )

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        db_session.delete.assert_called_once()
        db_session.commit.assert_called_once()

    def test_delete_traitement_not_found(self, client, db_session, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        response = client.delete("/api/traitements/999", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Traitement non trouvé"

    def test_delete_traitement_invalid_id(self, client, auth_headers):
        # Act
        response = client.delete("/api/traitements/invalid", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
