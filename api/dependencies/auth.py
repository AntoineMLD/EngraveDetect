from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from api.auth.auth import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def verify_auth(token: str = Depends(oauth2_scheme)):
    """
    Dépendance pour vérifier l'authentification.
    Retourne le nom d'utilisateur si le token est valide.
    """
    return verify_token(token)


# Utiliser directement get_current_user comme dépendance
require_token = Depends(verify_auth)
