# api/routes/traitements.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from database.models.base import Traitement
from database.config.database import get_db
from api.dependencies.auth import verify_auth

class TraitementBase(BaseModel):
    id: int
    nom: str
    type: str

    class Config:
        orm_mode = True

router = APIRouter()

# Routes GET (non protégées)
@router.get("/traitements", response_model=List[TraitementBase])
def get_traitements(db: Session = Depends(get_db)):
    traitements = db.query(Traitement).all()
    return [{"id": t.id, "nom": t.nom, "type": t.type} for t in traitements]

@router.get("/traitements/{traitement_id}", response_model=TraitementBase)
def get_traitement(traitement_id: int, db: Session = Depends(get_db)):
    traitement = db.query(Traitement).filter(Traitement.id == traitement_id).first()
    if traitement is None:
        raise HTTPException(status_code=404, detail="Traitement non trouvé")
    return {"id": traitement.id, "nom": traitement.nom, "type": traitement.type}

# Routes protégées (POST, PUT, DELETE)
@router.post("/traitements", response_model=TraitementBase)
async def create_traitement(
    traitement: TraitementBase, 
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_traitement = Traitement(nom=traitement.nom, type=traitement.type)
    db.add(db_traitement)
    db.commit()
    db.refresh(db_traitement)
    return {"id": db_traitement.id, "nom": db_traitement.nom, "type": db_traitement.type}

@router.put("/traitements/{traitement_id}", response_model=TraitementBase)
async def update_traitement(
    traitement_id: int, 
    traitement: TraitementBase, 
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_traitement = db.query(Traitement).filter(Traitement.id == traitement_id).first()
    if db_traitement is None:
        raise HTTPException(status_code=404, detail="Traitement non trouvé")
    
    db_traitement.nom = traitement.nom
    db_traitement.type = traitement.type
    db.commit()
    db.refresh(db_traitement)
    return db_traitement

@router.delete("/traitements/{traitement_id}")
async def delete_traitement(
    traitement_id: int, 
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_traitement = db.query(Traitement).filter(Traitement.id == traitement_id).first()
    if db_traitement is None:
        raise HTTPException(status_code=404, detail="Traitement non trouvé")
    
    db.delete(db_traitement)
    db.commit()
    return {"message": "Traitement supprimé"}
