from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from api.routes.verres import VerreBase
from database.models.base import Verre


# Mock data
class MockVerre(BaseModel):
    id: int
    nom: str
    variante: str
    hauteur_min: int
    hauteur_max: int
    indice: float
    url_gravure: str
    url_source: str
    fournisseur_id: int
    materiau_id: int
    gamme_id: int
    serie_id: int


@pytest.fixture
def mock_verre():
    return MockVerre(
        id=1,
        nom="Verre Test",
        variante="Variante Test",
        hauteur_min=10,
        hauteur_max=20,
        indice=1.5,
        url_gravure="http://example.com/gravure",
        url_source="http://example.com/source",
        fournisseur_id=1,
        materiau_id=1,
        gamme_id=1,
        serie_id=1,
    )


class TestGetVerres:
    def test_get_verres_returns_list(self, client, db_session, mock_verre):
        # Arrange
        db_session.query.return_value.all.return_value = [mock_verre]

        # Act
        response = client.get("/api/verres")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["nom"] == mock_verre.nom

    def test_get_verres_returns_empty_list(self, client, db_session):
        # Arrange
        db_session.query.return_value.all.return_value = []

        # Act
        response = client.get("/api/verres")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0


class TestGetVerre:
    def test_get_verre_success(self, client, db_session, mock_verre):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = (
            mock_verre
        )

        # Act
        response = client.get("/api/verre/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["nom"] == mock_verre.nom

    def test_get_verre_not_found(self, client, db_session):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        response = client.get("/api/verre/999")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Verre non trouvé"

    def test_get_verre_invalid_id(self, client):
        # Act
        response = client.get("/api/verre/invalid")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCreateVerre:
    def test_create_verre_success(self, client, db_session, auth_headers):
        # Arrange
        verre_data = {
            "nom": "Nouveau Verre",
            "variante": "Nouvelle Variante",
            "hauteur_min": 10,
            "hauteur_max": 20,
            "indice": 1.5,
        }
        mock_verre = Verre(id=1, **verre_data)
        db_session.add = MagicMock()
        db_session.commit = MagicMock()
        db_session.refresh = MagicMock(side_effect=lambda x: setattr(x, "id", 1))

        # Act
        response = client.post("/api/verres", json=verre_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["nom"] == verre_data["nom"]
        assert response.json()["id"] == 1
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()

    def test_create_verre_db_error(self, client, db_session, auth_headers):
        # Arrange
        verre_data = {"nom": "Test Verre"}
        db_session.commit.side_effect = SQLAlchemyError("DB Error")

        # Act
        response = client.post("/api/verres", json=verre_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Erreur lors de la création du verre" in response.json()["detail"]
        db_session.rollback.assert_called_once()


class TestUpdateVerre:
    def test_update_verre_success(self, client, db_session, mock_verre, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = (
            mock_verre
        )
        update_data = {"nom": "Verre Modifié"}

        # Act
        response = client.put(
            f"/api/verres/{mock_verre.id}", json=update_data, headers=auth_headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["nom"] == update_data["nom"]
        db_session.commit.assert_called_once()

    def test_update_verre_not_found(self, client, db_session, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None
        update_data = {"nom": "Verre Modifié"}

        # Act
        response = client.put("/api/verres/999", json=update_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Verre non trouvé"


class TestDeleteVerre:
    def test_delete_verre_success(self, client, db_session, mock_verre, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = (
            mock_verre
        )

        # Act
        response = client.delete(f"/api/verres/{mock_verre.id}", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        db_session.delete.assert_called_once()
        db_session.commit.assert_called_once()

    def test_delete_verre_not_found(self, client, db_session, auth_headers):
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        response = client.delete("/api/verres/999", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Verre non trouvé"

    def test_delete_verre_invalid_id(self, client, auth_headers):
        # Act
        response = client.delete("/api/verres/invalid", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
