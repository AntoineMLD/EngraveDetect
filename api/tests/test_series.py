from unittest.mock import MagicMock

import pytest
from fastapi import status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from api.routes.series import SerieBase
from database.models.base import Serie


# Mock data
class MockSerie(BaseModel):
    id: int
    nom: str
    description: str = None


@pytest.fixture
def mock_serie():
    return MockSerie(id=1, nom="Serie Test", description="Description Test")


class TestGetSeries:
    def test_get_series_returns_list(self, client, db_session, mock_serie):
        # Arrange
        db_session.query.return_value.all.return_value = [mock_serie]

        # Act
        response = client.get("/api/series")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["nom"] == mock_serie.nom

    def test_get_series_returns_empty_list(self, client, db_session):
        # Arrange
        db_session.query.return_value.all.return_value = []

        # Act
        response = client.get("/api/series")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0


class TestGetSerie:
    def test_get_serie_success(self, client, db_session, mock_serie):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = (
            mock_serie
        )

        # Act
        response = client.get("/api/series/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["nom"] == mock_serie.nom

    def test_get_serie_not_found(self, client, db_session):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        response = client.get("/api/series/999")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Serie non trouvée"

    def test_get_serie_invalid_id(self, client):
        # Act
        response = client.get("/api/series/invalid")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCreateSerie:
    def test_create_serie_success(self, client, db_session, auth_headers):
        # Arrange
        serie_data = {"nom": "Nouvelle Serie"}
        mock_serie = Serie(id=1, **serie_data)
        db_session.add = MagicMock()
        db_session.commit = MagicMock()
        db_session.refresh = MagicMock(side_effect=lambda x: setattr(x, "id", 1))

        # Act
        response = client.post("/api/series", json=serie_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["nom"] == serie_data["nom"]
        assert response.json()["id"] == 1
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()

    def test_create_serie_db_error(self, client, db_session, auth_headers):
        # Arrange
        serie_data = {"nom": "Test Serie"}
        db_session.commit.side_effect = SQLAlchemyError("DB Error")

        # Act
        response = client.post("/api/series", json=serie_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Erreur lors de la création de la serie" in response.json()["detail"]
        db_session.rollback.assert_called_once()


class TestUpdateSerie:
    def test_update_serie_success(self, client, db_session, mock_serie, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = (
            mock_serie
        )
        update_data = {"nom": "Serie Modifiée"}

        # Act
        response = client.put(
            f"/api/series/{mock_serie.id}", json=update_data, headers=auth_headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["nom"] == update_data["nom"]
        db_session.commit.assert_called_once()

    def test_update_serie_not_found(self, client, db_session, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None
        update_data = {"nom": "Serie Modifiée"}

        # Act
        response = client.put("/api/series/999", json=update_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Serie non trouvée"


class TestDeleteSerie:
    def test_delete_serie_success(self, client, db_session, mock_serie, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = (
            mock_serie
        )

        # Act
        response = client.delete(f"/api/series/{mock_serie.id}", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        db_session.delete.assert_called_once()
        db_session.commit.assert_called_once()

    def test_delete_serie_not_found(self, client, db_session, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        response = client.delete("/api/series/999", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Serie non trouvée"

    def test_delete_serie_invalid_id(self, client, auth_headers):
        # Act
        response = client.delete("/api/series/invalid", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
