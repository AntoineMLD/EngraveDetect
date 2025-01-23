# api/routes/materiaux.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from database.models.base import Materiau
from database.config.database import get_db
from api.dependencies.auth import verify_auth


class MateriauBase(BaseModel):
    nom: str 

    class Config:
        orm_mode = True 

router = APIRouter()

# Routes GET (non protégées)
@router.get("/materiaux", response_model=List[MateriauBase])
def get_materiaux(db: Session = Depends(get_db)):
    return db.query(Materiau).all()

@router.get("/materiaux/{materiau_id}", response_model=MateriauBase)
def get_materiau(materiau_id: int, db: Session = Depends(get_db)):
    materiau = db.query(Materiau).filter(Materiau.id == materiau_id).first()
    if materiau is None:
        raise HTTPException(status_code=404, detail="Materiau non trouvé")
    return materiau

# Routes protégées (POST, PUT, DELETE)
@router.post("/materiaux", response_model=MateriauBase)
async def create_materiau(
    materiau: MateriauBase, 
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_materiau = Materiau(nom=materiau.nom)
    db.add(db_materiau)
    db.commit()
    db.refresh(db_materiau)
    return db_materiau

@router.put("/materiaux/{materiau_id}", response_model=MateriauBase)
async def update_materiau(
    materiau_id: int, 
    materiau: MateriauBase, 
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_materiau = db.query(Materiau).filter(Materiau.id == materiau_id).first()
    if db_materiau is None:
        raise HTTPException(status_code=404, detail="Materiau non trouvé")
    
    db_materiau.nom = materiau.nom
    db.commit()
    db.refresh(db_materiau)
    return db_materiau

@router.delete("/materiaux/{materiau_id}")
async def delete_materiau(
    materiau_id: int, 
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_materiau = db.query(Materiau).filter(Materiau.id == materiau_id).first()
    if db_materiau is None:
        raise HTTPException(status_code=404, detail="Materiau non trouvé")
    
    db.delete(db_materiau)
    db.commit()
    return {"message": "Materiau supprimé"}