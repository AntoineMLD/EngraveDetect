from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from database.models.base import SymboleTag


@pytest.fixture
def symbole_test_data() -> Dict:
    return {
        "nom": "Test Symbole",
        "description": "Description du symbole de test"
    }


def test_create_symbole(client: TestClient, db_session: Session, auth_headers: Dict, symbole_test_data: Dict):
    """Test la création d'un symbole"""
    response = client.post("/api/symboles/", headers=auth_headers, json=symbole_test_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["nom"] == symbole_test_data["nom"]
    assert data["description"] == symbole_test_data["description"]
    assert "id" in data


def test_get_symboles(client: TestClient, db_session: Session, auth_headers: Dict, symbole_test_data: Dict):
    """Test la récupération de la liste des symboles"""
    # Créer un symbole de test
    symbole = SymboleTag(**symbole_test_data)
    db_session.add(symbole)
    db_session.commit()
    
    response = client.get("/api/symboles/", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["nom"] == symbole_test_data["nom"]


def test_get_symbole(client: TestClient, db_session: Session, auth_headers: Dict, symbole_test_data: Dict):
    """Test la récupération d'un symbole par son ID"""
    # Créer un symbole de test
    symbole = SymboleTag(**symbole_test_data)
    db_session.add(symbole)
    db_session.commit()
    
    response = client.get(f"/api/symboles/{symbole.id}", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["nom"] == symbole_test_data["nom"]
    assert data["description"] == symbole_test_data["description"]


def test_update_symbole(client: TestClient, db_session: Session, auth_headers: Dict, symbole_test_data: Dict):
    """Test la mise à jour d'un symbole"""
    # Créer un symbole de test
    symbole = SymboleTag(**symbole_test_data)
    db_session.add(symbole)
    db_session.commit()
    
    # Données de mise à jour
    update_data = {
        "nom": "Symbole Modifié",
        "description": "Description modifiée"
    }
    
    response = client.put(f"/api/symboles/{symbole.id}", headers=auth_headers, json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["nom"] == update_data["nom"]
    assert data["description"] == update_data["description"]


def test_delete_symbole(client: TestClient, db_session: Session, auth_headers: Dict, symbole_test_data: Dict):
    """Test la suppression d'un symbole"""
    # Créer un symbole de test
    symbole = SymboleTag(**symbole_test_data)
    db_session.add(symbole)
    db_session.commit()
    
    response = client.delete(f"/api/symboles/{symbole.id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Vérifier que le symbole a été supprimé
    deleted_symbole = db_session.query(SymboleTag).filter(SymboleTag.id == symbole.id).first()
    assert deleted_symbole is None


def test_get_symbole_not_found(client: TestClient, auth_headers: Dict):
    """Test la récupération d'un symbole inexistant"""
    response = client.get("/api/symboles/999999", headers=auth_headers)
    assert response.status_code == 404


def test_create_symbole_invalid_data(client: TestClient, auth_headers: Dict):
    """Test la création d'un symbole avec des données invalides"""
    invalid_data = {
        "description": "Description sans nom"  # Manque le champ 'nom' requis
    }
    
    response = client.post("/api/symboles/", headers=auth_headers, json=invalid_data)
    assert response.status_code == 422  # Validation error 