from fastapi import FastAPI, Depends, HTTPException, status
from api.routes.fournisseurs import router as fournisseur_router
from api.routes.gammes import router as gamme_router
from api.routes.materiaux import router as materiau_router
from api.routes.series import router as serie_router
from api.routes.traitements import router as traitement_router
from api.routes.verres import router as verre_router
from api.routes.detection import router as detection_router
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from api.auth.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
import os
from dotenv import load_dotenv, find_dotenv
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Trouver et charger le fichier .env
dotenv_path = find_dotenv()
logger.info(f"Fichier .env trouvé: {dotenv_path}")
load_dotenv(dotenv_path, override=True)  

app = FastAPI(title="API Verres")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Fonction de dépendance pour vérifier le token
async def verify_token(token: Annotated[str, Depends(oauth2_scheme)]):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token d'authentification invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

# Route pour obtenir un token
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Lire directement le contenu du fichier .env
    with open('.env', 'r') as f:
        env_content = f.read()
    logger.info("Contenu du fichier .env:")
    logger.info(env_content)
    
    # Récupérer les credentials depuis les variables d'environnement
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    # Logs pour le débogage
    logger.info(f"Tentative de connexion pour l'utilisateur: {form_data.username}")
    logger.info(f"Valeurs des variables d'environnement:")
    logger.info(f"ADMIN_USERNAME: {admin_username}")
    logger.info(f"ADMIN_PASSWORD: {admin_password}")
    
    if form_data.username != admin_username or form_data.password != admin_password:
        logger.warning(f"Échec de l'authentification pour l'utilisateur: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"Authentification réussie pour l'utilisateur: {form_data.username}")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Ajouter les routes
app.include_router(fournisseur_router)
app.include_router(gamme_router)
app.include_router(materiau_router)
app.include_router(serie_router)
app.include_router(traitement_router)
app.include_router(verre_router)
app.include_router(detection_router)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Verres"}