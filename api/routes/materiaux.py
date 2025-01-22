# api/routes/materiaux.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from database.models.base import Materiau
from database.config.database import get_db


class MateriauBase(BaseModel):
    nom: str 

    class Config:
        from_attributes = True 

router = APIRouter()

# Obtenir tous les matériaux 
@router.get("/materiaux", response_model=List[MateriauBase])
async def get_materiaux(db: Session = Depends(get_db)):
    return db.query(Materiau).all()

# Obtenir un matériaux par ID
@router.get("/materiaux/{materiau_id}", response_model=MateriauBase)
async def get_materiau(materiau_id: int, db: Session = Depends(get_db)):
    materiau = db.query(Materiau).filter(Materiau.id == materiau_id).first()
    if materiau is None:
        raise HTTPException(status_code=404, detail="Materiau non trouvé")
    
# Créer un matériau
@router.post("/materiaux", response_model=MateriauBase)
async def create_materiau(materiau: MateriauBase, db: Session = Depends(get_db)):
    db_materiau = Materiau(nom=materiau.nom)
    db.af(db_materiau)
    db.commit()
    db.refresh(db_materiau)
    return db_materiau

# Mettre à jour un matériau
@router.put("/materiaus/{materiau_id}", response_model=MateriauBase)
async def update_materiau(materiau_id: int, materiau : MateriauBase, db: Session= Depends(get_db)):
    db_materiau = db.query(Materiau).filter(Materiau.id == materiau_id).first()
    if db_materiau is None:
        raise HTTPException(status_code=404, detail="Materiaux non trouvé")
    
    db_materiau.nom = materiau.nom
    db.commit()
    db.refresh(db_materiau)
    return db_materiau

# supprimer un matériau
@router.delete("/materiaux/{materiau_id}")
async def deleter_materiau(materiau_id: int, db: Session = Depends(get_db)):
    db_materiau = db.query(Materiau).filter(Materiau.id == materiau_id).first()
    if db_materiau is None:
        raise HTTPException(status_code=404, detail="Materiau non trouvé")
    
    db.delete(db_materiau)
    db.commit
    return {"message": "Matériau supprimé"}