from fastapi import FastAPI
from api.routes.fournisseurs import router as fournisseur_router
from api.routes.gammes import router as gamme_router
from api.routes.materiaux import router as materiau_router
from api.routes.series import router as serie_router
from api.routes.traitements import router as traitement_router
from api.routes.verres import router as verre_router

app = FastAPI(title="API Verres")

# Ajouter les routes
app.include_router(fournisseur_router)
app.include_router(gamme_router)
app.include_router(materiau_router)
app.include_router(serie_router)
app.include_router(traitement_router)
app.include_router(verre_router)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Verres"}