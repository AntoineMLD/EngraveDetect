import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

# Configuration depuis les variables d'environnement
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Vérifier que les variables requises sont définies
if not all([SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD]):
    raise ValueError("Variables d'environnement manquantes pour l'authentification")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Fonction pour créer un token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    if SECRET_KEY is None:
        raise ValueError("La clé secrète n'est pas définie")

    to_encode = data.copy()
    current_time = datetime.utcnow()
    if expires_delta:
        expire = current_time + expires_delta
    else:
        expire = current_time + timedelta(minutes=15)
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Fonction pour vérifier un token
def verify_token(token: str):
    try:
        # Décoder le token sans vérifier l'expiration
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False}
        )

        # Vérifier manuellement l'expiration
        exp = payload.get("exp")
        if exp is not None and exp < int(datetime.utcnow().timestamp()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide"
            )

        # Vérifier le sujet
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide"
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide"
        )
