# api/routes/traitements.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from database.models.base import Traitement
from database.config.database import get_db

class TraitementBase(BaseModel):
    nom : str

    class Config:
        from_attributes = True 

router = APIRouter()

# obtenir tous les traitements
@router.get("/traitements", response_model=List[TraitementBase])
async def get_traitements(db: Session = Depends(get_db)):
    return db.query(Traitement).all()

# obtenir un traitement par ID 
@router.get("/traitement/{traitement_id}", response_model=TraitementBase)
async def get_traitement(traitement_id: int, db: Session = Depends(get_db)):
    traitement = db.query(Traitement).filter(Traitement.id == traitement_id).first()
    if traitement is None:
        raise HTTPException(status_code=404, detail="Traitement non trouvé")
    return traitement

# créer un traitement
@router.post("/traitement", response_model=TraitementBase)
async def create_traitement(traitement: TraitementBase, db: Session = Depends(get_db)):
    db_traitement = Traitement(nom=traitement.nom)
    db.add(db_traitement)
    db.commit()
    db.refresh(db_traitement)
    return db_traitement

# mettre à jour un traitement
@router.put("/traitements/{traitement_id}", response_model=BaseModel)
async def update_traitement(traitement_id: int, traitement: TraitementBase, db: Session = Depends(get_db)):
    db_traitement = db.query(Traitement).filter(Traitement.id == traitement_id).first()
    if db_traitement is None:
        raise HTTPException(status_code=404, detail="Traitement non trouvé")
    
    db_traitement.nom = traitement.nom
    db.commit()
    db.refresh(db_traitement)
    return db_traitement

# supprimer un traitement
@router.delete("/traitements/{traitement_id}")
async def delete_traitement(traitement_id: int, db: Session = Depends(get_db))
    db_traitement = db.query(Traitement).filter(Traitement.id == traitement_id).first()
    if db_traitement is None:
        raise HTTPException(status_code=404, detail="Traitement non trouvé")
    
    db.delete(db_traitement)
    db.commit()
    return {"message": "Traitement supprimé"}
