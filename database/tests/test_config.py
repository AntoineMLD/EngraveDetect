import os

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from database.config.database import (
    Base,
    check_database_connection,
    create_db_engine,
    get_database_url,
    get_db,
    init_database,
)


def test_get_database_url():
    """Test la génération de l'URL de la base de données"""
    url = get_database_url()
    assert url.startswith("sqlite:///")
    assert "data/verres.db" in url.replace("\\", "/")


def test_create_db_engine():
    """Test la création du moteur de base de données"""
    engine = create_db_engine()
    assert isinstance(engine, Engine)
    assert engine.url.drivername == "sqlite"


def test_get_db():
    """Test la création d'une session de base de données"""
    # Initialise la base de données avant le test
    init_database()

    db = next(get_db())
    try:
        assert isinstance(db, Session)
        # Test que la session est active
        assert db.is_active
    finally:
        db.close()


def test_init_database():
    """Test l'initialisation de la base de données"""
    # Devrait s'exécuter sans erreur
    init_database()
    # Vérifie que les tables ont été créées
    engine = create_db_engine()
    for table in Base.metadata.tables.values():
        assert engine.dialect.has_table(engine.connect(), table.name)


def test_check_database_connection():
    """Test la vérification de la connexion à la base de données"""
    # Initialise la base de données avant le test
    init_database()
    assert check_database_connection() is True


def test_database_session_rollback():
    """Test le rollback automatique en cas d'erreur"""
    # Initialise la base de données avant le test
    init_database()

    db = next(get_db())
    try:
        # Simuler une erreur avec une requête invalide
        with pytest.raises(Exception):
            db.execute(text("SELECT * FROM table_inexistante"))
        # Vérifie que la session est toujours utilisable après le rollback
        assert db.is_active
    finally:
        db.close()


def test_database_session_commit():
    """Test le commit d'une transaction"""
    # Initialise la base de données avant le test
    init_database()

    db = next(get_db())
    try:
        # Exécute une requête valide
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1
        db.commit()
        assert db.is_active
    finally:
        db.close()
