import logging
import os

import pytest

from database.utils.logger import CustomFormatter, setup_logger


def test_setup_logger_without_file():
    """Test la création d'un logger sans fichier"""
    logger = setup_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"
    assert logger.level == logging.DEBUG
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)


def test_setup_logger_with_file(tmp_path):
    """Test la création d'un logger avec fichier"""
    log_file = tmp_path / "test.log"
    logger = setup_logger("test_logger", str(log_file))

    assert isinstance(logger, logging.Logger)
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    assert any(
        isinstance(h, logging.handlers.RotatingFileHandler) for h in logger.handlers
    )
    assert os.path.exists(log_file)


def test_logger_levels(tmp_path):
    """Test les différents niveaux de log"""
    log_file = tmp_path / "test.log"
    logger = setup_logger("test_logger", str(log_file))

    # Test chaque niveau de log
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    # Vérifie que les messages ont été écrits dans le fichier
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Debug message" in content
        assert "Info message" in content
        assert "Warning message" in content
        assert "Error message" in content
        assert "Critical message" in content


def test_custom_formatter():
    """Test le formateur personnalisé"""
    formatter = CustomFormatter()

    # Crée un record de log factice
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)
    assert "test" in formatted  # Nom du logger
    assert "INFO" in formatted  # Niveau de log
    assert "Test message" in formatted  # Message


def test_logger_rotation(tmp_path):
    """Test la rotation des fichiers de log"""
    log_file = tmp_path / "test.log"
    logger = setup_logger("test_logger", str(log_file))

    # Récupère le handler de fichier
    file_handler = next(
        h
        for h in logger.handlers
        if isinstance(h, logging.handlers.RotatingFileHandler)
    )

    # Vérifie la configuration de la rotation
    assert file_handler.maxBytes == 10485760  # 10MB
    assert file_handler.backupCount == 5

    # Génère suffisamment de logs pour déclencher une rotation
    large_msg = "x" * 1024 * 1024  # 1MB de données
    for _ in range(11):  # Devrait créer au moins un fichier de backup
        logger.info(large_msg)

    # Vérifie qu'au moins un fichier de backup a été créé
    backup_files = list(tmp_path.glob("test.log.*"))
    assert len(backup_files) > 0


def test_logger_encoding(tmp_path):
    """Test l'encodage des logs"""
    log_file = tmp_path / "test.log"
    logger = setup_logger("test_logger", str(log_file))

    # Test avec des caractères spéciaux
    special_chars = "éèàùç漢字"
    logger.info(special_chars)

    # Vérifie que les caractères sont correctement encodés
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert special_chars in content
