from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from database.models.base import Fournisseur, Gamme, SymboleTag, Verre, VerreSymbole


@pytest.fixture
def verre_test_data(db_session: Session) -> Dict:
    """Crée les données de test nécessaires pour un verre"""
    # Créer un fournisseur et une gamme de test
    fournisseur = Fournisseur(nom="Test Fournisseur")
    gamme = Gamme(nom="Test Gamme")
    db_session.add_all([fournisseur, gamme])
    db_session.commit()

    return {"nom": "Test Verre", "fournisseur_id": fournisseur.id, "gamme_id": gamme.id}


@pytest.fixture
def symbole_test_data() -> Dict:
    return {"nom": "Test Symbole", "description": "Description du symbole de test"}


@pytest.fixture
def verre_symbole_test_data() -> Dict:
    return {"score_confiance": 0.85, "est_valide": False}


def test_create_verre_symbole(
    client: TestClient,
    db_session: Session,
    auth_headers: Dict,
    verre_test_data: Dict,
    symbole_test_data: Dict,
    verre_symbole_test_data: Dict,
):
    """Test la création d'une association verre-symbole"""
    # Créer un verre et un symbole de test
    verre = Verre(**verre_test_data)
    symbole = SymboleTag(**symbole_test_data)
    db_session.add_all([verre, symbole])
    db_session.commit()

    # Données pour l'association
    association_data = {
        "verre_id": verre.id,
        "symbole_id": symbole.id,
        **verre_symbole_test_data,
    }

    response = client.post(
        f"/api/verres/{verre.id}/symboles/", headers=auth_headers, json=association_data
    )
    assert response.status_code == 200

    data = response.json()
    assert data["verre_id"] == verre.id
    assert data["symbole_id"] == symbole.id
    assert data["score_confiance"] == verre_symbole_test_data["score_confiance"]
    assert data["est_valide"] == verre_symbole_test_data["est_valide"]


def test_get_symboles_for_verre(
    client: TestClient,
    db_session: Session,
    auth_headers: Dict,
    verre_test_data: Dict,
    symbole_test_data: Dict,
    verre_symbole_test_data: Dict,
):
    """Test la récupération des symboles associés à un verre"""
    # Créer un verre et un symbole de test
    verre = Verre(**verre_test_data)
    symbole = SymboleTag(**symbole_test_data)
    db_session.add_all([verre, symbole])
    db_session.commit()

    # Créer l'association
    association = VerreSymbole(
        verre_id=verre.id, symbole_id=symbole.id, **verre_symbole_test_data
    )
    db_session.add(association)
    db_session.commit()

    response = client.get(f"/api/verres/{verre.id}/symboles/", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["verre_id"] == verre.id
    assert data[0]["symbole_id"] == symbole.id


def test_validate_verre_symbole(
    client: TestClient,
    db_session: Session,
    auth_headers: Dict,
    verre_test_data: Dict,
    symbole_test_data: Dict,
    verre_symbole_test_data: Dict,
):
    """Test la validation d'une association verre-symbole"""
    # Créer un verre et un symbole de test
    verre = Verre(**verre_test_data)
    symbole = SymboleTag(**symbole_test_data)
    db_session.add_all([verre, symbole])
    db_session.commit()

    # Créer l'association
    association = VerreSymbole(
        verre_id=verre.id, symbole_id=symbole.id, **verre_symbole_test_data
    )
    db_session.add(association)
    db_session.commit()

    # Données de validation
    validation_data = {"est_valide": True, "valide_par": "testuser"}

    response = client.put(
        f"/api/verres/{verre.id}/symboles/{symbole.id}",
        headers=auth_headers,
        json=validation_data,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["est_valide"] == True
    assert data["valide_par"] == "testuser"


def test_delete_verre_symbole(
    client: TestClient,
    db_session: Session,
    auth_headers: Dict,
    verre_test_data: Dict,
    symbole_test_data: Dict,
    verre_symbole_test_data: Dict,
):
    """Test la suppression d'une association verre-symbole"""
    # Créer un verre et un symbole de test
    verre = Verre(**verre_test_data)
    symbole = SymboleTag(**symbole_test_data)
    db_session.add_all([verre, symbole])
    db_session.commit()

    # Créer l'association
    association = VerreSymbole(
        verre_id=verre.id, symbole_id=symbole.id, **verre_symbole_test_data
    )
    db_session.add(association)
    db_session.commit()

    response = client.delete(
        f"/api/verres/{verre.id}/symboles/{symbole.id}", headers=auth_headers
    )
    assert response.status_code == 200

    # Vérifier que l'association a été supprimée
    deleted_association = (
        db_session.query(VerreSymbole)
        .filter(
            VerreSymbole.verre_id == verre.id, VerreSymbole.symbole_id == symbole.id
        )
        .first()
    )
    assert deleted_association is None


def test_create_verre_symbole_invalid_verre(
    client: TestClient,
    db_session: Session,
    auth_headers: Dict,
    symbole_test_data: Dict,
    verre_symbole_test_data: Dict,
):
    """Test la création d'une association avec un verre inexistant"""
    # Créer un symbole de test
    symbole = SymboleTag(**symbole_test_data)
    db_session.add(symbole)
    db_session.commit()

    # Données pour l'association avec un verre inexistant
    association_data = {
        "verre_id": 999999,
        "symbole_id": symbole.id,
        **verre_symbole_test_data,
    }

    response = client.post(
        "/api/verres/999999/symboles/", headers=auth_headers, json=association_data
    )
    assert response.status_code == 404


def test_create_verre_symbole_invalid_symbole(
    client: TestClient,
    db_session: Session,
    auth_headers: Dict,
    verre_test_data: Dict,
    verre_symbole_test_data: Dict,
):
    """Test la création d'une association avec un symbole inexistant"""
    # Créer un verre de test
    verre = Verre(**verre_test_data)
    db_session.add(verre)
    db_session.commit()

    # Données pour l'association avec un symbole inexistant
    association_data = {
        "verre_id": verre.id,
        "symbole_id": 999999,
        **verre_symbole_test_data,
    }

    response = client.post(
        f"/api/verres/{verre.id}/symboles/", headers=auth_headers, json=association_data
    )
    assert response.status_code == 404
