# api/routes/fournisseurs.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from database.models.base import Fournisseur
from database.config.database import get_db
from api.dependencies.auth import verify_auth

# Les modèles Pydantic pour la validation des données
class FournisseurBase(BaseModel):
    nom: str

    class Config:
        orm_mode = True

router = APIRouter()

# Routes GET (non protégées)
@router.get("/fournisseurs", response_model=List[FournisseurBase])
def get_fournisseurs(db: Session = Depends(get_db)):
    fournisseurs = db.query(Fournisseur).all()
    return [FournisseurBase.from_orm(f) for f in fournisseurs]

# Obtenir un fournisseur par ID
@router.get("/fournisseurs/{fournisseur_id}", response_model=FournisseurBase)
def get_fournisseur(fournisseur_id: int, db: Session = Depends(get_db)):
    fournisseur = db.query(Fournisseur).filter(Fournisseur.id == fournisseur_id).first()
    if fournisseur is None:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
    return FournisseurBase.from_orm(fournisseur)

# Routes protégées (POST, PUT, DELETE)
@router.post("/fournisseurs", response_model=FournisseurBase)
async def create_fournisseur(
    fournisseur: FournisseurBase, 
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_fournisseur = Fournisseur(nom=fournisseur.nom)
    db.add(db_fournisseur)
    db.commit()
    db.refresh(db_fournisseur)
    return db_fournisseur

@router.put("/fournisseurs/{fournisseur_id}", response_model=FournisseurBase)
async def update_fournisseur(
    fournisseur_id: int, 
    fournisseur: FournisseurBase, 
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_fournisseur = db.query(Fournisseur).filter(Fournisseur.id == fournisseur_id).first()
    if db_fournisseur is None:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
    
    db_fournisseur.nom = fournisseur.nom
    db.commit()
    db.refresh(db_fournisseur)
    return db_fournisseur

@router.delete("/fournisseurs/{fournisseur_id}")
async def delete_fournisseur(
    fournisseur_id: int, 
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_fournisseur = db.query(Fournisseur).filter(Fournisseur.id == fournisseur_id).first()
    if db_fournisseur is None:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
    
    db.delete(db_fournisseur)
    db.commit()
    return {"message": "Fournisseur supprimé"}