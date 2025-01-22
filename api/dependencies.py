from database.config.database import SessionLocal


def get_db():
    return SessionLocal