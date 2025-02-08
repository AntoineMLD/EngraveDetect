import pytest
from fastapi.testclient import TestClient
import io
from PIL import Image
import numpy as np

def test_root(client):
    """Test de la route racine"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API Verres"}

def test_token_invalid_credentials(client):
    """Test de l'authentification avec des credentials invalides"""
    response = client.post(
        "/token",
        data={"username": "wrong", "password": "wrong"}
    )
    assert response.status_code == 401

def test_detect_invalid_file(client):
    """Test de la détection avec un fichier invalide"""
    response = client.post(
        "/api/detect",
        files={"file": ("test.txt", b"invalid content", "text/plain")}
    )
    assert response.status_code == 400

def test_detect_valid_image(client):
    """Test de la détection avec une image valide"""
    # Créer une image test
    img = Image.fromarray(np.zeros((100, 100), dtype=np.uint8))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    response = client.post(
        "/api/detect",
        files={"file": ("test.png", img_byte_arr, "image/png")}
    )
    assert response.status_code == 200
    assert "predicted_symbol" in response.json()
    assert "similarity_score" in response.json()
    assert "is_confident" in response.json() 