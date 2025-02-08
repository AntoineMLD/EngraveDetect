from unittest.mock import MagicMock

import pytest
from fastapi import status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from api.routes.gammes import GammeBase
from database.models.base import Gamme


# Mock data
class MockGamme(BaseModel):
    id: int
    nom: str
    description: str = None


@pytest.fixture
def mock_gamme():
    return MockGamme(id=1, nom="Gamme Test", description="Description Test")


class TestGetGammes:
    def test_get_gammes_returns_list(self, client, db_session, mock_gamme):
        # Arrange
        db_session.query.return_value.all.return_value = [mock_gamme]

        # Act
        response = client.get("/api/gammes")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["nom"] == mock_gamme.nom

    def test_get_gammes_returns_empty_list(self, client, db_session):
        # Arrange
        db_session.query.return_value.all.return_value = []

        # Act
        response = client.get("/api/gammes")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0


class TestGetGamme:
    def test_get_gamme_success(self, client, db_session, mock_gamme):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = (
            mock_gamme
        )

        # Act
        response = client.get("/api/gammes/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["nom"] == mock_gamme.nom

    def test_get_gamme_not_found(self, client, db_session):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        response = client.get("/api/gammes/999")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Gamme non trouvée"

    def test_get_gamme_invalid_id(self, client):
        # Act
        response = client.get("/api/gammes/invalid")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCreateGamme:
    def test_create_gamme_success(self, client, db_session, auth_headers):
        # Arrange
        gamme_data = {"nom": "Nouvelle Gamme"}
        mock_gamme = Gamme(id=1, **gamme_data)
        db_session.add = MagicMock()
        db_session.commit = MagicMock()
        db_session.refresh = MagicMock(side_effect=lambda x: setattr(x, "id", 1))

        # Act
        response = client.post("/api/gammes", json=gamme_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["nom"] == gamme_data["nom"]
        assert response.json()["id"] == 1
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()

    def test_create_gamme_db_error(self, client, db_session, auth_headers):
        # Arrange
        gamme_data = {"nom": "Test Gamme"}
        db_session.commit.side_effect = SQLAlchemyError("DB Error")

        # Act
        response = client.post("/api/gammes", json=gamme_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Erreur lors de la création de la gamme" in response.json()["detail"]
        db_session.rollback.assert_called_once()


class TestUpdateGamme:
    def test_update_gamme_success(self, client, db_session, mock_gamme, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = (
            mock_gamme
        )
        update_data = {"nom": "Gamme Modifiée"}

        # Act
        response = client.put(
            f"/api/gammes/{mock_gamme.id}", json=update_data, headers=auth_headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["nom"] == update_data["nom"]
        db_session.commit.assert_called_once()

    def test_update_gamme_not_found(self, client, db_session, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None
        update_data = {"nom": "Gamme Modifiée"}

        # Act
        response = client.put("/api/gammes/999", json=update_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Gamme non trouvée"


class TestDeleteGamme:
    def test_delete_gamme_success(self, client, db_session, mock_gamme, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = (
            mock_gamme
        )

        # Act
        response = client.delete(f"/api/gammes/{mock_gamme.id}", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        db_session.delete.assert_called_once()
        db_session.commit.assert_called_once()

    def test_delete_gamme_not_found(self, client, db_session, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        response = client.delete("/api/gammes/999", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Gamme non trouvée"

    def test_delete_gamme_invalid_id(self, client, auth_headers):
        # Act
        response = client.delete("/api/gammes/invalid", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
