import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.config.database import get_db
from database.models.base import Base

# Création d'une base de données en mémoire pour les tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """Crée un moteur de base de données de test"""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db_session(test_engine):
    """Crée une session de base de données de test"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def override_get_db(test_db_session):
    """Override la dépendance get_db pour utiliser la session de test"""

    def _get_test_db():
        try:
            yield test_db_session
        finally:
            test_db_session.close()

    return _get_test_db
