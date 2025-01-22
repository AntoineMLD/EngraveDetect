from fastapi import FastAPI
from api.routes.fournisseurs import router as fournisseur_router
from api.routes.gammes import router as gamme_router

app = FastAPI(title="API Verres")

# Ajouter les routes
app.include_router(fournisseur_router)
app.include_router(gamme_router)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Verres"}