import io

import pytest
from fastapi import status
from PIL import Image


def create_test_image():
    """Crée une image de test"""
    img = Image.new("RGB", (100, 100), color="white")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


class TestDetection:
    def test_detect_image_success(self, client, mocker):
        # Mock de la fonction predict_symbol
        mocker.patch(
            "api.routes.detection.predict_symbol", return_value=("test_symbol", 0.8)
        )

        # Mock du seuil de similarité
        mocker.patch("api.routes.detection.templates.similarity_threshold", 0.65)

        # Création d'une image de test
        img_bytes = create_test_image()

        # Envoi de la requête
        response = client.post(
            "/api/detect", files={"file": ("test.png", img_bytes, "image/png")}
        )

        # Vérification de la réponse
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["predicted_symbol"] == "test_symbol"
        assert data["similarity_score"] == 0.8
        assert data["is_confident"] is True
        assert data["message"] == "Détection réussie"
        assert "temp_detection.png" in data["image_path"]

    def test_detect_image_low_confidence(self, client, mocker):
        # Mock de la fonction predict_symbol avec une faible confiance
        mocker.patch(
            "api.routes.detection.predict_symbol", return_value=("test_symbol", 0.3)
        )

        # Mock du seuil de similarité
        mocker.patch("api.routes.detection.templates.similarity_threshold", 0.65)

        # Création d'une image de test
        img_bytes = create_test_image()

        # Envoi de la requête
        response = client.post(
            "/api/detect", files={"file": ("test.png", img_bytes, "image/png")}
        )

        # Vérification de la réponse
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["predicted_symbol"] == "test_symbol"
        assert data["similarity_score"] == 0.3
        assert data["is_confident"] is False
        assert "Confiance insuffisante" in data["message"]
        assert "temp_detection.png" in data["image_path"]

    def test_detect_invalid_extension(self, client):
        # Envoi d'un fichier avec une extension non autorisée
        response = client.post(
            "/api/detect", files={"file": ("test.txt", b"not an image", "text/plain")}
        )

        # Vérification de la réponse
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Format de fichier non supporté" in response.json()["detail"]

    def test_detect_corrupted_image(self, client):
        # Envoi d'un fichier corrompu avec une extension valide
        response = client.post(
            "/api/detect", files={"file": ("test.png", b"corrupted data", "image/png")}
        )

        # Vérification de la réponse
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "fichier semble corrompu" in response.json()["detail"]

    @pytest.mark.parametrize(
        "extension", [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]
    )
    def test_valid_extensions(self, client, mocker, extension):
        # Mock de la fonction predict_symbol
        mocker.patch(
            "api.routes.detection.predict_symbol", return_value=("test_symbol", 0.8)
        )

        # Mock du seuil de similarité
        mocker.patch("api.routes.detection.templates.similarity_threshold", 0.65)

        # Création d'une image de test
        img_bytes = create_test_image()

        # Envoi de la requête avec différentes extensions
        response = client.post(
            "/api/detect", files={"file": (f"test{extension}", img_bytes, "image/png")}
        )

        # Vérification de la réponse
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_confident"] is True
        assert data["predicted_symbol"] == "test_symbol"
